/**
 * Local Storage Service
 *
 * Stores camera images locally in browser for the pilot/demo
 * Alternative to GCP Cloud Storage that works entirely client-side
 */

/**
 * Save camera image to local storage with metadata
 * @param {Object} params - Save parameters
 * @param {number} params.cameraId - Camera ID
 * @param {number} params.viewId - View ID
 * @param {number} params.round - Collection round number
 * @param {string} params.collectionId - Collection ID
 * @param {Blob} params.imageBlob - Image blob data
 * @param {Object} params.metadata - Additional metadata
 * @returns {Promise<Object>} Save result
 */
export async function saveImageLocally({ cameraId, viewId, round, collectionId, imageBlob, metadata = {} }) {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19).replace('T', '_');
    const filename = `c${cameraId}_v${viewId}_r${round}_${timestamp}.jpg`;

    // Convert blob to base64 for localStorage
    const base64 = await blobToBase64(imageBlob);

    const imageRecord = {
      id: filename.replace('.jpg', ''),
      filename,
      cameraId,
      viewId,
      round,
      collectionId,
      timestamp,
      size: imageBlob.size,
      type: imageBlob.type,
      data: base64, // Store as base64
      metadata: {
        ...metadata,
        savedAt: new Date().toISOString(),
        storageType: 'localStorage'
      }
    };

    // Store in localStorage (limit to recent images to avoid quota)
    const storageKey = `qew_image_${filename}`;
    localStorage.setItem(storageKey, JSON.stringify(imageRecord));

    // Also track in collection index
    trackImageInCollection(collectionId, imageRecord);

    console.log(`[Local Storage] Saved: ${filename} (${(imageBlob.size / 1024).toFixed(1)} KB)`);

    return {
      ...imageRecord,
      localUrl: base64, // Can be used directly in <img> tags
      success: true
    };

  } catch (error) {
    console.error('[Local Storage] Save error:', error);
    throw error;
  }
}

/**
 * Convert blob to base64 data URL
 * @param {Blob} blob - Image blob
 * @returns {Promise<string>} Base64 data URL
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Track image in collection index
 * @param {string} collectionId - Collection ID
 * @param {Object} imageRecord - Image record
 */
function trackImageInCollection(collectionId, imageRecord) {
  const indexKey = `qew_collection_index_${collectionId}`;
  const existingIndex = JSON.parse(localStorage.getItem(indexKey) || '[]');

  existingIndex.push({
    filename: imageRecord.filename,
    cameraId: imageRecord.cameraId,
    viewId: imageRecord.viewId,
    timestamp: imageRecord.timestamp,
    size: imageRecord.size
  });

  localStorage.setItem(indexKey, JSON.stringify(existingIndex));
}

/**
 * Get images for a collection
 * @param {string} collectionId - Collection ID
 * @returns {Array} Array of image records
 */
export function getCollectionImages(collectionId) {
  const indexKey = `qew_collection_index_${collectionId}`;
  const index = JSON.parse(localStorage.getItem(indexKey) || '[]');

  return index.map(item => {
    const imageKey = `qew_image_${item.filename}`;
    const imageData = localStorage.getItem(imageKey);
    return imageData ? JSON.parse(imageData) : null;
  }).filter(Boolean);
}

/**
 * Clean up old images (keep last N collections)
 * @param {number} keepCollections - Number of collections to keep
 * @returns {number} Number of images deleted
 */
export function cleanupOldImages(keepCollections = 3) {
  try {
    const collectionKeys = Object.keys(localStorage)
      .filter(key => key.startsWith('qew_collection_index_'))
      .sort()
      .reverse();

    const keysToDelete = collectionKeys.slice(keepCollections);
    let deletedCount = 0;

    keysToDelete.forEach(indexKey => {
      const collectionId = indexKey.replace('qew_collection_index_', '');
      const images = getCollectionImages(collectionId);

      images.forEach(img => {
        const imageKey = `qew_image_${img.filename}`;
        localStorage.removeItem(imageKey);
        deletedCount++;
      });

      localStorage.removeItem(indexKey);
    });

    console.log(`[Local Storage] Cleanup: Deleted ${deletedCount} images`);
    return deletedCount;

  } catch (error) {
    console.error('[Local Storage] Cleanup error:', error);
    return 0;
  }
}

/**
 * Get storage statistics
 * @returns {Object} Storage stats
 */
export function getStorageStats() {
  const imageKeys = Object.keys(localStorage).filter(key => key.startsWith('qew_image_'));

  let totalSize = 0;
  imageKeys.forEach(key => {
    const data = localStorage.getItem(key);
    totalSize += data ? data.length : 0;
  });

  const collections = new Set(
    Object.keys(localStorage)
      .filter(key => key.startsWith('qew_collection_index_'))
      .map(key => key.replace('qew_collection_index_', ''))
  );

  return {
    totalImages: imageKeys.length,
    totalSizeBytes: totalSize,
    totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2),
    collections: collections.size,
    averageImageSize: imageKeys.length > 0 ? Math.round(totalSize / imageKeys.length) : 0
  };
}

/**
 * Check if local storage is available and has space
 * @returns {boolean} True if storage is available
 */
export function isLocalStorageAvailable() {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}
