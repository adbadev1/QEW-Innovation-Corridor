"""
Camera Image Collection Service
================================

Service for fetching images from QEW COMPASS traffic cameras.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio
from datetime import datetime
import aiohttp
from aiohttp import ClientTimeout

from config import settings

logger = logging.getLogger(__name__)


# COMPASS camera image URL pattern
# Real URLs are in format: http://www.mto.gov.on.ca/compass/camera/loc{camera_num}.jpg
# Example: http://www.mto.gov.on.ca/compass/camera/loc253.jpg
COMPASS_URL_PATTERN = "http://www.mto.gov.on.ca/compass/camera/loc{camera_num}.jpg"

# Timeout for camera image requests (seconds)
REQUEST_TIMEOUT = 10


class CameraImageService:
    """Service for collecting images from traffic cameras"""

    def __init__(self):
        """Initialize camera image service"""
        self.timeout = ClientTimeout(total=REQUEST_TIMEOUT)

    async def fetch_camera_image(
        self,
        camera_id: str,
        view_id: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Fetch current image from a COMPASS camera

        Args:
            camera_id: Camera identifier (e.g., "CAM_253")
            view_id: Optional view number for multi-view cameras

        Returns:
            Image bytes, or None if failed
        """
        try:
            # Extract camera number from camera_id
            # Format: CAM_253 -> 253
            if camera_id.startswith("CAM_"):
                camera_num = camera_id.split("_")[1]
            else:
                camera_num = camera_id

            # Build URL
            url = COMPASS_URL_PATTERN.format(camera_num=camera_num)

            # For multi-view cameras, append view parameter
            if view_id is not None:
                url = f"{url}?view={view_id}"

            # Fetch image
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        logger.info(f"✅ Fetched image from {camera_id} ({len(image_data)} bytes)")
                        return image_data
                    else:
                        logger.warning(f"⚠️  Camera {camera_id} returned status {response.status}")
                        return None

        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout fetching image from {camera_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to fetch image from {camera_id}: {e}")
            return None

    async def fetch_multiple_cameras(
        self,
        camera_ids: List[str],
        max_concurrent: int = 10
    ) -> List[Tuple[str, Optional[bytes]]]:
        """
        Fetch images from multiple cameras in parallel

        Args:
            camera_ids: List of camera identifiers
            max_concurrent: Maximum concurrent requests

        Returns:
            List of tuples (camera_id, image_data)
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_limit(camera_id: str):
            async with semaphore:
                image_data = await self.fetch_camera_image(camera_id)
                return (camera_id, image_data)

        tasks = [fetch_with_limit(cam_id) for cam_id in camera_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Camera fetch failed: {result}")
                processed_results.append((None, None))
            else:
                processed_results.append(result)

        return processed_results

    async def test_camera_connection(self, camera_id: str) -> Dict[str, Any]:
        """
        Test connection to a camera

        Args:
            camera_id: Camera identifier

        Returns:
            Connection test results
        """
        start_time = datetime.utcnow()

        try:
            # Extract camera number
            if camera_id.startswith("CAM_"):
                camera_num = camera_id.split("_")[1]
            else:
                camera_num = camera_id

            url = COMPASS_URL_PATTERN.format(camera_num=camera_num)

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    end_time = datetime.utcnow()
                    response_time = (end_time - start_time).total_seconds()

                    return {
                        "camera_id": camera_id,
                        "url": url,
                        "status": "online" if response.status == 200 else "offline",
                        "status_code": response.status,
                        "response_time_seconds": round(response_time, 3),
                        "content_type": response.headers.get("Content-Type"),
                        "content_length": int(response.headers.get("Content-Length", 0)),
                        "tested_at": datetime.utcnow().isoformat()
                    }

        except asyncio.TimeoutError:
            return {
                "camera_id": camera_id,
                "url": url,
                "status": "timeout",
                "status_code": None,
                "response_time_seconds": REQUEST_TIMEOUT,
                "error": "Request timeout",
                "tested_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "camera_id": camera_id,
                "url": url,
                "status": "error",
                "status_code": None,
                "response_time_seconds": None,
                "error": str(e),
                "tested_at": datetime.utcnow().isoformat()
            }

    async def test_multiple_cameras(
        self,
        camera_ids: List[str],
        max_concurrent: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Test connection to multiple cameras

        Args:
            camera_ids: List of camera identifiers
            max_concurrent: Maximum concurrent tests

        Returns:
            List of test results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def test_with_limit(camera_id: str):
            async with semaphore:
                return await self.test_camera_connection(camera_id)

        tasks = [test_with_limit(cam_id) for cam_id in camera_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Camera test {i} failed: {result}")
                processed_results.append({
                    "camera_id": camera_ids[i],
                    "status": "error",
                    "error": str(result),
                    "tested_at": datetime.utcnow().isoformat()
                })
            else:
                processed_results.append(result)

        return processed_results

    async def get_camera_stats(
        self,
        camera_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for camera connectivity

        Args:
            camera_ids: List of camera identifiers

        Returns:
            Connectivity statistics
        """
        test_results = await self.test_multiple_cameras(camera_ids)

        online = sum(1 for r in test_results if r.get("status") == "online")
        offline = sum(1 for r in test_results if r.get("status") == "offline")
        timeout = sum(1 for r in test_results if r.get("status") == "timeout")
        error = sum(1 for r in test_results if r.get("status") == "error")

        response_times = [
            r["response_time_seconds"]
            for r in test_results
            if r.get("response_time_seconds") is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        return {
            "total_cameras": len(camera_ids),
            "online": online,
            "offline": offline,
            "timeout": timeout,
            "error": error,
            "success_rate": round(online / len(camera_ids) * 100, 2) if camera_ids else 0,
            "average_response_time_seconds": round(avg_response_time, 3),
            "tested_at": datetime.utcnow().isoformat()
        }


# Global service instance
camera_service = CameraImageService()


# Convenience functions
async def fetch_camera_image(camera_id: str) -> Optional[bytes]:
    """
    Convenience function to fetch single camera image

    Args:
        camera_id: Camera identifier

    Returns:
        Image bytes or None
    """
    return await camera_service.fetch_camera_image(camera_id)


async def fetch_multiple_camera_images(camera_ids: List[str]) -> List[Tuple[str, Optional[bytes]]]:
    """
    Convenience function to fetch multiple camera images

    Args:
        camera_ids: List of camera identifiers

    Returns:
        List of (camera_id, image_data) tuples
    """
    return await camera_service.fetch_multiple_cameras(camera_ids)


async def test_camera_connectivity(camera_id: str) -> Dict[str, Any]:
    """
    Convenience function to test camera connectivity

    Args:
        camera_id: Camera identifier

    Returns:
        Test results
    """
    return await camera_service.test_camera_connection(camera_id)


async def get_camera_connectivity_stats(camera_ids: List[str]) -> Dict[str, Any]:
    """
    Convenience function to get camera connectivity statistics

    Args:
        camera_ids: List of camera identifiers

    Returns:
        Connectivity statistics
    """
    return await camera_service.get_camera_stats(camera_ids)
