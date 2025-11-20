"""
Cameras API Endpoints
=====================

CRUD operations for QEW COMPASS traffic cameras.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from database import get_db
from models import Camera

router = APIRouter()


# Pydantic schemas for request/response
class CameraCreate(BaseModel):
    """Schema for creating a new camera"""
    camera_id: str = Field(..., description="Camera ID (e.g., 'CAM_253')")
    source: str = Field(default="511ON", description="Data source")
    location: str = Field(..., description="Camera location description")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360)
    direction: Optional[str] = Field(None, pattern="^(N|NE|E|SE|S|SW|W|NW)$")
    direction_confidence: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    active: bool = True
    views: Optional[dict] = None


class CameraUpdate(BaseModel):
    """Schema for updating a camera"""
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    elevation: Optional[float] = None
    heading: Optional[float] = Field(None, ge=0, le=360)
    direction: Optional[str] = Field(None, pattern="^(N|NE|E|SE|S|SW|W|NW)$")
    direction_confidence: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    active: Optional[bool] = None
    views: Optional[dict] = None


class CameraResponse(BaseModel):
    """Schema for camera response"""
    id: int
    camera_id: str
    source: str
    location: str
    latitude: float
    longitude: float
    elevation: Optional[float]
    heading: Optional[float]
    direction: Optional[str]
    direction_confidence: Optional[str]
    active: bool
    views: Optional[dict]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# GET /api/cameras - List all cameras
@router.get("/", response_model=List[CameraResponse])
async def get_cameras(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    active_only: bool = Query(False, description="Filter active cameras only"),
    has_direction: bool = Query(False, description="Filter cameras with direction data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all cameras

    Returns list of camera objects with pagination support.
    """
    query = select(Camera)

    # Apply filters
    if active_only:
        query = query.where(Camera.active == True)

    if has_direction:
        query = query.where(Camera.heading.isnot(None))

    # Add ordering and pagination
    query = query.order_by(Camera.camera_id).offset(skip).limit(limit)

    result = await db.execute(query)
    cameras = result.scalars().all()

    return [CameraResponse.model_validate(camera) for camera in cameras]


# GET /api/cameras/{camera_id} - Get specific camera
@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific camera by camera_id

    Args:
        camera_id: Camera identifier (e.g., 'CAM_253')

    Returns:
        Camera object

    Raises:
        404: Camera not found
    """
    query = select(Camera).where(Camera.camera_id == camera_id)
    result = await db.execute(query)
    camera = result.scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    return CameraResponse.model_validate(camera)


# POST /api/cameras - Create new camera
@router.post("/", response_model=CameraResponse, status_code=201)
async def create_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new camera

    Args:
        camera_data: Camera creation data

    Returns:
        Created camera object

    Raises:
        400: Camera with this ID already exists
    """
    # Check if camera already exists
    existing = await db.execute(
        select(Camera).where(Camera.camera_id == camera_data.camera_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Camera {camera_data.camera_id} already exists"
        )

    # Create new camera
    camera = Camera(**camera_data.model_dump())
    db.add(camera)
    await db.commit()
    await db.refresh(camera)

    return CameraResponse.model_validate(camera)


# PUT /api/cameras/{camera_id} - Update camera
@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update existing camera

    Args:
        camera_id: Camera identifier
        camera_data: Fields to update

    Returns:
        Updated camera object

    Raises:
        404: Camera not found
    """
    query = select(Camera).where(Camera.camera_id == camera_id)
    result = await db.execute(query)
    camera = result.scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    # Update fields
    update_data = camera_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.commit()
    await db.refresh(camera)

    return CameraResponse.model_validate(camera)


# DELETE /api/cameras/{camera_id} - Delete camera
@router.delete("/{camera_id}", status_code=204)
async def delete_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete camera (soft delete - sets active=False)

    Args:
        camera_id: Camera identifier

    Raises:
        404: Camera not found
    """
    query = select(Camera).where(Camera.camera_id == camera_id)
    result = await db.execute(query)
    camera = result.scalar_one_or_none()

    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

    # Soft delete
    camera.active = False
    await db.commit()


# GET /api/cameras/stats - Get camera statistics
@router.get("/stats/summary")
async def get_camera_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get camera statistics

    Returns:
        Statistics about cameras in the system
    """
    # Total cameras
    total_query = select(func.count(Camera.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Active cameras
    active_query = select(func.count(Camera.id)).where(Camera.active == True)
    active_result = await db.execute(active_query)
    active = active_result.scalar()

    # Cameras with direction data
    direction_query = select(func.count(Camera.id)).where(Camera.heading.isnot(None))
    direction_result = await db.execute(direction_query)
    with_direction = direction_result.scalar()

    return {
        "total_cameras": total,
        "active_cameras": active,
        "inactive_cameras": total - active,
        "cameras_with_direction": with_direction,
        "cameras_without_direction": total - with_direction
    }
