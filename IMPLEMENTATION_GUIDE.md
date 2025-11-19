# QEW Camera Collection & AI Analysis - Implementation Guide

## 🎯 COMPLETE REDESIGN: GCP Storage + Automatic Gemini Analysis

### Overview

This system now:
1. **Downloads** real camera images from 511ON COMPASS system
2. **Uploads** images to Google Cloud Storage for persistence
3. **Automatically analyzes** each image with Gemini AI
4. **Tracks work zones** in browser localStorage for ML Validation Panel
5. **Broadcasts** V2X alerts for detected work zones

---

## 📋 Architecture

```
Camera Collection Cycle
  ↓
511ON COMPASS Camera Feed
  ↓
Download Image (src/services/gcpStorage.js)
  ↓
Upload to GCP Cloud Storage
  ↓
Automatic Gemini AI Analysis (src/services/autoWorkZoneAnalysis.js)
  ↓
Work Zone Detected?
  ├─ YES → Add to Work Zone History
  │         ├─ Save to localStorage
  │         ├─ Appears in ML Validation Panel
  │         └─ V2X Broadcast (if high risk)
  └─ NO  → Log "No work zone detected"
```

---

## 🔧 Implementation Status

### ✅ COMPLETED

1. **GCP Cloud Storage Service** (`src/services/gcpStorage.js`)
   - Download camera images from 511ON
   - Upload to GCS bucket: `gs://qew-camera-images/`
   - List, delete, and manage storage
   - Get storage statistics

2. **Automatic Work Zone Analysis** (`src/services/autoWorkZoneAnalysis.js`)
   - Analyze images immediately after upload
   - Detect work zones with Gemini AI
   - Add to work zone history
   - Batch analysis support
   - Progress tracking

3. **Work Zone History Tracker** (`src/utils/workZoneHistory.js`)
   - Persist detected work zones to localStorage
   - Track camera detection history
   - Get statistics

4. **Environment Configuration** (`.env.example`)
   - Added GCP project ID
   - Added GCS bucket name
   - GCP API key configuration

### 🔄 PENDING INTEGRATION

**CollectionContext.jsx** needs updates to:

```javascript
// REPLACE THIS (line 489-495):
// Simulate image download with timeout (replace with real API call)
await Promise.race([
  simulateImageDownload(camera.Id, view.Id, round + 1),
  new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Image download timeout')), 30000)
  )
]);

// WITH THIS:
import { downloadCameraImage, uploadCameraImage } from '../services/gcpStorage';
import { analyzeUploadedImage, getAnalysisSummary } from '../services/autoWorkZoneAnalysis';

// Inside the image collection loop:
try {
  // 1. Download live camera image
  logStatus(`→ → → Downloading image from ${viewName}...`, 'info', true);
  const imageBlob = await downloadCameraImage(view.Url);

  // 2. Upload to GCP Cloud Storage
  logStatus(`→ → → Uploading to GCP Storage...`, 'info', true);
  const uploadResult = await uploadCameraImage({
    cameraId: camera.Id,
    viewId: view.Id,
    round: round + 1,
    collectionId,
    imageBlob,
    metadata: {
      cameraLocation: camera.Location,
      latitude: camera.Latitude,
      longitude: camera.Longitude
    }
  });

  // 3. Automatically analyze with Gemini AI
  logStatus(`→ → → Analyzing with Gemini AI...`, 'info', true);
  const analysisResult = await analyzeUploadedImage({
    imageBlob,
    cameraId: camera.Id,
    viewId: view.Id,
    cameraLocation: camera.Location,
    latitude: camera.Latitude,
    longitude: camera.Longitude,
    collectionId,
    gcpImageUrl: uploadResult.publicUrl,
    registerBroadcast: null // TODO: Pass from context
  });

  // 4. Log analysis result
  const summary = getAnalysisSummary(analysisResult);
  logStatus(`→ → → ${summary}`, analysisResult.hasWorkZone ? 'success' : 'info', true);

  // 5. Track work zones detected
  if (analysisResult.hasWorkZone) {
    workZonesDetected++;
  }

  imagesCollected++;
  cameraImagesCount++;
  setTotalImages(imagesCollected);

} catch (imageError) {
  imagesFailed++;
  logStatus(`✗ Failed: ${imageError.message}`, 'error', true);
  logError('Image collection failed', {
    camera: camera.Id,
    view: view.Id,
    round: round + 1,
    error: imageError.message
  });
}
```

---

## 🗄️ GCP Cloud Storage Setup

### Required Steps:

1. **Create GCS Bucket:**
   ```bash
   gsutil mb -p YOUR_PROJECT_ID -c STANDARD -l us-central1 gs://qew-camera-images/
   ```

2. **Configure CORS:**
   ```bash
   cat > cors.json <<EOF
   [
     {
       "origin": ["http://localhost:8200", "https://your-production-domain.com"],
       "method": ["GET", "POST", "PUT"],
       "responseHeader": ["Content-Type"],
       "maxAgeSeconds": 3600
     }
   ]
   EOF

   gsutil cors set cors.json gs://qew-camera-images/
   ```

