# 📊 QEW Collection Run Reports

Complete guide to accessing, viewing, and exporting collection run reports.

---

## 🎯 Quick Access

### 1. **Visual Report Dashboard** (Recommended)
```
http://localhost:8200/collection-run-report.html
```
**Features:**
- Summary statistics with visual cards
- Detailed work zone cards with risk badges
- Export to JSON, CSV, or clipboard
- Auto-refreshes every 10 seconds
- Shows all historical work zones

### 2. **Latest Report (Console Style)**
```
http://localhost:8200/view-latest-report.html
```
**Features:**
- Terminal-style green-on-black display
- Summary of most recent collection run
- Quick copy-to-clipboard
- Raw JSON data viewer

---

## 📋 Current Collection Run Status

### Summary (Latest Run)

Open your browser console (F12) and run:

```javascript
// Get latest report
const report = JSON.parse(localStorage.getItem('qew_latest_collection_run'));
console.table(report.summary);
```

### View All Detected Work Zones

```javascript
// Get all work zones
const workZones = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
console.log(`🚧 Total Work Zones: ${workZones.length}`);
console.table(workZones);
```

### Quick Statistics

```javascript
const workZones = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
const highRisk = workZones.filter(wz => wz.riskScore >= 7).length;
const mediumRisk = workZones.filter(wz => wz.riskScore >= 4 && wz.riskScore < 7).length;
const lowRisk = workZones.filter(wz => wz.riskScore < 4).length;

console.log(`
📊 WORK ZONE STATISTICS
=======================
Total:       ${workZones.length}
High Risk:   ${highRisk}
Medium Risk: ${mediumRisk}
Low Risk:    ${lowRisk}
`);
```

---

## 💾 Export Options

### 1. **Export as JSON**

Visit: `http://localhost:8200/collection-run-report.html`

Click: **"📥 Download JSON Report"**

**File Format:**
```json
{
  "generatedAt": "2025-11-20T...",
  "summary": {
    "totalWorkZones": 6,
    "highRisk": 2,
    "mediumRisk": 3,
    "lowRisk": 1,
    "averageRiskScore": "5.83",
    "totalWorkers": 12,
    "totalVehicles": 8
  },
  "workZones": [...]
}
```

### 2. **Export as CSV**

Visit: `http://localhost:8200/collection-run-report.html`

Click: **"📊 Download CSV Report"**

**Column Headers:**
```
Work Zone ID, Camera ID, View ID, Location, Risk Score, Risk Level, Workers, Vehicles, Detected At, Hazards
```

### 3. **Copy to Clipboard**

Visit: `http://localhost:8200/collection-run-report.html`

Click: **"📋 Copy to Clipboard"**

**Format:** Plain text with full work zone details

---

## 📈 Report Contents

### Summary Statistics
- **Total Images:** Number of images in manifest
- **Images Analyzed:** Successfully analyzed by Gemini AI
- **Images Skipped:** Already analyzed (cached)
- **Errors:** Failed analysis attempts
- **Work Zones Detected:** Total work zones found
- **Success Rate:** (Analyzed / Total) × 100%
- **Detection Rate:** (Work Zones / Analyzed) × 100%

### Risk Statistics
- **High Risk (7-10):** Critical work zones requiring immediate attention
- **Medium Risk (4-6):** Moderate concern, monitor closely
- **Low Risk (0-3):** Minimal safety concerns
- **Average Risk Score:** Mean risk across all work zones
- **Total Workers:** Sum of detected workers across all zones
- **Total Vehicles:** Sum of detected vehicles across all zones

### Per-Work Zone Details
- **Camera ID:** COMPASS camera identifier
- **View ID:** Unique view identifier
- **Location:** Highway location (e.g., "QEW EB at Guelph Line")
- **Risk Score:** 0-10 scale (higher = more dangerous)
- **Workers:** Number of workers detected in image
- **Vehicles:** Number of vehicles detected in image
- **Detected At:** Timestamp of detection
- **Hazards:** List of identified safety hazards (if any)

