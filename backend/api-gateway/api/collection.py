"""
Camera Image Collection API Endpoints
======================================

Manage camera image collection runs and analysis orchestration.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field

from database import get_db
from models import CollectionRun, Camera, WorkZone
from services import analysis_orchestration_service

router = APIRouter()


# Pydantic schemas
class CollectionStartRequest(BaseModel):
    """Schema for starting a new collection run"""
    camera_ids: Optional[List[int]] = Field(None, description="Specific cameras to collect from (all if None)")
    auto_analyze: bool = Field(default=True, description="Automatically analyze images after collection")
    min_risk_threshold: int = Field(default=5, ge=1, le=10, description="Minimum risk score to store work zones")


class CollectionResponse(BaseModel):
    """Schema for collection run response"""
    id: int
    collection_id: str
    status: str
    total_cameras: int
    images_collected: int
    images_failed: int
    work_zones_detected: int
    high_risk_zones: int
    started_at: str
    completed_at: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class CollectionStatsResponse(BaseModel):
    """Schema for collection statistics"""
    total_runs: int
    successful_runs: int
    failed_runs: int
    total_images_collected: int
    total_work_zones_detected: int
    last_run_at: Optional[str]


# POST /api/collection/start - Start new collection run
@router.post("/start", response_model=CollectionResponse, status_code=201)
async def start_collection(
    request: CollectionStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new camera image collection run

    This initiates collection from all active cameras (or specified subset).
    If auto_analyze=True, triggers AI analysis after collection completes.

    Args:
        request: Collection configuration
        background_tasks: FastAPI background tasks for async processing

    Returns:
        Collection run object with unique collection_id for tracking
    """
    # Generate unique collection ID
    collection_id = f"COLLECT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    # Count cameras to collect from
    if request.camera_ids:
        total_cameras = len(request.camera_ids)
    else:
        count_query = select(func.count(Camera.id)).where(Camera.active == True)
        result = await db.execute(count_query)
        total_cameras = result.scalar()

    # Create collection run record
    collection_run = CollectionRun(
        collection_id=collection_id,
        status="in_progress",
        total_cameras=total_cameras,
        images_collected=0,
        images_failed=0,
        work_zones_detected=0,
        high_risk_zones=0
    )
    db.add(collection_run)
    await db.commit()
    await db.refresh(collection_run)

    # Queue background task for actual collection and analysis
    if request.auto_analyze:
        # Get camera IDs to analyze
        if request.camera_ids:
            camera_ids_to_process = request.camera_ids
        else:
            # Get all active cameras
            cameras_query = select(Camera.id).where(Camera.active == True)
            cameras_result = await db.execute(cameras_query)
            camera_ids_to_process = [row[0] for row in cameras_result.all()]

        # Queue the analysis workflow
        background_tasks.add_task(
            analysis_orchestration_service.run_full_analysis,
            camera_ids_to_process,
            collection_id,
            request.min_risk_threshold,
            db
        )

    return CollectionResponse.model_validate(collection_run)


# GET /api/collection/status/{collection_id} - Get collection status
@router.get("/status/{collection_id}", response_model=CollectionResponse)
async def get_collection_status(
    collection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a specific collection run

    Args:
        collection_id: Unique collection identifier

    Returns:
        Collection run status and progress
    """
    query = select(CollectionRun).where(CollectionRun.collection_id == collection_id)
    result = await db.execute(query)
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    return CollectionResponse.model_validate(collection)


# POST /api/collection/analyze - Trigger AI analysis on collected images
@router.post("/analyze/{collection_id}")
async def analyze_collection(
    collection_id: str,
    background_tasks: BackgroundTasks,
    min_risk_threshold: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI analysis on images from a collection run

    This can be called manually if auto_analyze was disabled, or to
    re-analyze with different parameters.

    Args:
        collection_id: Collection to analyze
        min_risk_threshold: Minimum risk score to store work zones

    Returns:
        Status message
    """
    query = select(CollectionRun).where(CollectionRun.collection_id == collection_id)
    result = await db.execute(query)
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    if collection.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot analyze collection with status '{collection.status}'"
        )

    # Queue background task for re-analysis
    background_tasks.add_task(
        analysis_orchestration_service.reanalyze_existing_images,
        collection_id,
        min_risk_threshold,
        db
    )

    return {
        "message": "Re-analysis queued",
        "collection_id": collection_id,
        "images_to_analyze": collection.images_collected,
        "min_risk_threshold": min_risk_threshold
    }


# GET /api/collection/history - Get collection history
@router.get("/history", response_model=List[CollectionResponse])
async def get_collection_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None, pattern="^(in_progress|completed|failed)$"),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    Get collection run history

    Args:
        skip: Pagination offset
        limit: Max results
        status: Filter by status
        days: Last N days

    Returns:
        List of collection runs
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = select(CollectionRun).where(CollectionRun.started_at >= cutoff)

    if status:
        query = query.where(CollectionRun.status == status)

    query = query.order_by(CollectionRun.started_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    collections = result.scalars().all()

    return [CollectionResponse.model_validate(c) for c in collections]


# GET /api/collection/latest - Get latest collection run
@router.get("/latest", response_model=CollectionResponse)
async def get_latest_collection(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent collection run

    Returns:
        Latest collection run
    """
    query = select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(1)
    result = await db.execute(query)
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="No collection runs found")

    return CollectionResponse.model_validate(collection)


# DELETE /api/collection/{collection_id} - Delete collection run
@router.delete("/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete collection run record

    Note: This only deletes the collection record, not the images or work zones.
    Use for cleanup of failed/incomplete collection runs.
    """
    query = select(CollectionRun).where(CollectionRun.collection_id == collection_id)
    result = await db.execute(query)
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

    await db.delete(collection)
    await db.commit()


# GET /api/collection/stats - Collection statistics
@router.get("/stats/summary", response_model=CollectionStatsResponse)
async def get_collection_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get collection statistics

    Args:
        days: Time window for statistics

    Returns:
        Collection statistics
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Total runs
    total_query = select(func.count(CollectionRun.id)).where(CollectionRun.started_at >= cutoff)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Successful runs
    success_query = select(func.count(CollectionRun.id)).where(
        and_(CollectionRun.started_at >= cutoff, CollectionRun.status == "completed")
    )
    success_result = await db.execute(success_query)
    successful = success_result.scalar()

    # Failed runs
    failed_query = select(func.count(CollectionRun.id)).where(
        and_(CollectionRun.started_at >= cutoff, CollectionRun.status == "failed")
    )
    failed_result = await db.execute(failed_query)
    failed = failed_result.scalar()

    # Total images collected
    images_query = select(func.sum(CollectionRun.images_collected)).where(
        CollectionRun.started_at >= cutoff
    )
    images_result = await db.execute(images_query)
    total_images = images_result.scalar() or 0

    # Total work zones detected
    wz_query = select(func.sum(CollectionRun.work_zones_detected)).where(
        CollectionRun.started_at >= cutoff
    )
    wz_result = await db.execute(wz_query)
    total_wz = wz_result.scalar() or 0

    # Last run timestamp
    last_query = select(CollectionRun.started_at).order_by(
        CollectionRun.started_at.desc()
    ).limit(1)
    last_result = await db.execute(last_query)
    last_run = last_result.scalar_one_or_none()

    return CollectionStatsResponse(
        total_runs=total,
        successful_runs=successful,
        failed_runs=failed,
        total_images_collected=int(total_images),
        total_work_zones_detected=int(total_wz),
        last_run_at=last_run.isoformat() if last_run else None
    )
