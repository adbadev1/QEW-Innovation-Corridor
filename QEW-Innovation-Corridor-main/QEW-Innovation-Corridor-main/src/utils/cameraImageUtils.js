// Utility functions for camera image handling
// Maps camera IDs to their latest scraped images

// Base path for camera images (relative to public folder)
const CAMERA_IMAGES_BASE = '/camera_images/qew_collection_20251115_150317';

// Camera image mapping - maps camera ID to array of image filenames
export const getCameraImages = (cameraId) => {
  // Extract numeric ID from camera ID (e.g., 'CAM_210' -> '210')
  const numericId = cameraId.replace('CAM_', '');
  
  // Map of camera IDs to their image files
  const cameraImageMap = {
    '4': [
      'cam4_view10_QEW at Burlington Skyway_Fort Erie Bound_round1_20251115_150317.jpg',
      'cam4_view11_QEW at Burlington Skyway_Looking Down_round1_20251115_150321.jpg',
      'cam4_view12_QEW at Burlington Skyway_Toronto Bound_round1_20251115_150323.jpg'
    ],
    '5': [
      'cam5_view13_QEW near Mississauga Road (2)_Toronto Bound_round1_20251115_150326.jpg',
      'cam5_view14_QEW near Mississauga Road (2)_Looking Down_round1_20251115_150329.jpg',
      'cam5_view15_QEW near Mississauga Road (2)_Fort Erie Bound_round1_20251115_150332.jpg'
    ],
    '210': ['cam210_view570_QEW West of Fifty Road__round1_20251115_150336.jpg'],
    '211': ['cam211_view571_QEW near Millen Road__round1_20251115_150339.jpg'],
    '212': ['cam212_view572_QEW near Grays Road__round1_20251115_150343.jpg'],
    '213': ['cam213_view573_QEW near Centennial Parkway__round1_20251115_150347.jpg'],
    '214': ['cam214_view574_QEW near Red Hill Valley Parkway__round1_20251115_150350.jpg'],
    '215': ['cam215_view575_QEW near Nikola Tesla Boulevard__round1_20251115_150354.jpg'],
    '216': ['cam216_view576_QEW near Woodward Avenue__round1_20251115_150357.jpg'],
    '217': ['cam217_view577_QEW West of Eastport Drive__round1_20251115_150400.jpg'],
    '218': ['cam218_view578_QEW East of Eastport Drive - Toronto Bound__round1_20251115_150405.jpg'],
    '219': ['cam219_view579_QEW Burlington Skyway - Hamilton Side__round1_20251115_150407.jpg'],
    '220': ['cam220_view580_QEW Burlington Skyway - Toronto Side__round1_20251115_150410.jpg'],
    '221': ['cam221_view581_QEW Ramp to Northshore Boulevard__round1_20251115_150414.jpg'],
    '222': ['cam222_view582_QEW East of Northshore Boulevard__round1_20251115_150417.jpg'],
    '223': ['cam223_view583_QEW near Trafalgar Road__round1_20251115_150420.jpg'],
    '224': ['cam224_view584_QEW near Fairview Street__round1_20251115_150424.jpg'],
    '225': ['cam225_view585_QEW near Highway 403_407 IC__round1_20251115_150428.jpg'],
    '226': ['cam226_view586_QEW West of Brant Street__round1_20251115_150430.jpg'],
    '227': ['cam227_view587_QEW East of Brant Street__round1_20251115_150434.jpg'],
    '228': ['cam228_view588_QEW near Guelph Line__round1_20251115_150438.jpg'],
    '229': ['cam229_view589_QEW East of Guelph Line__round1_20251115_150441.jpg'],
    '230': ['cam230_view590_QEW near Walkers Line__round1_20251115_150444.jpg'],
    '231': ['cam231_view591_QEW East of Walkers Line__round1_20251115_150446.jpg'],
    '232': ['cam232_view592_QEW near Appleby Line__round1_20251115_150449.jpg'],
    '233': ['cam233_view593_QEW East of Appleby Line__round1_20251115_150452.jpg'],
    '234': ['cam234_view594_QEW near Burloak Drive__round1_20251115_150454.jpg'],
    '235': ['cam235_view595_QEW East of Burloak Drive__round1_20251115_150458.jpg'],
    '236': ['cam236_view596_QEW near Bronte Road__round1_20251115_150501.jpg'],
    '237': ['cam237_view597_QEW East of Bronte Road__round1_20251115_150505.jpg'],
    '238': ['cam238_view598_QEW near Third Line__round1_20251115_150507.jpg'],
    '239': ['cam239_view599_QEW East of Third Line__round1_20251115_150511.jpg'],
    '240': ['cam240_view600_QEW near Fourth Line__round1_20251115_150513.jpg'],
    '241': ['cam241_view601_QEW near Dorval Drive__round1_20251115_150516.jpg']
  };
  
  const images = cameraImageMap[numericId];
  if (!images) return [];
  
  // Return full paths to images
  return images.map(img => `${CAMERA_IMAGES_BASE}/${img}`);
};

// Get the primary (first) image for a camera
export const getPrimaryCameraImage = (cameraId) => {
  const images = getCameraImages(cameraId);
  return images.length > 0 ? images[0] : null;
};

// Get timestamp from collection folder name
export const getCollectionTimestamp = () => {
  return '2025-11-15 15:03:17';
};

