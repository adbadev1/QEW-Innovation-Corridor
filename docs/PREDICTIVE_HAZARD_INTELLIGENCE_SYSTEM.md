# Predictive Highway Intelligence System (PHIS)

**Vision Document**  
**Author:** Corey  
**Date:** November 19, 2025  
**Status:** FUTURE ROADMAP  

---

## Executive Summary

A real-time, AI-powered system that **predicts hazards before they become critical** and **proactively warns drivers** through V2X infrastructure. This system analyzes camera feeds to provide lane-specific, directional, and temporal hazard assessments with predictive forecasting.

---

## Core Concept: Multi-Layer Temporal Analysis

Instead of just analyzing **"what's happening now"**, the system analyzes:

1. **PAST** - Historical patterns (last 24 hours, week, month)
2. **PRESENT** - Current conditions (real-time camera analysis)
3. **FUTURE** - Predictive modeling (next 5 minutes, 30 minutes, 2 hours)

---

## AI Analysis Layers

### Layer 1: Real-Time Scene Understanding (Current)

**Lane-Level Precision:**
- Which specific lane has the hazard (Lane 1, 2, 3, 4, HOV, shoulder)
- Lane closure status (open, partially blocked, fully closed)
- Lane shift patterns (temporary routing)

**Directional Analysis:**
- Eastbound vs Westbound
- On-ramp vs off-ramp
- Collector vs express lanes

**Work Zone Granularity:**
- Active work zone vs inactive (equipment present but no workers)
- Worker proximity to live traffic (0-5m = CRITICAL, 5-10m = HIGH, 10m+ = MODERATE)
- Number of workers per lane
- Equipment type (excavator, paving machine, arrow board, shadow vehicle)
- Barrier type (concrete K-rail, water-filled barriers, cones only)

**Environmental Conditions:**
- Weather (rain, fog, snow, ice, clear)
- Visibility (excellent, good, poor, zero)
- Road surface (dry, wet, icy, snow-covered)
- Time of day (dawn, day, dusk, night)
- Lighting conditions (natural, artificial, insufficient)

**Traffic Behavior:**
- Vehicle speed (per lane)
- Lane change frequency (erratic = danger)
- Following distance (tailgating detection)
- Heavy vehicle percentage (trucks, buses)
- Queue formation (backup detection)

### Layer 2: Temporal Pattern Recognition (Past → Present)

**Hazard Evolution Tracking:**
- "Work zone appeared 2 hours ago, workers getting closer to traffic"
- "Traffic slowing in Lane 2 for last 15 minutes → queue forming"
- "Visibility degrading over last 30 minutes (fog rolling in)"

**Incident Precursors:**
- "Lane changes increased 300% in last 10 minutes → collision risk"
- "Speed variance between lanes widening → merge conflict zone"
- "Heavy vehicle concentration in right lane → slow-moving hazard"

**Pattern Matching:**
- "Similar conditions led to 3 incidents in past 6 months"
- "This work zone configuration has 2x higher near-miss rate"
- "Rush hour + rain + this location = high-risk combination"

### Layer 3: Predictive Hazard Modeling (Present → Future)

**5-Minute Forecast:**
- "Worker will enter Lane 1 in 3 minutes (based on movement pattern)"
- "Queue will reach camera location in 4 minutes (based on backup growth rate)"
- "Lane closure will begin in 2 minutes (arrow board activated)"

**30-Minute Forecast:**
- "Rush hour traffic will reach work zone in 20 minutes → congestion spike"
- "Rain forecast in 15 minutes → visibility will drop, braking distance increases"
- "Shift change detected → 5 new workers entering zone in 25 minutes"

**2-Hour Forecast:**
- "Sunset in 90 minutes → lighting conditions will degrade"
- "Scheduled lane closure at 6 PM → traffic will divert to Lane 2"
- "Weather system approaching → wet road conditions expected"

---

## Proactive Warning System

### Multi-Tier Alert Architecture

#### Tier 1: PREDICTIVE (Before Hazard Materializes)
- **Trigger:** AI predicts hazard will occur in 5-30 minutes
- **Action:** Pre-warn drivers 2km upstream, suggest alternate routes, reduce speed limits gradually
- **Example:** "Work zone expansion predicted in 15 minutes. Reduce speed to 80 km/h. Consider using express lanes."

#### Tier 2: PROACTIVE (Hazard Exists, Driver Not Yet Near)
- **Trigger:** Hazard detected, driver 1-2km away
- **Action:** Lane-specific warnings, speed reduction, merge preparation, RSU broadcasts
- **Example:** "Work zone ahead in 1.2 km, Lane 1 closed. Merge left now. Reduce speed to 60 km/h."

