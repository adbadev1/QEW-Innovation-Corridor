/**
 * Image Search API Service
 *
 * Fetches construction work zone images for synthetic testing
 * Uses Google Custom Search API (free tier: 100 queries/day)
 *
 * SEARCH STRATEGY:
 * - Simple keyword-based image search
 * - Filters by construction/highway/work zone
 * - Returns sample images for AI testing
 * - Falls back to Unsplash if no API key
 */

const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || import.meta.env.VITE_GEMINI_API_KEY;
const GOOGLE_SEARCH_ENGINE_ID = import.meta.env.VITE_GOOGLE_SEARCH_ENGINE_ID || '017576662512468239146:omuauf_lfve';
const GOOGLE_CUSTOM_SEARCH_URL = 'https://www.googleapis.com/customsearch/v1';

/**
 * Search for construction work zone images for testing
 *
 * @param {Object} conditions - Search conditions
 * @param {string} conditions.direction - Camera direction ('eastbound' or 'westbound')
 * @param {string} conditions.weather - 'sunny', 'cloudy', 'rainy', 'snowy', 'clear'
 * @param {string} conditions.timeOfDay - 'morning', 'afternoon', 'evening', 'night'
 * @param {string} conditions.season - 'spring', 'summer', 'fall', 'winter'
 * @param {number} conditions.limit - Number of images to fetch (default: 8)
 * @returns {Promise<Array>} Array of image objects
 */
export async function searchWorkZoneImages(conditions) {
  const { direction = 'eastbound', weather = 'clear', timeOfDay = 'afternoon', season = 'summer', limit = 8 } = conditions;

  console.log('[Image Search] Starting search with conditions:', { direction, weather, timeOfDay, season, limit });

  // Build search query
  const queries = [
    'highway construction work zone',
    'road construction workers safety',
    'highway work zone traffic cones',
    'construction site highway barriers',
    'road work traffic control'
  ];

  const searchQuery = queries[Math.floor(Math.random() * queries.length)];
  console.log('[Image Search] Using search query:', searchQuery);

  try {
    // Use Google Custom Search if API key available
    if (GOOGLE_API_KEY && GOOGLE_API_KEY !== 'YOUR_GOOGLE_API_KEY') {
      console.log('[Image Search] Using Google Custom Search API with key:', GOOGLE_API_KEY?.substring(0, 10) + '...');

      const params = new URLSearchParams({
        key: GOOGLE_API_KEY,
        cx: GOOGLE_SEARCH_ENGINE_ID,
        q: searchQuery,
        searchType: 'image',
        num: limit.toString(),
        imgSize: 'large',
        safe: 'active'
      });

      const url = `${GOOGLE_CUSTOM_SEARCH_URL}?${params}`;
      console.log('[Image Search] Fetching from Google:', url.replace(GOOGLE_API_KEY, 'HIDDEN'));

      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[Image Search] Google API error:', response.status, errorText);
        throw new Error(`Google API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('[Image Search] Google API response:', data);

      if (!data.items || data.items.length === 0) {
        console.warn('[Image Search] No images from Google Search - using fallback');
        return getFallbackImages(conditions);
      }

      const images = data.items.map((item, idx) => ({
        id: `google_${idx}`,
        url: item.link,
        thumbnail: item.image?.thumbnailLink || item.link,
        description: item.title || 'Construction work zone',
        photographer: item.displayLink || 'Google Images',
        photographerUrl: item.image?.contextLink || item.link,
        source: 'Google Images',
        searchTerms: searchQuery,
        width: item.image?.width || 800,
        height: item.image?.height || 600
      }));

      console.log('[Image Search] Returning', images.length, 'Google images');
      return images;
    }

    // Fallback to Unsplash if no Google API key
    console.warn('[Image Search] No Google API key - using fallback images');
    const fallbackImages = getFallbackImages(conditions);
    console.log('[Image Search] Returning', fallbackImages.length, 'fallback images');
    return fallbackImages;

  } catch (error) {
    console.error('[Image Search] Error fetching images:', error);
    const fallbackImages = getFallbackImages(conditions);
    console.log('[Image Search] Error recovery - returning', fallbackImages.length, 'fallback images');
    return fallbackImages;
  }
}

/**
 * Fallback images for demo/testing when API is unavailable
 * These are free-to-use construction/work zone images
 */
function getFallbackImages(conditions) {
  const { limit = 8 } = conditions;

  // Using free stock images from Unsplash (no API key required for demo)
  const fallbackImages = [
    {
      id: 'demo_1',
      url: 'https://images.unsplash.com/photo-1581094271901-8022df4466f9?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1581094271901-8022df4466f9?w=400',
      description: 'Highway construction work zone with traffic cones',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'highway construction work zone',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_2',
      url: 'https://images.unsplash.com/photo-1572981420846-96f69e2a0e8d?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1572981420846-96f69e2a0e8d?w=400',
      description: 'Road construction with workers and equipment',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'road construction workers',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_3',
      url: 'https://images.unsplash.com/photo-1583947581924-860bda6a26df?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1583947581924-860bda6a26df?w=400',
      description: 'Highway work zone with barriers and signs',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'highway work zone barriers',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_4',
      url: 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400',
      description: 'Construction site with heavy machinery',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'construction heavy machinery',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_5',
      url: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=400',
      description: 'Road repair work with traffic management',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'road repair traffic management',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_6',
      url: 'https://images.unsplash.com/photo-1597423498219-04418210827d?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1597423498219-04418210827d?w=400',
      description: 'Highway construction zone with warning signs',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'highway construction warning signs',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_7',
      url: 'https://images.unsplash.com/photo-1571781331500-17827d1311f3?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1571781331500-17827d1311f3?w=400',
      description: 'Urban road construction with workers',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'urban road construction',
      width: 1200,
      height: 800
    },
    {
      id: 'demo_8',
      url: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=1200',
      thumbnail: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=400',
      description: 'Highway maintenance work zone',
      photographer: 'Unsplash',
      photographerUrl: 'https://unsplash.com',
      source: 'Unsplash (Fallback)',
      searchTerms: 'highway maintenance',
      width: 1200,
      height: 800
    }
  ];

  return fallbackImages.slice(0, limit);
}

/**
 * Download image from URL and convert to File object
 *
 * @param {string} imageUrl - URL of image to download
 * @param {string} filename - Filename for the downloaded image
 * @returns {Promise<File>} File object
 */
export async function downloadImageAsFile(imageUrl, filename = 'workzone.jpg') {
  try {
    // Fetch image with CORS mode
    const response = await fetch(imageUrl);

    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.status}`);
    }

    const blob = await response.blob();
    const file = new File([blob], filename, { type: blob.type });

    return file;
  } catch (error) {
    console.error('Error downloading image:', error);
    throw error;
  }
}

/**
 * Get image metadata for UI display
 *
 * @param {Object} image - Image object from search results
 * @returns {Object} Formatted metadata
 */
export function getImageMetadata(image) {
  return {
    id: image.id,
    description: image.description,
    photographer: image.photographer,
    source: image.source,
    searchTerms: image.searchTerms,
    dimensions: `${image.width}x${image.height}`,
    url: image.url
  };
}
