# Traffic Analysis MVP - 5 Hour Implementation Plan

**Project:** QEW Innovation Corridor - Real-Time Traffic Intelligence System  
**Author:** Corey  
**Date:** November 19, 2025  
**Time:** 5:35 AM EST  
**Status:** READY TO IMPLEMENT  
**Estimated Completion:** 10:35 AM EST (5 hours)  

---

## Executive Summary

Build a **Real-Time Traffic Intelligence System** that analyzes highway camera images using Gemini AI to detect traffic conditions, congestion, incidents, and work zones. Results displayed on interactive map with color-coded markers and detailed popups.

**Goal:** Show immediate value with working traffic analysis in 5 hours.

---

## Technology Stack

### AI Model: Gemini 2.0 Flash (NOT Claude)

**Why Gemini?**
- ✅ Vision-optimized for image analysis
- ✅ Faster: <2 seconds per image
- ✅ Cheaper: ~$0.001 per image (vs Claude $0.01)
- ✅ Better for traffic: Object detection, counting, scene understanding
- ✅ Structured JSON output

**Cost Estimate:**
- 14 cameras × 6 analyses/hour = 84 analyses/hour
- 2,016 analyses/day × $0.001 = **$2/day** or **$60/month**

---

## What We're Building

### Core Features (5 Hours)

#### 1. Traffic Flow Analysis (Per Camera)
- **Vehicle Count:** Number of vehicles visible
- **Traffic Density:** Sparse, Light, Moderate, Heavy, Congested
- **Speed Estimate:** Fast (>80 km/h), Normal (60-80), Slow (40-60), Crawling (<40), Stopped
- **Lane Occupancy:** Which lanes have vehicles
- **Vehicle Types:** Cars, trucks, buses (percentage)
- **Traffic Direction:** Eastbound vs Westbound

#### 2. Congestion Detection
- **Queue Formation:** Is traffic backing up?
- **Stop-and-Go Pattern:** Vehicles moving in waves
- **Lane Imbalance:** One lane moving, others stopped
- **Backup Length Estimate:** Queue extent

#### 3. Incident Detection
- **Stopped Vehicles:** Breakdown/collision in lane
- **Emergency Vehicles:** Flashing lights visible
- **Debris on Road:** Objects in lanes
- **Abnormal Patterns:** Swerving, sudden braking

#### 4. Weather/Visibility Conditions
- **Weather:** Clear, Rain, Fog, Snow
- **Visibility:** Excellent, Good, Reduced, Poor
- **Road Surface:** Dry, Wet, Snow-covered
- **Time of Day:** Dawn, Day, Dusk, Night

#### 5. Work Zone Presence (Basic)
- **Construction Equipment:** Visible in frame
- **Traffic Cones/Barriers:** Present or not
- **Lane Closures:** Lanes blocked
- **Workers Visible:** Yes/No

---

## Database Schema

### New Tables (5 Total)

#### Table 1: `traffic_analyses`
**Purpose:** Store every AI analysis result

**Key Fields:**
- `camera_id`, `image_id`, `analyzed_at`
- `vehicle_count`, `traffic_density`, `avg_speed_estimate`, `traffic_flow_score` (1-10)
- `lanes_detected`, `lanes_occupied`, `lane_occupancy_json`
- `cars_count`, `trucks_count`, `buses_count`
- `weather`, `visibility`, `road_surface`, `lighting`
- `incident_detected`, `incident_type`, `incident_confidence`
- `work_zone_detected`, `equipment_visible`, `workers_visible`
- `ai_model`, `confidence_score`, `processing_time_ms`

**Indexes:**
- `idx_traffic_camera_time` on (camera_id, analyzed_at)
- `idx_traffic_incidents` on (incident_detected, analyzed_at)

#### Table 2: `traffic_snapshots`
**Purpose:** Current traffic state (latest per camera) - FAST READS

**Key Fields:**
- `camera_id` (PRIMARY KEY)
- `latest_analysis_id`
- `traffic_density`, `avg_speed_estimate`, `vehicle_count`
- `incident_detected`, `work_zone_detected`
- `updated_at`

#### Table 3: `congestion_events`
**Purpose:** Track congestion episodes over time

**Key Fields:**
- `camera_id`, `started_at`, `ended_at`, `duration_minutes`
- `severity` (minor, moderate, severe)
- `max_vehicle_count`, `avg_speed_during`
- `cause` (incident, work_zone, rush_hour, unknown)
- `status` (active, resolved)

**Index:** `idx_congestion_active` on (status, started_at)

#### Table 4: `incident_alerts`
**Purpose:** Track detected incidents and responses