3. **Set Bucket Permissions:**
   ```bash
   # Make bucket public for reads (or use signed URLs)
   gsutil iam ch allUsers:objectViewer gs://qew-camera-images/
   ```

4. **Environment Variables:**
   Create `.env` file:
   ```bash
   VITE_GEMINI_API_KEY=your_actual_gemini_api_key
   VITE_GCP_PROJECT_ID=your-gcp-project-id
   VITE_GCP_STORAGE_BUCKET=qew-camera-images
   VITE_GEMINI_MODEL=gemini-2.0-flash-exp
   ```

---

## 🧪 Testing Workflow

### 1. Manual Test Collection

```javascript
// In Camera Collection Panel:
1. Set interval: 0 hours, 1 minute
2. Images per camera: 1
3. Click "START AUTOMATIC COLLECTION"
4. Watch logs for:
   - "Downloading image from..."
   - "Uploading to GCP Storage..."
   - "Analyzing with Gemini AI..."
   - "🚧 Work Zone: Risk X/10..." (if detected)
```

### 2. Verify GCP Storage

```bash
# List uploaded images
gsutil ls gs://qew-camera-images/collections/

# Check latest collection
gsutil ls gs://qew-camera-images/collections/qew_collection_*/
```

### 3. Verify ML Validation Panel

```
1. Collection completes
2. Work zones detected → added to history
3. Open "ML Vision Model Validation" panel
4. Should show: "Cameras with detected work zones: X / 46"
5. Dropdown populated with cameras that detected work zones
6. Can re-analyze same cameras
```

---

## 📊 Expected Behavior

### Collection Log Output:

```
▶ COLLECTION #1 STARTED
Collection ID: qew_collection_20251118_231530
Cameras: 46 | Images per camera: 1

[1/46] Scraping QEW East of Mississauga Road (ID: 253)
→ GPS: [43.5581, -79.6080]
→ Processing 1 camera views...
→ → View 1/1: Main View
→ → → Downloading image from Main View...
→ → → Uploading to GCP Storage...
→ → → Analyzing with Gemini AI...
→ → → 🚧 Work Zone: Risk 7/10 | Workers: 3 | Vehicles: 2 | Barriers: YES
→ → → ✓ Added to work zone history: Camera 253
✓ Camera 253 complete (1 images)

...

✓ COLLECTION #1 COMPLETE
Images collected: 46 | Failed: 2 | Duration: 180s
Work zones detected: 5
Total this session: 46
Collection saved: qew_collection_20251118_231530
```

---

## 🔐 Security Considerations

1. **API Keys**: Never commit real API keys to git
2. **Bucket Access**: Use signed URLs for production
3. **CORS**: Restrict to production domains only
4. **Rate Limiting**: Gemini API has quotas
5. **Storage Costs**: Monitor GCS usage

---

## 📈 Future Enhancements

1. **Batch Upload**: Upload multiple images concurrently
2. **Progress UI**: Show real-time analysis progress in panel
3. **Error Recovery**: Retry failed uploads/analyses
4. **Compression**: Compress images before upload
5. **Thumbnails**: Generate thumbnails for faster loading
6. **Export**: Export work zone detection reports
7. **Alerts**: Email/SMS notifications for critical detections

---

## 🐛 Troubleshooting

### Images Not Uploading

```
✗ Check GCP_API_KEY is valid
✗ Check bucket exists: gsutil ls gs://qew-camera-images/
✗ Check CORS configuration
✗ Check browser console for errors
```

### Gemini Analysis Failing

```
✗ Check VITE_GEMINI_API_KEY is set
✗ Check API quota: https://console.cloud.google.com/apis/dashboard
✗ Check network connectivity
✗ Review browser console for API errors
```

### Work Zones Not Appearing in ML Panel

```
✗ Check localStorage: localStorage.getItem('qew_workzone_camera_history')
✗ Verify Gemini returned hasWorkZone: true
✗ Check browser console for workZoneHistory errors
```

---

## 📝 Implementation Checklist

- [x] Create GCP Storage service
- [x] Create auto-analysis service
- [x] Update .env.example
- [ ] Update CollectionContext.jsx (integrate GCP + analysis)
- [ ] Add work zone counter to collection stats
- [ ] Add progress tracking UI
- [ ] Test end-to-end with real cameras
- [ ] Document GCP setup instructions
- [ ] Add error handling for offline cameras
- [ ] Implement retry logic for failed uploads

---

## 🎓 Key Files Reference

| File | Purpose |
|------|---------|
| `src/services/gcpStorage.js` | GCP Cloud Storage API integration |
| `src/services/autoWorkZoneAnalysis.js` | Automatic Gemini AI analysis |
| `src/services/geminiVision.js` | Gemini Vision API wrapper |
| `src/utils/workZoneHistory.js` | Work zone detection history |
| `src/contexts/CollectionContext.jsx` | Camera collection orchestration |
| `src/components/MLValidationPanel.jsx` | ML validation UI |
| `.env.example` | Environment configuration template |

---

**Status**: Implementation 80% complete. Integration into CollectionContext pending.

**Next Step**: Update CollectionContext.jsx to replace `simulateImageDownload` with the real GCP + AI workflow.
