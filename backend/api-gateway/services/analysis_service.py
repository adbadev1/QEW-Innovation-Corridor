"""
Analysis Orchestration Service
===============================

Orchestrates the complete workflow:
Camera Image Collection → GCP Upload → Gemini Analysis → Work Zone Storage
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Camera, WorkZone, CollectionRun
from .camera_service import camera_service
from .gcp_storage_service import gcp_storage_service
from .gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AnalysisOrchestrationService:
    """
    Service for orchestrating end-to-end work zone detection

    Workflow:
    1. Fetch images from COMPASS cameras
    2. Upload to GCP Cloud Storage
    3. Analyze with Gemini Vision API
    4. Store detected work zones in database
    5. Update collection run statistics
    """

    async def run_full_analysis(
        self,
        camera_ids: List[int],
        collection_id: str,
        min_risk_threshold: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Run complete analysis workflow for specified cameras

        Args:
            camera_ids: List of camera database IDs
            collection_id: Collection run identifier
            min_risk_threshold: Minimum risk score to store work zones
            db: Database session

        Returns:
            Analysis summary
        """
        logger.info(f"🚀 Starting full analysis for collection {collection_id}")
        start_time = datetime.utcnow()

        # Get collection run
        collection_query = select(CollectionRun).where(
            CollectionRun.collection_id == collection_id
        )
        collection_result = await db.execute(collection_query)
        collection_run = collection_result.scalar_one_or_none()

        if not collection_run:
            raise ValueError(f"Collection {collection_id} not found")

        try:
            # Step 1: Fetch cameras from database
            cameras_query = select(Camera).where(Camera.id.in_(camera_ids))
            cameras_result = await db.execute(cameras_query)
            cameras = list(cameras_result.scalars().all())

            logger.info(f"📷 Fetching images from {len(cameras)} cameras...")

            # Step 2: Fetch camera images
            camera_id_strings = [cam.camera_id for cam in cameras]
            fetch_results = await camera_service.fetch_multiple_cameras(camera_id_strings)

            # Track statistics
            images_collected = 0
            images_failed = 0
            work_zones_detected = 0
            high_risk_zones = 0

            # Step 3: Process each camera image
            for (camera_id_str, image_data), camera in zip(fetch_results, cameras):
                if image_data is None:
                    images_failed += 1
                    logger.warning(f"⚠️  Failed to fetch image from {camera_id_str}")
                    continue

                images_collected += 1

                try:
                    # Upload to GCP
                    filename = f"{camera_id_str}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
                    gcp_url = await gcp_storage_service.upload_image(
                        image_data,
                        filename,
                        camera_id_str
                    )

                    if not gcp_url:
                        logger.warning(f"⚠️  Failed to upload {camera_id_str} to GCP")
                        continue

                    # Analyze with Gemini
                    logger.info(f"🔍 Analyzing {camera_id_str}...")
                    analysis = await gemini_service.analyze_work_zone(gcp_url, "url")

                    # Store work zone if detected and risk >= threshold
                    if analysis["has_work_zone"] and analysis["risk_score"] >= min_risk_threshold:
                        work_zone = WorkZone(
                            camera_id=camera.id,
                            latitude=camera.latitude,
                            longitude=camera.longitude,
                            risk_score=analysis["risk_score"],
                            confidence=analysis["confidence"],
                            workers=analysis.get("workers", 0),
                            vehicles=analysis.get("vehicles", 0),
                            equipment=analysis.get("equipment", 0),
                            barriers=analysis.get("barriers", False),
                            hazards=analysis.get("hazards"),
                            violations=analysis.get("violations"),
                            recommendations=analysis.get("recommendations"),
                            mto_book_compliance=analysis.get("mto_book_compliance", False),
                            gcp_image_url=gcp_url,
                            collection_id=collection_id,
                            model="gemini-2.0-flash-exp",
                            synthetic=False,
                            status="active"
                        )

                        db.add(work_zone)
                        work_zones_detected += 1

                        if analysis["risk_score"] >= 7:
                            high_risk_zones += 1

                        logger.info(
                            f"✅ Work zone detected at {camera_id_str}: "
                            f"Risk {analysis['risk_score']}/10"
                        )

                except Exception as e:
                    logger.error(f"❌ Error processing {camera_id_str}: {e}", exc_info=True)
                    images_failed += 1

            # Step 4: Update collection run
            collection_run.images_collected = images_collected
            collection_run.images_failed = images_failed
            collection_run.work_zones_detected = work_zones_detected
            collection_run.high_risk_zones = high_risk_zones
            collection_run.status = "completed"
            collection_run.completed_at = datetime.utcnow()

            await db.commit()

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.info(
                f"✅ Analysis complete: {work_zones_detected} work zones detected "
                f"in {duration:.1f}s"
            )

            return {
                "collection_id": collection_id,
                "status": "completed",
                "cameras_processed": len(cameras),
                "images_collected": images_collected,
                "images_failed": images_failed,
                "work_zones_detected": work_zones_detected,
                "high_risk_zones": high_risk_zones,
                "duration_seconds": round(duration, 2),
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat()
            }

        except Exception as e:
            # Mark collection as failed
            collection_run.status = "failed"
            collection_run.error_message = str(e)
            collection_run.completed_at = datetime.utcnow()
            await db.commit()

            logger.error(f"❌ Analysis failed: {e}", exc_info=True)
            raise

    async def analyze_single_camera(
        self,
        camera_id: int,
        min_risk_threshold: int,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze single camera image

        Args:
            camera_id: Camera database ID
            min_risk_threshold: Minimum risk to store work zone
            db: Database session

        Returns:
            Analysis result or None
        """
        try:
            # Get camera
            camera_query = select(Camera).where(Camera.id == camera_id)
            camera_result = await db.execute(camera_query)
            camera = camera_result.scalar_one_or_none()

            if not camera:
                raise ValueError(f"Camera {camera_id} not found")

            # Fetch image
            logger.info(f"📷 Fetching image from {camera.camera_id}...")
            image_data = await camera_service.fetch_camera_image(camera.camera_id)

            if not image_data:
                return None

            # Upload to GCP
            filename = f"{camera.camera_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
            gcp_url = await gcp_storage_service.upload_image(
                image_data,
                filename,
                camera.camera_id
            )

            if not gcp_url:
                return None

            # Analyze
            logger.info(f"🔍 Analyzing {camera.camera_id}...")
            analysis = await gemini_service.analyze_work_zone(gcp_url, "url")

            # Store if work zone detected
            work_zone_id = None
            if analysis["has_work_zone"] and analysis["risk_score"] >= min_risk_threshold:
                work_zone = WorkZone(
                    camera_id=camera.id,
                    latitude=camera.latitude,
                    longitude=camera.longitude,
                    risk_score=analysis["risk_score"],
                    confidence=analysis["confidence"],
                    workers=analysis.get("workers", 0),
                    vehicles=analysis.get("vehicles", 0),
                    equipment=analysis.get("equipment", 0),
                    barriers=analysis.get("barriers", False),
                    hazards=analysis.get("hazards"),
                    violations=analysis.get("violations"),
                    recommendations=analysis.get("recommendations"),
                    mto_book_compliance=analysis.get("mto_book_compliance", False),
                    gcp_image_url=gcp_url,
                    model="gemini-2.0-flash-exp",
                    synthetic=False,
                    status="active"
                )

                db.add(work_zone)
                await db.commit()
                await db.refresh(work_zone)
                work_zone_id = work_zone.id

            return {
                "camera_id": camera.camera_id,
                "camera_location": camera.location,
                "image_url": gcp_url,
                "analysis": analysis,
                "work_zone_id": work_zone_id,
                "analyzed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Single camera analysis failed: {e}", exc_info=True)
            return None

    async def reanalyze_existing_images(
        self,
        collection_id: str,
        min_risk_threshold: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Re-analyze images from an existing collection

        Useful for testing different prompts or thresholds.

        Args:
            collection_id: Collection to re-analyze
            min_risk_threshold: New risk threshold
            db: Database session

        Returns:
            Re-analysis summary
        """
        logger.info(f"🔄 Re-analyzing collection {collection_id}")

        # Get existing work zones from this collection
        wz_query = select(WorkZone).where(WorkZone.collection_id == collection_id)
        wz_result = await db.execute(wz_query)
        existing_work_zones = list(wz_result.scalars().all())

        if not existing_work_zones:
            logger.warning(f"⚠️  No work zones found for collection {collection_id}")
            return {
                "collection_id": collection_id,
                "images_reanalyzed": 0,
                "new_work_zones_detected": 0,
                "message": "No images found to re-analyze"
            }

        new_detections = 0

        for wz in existing_work_zones:
            if not wz.gcp_image_url:
                continue

            try:
                # Re-analyze with new threshold
                analysis = await gemini_service.analyze_work_zone(wz.gcp_image_url, "url")

                # Update work zone
                wz.risk_score = analysis["risk_score"]
                wz.confidence = analysis["confidence"]
                wz.workers = analysis.get("workers", 0)
                wz.vehicles = analysis.get("vehicles", 0)
                wz.equipment = analysis.get("equipment", 0)
                wz.barriers = analysis.get("barriers", False)
                wz.hazards = analysis.get("hazards")
                wz.violations = analysis.get("violations")
                wz.recommendations = analysis.get("recommendations")
                wz.mto_book_compliance = analysis.get("mto_book_compliance", False)

                # Update status based on new threshold
                if analysis["risk_score"] < min_risk_threshold:
                    wz.status = "archived"
                elif wz.status == "archived":
                    wz.status = "active"
                    new_detections += 1

                logger.info(f"✅ Re-analyzed work zone {wz.id}: Risk {analysis['risk_score']}/10")

            except Exception as e:
                logger.error(f"❌ Failed to re-analyze work zone {wz.id}: {e}")

        await db.commit()

        return {
            "collection_id": collection_id,
            "images_reanalyzed": len(existing_work_zones),
            "new_work_zones_detected": new_detections,
            "min_risk_threshold": min_risk_threshold,
            "reanalyzed_at": datetime.utcnow().isoformat()
        }


# Global service instance
analysis_orchestration_service = AnalysisOrchestrationService()


# Convenience functions
async def run_camera_analysis(
    camera_ids: List[int],
    collection_id: str,
    min_risk_threshold: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Convenience function for full analysis workflow

    Args:
        camera_ids: List of camera database IDs
        collection_id: Collection identifier
        min_risk_threshold: Minimum risk score
        db: Database session

    Returns:
        Analysis summary
    """
    return await analysis_orchestration_service.run_full_analysis(
        camera_ids,
        collection_id,
        min_risk_threshold,
        db
    )


async def analyze_single_camera_image(
    camera_id: int,
    min_risk_threshold: int,
    db: AsyncSession
) -> Optional[Dict[str, Any]]:
    """
    Convenience function for single camera analysis

    Args:
        camera_id: Camera database ID
        min_risk_threshold: Minimum risk score
        db: Database session

    Returns:
        Analysis result or None
    """
    return await analysis_orchestration_service.analyze_single_camera(
        camera_id,
        min_risk_threshold,
        db
    )
