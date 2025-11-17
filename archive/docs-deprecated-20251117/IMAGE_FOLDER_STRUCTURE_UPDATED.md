# Image Folder Structure Updated

**Date:** 2025-11-16  
**Status:** ✅ COMPLETE - Ready to Use

---

## 🎯 What Changed

### **OLD Structure:**
```
ai_camera_direction/
├── satellite_images/
│   ├── satellite_cam1_view1.jpg
│   ├── satellite_cam1_view2.jpg
│   ├── satellite_cam2_view3.jpg
│   └── ...
└── camera_images/
    ├── camera_cam1_view1.jpg
    ├── camera_cam1_view2.jpg
    ├── camera_cam2_view3.jpg
    └── ...
```

**Problem:** All satellite images in one folder, all camera images in another folder.

---

### **NEW Structure:**
```
ai_camera_direction/
└── data/
    └── images/
        ├── cam1_v1/
        │   ├── satellite.jpg
        │   └── camera.jpg
        ├── cam1_v2/
        │   ├── satellite.jpg
        │   └── camera.jpg
        ├── cam2_v3/
        │   ├── satellite.jpg
        │   └── camera.jpg
        ├── cam4_v10/
        │   ├── satellite.jpg
        │   └── camera.jpg
        └── ...
```

**Benefits:**
- ✅ Each camera has its own folder
- ✅ Satellite and camera images together
- ✅ Shorter folder names (`cam1_v1` instead of `camera_cam1_view1.jpg`)
- ✅ Easier to browse and manage
- ✅ Better organization for export

---

## 📝 Updated Files

### **1. `backend/satellite_fetcher.py`**
**Changes:**
- Changed `output_dir` to `base_output_dir = 'data/images'`
- Creates individual folder per camera: `cam{camera_id}_v{view_id}`
- Saves as `satellite.jpg` instead of `satellite_cam{id}_view{id}.jpg`

### **2. `backend/camera_fetcher.py`**
**Changes:**
- Changed `output_dir` to `base_output_dir = 'data/images'`
- Creates individual folder per camera: `cam{camera_id}_v{view_id}`
- Saves as `camera.jpg` instead of `camera_cam{id}_view{id}.jpg`

### **3. New: `cleanup_data.py`**
**Purpose:** Clean up old data and images before reprocessing

---

## 🗑️ How to Clean Up Old Data

### **Run the cleanup script:**

```bash
cd ai_camera_direction
python cleanup_data.py
```

**What it does:**
1. Deletes all records from `ai_direction_assessments` table
2. Deletes old `satellite_images/` folder
3. Deletes old `camera_images/` folder
4. Deletes old `data/images/` folder
5. Creates fresh `data/images/` directory

**Output:**
```
🗑️  Cleaning up old data and images...
============================================================

📁 Found database: data/camera_directions.db
   Records in database: 4
   ✅ Deleted 4 records from database

📁 Found old folder: satellite_images
   Files in folder: 4
   ✅ Deleted folder and all contents

📁 Found old folder: camera_images
   Files in folder: 4
   ✅ Deleted folder and all contents

✅ Created fresh images directory: data/images

============================================================
✅ Cleanup complete! Ready for fresh processing.

New folder structure will be:
  data/images/
    ├── cam1_v1/
    │   ├── satellite.jpg
    │   └── camera.jpg
    ├── cam1_v2/
    │   ├── satellite.jpg
    │   └── camera.jpg
    └── ...
============================================================
```

---

## 🚀 After Cleanup

### **1. Run the GUI:**
```bash
python main.py
```

### **2. Click "Start Processing"**

### **3. Watch the new folder structure:**
```
data/images/
├── cam4_v10/
│   ├── satellite.jpg  ← Satellite image for camera 4, view 10
│   └── camera.jpg     ← Camera image for camera 4, view 10
├── cam4_v11/
│   ├── satellite.jpg
│   └── camera.jpg
├── cam4_v12/
│   ├── satellite.jpg
│   └── camera.jpg
└── ...
```

---

## 📊 Folder Naming Convention

### **Format:**
```
cam{camera_id}_v{view_id}
```

### **Examples:**
- `cam1_v1` = Camera 1, View 1
- `cam4_v10` = Camera 4, View 10
- `cam5_v13` = Camera 5, View 13
- `cam46_v150` = Camera 46, View 150

### **Files in each folder:**
- `satellite.jpg` - Satellite/aerial image
- `camera.jpg` - Traffic camera image

---

## 💾 Database Updates

### **Image paths in database:**

**OLD:**
```
satellite_image_path: "satellite_images/satellite_cam1_view1.jpg"
camera_image_path: "camera_images/camera_cam1_view1.jpg"
```

**NEW:**
```
satellite_image_path: "data/images/cam1_v1/satellite.jpg"
camera_image_path: "data/images/cam1_v1/camera.jpg"
```

---

## ✅ Benefits of New Structure

1. **Better Organization**
   - Related images grouped together
   - Easy to find both images for a camera

2. **Shorter Names**
   - `cam1_v1` vs `satellite_cam1_view1.jpg`
   - Cleaner, more readable

3. **Easier Export**
   - Can zip individual camera folders
   - Can share specific camera data easily

4. **Better for Web**
   - Can serve entire camera folder
   - Predictable URLs: `/images/cam1_v1/satellite.jpg`

5. **Scalability**
   - Can add more images per camera later
   - Can add metadata files per camera

---

## 🎯 Next Steps

1. **Run cleanup script:**
   ```bash
   python cleanup_data.py
   ```

2. **Start the GUI:**
   ```bash
   python main.py
   ```

3. **Process all cameras:**
   - Click "Start Processing"
   - Wait ~3-5 minutes (with Gemini 2.0 Flash)

4. **Check new folder structure:**
   - Browse to `data/images/`
   - See individual camera folders
   - Each folder has 2 images

---

**The image organization is now much cleaner and easier to manage!** 🎉

