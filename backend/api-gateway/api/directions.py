"""
Camera Direction API Endpoints
===============================

Integration of Corey's AI camera direction analysis work.
Manage camera heading/direction data for QEW COMPASS cameras.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
import csv
import io

from database import get_db
from models import Camera, CameraDirection

router = APIRouter()


# Pydantic schemas
class DirectionAnalysisRequest(BaseModel):
    """Schema for triggering direction analysis"""
    camera_id: Optional[int] = Field(None, description="Specific camera to analyze (all if None)")
    view_id: Optional[int] = Field(None, description="Specific view to analyze")
    force_reanalysis: bool = Field(default=False, description="Re-analyze even if direction exists")


class CameraDirectionCreate(BaseModel):
    """Schema for creating camera direction data"""
    camera_id: int
    view_id: Optional[int] = None
    heading: float = Field(..., ge=0, le=360, description="Camera heading in degrees (0=N, 90=E, 180=S, 270=W)")
    direction: str = Field(..., pattern="^(N|NE|E|SE|S|SW|W|NW)$")
    confidence: str = Field(default="medium", pattern="^(high|medium|low)$")
    eastbound_heading: Optional[float] = Field(None, ge=0, le=360)
    westbound_heading: Optional[float] = Field(None, ge=0, le=360)
    source: str = Field(default="ai_analysis", description="Data source (ai_analysis, manual, csv_import)")
    notes: Optional[str] = None


class CameraDirectionUpdate(BaseModel):
    """Schema for updating camera direction"""
    heading: Optional[float] = Field(None, ge=0, le=360)
    direction: Optional[str] = Field(None, pattern="^(N|NE|E|SE|S|SW|W|NW)$")
    confidence: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    eastbound_heading: Optional[float] = Field(None, ge=0, le=360)
    westbound_heading: Optional[float] = Field(None, ge=0, le=360)
    notes: Optional[str] = None


class CameraDirectionResponse(BaseModel):
    """Schema for camera direction response"""
    id: int
    camera_id: int
    view_id: Optional[int]
    heading: float
    direction: str
    confidence: str
    eastbound_heading: Optional[float]
    westbound_heading: Optional[float]
    source: str
    notes: Optional[str]
    analyzed_at: str

    class Config:
        from_attributes = True


class CameraWithDirectionResponse(BaseModel):
    """Schema for camera with direction data"""
    camera_id: str
    location: str
    latitude: float
    longitude: float
    heading: Optional[float]
    direction: Optional[str]
    direction_confidence: Optional[str]
    has_direction_analysis: bool
    direction_views: List[CameraDirectionResponse]


# POST /api/directions/analyze - Trigger AI direction analysis
@router.post("/analyze")
async def analyze_camera_directions(
    request: DirectionAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI analysis to determine camera heading/direction

    This uses Corey's AI camera direction analysis system to determine
    which direction cameras are facing based on image analysis.

    Args:
        request: Analysis parameters

    Returns:
        Status message
    """
    if request.camera_id:
        # Verify camera exists
        camera_query = select(Camera).where(Camera.id == request.camera_id)
        camera_result = await db.execute(camera_query)
        camera = camera_result.scalar_one_or_none()

        if not camera:
            raise HTTPException(status_code=404, detail=f"Camera {request.camera_id} not found")

        # TODO: Queue background task for AI direction analysis
        # background_tasks.add_task(
        #     analyze_camera_direction_task,
        #     request.camera_id,
        #     request.view_id,
        #     request.force_reanalysis
        # )

        return {
            "message": "Direction analysis queued",
            "camera_id": request.camera_id,
            "view_id": request.view_id
        }
    else:
        # Analyze all cameras
        count_query = select(func.count(Camera.id)).where(Camera.active == True)
        result = await db.execute(count_query)
        total_cameras = result.scalar()

        # TODO: Queue bulk analysis task
        # background_tasks.add_task(analyze_all_cameras_task, request.force_reanalysis)

        return {
            "message": "Bulk direction analysis queued",
            "cameras_to_analyze": total_cameras
        }