### Camera Breakdown
- Per-camera analysis statistics
- Number of views analyzed per camera
- Work zones detected per camera
- Errors per camera

---

## 🔄 Automatic Reporting

Collection runs **automatically generate reports** when:

1. Auto-analysis completes in `src/services/scrapedImageAnalysis.js`
2. Report is saved to localStorage (key: `qew_latest_collection_run`)
3. Console logs display link to view report
4. Report is added to history (last 10 runs kept)

**Console Output:**
```
======================================================================
📊 COLLECTION RUN REPORT GENERATED
======================================================================
📄 View detailed report at: http://localhost:8200/collection-run-report.html
📥 Export options: JSON, CSV, or copy to clipboard
======================================================================
```

---

## 📁 LocalStorage Keys

### Primary Keys

| Key | Description |
|-----|-------------|
| `qew_workzone_camera_history` | All detected work zones (persistent) |
| `qew_latest_collection_run` | Most recent report (quick access) |
| `qew_collection_run_reports` | Last 10 reports (history) |

### Access in Browser Console

```javascript
// Get all localStorage keys
Object.keys(localStorage).filter(key => key.startsWith('qew_'));

// Get specific report
const latest = JSON.parse(localStorage.getItem('qew_latest_collection_run'));
const history = JSON.parse(localStorage.getItem('qew_collection_run_reports'));

// Count work zones
const workZones = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
console.log(`Total work zones: ${workZones.length}`);
```

---

## 🚧 Current Collection Run Results

### Latest Run Status

**Run Date:** [Check browser console for timestamp]

**Summary:**
```
Total Images:        50
Images Analyzed:     6  (stopped due to quota limit)
Images Skipped:      0
Errors:              44 (quota exceeded)
Work Zones Detected: 6
Success Rate:        12%
Detection Rate:      100%
```

**Quota Status:**
- ✅ Analyzed 6 images successfully
- ❌ Hit daily quota limit (1,500 requests/day)
- ⏰ Remaining 44 images pending quota reset (24 hours)

**Next Steps:**
1. Wait 24 hours for quota reset (free)
2. OR upgrade to full paid tier (~$0.50 for remaining images)
3. OR try different Gemini model (may have separate quota)

---

## 🎨 Visual Report Features

### Collection Run Report Dashboard
**URL:** `http://localhost:8200/collection-run-report.html`

**Features:**
- 📊 **Summary Cards:** Visual metrics with color gradients
- 🚧 **Work Zone Cards:** Detailed breakdown with risk badges
  - 🔴 Red border = High Risk (7-10)
  - 🟡 Yellow border = Medium Risk (4-6)
  - 🟢 Green border = Low Risk (0-3)
- 📹 **Camera Breakdown:** Per-camera statistics
- 💾 **Export Options:** JSON, CSV, Clipboard
- 📄 **Raw JSON:** View underlying data structure
- 🔄 **Auto-Refresh:** Updates every 10 seconds

### Latest Report Viewer
**URL:** `http://localhost:8200/view-latest-report.html`

**Features:**
- 🖥️ **Console Style:** Green-on-black terminal aesthetic
- ⚡ **Fast Access:** Displays most recent run only
- 📋 **Quick Copy:** One-click clipboard export
- 🔄 **Manual Refresh:** Reload button for updates

---

## 📝 Example Report

### Console Output (Text Format)

