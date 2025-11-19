"""
FastAPI Backend for QEW Innovation Corridor
Main application entry point
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
from pathlib import Path
import uvicorn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi_backend.config import (
    CORS_ORIGINS,
    HOST,
    PORT,
    RELOAD,
    CAMERA_IMAGES_DIR,
    SATELLITE_IMAGES_DIR,
    CAMERA_TEMP_IMAGES_DIR
)
from fastapi_backend.database import CameraDatabase, DirectionDatabase
from fastapi_backend.services import CameraScraperService, DirectionAnalyzerService, WebAppExporter
from fastapi_backend.routers import camera_directions

# Create FastAPI app
app = FastAPI(
    title="QEW Innovation Corridor API",
    description="Unified backend for camera scraping and AI direction analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories for images
if os.path.exists(CAMERA_IMAGES_DIR):
    app.mount("/images/camera", StaticFiles(directory=CAMERA_IMAGES_DIR), name="camera_images")
if os.path.exists(SATELLITE_IMAGES_DIR):
    app.mount("/images/satellite", StaticFiles(directory=SATELLITE_IMAGES_DIR), name="satellite_images")

# Register routers
app.include_router(camera_directions.router)

# Initialize services (will be created per request or as singletons)
camera_scraper = None
direction_analyzer = None
webapp_exporter = WebAppExporter()


# Pydantic models for request/response
class ScraperStartRequest(BaseModel):
    images_per_camera: Optional[int] = 1
    delay_between_captures: Optional[int] = 60


class DirectionAnalysisRequest(BaseModel):
    camera_id: int
    view_id: int
    platform: Optional[str] = "Gemini"
    model: Optional[str] = "Gemini 2.0 Flash"


class BatchAnalysisRequest(BaseModel):
    platform: Optional[str] = "Gemini"
    model: Optional[str] = "Gemini 2.0 Flash"


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QEW Innovation Corridor API",
        "version": "1.0.0",
        "endpoints": {
            "cameras": "/api/cameras",
            "scraper": "/api/scraper",
            "directions": "/api/directions",
            "images": "/images",
            "export": "/api/export"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# CAMERA SCRAPER ENDPOINTS
# ============================================================================

@app.post("/api/scraper/start")
async def start_scraper(request: ScraperStartRequest, background_tasks: BackgroundTasks):
    """Start camera scraping process"""
    global camera_scraper
    
    if camera_scraper and camera_scraper.is_running:
        raise HTTPException(status_code=400, detail="Scraper is already running")
    
    camera_scraper = CameraScraperService()
    
    # Run scraping in background
    background_tasks.add_task(
        camera_scraper.scrape_cameras,
        images_per_camera=request.images_per_camera,
        delay_between_captures=request.delay_between_captures
    )
    
    return {
        "message": "Camera scraping started",
        "images_per_camera": request.images_per_camera,
        "delay_between_captures": request.delay_between_captures
    }


@app.post("/api/scraper/stop")
async def stop_scraper():
    """Stop camera scraping process"""
    global camera_scraper
    
    if not camera_scraper or not camera_scraper.is_running:
        raise HTTPException(status_code=400, detail="Scraper is not running")
    
    camera_scraper.stop_scraping()
    return {"message": "Camera scraping stopped"}


@app.get("/api/scraper/status")
async def get_scraper_status():
    """Get camera scraper status"""
    global camera_scraper

    if not camera_scraper:
        return {"is_running": False, "status": "not_started"}

    return camera_scraper.get_status()


# ============================================================================
# CAMERA DATA ENDPOINTS
# ============================================================================

@app.get("/api/cameras/latest")
async def get_latest_cameras():
    """Get latest camera data with most recent images"""
    try:
        db = CameraDatabase()

        # Get all cameras
        cameras = db.get_all_cameras()

        # Get latest collection
        collections = db.get_all_collections()
        if not collections:
            return {"cameras": [], "collection_id": None}

        latest_collection = collections[0]  # Already sorted by start_time DESC
        collection_id = latest_collection['collection_id']

        # Build response with images
        result = []
        for camera in cameras:
            camera_data = dict(camera)

            # Get views
            views = db.get_camera_views(camera['camera_id'])
            camera_data['Views'] = []

            for view in views:
                view_data = dict(view)

                # Get images for this view from latest collection
                db.cursor.execute("""
                    SELECT * FROM images
                    WHERE camera_id = ? AND view_id = ? AND collection_id = ?
                    ORDER BY timestamp DESC, capture_round DESC
                """, (camera['camera_id'], view['view_id'], collection_id))

                images = [dict(row) for row in db.cursor.fetchall()]
                view_data['Images'] = images

                camera_data['Views'].append(view_data)

            result.append(camera_data)

        db.close()

        return {
            "cameras": result,
            "collection_id": collection_id,
            "total_cameras": len(result)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cameras/{camera_id}")
async def get_camera(camera_id: int):
    """Get specific camera by ID"""
    try:
        db = CameraDatabase()
        camera = db.get_camera_by_id(camera_id)

        if not camera:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

        # Get views
        views = db.get_camera_views(camera_id)
        camera_data = dict(camera)
        camera_data['Views'] = [dict(v) for v in views]

        db.close()
        return camera_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/collections/latest")
async def get_latest_collection():
    """Get latest collection info"""
    try:
        db = CameraDatabase()
        collections = db.get_all_collections()
        db.close()

        if not collections:
            return None

        return dict(collections[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    try:
        db = CameraDatabase()

        cameras = db.get_all_cameras()
        collections = db.get_all_collections()

        db.cursor.execute("SELECT COUNT(*) as count FROM images")
        total_images = db.cursor.fetchone()['count']

        db.close()

        return {
            "total_cameras": len(cameras),
            "total_collections": len(collections),
            "total_images": total_images
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI DIRECTION ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/directions/analyze")
async def analyze_direction(request: DirectionAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze direction for a specific camera view"""
    global direction_analyzer

    direction_analyzer = DirectionAnalyzerService(
        platform=request.platform,
        model=request.model
    )

    # Run analysis in background
    background_tasks.add_task(
        direction_analyzer.analyze_camera,
        camera_id=request.camera_id,
        view_id=request.view_id
    )

    return {
        "message": "Direction analysis started",
        "camera_id": request.camera_id,
        "view_id": request.view_id,
        "platform": request.platform,
        "model": request.model
    }