# GET /api/directions - Get all camera directions
@router.get("/", response_model=List[CameraDirectionResponse])
async def get_camera_directions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    camera_id: Optional[int] = Query(None, description="Filter by camera"),
    confidence: Optional[str] = Query(None, pattern="^(high|medium|low)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get camera direction data

    Args:
        skip: Pagination offset
        limit: Max results
        camera_id: Filter by specific camera
        confidence: Filter by confidence level

    Returns:
        List of camera direction records
    """
    query = select(CameraDirection)

    if camera_id:
        query = query.where(CameraDirection.camera_id == camera_id)

    if confidence:
        query = query.where(CameraDirection.confidence == confidence)

    query = query.order_by(CameraDirection.analyzed_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    directions = result.scalars().all()

    return [CameraDirectionResponse.model_validate(d) for d in directions]


# GET /api/directions/cameras - Get cameras with direction data
@router.get("/cameras", response_model=List[CameraWithDirectionResponse])
async def get_cameras_with_directions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    has_direction: bool = Query(False, description="Filter cameras with direction data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cameras with their direction analysis data

    Args:
        skip: Pagination offset
        limit: Max results
        has_direction: Only show cameras with direction data

    Returns:
        List of cameras with direction information
    """
    # Query cameras
    camera_query = select(Camera)

    if has_direction:
        camera_query = camera_query.where(Camera.heading.isnot(None))

    camera_query = camera_query.order_by(Camera.camera_id).offset(skip).limit(limit)
    camera_result = await db.execute(camera_query)
    cameras = camera_result.scalars().all()

    # Build response with direction data
    response = []
    for camera in cameras:
        # Get direction analysis records for this camera
        dir_query = select(CameraDirection).where(CameraDirection.camera_id == camera.id)
        dir_result = await db.execute(dir_query)
        direction_records = dir_result.scalars().all()

        response.append(CameraWithDirectionResponse(
            camera_id=camera.camera_id,
            location=camera.location,
            latitude=camera.latitude,
            longitude=camera.longitude,
            heading=camera.heading,
            direction=camera.direction,
            direction_confidence=camera.direction_confidence,
            has_direction_analysis=len(direction_records) > 0,
            direction_views=[CameraDirectionResponse.model_validate(d) for d in direction_records]
        ))

    return response


# POST /api/directions - Create direction record
@router.post("/", response_model=CameraDirectionResponse, status_code=201)
async def create_camera_direction(
    direction_data: CameraDirectionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new camera direction record

    This can be used to manually add direction data or import from
    Corey's analysis system.

    Args:
        direction_data: Direction data to create

    Returns:
        Created direction record
    """
    # Verify camera exists
    camera_query = select(Camera).where(Camera.id == direction_data.camera_id)
    camera_result = await db.execute(camera_query)
    camera = camera_result.scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {direction_data.camera_id} not found")

    # Create direction record
    direction = CameraDirection(**direction_data.model_dump())
    db.add(direction)

    # Update camera with direction data (use primary direction)
    if not camera.heading or direction_data.confidence == "high":
        camera.heading = direction_data.heading
        camera.direction = direction_data.direction
        camera.direction_confidence = direction_data.confidence

    await db.commit()
    await db.refresh(direction)

    return CameraDirectionResponse.model_validate(direction)


# PUT /api/directions/{camera_id} - Update camera direction
@router.put("/{camera_id}", response_model=CameraDirectionResponse)
async def update_camera_direction(
    camera_id: int,
    direction_data: CameraDirectionUpdate,
    view_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Update camera direction record

    Args:
        camera_id: Camera to update
        view_id: Specific view to update (if camera has multiple views)
        direction_data: Fields to update

    Returns:
        Updated direction record
    """
    # Find direction record
    query = select(CameraDirection).where(CameraDirection.camera_id == camera_id)
    if view_id is not None:
        query = query.where(CameraDirection.view_id == view_id)
    else:
        query = query.where(CameraDirection.view_id.is_(None))

    result = await db.execute(query)
    direction = result.scalar_one_or_none()

    if not direction:
        raise HTTPException(
            status_code=404,
            detail=f"Direction record for camera {camera_id}, view {view_id} not found"
        )

    # Update fields
    update_data = direction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(direction, field, value)

    # Update camera's primary direction if this is the main view
    if view_id is None or direction.confidence == "high":
        camera_query = select(Camera).where(Camera.id == camera_id)
        camera_result = await db.execute(camera_query)
        camera = camera_result.scalar_one()

        if direction_data.heading is not None:
            camera.heading = direction_data.heading
        if direction_data.direction is not None:
            camera.direction = direction_data.direction
        if direction_data.confidence is not None:
            camera.direction_confidence = direction_data.confidence

    await db.commit()
    await db.refresh(direction)

    return CameraDirectionResponse.model_validate(direction)


# POST /api/directions/import-csv - Import from Corey's CSV
@router.post("/import-csv")
async def import_directions_csv(
    file: UploadFile = File(..., description="CSV file with camera direction data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Import camera direction data from CSV file

    Expected CSV format:
    camera_id,heading,direction,confidence,eastbound_heading,westbound_heading,notes

    Args:
        file: CSV file upload

    Returns:
        Import statistics
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    # Read CSV
    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)

    imported = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            # Find camera by camera_id
            camera_query = select(Camera).where(Camera.camera_id == row['camera_id'])
            camera_result = await db.execute(camera_query)
            camera = camera_result.scalar_one_or_none()

            if not camera:
                errors.append(f"Row {row_num}: Camera {row['camera_id']} not found")
                continue

            # Create direction record
            direction_data = CameraDirectionCreate(
                camera_id=camera.id,
                heading=float(row['heading']),
                direction=row['direction'],
                confidence=row.get('confidence', 'medium'),
                eastbound_heading=float(row['eastbound_heading']) if row.get('eastbound_heading') else None,
                westbound_heading=float(row['westbound_heading']) if row.get('westbound_heading') else None,
                source='csv_import',
                notes=row.get('notes')
            )

            direction = CameraDirection(**direction_data.model_dump())
            db.add(direction)

            # Update camera
            camera.heading = direction_data.heading
            camera.direction = direction_data.direction
            camera.direction_confidence = direction_data.confidence

            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    await db.commit()

    return {
        "message": "Import completed",
        "imported": imported,
        "errors": errors,
        "error_count": len(errors)
    }


# DELETE /api/directions/{camera_id} - Delete direction record
@router.delete("/{camera_id}", status_code=204)
async def delete_camera_direction(
    camera_id: int,
    view_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete camera direction record

    Args:
        camera_id: Camera ID
        view_id: Specific view to delete (if camera has multiple views)
    """
    query = select(CameraDirection).where(CameraDirection.camera_id == camera_id)
    if view_id is not None:
        query = query.where(CameraDirection.view_id == view_id)

    result = await db.execute(query)
    direction = result.scalar_one_or_none()

    if not direction:
        raise HTTPException(
            status_code=404,
            detail=f"Direction record for camera {camera_id}, view {view_id} not found"
        )

    await db.delete(direction)
    await db.commit()


# GET /api/directions/stats - Direction statistics
@router.get("/stats/summary")
async def get_direction_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get camera direction statistics

    Returns:
        Statistics about camera direction analysis
    """
    # Total cameras with direction data
    cameras_with_direction_query = select(func.count(Camera.id)).where(Camera.heading.isnot(None))
    cameras_result = await db.execute(cameras_with_direction_query)
    cameras_with_direction = cameras_result.scalar()

    # Total cameras without direction
    cameras_without_direction_query = select(func.count(Camera.id)).where(Camera.heading.is_(None))
    no_dir_result = await db.execute(cameras_without_direction_query)
    cameras_without_direction = no_dir_result.scalar()

    # High confidence directions
    high_conf_query = select(func.count(CameraDirection.id)).where(
        CameraDirection.confidence == "high"
    )
    high_conf_result = await db.execute(high_conf_query)
    high_confidence = high_conf_result.scalar()

    # Medium confidence
    med_conf_query = select(func.count(CameraDirection.id)).where(
        CameraDirection.confidence == "medium"
    )
    med_conf_result = await db.execute(med_conf_query)
    medium_confidence = med_conf_result.scalar()

    # Low confidence
    low_conf_query = select(func.count(CameraDirection.id)).where(
        CameraDirection.confidence == "low"
    )
    low_conf_result = await db.execute(low_conf_query)
    low_confidence = low_conf_result.scalar()

    # Total direction records
    total_records_query = select(func.count(CameraDirection.id))
    total_result = await db.execute(total_records_query)
    total_records = total_result.scalar()

    return {
        "cameras_with_direction": cameras_with_direction,
        "cameras_without_direction": cameras_without_direction,
        "total_direction_records": total_records,
        "high_confidence_records": high_confidence,
        "medium_confidence_records": medium_confidence,
        "low_confidence_records": low_confidence
    }
