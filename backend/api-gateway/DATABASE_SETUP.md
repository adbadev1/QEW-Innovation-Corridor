# Database Setup Instructions for Corey (cbarronalive123)

## 🎯 Quick Setup (Recommended)

The database file is **not** included in git (it's local-only). You need to create it on your machine.

### One-Command Setup:

```bash
cd backend/api-gateway
./setup_database.sh
```

This script will:
1. ✅ Remove any old database
2. ✅ Create fresh database schema (Alembic migrations)
3. ✅ Seed 46 QEW COMPASS cameras
4. ✅ Seed 48 camera direction records
5. ✅ Verify the database is ready

---

## 📋 Manual Setup (If Script Fails)

If the script doesn't work, follow these steps:

### Step 1: Ensure Virtual Environment

```bash
cd backend/api-gateway

# Check if venv exists
ls venv/

# If not, create it:
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Remove Old Database (if exists)

```bash
rm qew_corridor.db  # Only if it exists
```

### Step 3: Create Database Schema

```bash
./venv/bin/alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> c7495cd14e3f, Initial database schema
```

### Step 4: Seed Camera Data

```bash
./venv/bin/python3 seed_cameras.py
```

When prompted: Just press **Enter** (don't type anything)

Expected output:
```
✅ Database seeding complete!
📊 Cameras inserted: 46
```

### Step 5: Seed Camera Directions

```bash
./venv/bin/python3 seed_directions.py
```

When prompted: Just press **Enter**

Expected output:
```
✅ Direction seeding complete!
📊 Direction records inserted: 48
✅ Updated 5 cameras with primary heading data
```

### Step 6: Verify Database

```bash
./venv/bin/python3 -c "
import sqlite3
conn = sqlite3.connect('qew_corridor.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM cameras')
print(f'Cameras: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM camera_directions')
print(f'Direction records: {cursor.fetchone()[0]}')

conn.close()
"
```

Expected output:
```
Cameras: 46
Direction records: 48
```

---

## ✅ Verification

After setup, you should see:

```bash
ls -lh qew_corridor.db
# Should show: ~100 KB file
```

---

## 🚀 Start the Backend

```bash
cd backend/api-gateway
source venv/bin/activate
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Test the API

```bash
# Get all cameras
curl http://localhost:8000/api/cameras | jq

# Get cameras with direction data (for spotlights)
curl http://localhost:8000/api/directions/cameras | jq

# Get camera statistics
curl http://localhost:8000/api/cameras/stats/summary | jq
```

---

## 📊 Expected Database Contents

```
Tables:
├── cameras (46 records)
├── camera_directions (48 records)
├── work_zones (0 records - will populate during operation)
├── collection_runs (0 records - will populate during operation)
└── alembic_version (migration tracking)
```

---

## 🐛 Troubleshooting

### Error: "No module named 'sqlalchemy'"

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "no such table: cameras"

**Solution:** Run Alembic migrations first:
```bash
./venv/bin/alembic upgrade head
```

### Error: "NOT NULL constraint failed"

**Solution:** Delete the database and start fresh:
```bash
rm qew_corridor.db
./setup_database.sh
```

### Database is empty or has wrong data

**Solution:** Re-run the seeding scripts:
```bash
# Remove database
rm qew_corridor.db

# Recreate schema
./venv/bin/alembic upgrade head

# Seed data
./venv/bin/python3 seed_cameras.py  # Press Enter when prompted
./venv/bin/python3 seed_directions.py  # Press Enter when prompted
```

---

## 📝 Why is the Database Not in Git?

**Answer:** Database files (`.db`) are in `.gitignore` because:
1. They're binary files that change frequently
2. Each developer should have their own local database
3. Database size can grow large
4. Reduces merge conflicts

**Instead, we store:**
- ✅ Migration scripts (`alembic/versions/*.py`)
- ✅ Seeding scripts (`seed_*.py`)
- ✅ Source data (`camera_scraper/*.json`, `*.csv`)

This way, every developer can recreate the exact same database from scratch!

---

## 🔗 Related Documentation

- **Full Backend Setup:** `docs/onboarding/FULLSTACK_SETUP.md`
- **Quick Start:** `docs/onboarding/QUICK_START.md`
- **Refactoring Status:** `docs/development/REFACTORING_STATUS.md`

---

**Questions?** Ping in Slack or open an issue on GitHub.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
