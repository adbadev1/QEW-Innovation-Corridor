"""
Work Zones API Endpoints
=========================

Manage AI-detected work zones with risk assessments.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel, Field

from database import get_db
from models import WorkZone, Camera

router = APIRouter()


# Pydantic schemas
class WorkZoneCreate(BaseModel):
    """Schema for creating a work zone"""
    camera_id: int
    view_id: Optional[int] = None
    latitude: float
    longitude: float
    risk_score: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    workers: int = Field(default=0, ge=0)
    vehicles: int = Field(default=0, ge=0)
    equipment: int = Field(default=0, ge=0)
    barriers: bool = False
    hazards: Optional[List[str]] = None
    violations: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    mto_book_compliance: bool = False
    gcp_image_url: Optional[str] = None
    collection_id: Optional[str] = None
    model: str = "gemini-2.0-flash-exp"
    synthetic: bool = False


class WorkZoneResponse(BaseModel):
    """Schema for work zone response"""
    id: int
    camera_id: int
    view_id: Optional[int]
    latitude: float
    longitude: float
    risk_score: int
    confidence: float
    workers: int
    vehicles: int
    equipment: int
    barriers: bool
    hazards: Optional[List[str]]
    violations: Optional[List[str]]
    recommendations: Optional[List[str]]
    mto_book_compliance: bool
    gcp_image_url: Optional[str]
    collection_id: Optional[str]
    model: str
    synthetic: bool
    status: str
    detected_at: str
    resolved_at: Optional[str]

    class Config:
        from_attributes = True


# GET /api/work-zones - List work zones
@router.get("/", response_model=List[WorkZoneResponse])
async def get_work_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(active|resolved|archived)$"),
    min_risk: int = Query(0, ge=0, le=10, description="Minimum risk score"),
    hours: Optional[int] = Query(None, ge=1, description="Last N hours"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of work zones with filtering

    Args:
        skip: Pagination offset
        limit: Max results
        status: Filter by status (active/resolved/archived)
        min_risk: Minimum risk score
        hours: Only show detections from last N hours

    Returns:
        List of work zone objects
    """
    query = select(WorkZone)

    # Apply filters
    if status:
        query = query.where(WorkZone.status == status)

    if min_risk > 0:
        query = query.where(WorkZone.risk_score >= min_risk)

    if hours:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = query.where(WorkZone.detected_at >= cutoff)

    # Ordering and pagination
    query = query.order_by(WorkZone.detected_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    work_zones = result.scalars().all()

    return [WorkZoneResponse.model_validate(wz) for wz in work_zones]


# GET /api/work-zones/active - Get currently active work zones
@router.get("/active", response_model=List[WorkZoneResponse])
async def get_active_work_zones(
    min_risk: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Get currently active work zones

    Only returns work zones with status='active' and risk >= min_risk.
    This is the primary endpoint for the dashboard map.
    """
    query = select(WorkZone).where(
        and_(
            WorkZone.status == "active",
            WorkZone.risk_score >= min_risk
        )
    ).order_by(WorkZone.risk_score.desc())

    result = await db.execute(query)
    work_zones = result.scalars().all()

    return [WorkZoneResponse.model_validate(wz) for wz in work_zones]


# GET /api/work-zones/history - Get historical work zones
@router.get("/history", response_model=List[WorkZoneResponse])
async def get_work_zone_history(
    camera_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=90),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get work zone detection history

    Args:
        camera_id: Filter by specific camera
        days: Last N days
        skip: Pagination offset
        limit: Max results

    Returns:
        Historical work zone detections
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = select(WorkZone).where(WorkZone.detected_at >= cutoff)

    if camera_id:
        query = query.where(WorkZone.camera_id == camera_id)

    query = query.order_by(WorkZone.detected_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    work_zones = result.scalars().all()

    return [WorkZoneResponse.model_validate(wz) for wz in work_zones]


# GET /api/work-zones/{id} - Get specific work zone
@router.get("/{work_zone_id}", response_model=WorkZoneResponse)
async def get_work_zone(
    work_zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific work zone by ID"""
    query = select(WorkZone).where(WorkZone.id == work_zone_id)
    result = await db.execute(query)
    work_zone = result.scalar_one_or_none()

    if not work_zone:
        raise HTTPException(status_code=404, detail=f"Work zone {work_zone_id} not found")

    return WorkZoneResponse.model_validate(work_zone)


# POST /api/work-zones - Create new work zone
@router.post("/", response_model=WorkZoneResponse, status_code=201)
async def create_work_zone(
    work_zone_data: WorkZoneCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new work zone detection

    This is called after AI analysis detects a work zone.
    """
    # Verify camera exists
    camera_query = select(Camera).where(Camera.id == work_zone_data.camera_id)
    camera_result = await db.execute(camera_query)
    camera = camera_result.scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {work_zone_data.camera_id} not found")

    # Create work zone
    work_zone = WorkZone(**work_zone_data.model_dump())
    db.add(work_zone)
    await db.commit()
    await db.refresh(work_zone)

    return WorkZoneResponse.model_validate(work_zone)


# PUT /api/work-zones/{id}/resolve - Mark work zone as resolved
@router.put("/{work_zone_id}/resolve")
async def resolve_work_zone(
    work_zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark work zone as resolved"""
    query = select(WorkZone).where(WorkZone.id == work_zone_id)
    result = await db.execute(query)
    work_zone = result.scalar_one_or_none()

    if not work_zone:
        raise HTTPException(status_code=404, detail=f"Work zone {work_zone_id} not found")

    work_zone.status = "resolved"
    work_zone.resolved_at = datetime.utcnow()
    await db.commit()

    return {"message": "Work zone resolved", "id": work_zone_id}


# DELETE /api/work-zones/{id} - Delete work zone
@router.delete("/{work_zone_id}", status_code=204)
async def delete_work_zone(
    work_zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete work zone (for testing/cleanup)"""
    query = select(WorkZone).where(WorkZone.id == work_zone_id)
    result = await db.execute(query)
    work_zone = result.scalar_one_or_none()

    if not work_zone:
        raise HTTPException(status_code=404, detail=f"Work zone {work_zone_id} not found")

    await db.delete(work_zone)
    await db.commit()


# GET /api/work-zones/stats - Get statistics
@router.get("/stats/summary")
async def get_work_zone_stats(
    hours: int = Query(24, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get work zone statistics

    Args:
        hours: Time window for statistics

    Returns:
        Statistics about work zone detections
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    # Total detections
    total_query = select(func.count(WorkZone.id)).where(WorkZone.detected_at >= cutoff)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Active work zones
    active_query = select(func.count(WorkZone.id)).where(
        and_(WorkZone.status == "active", WorkZone.detected_at >= cutoff)
    )
    active_result = await db.execute(active_query)
    active = active_result.scalar()

    # High risk (>= 7)
    high_risk_query = select(func.count(WorkZone.id)).where(
        and_(
            WorkZone.detected_at >= cutoff,
            WorkZone.risk_score >= 7
        )
    )
    high_risk_result = await db.execute(high_risk_query)
    high_risk = high_risk_result.scalar()

    # Average risk score
    avg_risk_query = select(func.avg(WorkZone.risk_score)).where(WorkZone.detected_at >= cutoff)
    avg_risk_result = await db.execute(avg_risk_query)
    avg_risk = avg_risk_result.scalar() or 0

    return {
        "time_window_hours": hours,
        "total_detections": total,
        "active_work_zones": active,
        "high_risk_zones": high_risk,
        "average_risk_score": round(float(avg_risk), 2)
    }
