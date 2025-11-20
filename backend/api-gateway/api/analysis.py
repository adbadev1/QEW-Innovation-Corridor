"""
AI Image Analysis API Endpoints
================================

Gemini Vision API integration for work zone detection and risk assessment.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
import base64

from database import get_db
from models import Camera, WorkZone
from services import gemini_service, analysis_orchestration_service

router = APIRouter()


# Pydantic schemas
class ImageAnalysisRequest(BaseModel):
    """Schema for single image analysis request"""
    image_url: Optional[str] = Field(None, description="GCP Storage URL of image")
    image_base64: Optional[str] = Field(None, description="Base64-encoded image data")
    camera_id: Optional[int] = Field(None, description="Camera that captured the image")
    model: str = Field(default="gemini-2.0-flash-exp", description="Gemini model to use")
    min_risk_threshold: int = Field(default=5, ge=1, le=10, description="Minimum risk to store work zone")


class BatchAnalysisRequest(BaseModel):
    """Schema for batch image analysis"""
    image_urls: List[str] = Field(..., description="List of GCP Storage URLs")
    camera_ids: Optional[List[int]] = Field(None, description="Corresponding camera IDs")
    model: str = Field(default="gemini-2.0-flash-exp")
    min_risk_threshold: int = Field(default=5, ge=1, le=10)


class WorkZoneDetection(BaseModel):
    """Schema for detected work zone"""
    has_work_zone: bool
    risk_score: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    workers: int = Field(default=0, ge=0)
    vehicles: int = Field(default=0, ge=0)
    equipment: int = Field(default=0, ge=0)
    barriers: bool = False
    lane_closures: int = Field(default=0, ge=0)
    hazards: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    mto_book_compliance: bool = False
    analysis_text: str = Field(..., description="Full AI analysis text")


class ImageAnalysisResponse(BaseModel):
    """Schema for analysis response"""
    image_url: Optional[str]
    camera_id: Optional[int]
    camera_location: Optional[str]
    detection: WorkZoneDetection
    work_zone_id: Optional[int] = Field(None, description="Created work zone ID if risk >= threshold")
    model: str
    analyzed_at: str


class BatchAnalysisResponse(BaseModel):
    """Schema for batch analysis response"""
    total_images: int
    images_analyzed: int
    images_failed: int
    work_zones_detected: int
    high_risk_zones: int
    results: List[ImageAnalysisResponse]
    started_at: str
    completed_at: str


# POST /api/analysis/image - Analyze single image
@router.post("/image", response_model=ImageAnalysisResponse)
async def analyze_image(
    request: ImageAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze single camera image with Gemini Vision API

    Detects work zones, assesses risk, identifies hazards, and checks
    MTO BOOK 7 compliance.

    Args:
        request: Image data and analysis parameters

    Returns:
        Work zone detection results
    """
    if not request.image_url and not request.image_base64:
        raise HTTPException(status_code=400, detail="Either image_url or image_base64 required")

    # Get camera info if provided
    camera = None
    camera_location = None
    if request.camera_id:
        camera_query = select(Camera).where(Camera.id == request.camera_id)
        camera_result = await db.execute(camera_query)
        camera = camera_result.scalar_one_or_none()
        if camera:
            camera_location = camera.location

    # Call Gemini Vision API for analysis
    image_type = "base64" if request.image_base64 else "url"
    image_data = request.image_base64 or request.image_url

    analysis_result = await gemini_service.analyze_work_zone(image_data, image_type)

    # Convert to WorkZoneDetection schema
    detection = WorkZoneDetection(
        has_work_zone=analysis_result.get("has_work_zone", False),
        risk_score=analysis_result.get("risk_score", 0),
        confidence=analysis_result.get("confidence", 0.0),
        workers=analysis_result.get("workers", 0),
        vehicles=analysis_result.get("vehicles", 0),
        equipment=analysis_result.get("equipment", 0),
        barriers=analysis_result.get("barriers", False),
        lane_closures=analysis_result.get("lane_closures", 0),
        hazards=analysis_result.get("hazards", []),
        violations=analysis_result.get("violations", []),
        recommendations=analysis_result.get("recommendations", []),
        mto_book_compliance=analysis_result.get("mto_book_compliance", False),
        analysis_text=analysis_result.get("analysis_text", "")
    )

    # If work zone detected and risk >= threshold, create work zone record
    work_zone_id = None
    if detection.has_work_zone and detection.risk_score >= request.min_risk_threshold and camera:
        work_zone = WorkZone(
            camera_id=camera.id,
            latitude=camera.latitude,
            longitude=camera.longitude,
            risk_score=detection.risk_score,
            confidence=detection.confidence,
            workers=detection.workers,
            vehicles=detection.vehicles,
            equipment=detection.equipment,
            barriers=detection.barriers,
            hazards=detection.hazards if detection.hazards else None,
            violations=detection.violations if detection.violations else None,
            recommendations=detection.recommendations if detection.recommendations else None,
            mto_book_compliance=detection.mto_book_compliance,
            gcp_image_url=request.image_url,
            model=request.model,
            synthetic=False
        )
        db.add(work_zone)
        await db.commit()
        await db.refresh(work_zone)
        work_zone_id = work_zone.id

    return ImageAnalysisResponse(
        image_url=request.image_url,
        camera_id=request.camera_id,
        camera_location=camera_location,
        detection=detection,
        work_zone_id=work_zone_id,
        model=request.model,
        analyzed_at=datetime.utcnow().isoformat()
    )


