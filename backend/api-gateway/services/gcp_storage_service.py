"""
GCP Cloud Storage Service
==========================

Service for managing camera images in Google Cloud Storage.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import io

try:
    from google.cloud import storage
    from google.cloud.exceptions import GoogleCloudError
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    logging.warning("google-cloud-storage not installed. GCP features disabled.")

from config import settings

logger = logging.getLogger(__name__)


class GCPStorageService:
    """Service for GCP Cloud Storage operations"""

    def __init__(self):
        """Initialize GCP Storage client"""
        self.bucket_name = settings.GCP_STORAGE_BUCKET
        self.project_id = settings.GCP_PROJECT_ID
        self.api_available = GCP_AVAILABLE

        if self.api_available:
            try:
                self.client = storage.Client(project=self.project_id)
                self.bucket = self.client.bucket(self.bucket_name)
                logger.info(f"✅ GCP Storage initialized: gs://{self.bucket_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize GCP Storage: {e}")
                self.api_available = False

    async def upload_image(
        self,
        image_data: bytes,
        filename: str,
        camera_id: str,
        content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Upload camera image to GCP Storage

        Args:
            image_data: Raw image bytes
            filename: Image filename
            camera_id: Camera identifier
            content_type: MIME type

        Returns:
            Public URL of uploaded image, or None if failed
        """
        if not self.api_available:
            logger.warning("GCP Storage not available")
            return None

        try:
            # Create blob path: camera_images/{camera_id}/{timestamp}_{filename}
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_path = f"camera_images/{camera_id}/{timestamp}_{filename}"

            # Upload to GCS
            blob = self.bucket.blob(blob_path)
            await asyncio.to_thread(
                blob.upload_from_string,
                image_data,
                content_type=content_type
            )

            # Make public (bucket already configured as public)
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"

            logger.info(f"✅ Image uploaded: {blob_path}")
            return public_url

        except Exception as e:
            logger.error(f"❌ GCP upload failed: {e}", exc_info=True)
            return None

    async def download_image(self, blob_path: str) -> Optional[bytes]:
        """
        Download image from GCP Storage

        Args:
            blob_path: Path to blob in bucket

        Returns:
            Image bytes, or None if failed
        """
        if not self.api_available:
            logger.warning("GCP Storage not available")
            return None

        try:
            blob = self.bucket.blob(blob_path)
            image_data = await asyncio.to_thread(blob.download_as_bytes)
            logger.info(f"✅ Image downloaded: {blob_path}")
            return image_data

        except Exception as e:
            logger.error(f"❌ GCP download failed: {e}", exc_info=True)
            return None

    async def list_camera_images(
        self,
        camera_id: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all images for a specific camera

        Args:
            camera_id: Camera identifier
            max_results: Maximum number of results

        Returns:
            List of image metadata dicts
        """
        if not self.api_available:
            logger.warning("GCP Storage not available")
            return []

        try:
            prefix = f"camera_images/{camera_id}/"
            blobs = await asyncio.to_thread(
                lambda: list(self.client.list_blobs(
                    self.bucket_name,
                    prefix=prefix,
                    max_results=max_results
                ))
            )

            images = []
            for blob in blobs:
                images.append({
                    "filename": blob.name,
                    "public_url": f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}",
                    "size": blob.size,
                    "created_at": blob.time_created.isoformat() if blob.time_created else None,
                    "content_type": blob.content_type
                })

            logger.info(f"✅ Found {len(images)} images for camera {camera_id}")
            return images

        except Exception as e:
            logger.error(f"❌ GCP list failed: {e}", exc_info=True)
            return []

    async def delete_image(self, blob_path: str) -> bool:
        """
        Delete image from GCP Storage

        Args:
            blob_path: Path to blob

        Returns:
            True if successful, False otherwise
        """
        if not self.api_available:
            logger.warning("GCP Storage not available")
            return False

        try:
            blob = self.bucket.blob(blob_path)
            await asyncio.to_thread(blob.delete)
            logger.info(f"✅ Image deleted: {blob_path}")
            return True

        except Exception as e:
            logger.error(f"❌ GCP delete failed: {e}", exc_info=True)
            return False

    async def generate_signed_url(
        self,
        blob_path: str,
        expiration_minutes: int = 60
    ) -> Optional[str]:
        """
        Generate signed URL for temporary access

        Args:
            blob_path: Path to blob
            expiration_minutes: URL expiration time

        Returns:
            Signed URL, or None if failed
        """
        if not self.api_available:
            logger.warning("GCP Storage not available")
            return None

        try:
            blob = self.bucket.blob(blob_path)
            expiration = timedelta(minutes=expiration_minutes)

            signed_url = await asyncio.to_thread(
                blob.generate_signed_url,
                expiration=expiration,
                version="v4"
            )

            logger.info(f"✅ Signed URL generated: {blob_path}")
            return signed_url

        except Exception as e:
            logger.error(f"❌ Signed URL generation failed: {e}", exc_info=True)
            return None

    async def batch_upload(
        self,
        images: List[Dict[str, Any]]
    ) -> List[Optional[str]]:
        """
        Upload multiple images in parallel

        Args:
            images: List of dicts with 'data', 'filename', 'camera_id' keys

        Returns:
            List of public URLs (None for failed uploads)
        """
        tasks = [
            self.upload_image(
                img['data'],
                img['filename'],
                img['camera_id'],
                img.get('content_type', 'image/jpeg')
            )
            for img in images
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        urls = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Upload {i} failed: {result}")
                urls.append(None)
            else:
                urls.append(result)

        return urls

    def get_public_url(self, blob_path: str) -> str:
        """
        Get public URL for a blob

        Args:
            blob_path: Path to blob in bucket

        Returns:
            Public URL
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"


# Global service instance
gcp_storage_service = GCPStorageService()


# Convenience functions
async def upload_camera_image(
    image_data: bytes,
    filename: str,
    camera_id: str
) -> Optional[str]:
    """
    Convenience function to upload camera image

    Args:
        image_data: Image bytes
        filename: Image filename
        camera_id: Camera identifier

    Returns:
        Public URL or None
    """
    return await gcp_storage_service.upload_image(image_data, filename, camera_id)


async def list_camera_images(camera_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Convenience function to list camera images

    Args:
        camera_id: Camera identifier
        max_results: Maximum results

    Returns:
        List of image metadata
    """
    return await gcp_storage_service.list_camera_images(camera_id, max_results)


async def delete_camera_image(blob_path: str) -> bool:
    """
    Convenience function to delete image

    Args:
        blob_path: Path to blob

    Returns:
        True if successful
    """
    return await gcp_storage_service.delete_image(blob_path)