@app.post("/api/directions/analyze-batch")
async def analyze_batch(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze all pending cameras"""
    global direction_analyzer

    direction_analyzer = DirectionAnalyzerService(
        platform=request.platform,
        model=request.model
    )

    # Run batch analysis in background
    background_tasks.add_task(
        direction_analyzer.analyze_pending_cameras
    )

    pending_count = direction_analyzer.get_pending_count()

    return {
        "message": "Batch analysis started",
        "pending_cameras": pending_count,
        "platform": request.platform,
        "model": request.model
    }


@app.post("/api/directions/stop")
async def stop_direction_analysis():
    """Stop direction analysis process"""
    global direction_analyzer

    if not direction_analyzer or not direction_analyzer.is_running:
        raise HTTPException(status_code=400, detail="Direction analysis is not running")

    direction_analyzer.stop_analysis()
    return {"message": "Direction analysis stopped"}


@app.get("/api/directions/status")
async def get_direction_status():
    """Get direction analysis status"""
    global direction_analyzer

    if not direction_analyzer:
        return {"is_running": False, "status": "not_started"}

    return direction_analyzer.get_status()


@app.get("/api/directions/{camera_id}/{view_id}")
async def get_direction(camera_id: int, view_id: int):
    """Get direction assessment for specific camera view"""
    try:
        db = DirectionDatabase()
        assessment = db.get_assessment(camera_id, view_id)
        db.close()

        if not assessment:
            raise HTTPException(
                status_code=404,
                detail=f"No assessment found for camera {camera_id}, view {view_id}"
            )

        return assessment

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/directions/pending")
async def get_pending_cameras():
    """Get list of cameras that need direction analysis"""
    try:
        db = DirectionDatabase()
        pending = db.get_pending_cameras()
        db.close()

        return {
            "pending_cameras": pending,
            "count": len(pending)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/directions")
async def get_all_directions():
    """Get all direction assessments"""
    try:
        db = DirectionDatabase()
        assessments = db.get_all_assessments()
        db.close()

        return {
            "assessments": assessments,
            "count": len(assessments)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBAPP EXPORT ENDPOINTS
# ============================================================================

@app.post("/api/export/webapp")
async def export_to_webapp():
    """Manually trigger export of latest camera data to webapp"""
    try:
        global webapp_exporter

        result = webapp_exporter.export_latest_collection()

        if result:
            return {
                "status": "success",
                "message": "WebApp data exported successfully",
                "collection_id": result['collection_id'],
                "cameras": result['cameras'],
                "images": result['images'],
                "timestamp": result['timestamp']
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="No completed collections found to export"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# IMAGE SERVING ENDPOINTS
# ============================================================================

@app.get("/api/images/{collection_id}/{filename}")
async def get_image(collection_id: str, filename: str):
    """Serve camera image file"""
    image_path = os.path.join(CAMERA_IMAGES_DIR, collection_id, filename)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def start_server():
    """Start the FastAPI server"""
    uvicorn.run(
        "fastapi_backend.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    )


if __name__ == "__main__":
    start_server()

