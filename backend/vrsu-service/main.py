"""
Virtual RSU (vRSU) Broadcast Service
====================================

Cloud-based V2X message broadcasting service for QEW Innovation Corridor.
Replaces physical Roadside Units (RSUs) with cloud infrastructure.

Features:
- SAE J2735 message generation
- 5G/LTE message broadcasting
- GCP Cloud Run deployment
- Real-time work zone alerts

Cost: $500-1000/month (vs $4-8M for physical RSUs)
Coverage: Entire QEW corridor via 5G cellular

Author: ADBA Labs
Project: QEW Innovation Corridor vRSU
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from j2735_encoder import (
    J2735MessageEncoder,
    Position,
    WorkZoneDetails
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QEW vRSU Service",
    description="Virtual Roadside Unit for V2X message broadcasting",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SAE J2735 encoder
encoder = J2735MessageEncoder()

# In-memory message store (replace with BigQuery in production)
broadcast_history: List[Dict] = []
MAX_HISTORY_SIZE = 1000


# Pydantic models for API requests
class WorkZoneAnalysis(BaseModel):
    """Work zone analysis from Gemini AI"""
    camera_id: str = Field(..., description="Camera ID (e.g., 'CAM_QEW_BURLOAK')")
    latitude: float = Field(..., description="Work zone latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Work zone longitude", ge=-180, le=180)
    elevation: Optional[float] = Field(None, description="Elevation in meters")

    risk_score: int = Field(..., description="Risk score (1-10)", ge=1, le=10)
    workers: int = Field(0, description="Number of workers", ge=0)
    vehicles: int = Field(0, description="Number of vehicles", ge=0)
    distance_to_zone: int = Field(500, description="Distance to work zone (meters)", ge=0)

    hazards: List[str] = Field(default_factory=list, description="List of hazards")
    violations: List[str] = Field(default_factory=list, description="MTO violations")
    confidence: float = Field(1.0, description="AI confidence (0-1)", ge=0, le=1)


class BroadcastRequest(BaseModel):
    """V2X broadcast request"""
    analysis: WorkZoneAnalysis
    message_type: str = Field("TIM", description="Message type: TIM or RSA")
    priority: str = Field("MEDIUM", description="Priority: LOW, MEDIUM, HIGH, CRITICAL")


class BroadcastResponse(BaseModel):
    """V2X broadcast response"""
    success: bool
    message_id: str
    message_type: str
    timestamp: str
    message_size: int
    broadcast_status: str
    j2735_message: Dict


# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "QEW vRSU Service",
        "status": "operational",
        "version": "1.0.0",
        "messages_broadcast": len(broadcast_history),
        "uptime": "healthy"
    }


# Main broadcast endpoint
@app.post("/api/v1/broadcast", response_model=BroadcastResponse)
async def broadcast_message(
    request: BroadcastRequest,
    background_tasks: BackgroundTasks
):
    """
    Broadcast V2X message to connected vehicles

    Args:
        request: Broadcast request with work zone analysis

    Returns:
        Broadcast response with message details
    """
    try:
        analysis = request.analysis

        # Create position object
        position = Position(
            lat=analysis.latitude,
            lon=analysis.longitude,
            elevation=analysis.elevation
        )

        # Create work zone details
        work_zone = WorkZoneDetails(
            risk_score=analysis.risk_score,
            workers=analysis.workers,
            vehicles=analysis.vehicles,
            distance_to_zone=analysis.distance_to_zone,
            hazards=analysis.hazards,
            violations=analysis.violations
        )

        # Generate appropriate message
        if request.message_type.upper() == "TIM":
            j2735_message = encoder.encode_tim_message(
                position=position,
                work_zone=work_zone,
                priority=request.priority
            )
        elif request.message_type.upper() == "RSA":
            j2735_message = encoder.encode_rsa_message(
                position=position,
                work_zone=work_zone
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid message_type: {request.message_type}. Must be 'TIM' or 'RSA'."
            )

        # Validate message
        if not encoder.validate_message(j2735_message):
            raise HTTPException(
                status_code=500,
                detail="Generated message failed validation"
            )

        # Calculate message size
        message_size = encoder.get_message_size(j2735_message)

        # Check size limit (SAE J2735 recommendation)
        if message_size > 1400:
            logger.warning(f"Message size ({message_size} bytes) exceeds recommended limit (1400 bytes)")

        # Generate message ID
        message_id = j2735_message.get("packetID", "unknown")

        # Simulate 5G broadcast (in production, integrate with MEC/5G network)
        broadcast_status = await simulate_5g_broadcast(j2735_message, analysis.camera_id)

        # Store in history
        broadcast_record = {
            "message_id": message_id,
            "message_type": request.message_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "camera_id": analysis.camera_id,
            "risk_score": analysis.risk_score,
            "message_size": message_size,
            "broadcast_status": broadcast_status,
            "j2735_message": j2735_message
        }

        broadcast_history.append(broadcast_record)

        # Trim history if too large
        if len(broadcast_history) > MAX_HISTORY_SIZE:
            broadcast_history.pop(0)

        # Log broadcast
        logger.info(
            f"Broadcast {request.message_type} message | "
            f"ID: {message_id} | "
            f"Camera: {analysis.camera_id} | "
            f"Risk: {analysis.risk_score}/10 | "
            f"Size: {message_size}B"
        )

        # Return response
        return BroadcastResponse(
            success=True,
            message_id=message_id,
            message_type=request.message_type,
            timestamp=broadcast_record["timestamp"],
            message_size=message_size,
            broadcast_status=broadcast_status,
            j2735_message=j2735_message
        )

    except Exception as e:
        logger.error(f"Broadcast error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get broadcast history
@app.get("/api/v1/broadcasts")
async def get_broadcasts(limit: int = 10, camera_id: Optional[str] = None):
    """
    Get recent broadcast history

    Args:
        limit: Number of broadcasts to return (max 100)
        camera_id: Filter by camera ID (optional)

    Returns:
        List of recent broadcasts
    """
    limit = min(limit, 100)  # Cap at 100

    # Filter by camera if specified
    if camera_id:
        filtered = [b for b in broadcast_history if b["camera_id"] == camera_id]
        return {"broadcasts": filtered[-limit:][::-1], "total": len(filtered)}

    return {"broadcasts": broadcast_history[-limit:][::-1], "total": len(broadcast_history)}


# Get broadcast statistics
@app.get("/api/v1/stats")
async def get_statistics():
    """
    Get broadcast statistics

    Returns:
        Statistics about vRSU broadcasts
    """
    if not broadcast_history:
        return {
            "total_broadcasts": 0,
            "tim_count": 0,
            "rsa_count": 0,
            "avg_risk_score": 0,
            "avg_message_size": 0
        }

    total = len(broadcast_history)
    tim_count = sum(1 for b in broadcast_history if b["message_type"] == "TIM")
    rsa_count = sum(1 for b in broadcast_history if b["message_type"] == "RSA")
    avg_risk = sum(b["risk_score"] for b in broadcast_history) / total
    avg_size = sum(b["message_size"] for b in broadcast_history) / total

    return {
        "total_broadcasts": total,
        "tim_count": tim_count,
        "rsa_count": rsa_count,
        "avg_risk_score": round(avg_risk, 2),
        "avg_message_size": round(avg_size, 0),
        "last_broadcast": broadcast_history[-1]["timestamp"] if broadcast_history else None
    }


async def simulate_5g_broadcast(message: Dict, camera_id: str) -> str:
    """
    Simulate 5G MEC broadcast

    In production, this would integrate with:
    - Rogers 5G MEC (Multi-Access Edge Computing)
    - Bell 5G MEC
    - AWS Wavelength

    Args:
        message: SAE J2735 message
        camera_id: Camera ID for logging

    Returns:
        Broadcast status
    """
    # Simulate successful broadcast
    # In production: POST to 5G MEC endpoint
    logger.info(f"5G MEC Broadcast simulated for {camera_id}")

    return "broadcast_success_5g_mec"


# Test endpoint for development
@app.post("/api/v1/test/broadcast")
async def test_broadcast():
    """
    Test endpoint to generate sample broadcast

    Returns:
        Sample broadcast response
    """
    test_analysis = WorkZoneAnalysis(
        camera_id="CAM_QEW_BURLOAK",
        latitude=43.3850,
        longitude=-79.7400,
        elevation=80.0,
        risk_score=8,
        workers=4,
        vehicles=2,
        distance_to_zone=500,
        hazards=[
            "Workers within 2m of active traffic lane",
            "Approaching vehicle speed >80 km/h",
            "Missing advance warning signage"
        ],
        violations=[
            "BOOK 7 Section 3.2: Insufficient safety measures",
            "BOOK 7 Section 4.1: Missing or inadequate barriers"
        ],
        confidence=0.92
    )

    request = BroadcastRequest(
        analysis=test_analysis,
        message_type="TIM",
        priority="HIGH"
    )

    return await broadcast_message(request, BackgroundTasks())


# Main entry point
if __name__ == "__main__":
    # Use port 8081 for local development (8080 is SPARC AI)
    # Cloud Run will override with $PORT env var (defaults to 8080)
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