# POST /api/analysis/upload - Analyze uploaded image
@router.post("/upload", response_model=ImageAnalysisResponse)
async def analyze_uploaded_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    camera_id: Optional[int] = Form(None),
    model: str = Form(default="gemini-2.0-flash-exp"),
    min_risk_threshold: int = Form(default=5),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze uploaded image file

    Accepts image upload (JPEG, PNG) and performs work zone analysis.

    Args:
        file: Image file upload
        camera_id: Associated camera
        model: Gemini model to use
        min_risk_threshold: Minimum risk to store work zone

    Returns:
        Analysis results
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG)")

    # Read and encode image
    image_data = await file.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Use the image analysis function
    request = ImageAnalysisRequest(
        image_base64=image_base64,
        camera_id=camera_id,
        model=model,
        min_risk_threshold=min_risk_threshold
    )

    return await analyze_image(request, db)


# POST /api/analysis/batch - Batch analyze images
@router.post("/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
    request: BatchAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch analyze multiple camera images

    Processes multiple images in parallel (rate-limited by Gemini API).

    Args:
        request: Batch of images to analyze

    Returns:
        Batch analysis results
    """
    if not request.image_urls:
        raise HTTPException(status_code=400, detail="No images provided")

    if request.camera_ids and len(request.camera_ids) != len(request.image_urls):
        raise HTTPException(
            status_code=400,
            detail="camera_ids length must match image_urls length"
        )

    started_at = datetime.utcnow()
    results = []
    images_failed = 0
    work_zones_detected = 0
    high_risk_zones = 0

    # Process each image
    for idx, image_url in enumerate(request.image_urls):
        try:
            camera_id = request.camera_ids[idx] if request.camera_ids else None

            analysis_request = ImageAnalysisRequest(
                image_url=image_url,
                camera_id=camera_id,
                model=request.model,
                min_risk_threshold=request.min_risk_threshold
            )

            result = await analyze_image(analysis_request, db)
            results.append(result)

            if result.detection.has_work_zone:
                work_zones_detected += 1
                if result.detection.risk_score >= 7:
                    high_risk_zones += 1

        except Exception as e:
            images_failed += 1
            # Add error result
            results.append(ImageAnalysisResponse(
                image_url=image_url,
                camera_id=camera_id if request.camera_ids else None,
                camera_location=None,
                detection=WorkZoneDetection(
                    has_work_zone=False,
                    risk_score=0,
                    confidence=0.0,
                    analysis_text=f"Analysis failed: {str(e)}"
                ),
                work_zone_id=None,
                model=request.model,
                analyzed_at=datetime.utcnow().isoformat()
            ))

    completed_at = datetime.utcnow()

    return BatchAnalysisResponse(
        total_images=len(request.image_urls),
        images_analyzed=len(request.image_urls) - images_failed,
        images_failed=images_failed,
        work_zones_detected=work_zones_detected,
        high_risk_zones=high_risk_zones,
        results=results,
        started_at=started_at.isoformat(),
        completed_at=completed_at.isoformat()
    )


# GET /api/analysis/history - Analysis history
@router.get("/history")
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    camera_id: Optional[int] = Query(None),
    min_risk: int = Query(0, ge=0, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis history

    This returns work zones that were created from AI analysis.

    Args:
        skip: Pagination offset
        limit: Max results
        camera_id: Filter by camera
        min_risk: Minimum risk score

    Returns:
        List of analyzed work zones
    """
    query = select(WorkZone).where(WorkZone.synthetic == False)

    if camera_id:
        query = query.where(WorkZone.camera_id == camera_id)

    if min_risk > 0:
        query = query.where(WorkZone.risk_score >= min_risk)

    query = query.order_by(WorkZone.detected_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    work_zones = result.scalars().all()

    # Build response with camera info
    history = []
    for wz in work_zones:
        camera_query = select(Camera).where(Camera.id == wz.camera_id)
        camera_result = await db.execute(camera_query)
        camera = camera_result.scalar_one_or_none()

        history.append({
            "work_zone_id": wz.id,
            "camera_id": wz.camera_id,
            "camera_location": camera.location if camera else None,
            "risk_score": wz.risk_score,
            "confidence": wz.confidence,
            "workers": wz.workers,
            "vehicles": wz.vehicles,
            "barriers": wz.barriers,
            "hazards": wz.hazards,
            "violations": wz.violations,
            "mto_book_compliance": wz.mto_book_compliance,
            "image_url": wz.gcp_image_url,
            "model": wz.model,
            "detected_at": wz.detected_at.isoformat(),
            "status": wz.status
        })

    return history


# POST /api/analysis/prompt - Test analysis prompt
@router.post("/prompt")
async def test_analysis_prompt(
    prompt: str = Form(..., description="Analysis prompt to test"),
    image_url: Optional[str] = Form(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Test different analysis prompts

    Development endpoint for testing different prompt strategies with
    Gemini Vision API.

    Args:
        prompt: Custom prompt to test
        image_url: Image URL
        image_base64: Base64 image

    Returns:
        Raw AI response
    """
    if not image_url and not image_base64:
        raise HTTPException(status_code=400, detail="Image required")

    # Call Gemini with custom prompt
    image_type = "base64" if image_base64 else "url"
    image_data = image_base64 or image_url

    result = await gemini_service.analyze_work_zone(
        image_data,
        image_type,
        custom_prompt=prompt
    )

    return {
        "prompt": prompt,
        "result": result,
        "analyzed_at": datetime.utcnow().isoformat()
    }


# GET /api/analysis/stats - Analysis statistics
@router.get("/stats/summary")
async def get_analysis_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI analysis statistics

    Returns:
        Analysis performance metrics
    """
    # Total AI-detected work zones (non-synthetic)
    total_query = select(func.count(WorkZone.id)).where(WorkZone.synthetic == False)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # High confidence detections (>= 0.8)
    high_conf_query = select(func.count(WorkZone.id)).where(
        and_(WorkZone.synthetic == False, WorkZone.confidence >= 0.8)
    )
    high_conf_result = await db.execute(high_conf_query)
    high_confidence = high_conf_result.scalar()

    # Average confidence
    avg_conf_query = select(func.avg(WorkZone.confidence)).where(WorkZone.synthetic == False)
    avg_conf_result = await db.execute(avg_conf_query)
    avg_confidence = avg_conf_result.scalar() or 0

    # Average risk score
    avg_risk_query = select(func.avg(WorkZone.risk_score)).where(WorkZone.synthetic == False)
    avg_risk_result = await db.execute(avg_risk_query)
    avg_risk = avg_risk_result.scalar() or 0

    # MTO BOOK 7 compliant work zones
    compliant_query = select(func.count(WorkZone.id)).where(
        and_(WorkZone.synthetic == False, WorkZone.mto_book_compliance == True)
    )
    compliant_result = await db.execute(compliant_query)
    compliant = compliant_result.scalar()

    return {
        "total_ai_detections": total,
        "high_confidence_detections": high_confidence,
        "average_confidence": round(float(avg_confidence), 3),
        "average_risk_score": round(float(avg_risk), 2),
        "mto_compliant_zones": compliant,
        "mto_non_compliant_zones": total - compliant
    }
