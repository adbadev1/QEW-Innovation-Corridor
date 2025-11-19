/**
 * Thumbnail Storage Service
 *
 * Stores small thumbnails from latest collection run for map display
 * Uses localStorage with aggressive compression to avoid quota issues
 */

const THUMBNAIL_KEY = 'qew_latest_thumbnails';
const MAX_THUMBNAIL_SIZE = 50 * 1024; // 50KB max per thumbnail

/**
 * Resize and compress image to thumbnail
 * @param {Blob} imageBlob - Original image blob
 * @param {number} maxWidth - Maximum width
 * @param {number} maxHeight - Maximum height
 * @param {number} quality - JPEG quality (0-1)
 * @returns {Promise<string>} Base64 thumbnail data URL
 */
async function createThumbnail(imageBlob, maxWidth = 320, maxHeight = 240, quality = 0.6) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    img.onload = () => {
      // Calculate dimensions maintaining aspect ratio
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width = Math.round((width * maxHeight) / height);
          height = maxHeight;
        }
      }

      canvas.width = width;
      canvas.height = height;

      // Draw resized image
      ctx.drawImage(img, 0, 0, width, height);

      // Convert to compressed JPEG
      const thumbnailDataUrl = canvas.toDataURL('image/jpeg', quality);

      // Check size
      if (thumbnailDataUrl.length > MAX_THUMBNAIL_SIZE) {
        console.warn('Thumbnail still too large, reducing quality');
        resolve(canvas.toDataURL('image/jpeg', 0.4));
      } else {
        resolve(thumbnailDataUrl);
      }
    };

    img.onerror = reject;

    // Create blob URL for image
    const blobUrl = URL.createObjectURL(imageBlob);
    img.src = blobUrl;
  });
}

/**
 * Save thumbnail for a camera view
 * @param {number} cameraId - Camera ID
 * @param {number} viewId - View ID
 * @param {Blob} imageBlob - Image blob
 * @param {Object} metadata - Additional metadata
 */
export async function saveThumbnail(cameraId, viewId, imageBlob, metadata = {}) {
  try {
    // Create compressed thumbnail
    const thumbnailData = await createThumbnail(imageBlob);

    // Load existing thumbnails
    const thumbnails = getAllThumbnails();

    // Add/update thumbnail
    const key = `${cameraId}_${viewId}`;
    thumbnails[key] = {
      cameraId,
      viewId,
      thumbnail: thumbnailData,
      timestamp: new Date().toISOString(),
      size: thumbnailData.length,
      metadata
    };

    // Save back to localStorage
    localStorage.setItem(THUMBNAIL_KEY, JSON.stringify(thumbnails));

    console.log(`[Thumbnails] Saved thumbnail for camera ${cameraId} view ${viewId} (${(thumbnailData.length / 1024).toFixed(1)} KB)`);

    return true;
  } catch (error) {
    console.error('[Thumbnails] Failed to save thumbnail:', error);
    return false;
  }
}

/**
 * Get all thumbnails
 * @returns {Object} Map of camera_view keys to thumbnail data
 */
export function getAllThumbnails() {
  try {
    const stored = localStorage.getItem(THUMBNAIL_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('[Thumbnails] Failed to load thumbnails:', error);
    return {};
  }
}

/**
 * Get thumbnail for specific camera view
 * @param {number} cameraId - Camera ID
 * @param {number} viewId - View ID
 * @returns {Object|null} Thumbnail data or null
 */
export function getThumbnail(cameraId, viewId) {
  const thumbnails = getAllThumbnails();
  const key = `${cameraId}_${viewId}`;
  return thumbnails[key] || null;
}

/**
 * Clear all thumbnails
 */
export function clearAllThumbnails() {
  try {
    localStorage.removeItem(THUMBNAIL_KEY);
    console.log('[Thumbnails] Cleared all thumbnails');
    return true;
  } catch (error) {
    console.error('[Thumbnails] Failed to clear thumbnails:', error);
    return false;
  }
}

/**
 * Get thumbnail statistics
 * @returns {Object} Statistics about stored thumbnails
 */
export function getThumbnailStats() {
  const thumbnails = getAllThumbnails();
  const keys = Object.keys(thumbnails);

  let totalSize = 0;
  keys.forEach(key => {
    totalSize += thumbnails[key].size || 0;
  });

  return {
    count: keys.length,
    totalSizeBytes: totalSize,
    totalSizeKB: (totalSize / 1024).toFixed(1),
    averageSizeKB: keys.length > 0 ? (totalSize / keys.length / 1024).toFixed(1) : 0,
    oldestTimestamp: keys.length > 0
      ? Object.values(thumbnails).reduce((oldest, thumb) =>
          new Date(thumb.timestamp) < new Date(oldest) ? thumb.timestamp : oldest,
          Object.values(thumbnails)[0].timestamp
        )
      : null
  };
}

/**
 * Merge thumbnails into camera data structure
 * @param {Array} cameras - Camera array from JSON
 * @returns {Array} Updated cameras with latest thumbnails
 */
export function mergeThumbnailsIntoCameras(cameras) {
  const thumbnails = getAllThumbnails();

  return cameras.map(camera => {
    const updatedViews = camera.Views.map(view => {
      const thumbnail = getThumbnail(camera.Id, view.Id);

      if (thumbnail) {
        // Add latest thumbnail to view
        return {
          ...view,
          LatestImage: {
            dataUrl: thumbnail.thumbnail,
            timestamp: thumbnail.timestamp,
            metadata: thumbnail.metadata
          }
        };
      }

      return view;
    });

    return {
      ...camera,
      Views: updatedViews
    };
  });
}