#### Tier 3: REACTIVE (Hazard Imminent)
- **Trigger:** Driver within 500m of hazard
- **Action:** Critical warnings, emergency braking suggestions, lane change prohibitions
- **Example:** "DANGER: Workers in Lane 1, 300m ahead. DO NOT CHANGE LANES. Slow to 40 km/h immediately."

---

## Lane-Specific Intelligence

### Per-Lane Risk Scoring (1-10 scale)

**Example Scenario: Eastbound QEW at Guelph Line**

| Lane | Status | Risk Score | Hazard | Recommendation |
|------|--------|------------|--------|----------------|
| Lane 1 (Left) | CRITICAL | 9/10 | Workers 3m from traffic, no barrier | AVOID - CLOSED |
| Lane 2 | HIGH | 7/10 | Equipment encroaching, reduced width | CAUTION - 60 km/h |
| Lane 3 | MODERATE | 4/10 | Merge traffic from Lane 1 | ALERT - EXPECT MERGES |
| Lane 4 (Right) | LOW | 2/10 | Clear, but slower trucks | SAFE - 80 km/h |
| Shoulder | BLOCKED | 10/10 | Construction staging area | NO STOPPING |

**AI Recommendation:** "Use Lane 3 or Lane 4. Expect merging traffic from Lane 1. Maintain 80 km/h."

---

## Predictive Hazard Scenarios

### Scenario 1: Worker Movement Prediction

**Current State:**
- 3 workers visible, 1 walking toward Lane 1

**AI Prediction:**
- Worker trajectory: Moving toward Lane 1 at 0.5 m/s
- Time to danger: 45 seconds
- Confidence: 92%

**Proactive Action:**
- T-30s: Pre-warn drivers 500m upstream
- T-15s: RSU broadcast
- T-0s: Critical alert

### Scenario 2: Queue Propagation Prediction

**Current State:**
- Camera 1: 100 km/h
- Camera 2 (2km east): 40 km/h queue
- Camera 3 (4km east): Stopped (incident)

**AI Prediction:**
- Queue growth: 500m every 3 minutes
- ETA to Camera 1: 12 minutes

**Proactive Action:**
- T-12 min: Alert approaching drivers
- T-6 min: Reduce speed to 80 km/h
- T-3 min: Dynamic signs activated
- T-0 min: Drivers already prepared

### Scenario 3: Environmental Degradation Prediction

**Current State:**
- Visibility: Good (5km), Overcast, Dry roads, 5:30 PM

**AI Prediction:**
- Rain: 80% in 20 minutes
- Sunset: 45 minutes
- Result: Visibility <500m, wet roads, low light

**Proactive Action:**
- T-20 min: Rain warning
- T-10 min: Visibility degrading alert
- T-0 min: Wet road speed reduction
- T+45 min: Low visibility + wet roads extreme caution

---

## Multi-Camera Correlation

### Upstream/Downstream Intelligence

**14-Camera QEW Corridor Example:**

```
[CAM 1] → [CAM 2] → [CAM 3] → ... → [CAM 14]
 Clear    Work Zone  Queue Forming    Incident
Risk: 1   Risk: 7    Risk: 8          Risk: 10
```

**AI Correlation:**
- Incident at CAM 14 causing queue at CAM 13
- Queue propagating westbound at 500m/3min
- Work zone at CAM 2 will compound congestion in 15 min
- Recommend diverting at CAM 1

**Proactive Routing:**
- Drivers at CAM 1: "Major delays ahead. Consider Highway 403."
- Drivers at CAM 2: "Already in corridor. Expect 20-min delay. Stay Lane 3."

---

## AI Model Architecture

### Multi-Model Ensemble

1. **Object Detection (YOLOv8):** Workers, vehicles, equipment, barriers
2. **Semantic Segmentation:** Lanes, road surface, shoulders, work zones
3. **Pose Estimation:** Worker positions, movement trajectories
4. **Optical Flow:** Traffic speed, lane changes, queue formation
5. **Weather Classifier:** Clear, rain, fog, snow, visibility scoring
6. **Temporal Prediction (LSTM/Transformer):** Future state forecasting
7. **Risk Scoring (Ensemble):** Per-lane risk scores, confidence levels

---

## Data Fusion Sources

**Beyond Camera Images:**

1. **Weather APIs:** Real-time precipitation, visibility, wind, forecasts
2. **Traffic APIs:** MTO traffic data, Waze/Google Maps crowdsourced
3. **Work Zone Schedules:** Planned closures, shift times, MTO BOOK 7 compliance
4. **Historical Incidents:** Past collisions, near-misses, patterns
5. **Connected Vehicles (V2X):** Real-time speed, braking, traction events
6. **Road Sensors:** Pavement temp, moisture, ice, traffic counters

---

## Risk Assessment Matrix

### Multi-Dimensional Risk Calculation