**Key Fields:**
- `camera_id`, `detected_at`, `resolved_at`
- `incident_type` (stopped_vehicle, debris, emergency, collision)
- `severity` (low, medium, high, critical)
- `confidence`, `lane_number`, `direction`
- `alert_sent`, `rsu_broadcast_id`, `ops_center_notified`
- `status` (active, investigating, resolved, false_positive)

**Index:** `idx_incidents_active` on (status, detected_at)

#### Table 5: `traffic_trends`
**Purpose:** Aggregated hourly/daily patterns

**Key Fields:**
- `camera_id`, `period_start`, `period_end`, `period_type` (hourly, daily, weekly)
- `avg_vehicle_count`, `avg_traffic_flow_score`
- `peak_vehicle_count`, `peak_time`
- `congestion_minutes`, `congestion_percentage`
- `incident_count`

**Index:** `idx_trends_camera_period` on (camera_id, period_start)

---

## Gemini Prompt Design

### Optimized for Token Efficiency (~100 tokens)

```
Analyze this highway camera image for traffic conditions.

OUTPUT JSON ONLY (no markdown):
{
  "vehicleCount": <number>,
  "trafficDensity": "sparse|light|moderate|heavy|congested",
  "avgSpeed": "fast|normal|slow|crawling|stopped",
  "flowScore": <1-10>,
  "lanesDetected": <number>,
  "lanesOccupied": <number>,
  "cars": <number>,
  "trucks": <number>,
  "buses": <number>,
  "weather": "clear|rain|fog|snow",
  "visibility": "excellent|good|reduced|poor",
  "roadSurface": "dry|wet|snow",
  "lighting": "daylight|dusk|night",
  "incidentDetected": <boolean>,
  "incidentType": "stopped_vehicle|debris|emergency|null",
  "workZone": <boolean>,
  "equipment": <boolean>,
  "workers": <boolean>,
  "confidence": <0.0-1.0>
}
```

---

## 5-Hour Implementation Timeline

### Hour 1: Database Setup (5:35 AM - 6:35 AM)

**Tasks:**
1. Create database migration script for 5 new tables
2. Execute migration on `camera_data.db`
3. Verify table creation and indexes
4. Test insert/select operations

**Deliverables:**
- ✅ `fastapi_backend/database/migrations/add_traffic_analysis_tables.sql`
- ✅ All 5 tables created with proper indexes
- ✅ Test data inserted successfully

---

### Hour 2: Gemini Traffic Analyzer Service (6:35 AM - 7:35 AM)

**Tasks:**
1. Create `fastapi_backend/services/traffic_analyzer.py`
2. Implement Gemini 2.0 Flash integration
3. Design optimized prompt (100 tokens)
4. Parse JSON response
5. Handle errors and retries
6. Test with sample camera images

**Deliverables:**
- ✅ `TrafficAnalyzer` class with `analyze_image()` method
- ✅ Returns structured traffic data dict
- ✅ Error handling for API failures
- ✅ Logging with timestamps

**Key Methods:**
```python
class TrafficAnalyzer:
    def __init__(self):
        # Initialize Gemini client

    async def analyze_image(self, image_path: str) -> dict:
        # Analyze image, return traffic data

    def _parse_response(self, response: str) -> dict:
        # Parse JSON from Gemini

    def _calculate_flow_score(self, data: dict) -> int:
        # Calculate 1-10 flow score
```

---

### Hour 3: FastAPI Endpoints (7:35 AM - 8:35 AM)

**Tasks:**
1. Create `fastapi_backend/routers/traffic.py`
2. Implement 5 API endpoints
3. Database integration (save/retrieve traffic data)
4. Test endpoints with Postman/curl

**Deliverables:**
- ✅ `POST /api/traffic/analyze/{camera_id}` - Analyze specific camera
- ✅ `POST /api/traffic/analyze-all` - Batch analyze all cameras
- ✅ `GET /api/traffic/latest/{camera_id}` - Get latest traffic data
- ✅ `GET /api/traffic/snapshot` - Get all cameras' current state
- ✅ `GET /api/traffic/incidents` - Get active incidents

**Endpoint Details:**

**POST /api/traffic/analyze/{camera_id}**
- Fetch latest image for camera
- Call Gemini analyzer
- Save to `traffic_analyses` table
- Update `traffic_snapshots` table
- Detect congestion/incidents
- Return analysis result

**POST /api/traffic/analyze-all**
- Loop through all cameras
- Analyze each (parallel processing)
- Save all results
- Return summary (success/failure counts)

**GET /api/traffic/latest/{camera_id}**
- Query `traffic_snapshots` table
- Return current traffic state
- Include timestamp

**GET /api/traffic/snapshot**
- Query all rows from `traffic_snapshots`
- Return array of camera traffic states
- Used by frontend map

**GET /api/traffic/incidents**
- Query `incident_alerts` WHERE status='active'
- Return active incidents
- Include camera location data

