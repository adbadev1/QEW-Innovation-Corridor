# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1️⃣ Get Claude API Key

Go to: https://console.anthropic.com/
- Sign up or log in
- Create API key
- Copy the key (starts with `sk-ant-...`)

### 2️⃣ Configure .env File

Edit the `.env` file in this folder and paste your API key:

```bash
CLAUDE_API_KEY=sk-ant-your-actual-key-here
```

Save the file.

### 3️⃣ Run the Application

```bash
..\camera_scraper\venv\Scripts\python.exe main.py
```

That's it! The GUI will open with your API key already loaded.

---

## 📝 What Happens Next

1. **GUI Opens** - API key auto-loaded from .env (green background)
2. **Click "Start Processing"** - Begins analyzing all 50 cameras
3. **Watch Progress** - See satellite and camera images side-by-side
4. **Read AI Analysis** - Console shows direction, landmarks, reasoning
5. **Results Saved** - All assessments stored in `data/camera_directions.db`

---

## ⏱️ Expected Time

- **Per camera**: ~10-15 seconds
- **Total (50 cameras)**: ~8-12 minutes
- **Cost**: ~$0.50-1.00 (Claude API)

---

## 🎯 What You'll Get

Each camera will have:
- ✅ **Direction**: N, NE, E, SE, S, SW, W, NW
- ✅ **Heading**: Precise degrees (0-360°)
- ✅ **Confidence**: AI confidence score
- ✅ **Landmarks**: Identified features
- ✅ **Reasoning**: AI's explanation
- ✅ **Images**: Satellite + camera saved

---

## ❓ Troubleshooting

**"No API key found"**
- Make sure you edited `.env` file
- Check the key starts with `sk-ant-`
- No quotes needed around the key

**"Database not found"**
- Ensure `camera_scraper/camera_data.db` exists
- Run camera scraper first if needed

**"Satellite images fail"**
- Internet connection required
- Consider adding Google Maps API key for better results

---

## 📊 After Processing

View results:
```bash
# Open database
..\camera_scraper\venv\Scripts\python.exe -c "from backend.database import DirectionDatabase; db = DirectionDatabase(); print(f'Processed: {len(db.get_all_assessments())} cameras'); db.close()"
```

Or query specific camera:
```python
from backend.database import DirectionDatabase

db = DirectionDatabase()
result = db.get_assessment(camera_id=4, view_id=10)
print(f"Direction: {result['direction']}")
print(f"Heading: {result['heading_degrees']}°")
print(f"Reasoning: {result['reasoning']}")
db.close()
```

---

## 🎉 That's It!

You're ready to automatically determine camera directions using AI!