**Risk Score = f(Severity, Exposure, Likelihood, Predictability)**

| Factor | Weight | Example |
|--------|--------|---------|
| Hazard Severity | 40% | Worker in Lane 1 (10/10) vs Cone (2/10) |
| Exposure | 25% | Rush hour (10/10) vs Midnight (2/10) |
| Likelihood | 20% | Historical incident rate at location |
| Predictability | 15% | 30 min warning (low) vs 30 sec (high) |

**Example:** Worker in Lane 1, rush hour, high-incident location, 45s warning
- Score: (10×0.4) + (9×0.25) + (8×0.2) + (3×0.15) = **8.5/10 = CRITICAL**

---

## Dynamic Response System

| Risk Score | Classification | Automated Actions |
|------------|----------------|-------------------|
| 9-10 | CRITICAL | Emergency RSU (500m), 40 km/h, alert patrol, close lane |
| 7-8 | HIGH | RSU (1km), 60 km/h, dynamic signs, alert ops center |
| 5-6 | MODERATE | RSU advisory (2km), suggest lane changes, update apps |
| 3-4 | LOW | Informational messages, passive monitoring |
| 1-2 | MINIMAL | Normal operations, data logging |

---

## Enhanced Red Pin Data Structure

**Current Red Pin:**
```javascript
{
  lat, lon, cameraId, riskScore, status, workers, vehicles,
  barriers, hazards, v2xAlert, vrsuBroadcast
}
```

**Enhanced with Predictive AI:**
```javascript
{
  // ... existing fields ...

  laneAnalysis: [
    { lane: 1, status: "CLOSED", risk: 9, hazard: "Workers", rec: "AVOID" },
    { lane: 2, status: "RESTRICTED", risk: 7, hazard: "Equipment", rec: "60 km/h" },
    { lane: 3, status: "OPEN", risk: 4, hazard: "Merges", rec: "CAUTION" },
    { lane: 4, status: "OPEN", risk: 2, hazard: "None", rec: "SAFE" }
  ],

  direction: "Eastbound",
  affectedLanes: "Lanes 1-2 of 4",

  conditions: {
    weather: "Clear", visibility: "Excellent", roadSurface: "Dry",
    lighting: "Daylight", temperature: 18
  },

  predictions: {
    next5min: { risk: 8, event: "Worker enters Lane 1", confidence: 0.92 },
    next30min: { risk: 9, event: "Rush hour arrives", confidence: 0.85 },
    next2hours: { risk: 6, event: "Sunset - lighting degrades", confidence: 0.95 }
  },

  history: {
    workZoneAge: "2h 15min",
    workerProximityTrend: "Getting closer",
    trafficSpeedTrend: "Slowing (100→85 km/h)",
    incidentHistory: "3 near-misses in 6 months"
  },

  corridorContext: {
    upstreamCameras: [{ id: "CAM_000", distance: -2000, status: "Clear", risk: 1 }],
    downstreamCameras: [
      { id: "CAM_002", distance: 2000, status: "Queue", risk: 8 },
      { id: "CAM_003", distance: 4000, status: "Incident", risk: 10 }
    ],
    queuePropagation: { direction: "Westbound", speed: "500m/3min", eta: "12 min" }
  }
}
```

---

## Implementation Roadmap

### Phase 1: Enhanced Real-Time Analysis (3 months)
- Lane detection and segmentation
- Directional analysis (EB/WB, lane numbers)
- Environmental condition classification
- Per-lane risk scoring

### Phase 2: Temporal Pattern Recognition (6 months)
- Historical data collection
- Trend analysis (worker movement, traffic speed)
- Pattern matching with incident database
- Near-miss detection

### Phase 3: Predictive Modeling (9 months)
- LSTM/Transformer training
- 5-minute hazard forecasting
- Worker trajectory prediction
- Queue propagation modeling

### Phase 4: Multi-Camera Correlation (12 months)
- Corridor-wide situational awareness
- Upstream/downstream intelligence
- Traffic flow modeling across 14 cameras
- Proactive routing recommendations

### Phase 5: Continuous Learning (Ongoing)
- Incident feedback loop
- Model retraining pipeline
- False positive reduction
- Driver behavior optimization

---

## The Ultimate Vision

**A highway system that:**

✅ Predicts hazards before they become critical
✅ Warns drivers with lane-specific, actionable guidance
✅ Adapts in real-time to changing conditions
✅ Learns from every incident and near-miss
✅ Coordinates across entire corridor
✅ Integrates weather, traffic, work zones, historical data
✅ Provides 5-min, 30-min, 2-hour forecasts
✅ Reduces incidents through proactive intervention

**Result:** A self-aware, predictive highway that keeps workers and drivers safe through AI-powered foresight, not just reaction.

---

**This is the future of highway safety.** 🚀


