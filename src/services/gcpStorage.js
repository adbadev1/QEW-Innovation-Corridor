/**
 * GCP Cloud Storage Service
 *
 * Uploads camera images to Google Cloud Storage bucket
 * Provides persistent storage for camera collection images
 *
 * SETUP REQUIRED:
 * 1. Create GCS bucket: gs://qew-camera-images/
 * 2. Set up CORS for browser uploads
 * 3. Configure signed URLs or public bucket access
 * 4. Add GCP_STORAGE_BUCKET to environment variables
 *
 * Storage Structure:
 * gs://qew-camera-images/
 *   ├── collections/
 *   │   ├── qew_collection_20251118_181530/
 *   │   │   ├── c253_v613_r1_20251118_181719.jpg
 *   │   │   ├── c253_v614_r1_20251118_181720.jpg
 *   │   │   └── ...
 *   │   └── qew_collection_20251118_191530/
 *   │       └── ...
 *   └── metadata/
 *       └── collection_manifest.json
 */

const GCS_BUCKET = import.meta.env.VITE_GCP_STORAGE_BUCKET || 'qew-camera-images';
const GCS_PROJECT = import.meta.env.VITE_GCP_PROJECT_ID;
// IMPORTANT: Only use dedicated GCP Storage API key (NOT Gemini API key)
const GCS_API_KEY = import.meta.env.VITE_GCP_STORAGE_API_KEY;

// Base URL for Google Cloud Storage API
const GCS_API_BASE = 'https://storage.googleapis.com';
const GCS_UPLOAD_BASE = `${GCS_API_BASE}/upload/storage/v1/b/${GCS_BUCKET}/o`;

/**
 * Download camera image from 511ON URL
 * @param {string} imageUrl - Camera view URL (e.g., https://511on.ca/map/Cctv/613)
 * @returns {Promise<Blob>} Image blob
 */
export async function downloadCameraImage(imageUrl) {
  try {
    console.log(`[GCP Storage] Downloading image from: ${imageUrl}`);

    // Try direct fetch first (may fail due to CORS)
    let response;
    try {
      response = await fetch(imageUrl, {
        mode: 'cors',
        credentials: 'omit',
        cache: 'no-cache'
      });
    } catch (corsError) {
      console.warn('[GCP Storage] CORS error, trying proxy...', corsError.message);

      // Fallback to CORS proxy
      const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(imageUrl)}`;
      console.log(`[GCP Storage] Using proxy: ${proxyUrl}`);
      response = await fetch(proxyUrl);
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();

    // Check if image is empty (0 bytes means camera offline)
    if (blob.size === 0) {
      throw new Error('Camera returned empty image (offline)');
    }

    // Validate it's actually an image
    if (!blob.type.startsWith('image/')) {
      console.warn(`[GCP Storage] Unexpected content type: ${blob.type}, but continuing...`);
    }

    console.log(`[GCP Storage] Downloaded: ${blob.size} bytes (${blob.type})`);
    return blob;

  } catch (error) {
    console.error('[GCP Storage] Download failed:', error.message);
    throw error;
  }
}

/**
 * Upload camera image to GCP Cloud Storage
 * @param {Object} params - Upload parameters
 * @param {number} params.cameraId - Camera ID
 * @param {number} params.viewId - View ID
 * @param {number} params.round - Collection round number
 * @param {string} params.collectionId - Collection ID (e.g., "qew_collection_20251118_181530")
 * @param {Blob} params.imageBlob - Image blob data
 * @param {Object} params.metadata - Additional metadata
 * @returns {Promise<Object>} Upload result with GCS URL
 */
export async function uploadCameraImage({ cameraId, viewId, round, collectionId, imageBlob, metadata = {} }) {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19).replace('T', '_');
    const filename = `c${cameraId}_v${viewId}_r${round}_${timestamp}.jpg`;
    const objectPath = `collections/${collectionId}/${filename}`;

    console.log(`[GCP Storage] Uploading to: gs://${GCS_BUCKET}/${objectPath}`);

    // Prepare upload request
    const uploadUrl = `${GCS_UPLOAD_BASE}?uploadType=media&name=${encodeURIComponent(objectPath)}&key=${GCS_API_KEY}`;

    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': imageBlob.type,
        'Content-Length': imageBlob.size.toString()
      },
      body: imageBlob
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[GCP Storage] Upload failed:', response.status, errorText);
      throw new Error(`GCS upload failed: ${response.status} - ${errorText}`);
    }

    const result = await response.json();

    const uploadRecord = {
      id: filename.replace('.jpg', ''),
      filename,
      path: objectPath,
      cameraId,
      viewId,
      round,
      collectionId,
      timestamp,
      size: imageBlob.size,
      type: imageBlob.type,
      gcsUrl: `gs://${GCS_BUCKET}/${objectPath}`,
      publicUrl: `${GCS_API_BASE}/${GCS_BUCKET}/${objectPath}`,
      metadata: {
        ...metadata,
        uploadedAt: new Date().toISOString(),
        bucket: GCS_BUCKET,
        generation: result.generation,
        metageneration: result.metageneration
      }
    };

    console.log(`[GCP Storage] Upload successful: ${uploadRecord.publicUrl}`);
    return uploadRecord;

  } catch (error) {
    console.error('[GCP Storage] Upload error:', error);
    throw error;
  }
}