```
========================================
QEW COLLECTION RUN REPORT
========================================

REPORT ID: run-1732135678901
RUN DATE: 11/20/2025, 3:47:58 PM
GENERATED: 11/20/2025, 3:47:58 PM

----------------------------------------
SUMMARY STATISTICS
----------------------------------------
Total Images:        50
Images Analyzed:     6
Images Skipped:      0
Errors:              44
Work Zones Detected: 6
Success Rate:        12%
Detection Rate:      100%

----------------------------------------
RISK STATISTICS
----------------------------------------
High Risk (7-10):    2
Medium Risk (4-6):   3
Low Risk (0-3):      1
Average Risk Score:  5.83/10
Total Workers:       12
Total Vehicles:      8

----------------------------------------
DETECTED WORK ZONES (6)
----------------------------------------

Work Zone #1
  Camera ID:   210
  View ID:     570
  Location:    QEW WB at Guelph Line
  Risk Score:  8/10 (HIGH)
  Workers:     3
  Vehicles:    2
  Detected:    11/20/2025, 3:45:23 PM

Work Zone #2
  Camera ID:   212
  View ID:     571
  Location:    QEW EB at Walkers Line
  Risk Score:  7/10 (HIGH)
  Workers:     2
  Vehicles:    1
  Detected:    11/20/2025, 3:46:01 PM

[... remaining work zones ...]

========================================
```

---

## 🛠️ Troubleshooting

### No Report Displayed

**Issue:** Report viewer shows "No data"

**Solutions:**
1. Run a collection: Reload dashboard to trigger auto-analysis
2. Check localStorage:
   ```javascript
   localStorage.getItem('qew_workzone_camera_history');
   ```
3. Verify images exist:
   ```
   http://localhost:8200/camera_images/manifest.json
   ```

### Export Fails

**Issue:** "Failed to copy" or download error

**Solutions:**
1. Allow clipboard permissions in browser
2. Check browser console for errors
3. Try different export format (JSON vs CSV vs Clipboard)

### Report Not Updating

**Issue:** Report shows old data

**Solutions:**
1. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+F5)
2. Clear browser cache
3. Manually reload page
4. Check auto-refresh is enabled (collection-run-report.html)

### Missing Work Zones

**Issue:** Fewer work zones than expected

**Solutions:**
1. Check quota status (may have hit limit)
2. Review console logs for errors
3. Verify images analyzed:
   ```javascript
   const report = JSON.parse(localStorage.getItem('qew_latest_collection_run'));
   console.log(report.summary);
   ```

---

## 📚 Related Documentation

- **`GCP_AI_INTEGRATION_COMPLETE.md`** - Gemini AI setup and configuration
- **`DATABASE_FLOW.md`** - Data flow from scraper to dashboard
- **`GEMINI_API_UPGRADE_GUIDE.md`** - API quota and billing information
- **`docs/MVP_WORKFLOW.md`** - Complete 6-month roadmap

---

## 🤖 Built with Claude Code

**Last Updated:** 2025-11-20
**Feature:** Comprehensive collection run reporting system
**Status:** ✅ Production Ready

---

## 🎯 Quick Commands Reference

### Browser Console Commands

```javascript
// View latest report summary
const report = JSON.parse(localStorage.getItem('qew_latest_collection_run'));
console.table(report.summary);

// View all work zones
const workZones = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
console.table(workZones);

// Count by risk level
const high = workZones.filter(wz => wz.riskScore >= 7).length;
const medium = workZones.filter(wz => wz.riskScore >= 4 && wz.riskScore < 7).length;
const low = workZones.filter(wz => wz.riskScore < 4).length;
console.log(`High: ${high}, Medium: ${medium}, Low: ${low}`);

// View report history
const history = JSON.parse(localStorage.getItem('qew_collection_run_reports') || '[]');
console.log(`Total reports: ${history.length}`);
console.table(history.map(r => r.summary));

// Clear all reports (WARNING: Cannot undo)
localStorage.removeItem('qew_workzone_camera_history');
localStorage.removeItem('qew_latest_collection_run');
localStorage.removeItem('qew_collection_run_reports');
```

### URL Quick Links

```
Visual Dashboard:    http://localhost:8200/collection-run-report.html
Latest Report:       http://localhost:8200/view-latest-report.html
Image Manifest:      http://localhost:8200/camera_images/manifest.json
Quota Test:          http://localhost:8200/test-gemini-quota.html
```

---

**Need Help?** Check browser console for detailed logs and error messages.