---

### Hour 4: Background Analysis Job (8:35 AM - 9:35 AM)

**Tasks:**
1. Create `fastapi_backend/services/traffic_scheduler.py`
2. Implement scheduled task (every 10 minutes)
3. Analyze all cameras in batch
4. Detect congestion events
5. Detect incidents and create alerts
6. Update snapshots table
7. Test scheduling

**Deliverables:**
- ✅ `TrafficScheduler` class with background task
- ✅ Runs every 10 minutes automatically
- ✅ Congestion event detection logic
- ✅ Incident alert creation logic
- ✅ Logging of all analyses

**Key Logic:**

**Congestion Detection:**
```python
if traffic_flow_score <= 4 and vehicle_count > 20:
    # Check if existing congestion event
    # If not, create new congestion_event
    # If yes, update duration
```

**Incident Detection:**
```python
if incident_detected and confidence > 0.7:
    # Check if existing incident alert
    # If not, create new incident_alert
    # Trigger RSU broadcast (future)
    # Notify ops center (future)
```

---

### Hour 5: Frontend Integration (9:35 AM - 10:35 AM)

**Tasks:**
1. Update map marker colors based on traffic flow score
2. Enhance Red Pin popup with traffic data
3. Add incident badges to markers
4. Test real-time updates
5. Polish UI/UX

**Deliverables:**
- ✅ Color-coded map markers (green/yellow/orange/red/blue/purple)
- ✅ Enhanced popup with traffic metrics
- ✅ Incident alerts visible on map
- ✅ Auto-refresh every 2 minutes

**Map Marker Color Coding:**
- 🟢 **Green:** Free-flowing (flow score 8-10)
- 🟡 **Yellow:** Moderate traffic (flow score 5-7)
- 🟠 **Orange:** Heavy traffic (flow score 3-4)
- 🔴 **Red:** Congested (flow score 1-2)
- 🔵 **Blue:** Incident detected
- 🟣 **Purple:** Work zone active

**Enhanced Popup Example:**
```
📍 Camera: Guelph Line EB
🚗 Traffic: MODERATE (32 vehicles)
⚡ Speed: SLOW (40-60 km/h)
📊 Flow Score: 4/10

🌤️ Conditions: Clear, Dry, Daylight
🚧 Work Zone: NO
⚠️ Incidents: NONE

🕐 Updated: 2 minutes ago
```

---

## File Structure

```
fastapi_backend/
├── database/
│   ├── migrations/
│   │   └── add_traffic_analysis_tables.sql  [NEW]
│   └── camera_data.db  [MODIFIED - 5 new tables]
├── services/
│   ├── traffic_analyzer.py  [NEW]
│   └── traffic_scheduler.py  [NEW]
├── routers/
│   └── traffic.py  [NEW]
└── main.py  [MODIFIED - register traffic router]

docs/
├── TRAFFIC_ANALYSIS_MVP_PLAN.md  [THIS FILE]
└── PREDICTIVE_HAZARD_INTELLIGENCE_SYSTEM.md  [CREATED EARLIER]
```

---

## Success Criteria

### After 5 Hours, We Can Demo:

1. ✅ **Open map** → See color-coded traffic conditions on all 14 cameras
2. ✅ **Click camera** → See real-time traffic metrics (count, speed, density)
3. ✅ **Detect incident** → Red marker appears, popup shows "Stopped vehicle in Lane 2"
4. ✅ **Track congestion** → See which cameras have heavy traffic right now
5. ✅ **Historical view** → "This camera had 3 congestion events today"
6. ✅ **Auto-refresh** → Map updates every 2 minutes with latest traffic data
7. ✅ **API access** → All traffic data available via REST endpoints

---

## Next Steps (After MVP)

### Phase 2 Enhancements (Future):
- Lane-specific analysis (which lane has congestion)
- Predictive modeling (queue propagation forecasting)
- Multi-camera correlation (upstream/downstream intelligence)
- RSU broadcast integration (automatic V2X alerts)
- Historical trend analysis dashboard
- Email/SMS alerts for critical incidents
- Integration with MTO traffic APIs
- Machine learning model training on collected data

---

## Notes

- **Backend AI Approach:** Corey's architecture (AI in FastAPI backend) is the approved approach
- **Mohammed's Frontend AI:** NOT recommended for production (see `AI_ARCHITECTURE_DECISION.md`)
- **Database Portability:** All paths are relative (no absolute paths like `C:\...`)
- **Logging:** Full timestamps on all log entries
- **Error Handling:** Single retry logic for failed API calls

---

**Ready to start implementation at 5:35 AM EST!** 🚀

**Estimated Completion:** 10:35 AM EST
**Total Time:** 5 hours
**Deliverables:** Working Real-Time Traffic Intelligence System