/**
 * Get public URL for uploaded image
 * @param {string} objectPath - Object path in bucket (e.g., "collections/qew_collection_.../c253_v613_r1_....jpg")
 * @returns {string} Public URL
 */
export function getImageUrl(objectPath) {
  return `${GCS_API_BASE}/${GCS_BUCKET}/${objectPath}`;
}

/**
 * List all images in a collection
 * @param {string} collectionId - Collection ID
 * @returns {Promise<Array>} Array of image objects
 */
export async function listCollectionImages(collectionId) {
  try {
    const prefix = `collections/${collectionId}/`;
    const listUrl = `${GCS_API_BASE}/storage/v1/b/${GCS_BUCKET}/o?prefix=${encodeURIComponent(prefix)}&key=${GCS_API_KEY}`;

    const response = await fetch(listUrl);

    if (!response.ok) {
      throw new Error(`Failed to list objects: ${response.status}`);
    }

    const data = await response.json();

    return (data.items || []).map(item => ({
      filename: item.name.split('/').pop(),
      path: item.name,
      publicUrl: `${GCS_API_BASE}/${GCS_BUCKET}/${item.name}`,
      size: parseInt(item.size),
      updated: item.updated,
      contentType: item.contentType
    }));

  } catch (error) {
    console.error('[GCP Storage] List failed:', error);
    return [];
  }
}

/**
 * Delete old collections (keep last N collections)
 * @param {number} keepCollections - Number of collections to keep
 * @returns {Promise<number>} Number of objects deleted
 */
export async function cleanupOldCollections(keepCollections = 5) {
  try {
    // List all collection directories
    const listUrl = `${GCS_API_BASE}/storage/v1/b/${GCS_BUCKET}/o?prefix=collections/&delimiter=/&key=${GCS_API_KEY}`;
    const response = await fetch(listUrl);

    if (!response.ok) {
      throw new Error(`Failed to list collections: ${response.status}`);
    }

    const data = await response.json();
    const prefixes = data.prefixes || [];

    // Sort collections by name (contains timestamp)
    const sortedCollections = prefixes.sort().reverse();

    // Delete old collections
    const collectionsToDelete = sortedCollections.slice(keepCollections);
    let deletedCount = 0;

    for (const collectionPrefix of collectionsToDelete) {
      // List all objects in this collection
      const objectsResponse = await fetch(
        `${GCS_API_BASE}/storage/v1/b/${GCS_BUCKET}/o?prefix=${encodeURIComponent(collectionPrefix)}&key=${GCS_API_KEY}`
      );

      if (objectsResponse.ok) {
        const objectsData = await objectsResponse.json();
        const objects = objectsData.items || [];

        // Delete each object
        for (const obj of objects) {
          const deleteUrl = `${GCS_API_BASE}/storage/v1/b/${GCS_BUCKET}/o/${encodeURIComponent(obj.name)}?key=${GCS_API_KEY}`;
          const deleteResponse = await fetch(deleteUrl, { method: 'DELETE' });

          if (deleteResponse.ok) {
            deletedCount++;
          }
        }
      }
    }

    console.log(`[GCP Storage] Cleanup complete: ${deletedCount} objects deleted`);
    return deletedCount;

  } catch (error) {
    console.error('[GCP Storage] Cleanup failed:', error);
    return 0;
  }
}

/**
 * Get storage statistics
 * @returns {Promise<Object>} Storage stats
 */
export async function getStorageStats() {
  try {
    const listUrl = `${GCS_API_BASE}/storage/v1/b/${GCS_BUCKET}/o?prefix=collections/&key=${GCS_API_KEY}`;
    const response = await fetch(listUrl);

    if (!response.ok) {
      throw new Error(`Failed to get stats: ${response.status}`);
    }

    const data = await response.json();
    const items = data.items || [];

    const totalSize = items.reduce((sum, item) => sum + parseInt(item.size || 0), 0);
    const collections = new Set(items.map(item => item.name.split('/')[1]));

    return {
      totalImages: items.length,
      totalSizeBytes: totalSize,
      totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2),
      collections: collections.size,
      averageImageSize: items.length > 0 ? Math.round(totalSize / items.length) : 0
    };

  } catch (error) {
    console.error('[GCP Storage] Get stats failed:', error);
    return {
      totalImages: 0,
      totalSizeBytes: 0,
      totalSizeMB: '0.00',
      collections: 0,
      averageImageSize: 0
    };
  }
}

/**
 * Convert blob to File object (for Gemini AI analysis)
 * @param {Blob} blob - Image blob
 * @param {string} filename - Filename
 * @returns {File} File object
 */
export function blobToFile(blob, filename) {
  return new File([blob], filename, { type: blob.type });
}

/**
 * Check if GCP Storage is configured
 * @returns {boolean} True if API key is configured
 */
export function isGCPConfigured() {
  return !!GCS_API_KEY && GCS_API_KEY !== 'YOUR_GOOGLE_API_KEY';
}
