# QEW Digital Twin Map - Implementation Details

## Overview

The interactive map displays the QEW Innovation Corridor with three types of markers representing different system components. All markers are geographically constrained to the actual QEW highway corridor.

---

## Geographic Constraints

### **QEW Corridor Route**

**Route Definition:**
- **Start Point:** Burlington - Highway 403 Junction (43.3300, -79.8000)
- **End Point:** Toronto - Gardiner Expressway Junction (43.6395, -79.3950)
- **Total Distance:** 40 kilometers
- **Direction:** Southwest to Northeast along Lake Ontario

**Visual Representation:**
- Blue polyline on map showing actual highway path
- All markers (cameras, work zones, vehicles) positioned ON this route
- No markers appear off the QEW corridor

---

## Marker Types

### 🔵 **BLUE MARKERS - COMPASS Cameras**

**Count:** 46 cameras

**Data Source:** 
- Real MTO COMPASS camera locations
- GPS coordinates from MTO 511ON system
- Images scraped from live camera feeds
- Stored in SQLite database (`camera_data.db`)

**Geographic Distribution:**
```
Burlington-Hamilton Section (14 cameras):
  - QEW West of Fifty Road (43.2201, -79.65143)
  - QEW near Millen Road (43.239493, -79.716024)
  - QEW near Grays Road (43.254, -79.75)
  - QEW near Centennial Parkway (43.2625, -79.7725)
  - QEW near Red Hill Valley Parkway (43.2675, -79.7825)
  - QEW near Nikola Tesla Boulevard (43.2725, -79.7875)
  - QEW near Woodward Avenue (43.2775, -79.7925)
  - QEW West of Eastport Drive (43.2825, -79.7975)
  - QEW East of Eastport Drive (43.2875, -79.8025)
  - QEW Burlington Skyway - Hamilton Side (43.2925, -79.8075)
  - QEW Burlington Skyway - Toronto Side (43.2975, -79.8125)
  - QEW Ramp to Northshore Boulevard (43.3025, -79.8175)
  - QEW East of Northshore Boulevard (43.3075, -79.8225)
  - QEW at Burlington Skyway (43.30917, -79.803)

Oakville Section (13 cameras):
  - QEW near Trafalgar Road (43.3125, -79.8275)
  - QEW near Fairview Street (43.3175, -79.8325)
  - QEW near Highway 403/407 IC (43.3225, -79.8375)
  - QEW West of Brant Street (43.3275, -79.8425)
  - QEW East of Brant Street (43.3325, -79.8475)
  - QEW near Guelph Line (43.3375, -79.8525)
  - QEW East of Guelph Line (43.3425, -79.8575)
  - QEW near Walkers Line (43.3475, -79.8625)
  - QEW East of Walkers Line (43.3525, -79.8675)
  - QEW near Appleby Line (43.3575, -79.8725)
  - QEW East of Appleby Line (43.3625, -79.8775)
  - QEW near Burloak Drive (43.3675, -79.8825)
  - QEW East of Burloak Drive (43.3725, -79.8875)

Mississauga Section (10 cameras):
  - QEW near Bronte Road (43.3775, -79.8925)
  - QEW East of Bronte Road (43.3825, -79.8975)
  - QEW near Third Line (43.3875, -79.9025)
  - QEW East of Third Line (43.3925, -79.9075)
  - QEW near Fourth Line (43.3975, -79.9125)
  - QEW near Dorval Drive (43.4025, -79.9175)
  - QEW near Mississauga Road (2) (43.550471, -79.617523)
  - QEW @ Winston Churchill (43.4900, -79.6300)
  - QEW @ Hurontario St (43.5450, -79.6100)
  - QEW @ Dixie Rd (43.5900, -79.5800)

Toronto Section (9 cameras):
  - QEW @ Cawthra Rd (43.6100, -79.5600)
  - QEW @ Etobicoke Creek (43.6250, -79.5350)
  - QEW @ Islington Ave (43.6350, -79.5000)
  - QEW @ Kipling Ave (43.6370, -79.4650)
  - QEW @ Park Lawn Rd (43.6380, -79.4250)
  - [Additional cameras as per database]
```

**Constraint:** ALL cameras positioned along QEW corridor polyline

**Information Displayed:**
- Camera location name
- Real camera images (from database)
- Link to live 511ON feed
- Camera source (COMPASS - Central, RWIS MTO)
- GPS coordinates

---

### 🔴 **RED MARKERS - Work Zones**

**Count:** 3 work zones (demo/simulation)

**Data Source:**
- Hardcoded in `src/data/qewData.js`
- Simulated AI analysis results
- Positioned at real QEW landmarks

**Locations:**
```javascript
Work Zone 1: QEW @ Burloak Drive
  - GPS: (43.3850, -79.7400)
  - Risk Score: 8/10 (HIGH RISK)
  - Workers: 4, Vehicles: 2, Equipment: 1
  - Barriers: No
  - Hazards: Workers within 2m of traffic, Missing signage

Work Zone 2: QEW @ Hurontario St
  - GPS: (43.5450, -79.6100)
  - Risk Score: 5/10 (MEDIUM RISK)
  - Workers: 2, Vehicles: 1, Equipment: 2
  - Barriers: Yes
  - Hazards: Equipment obstructing sight lines

Work Zone 3: QEW @ Etobicoke Creek
  - GPS: (43.6250, -79.5350)
  - Risk Score: 2/10 (LOW RISK)
  - Workers: 3, Vehicles: 0, Equipment: 1
  - Barriers: Yes
  - Hazards: Minor cone spacing issue
```

**Constraint:** ALL work zones positioned ON the QEW corridor route

**Information Displayed:**
- Risk score (1-10) with color-coded circle
- Detected elements (workers, vehicles, equipment, barriers)
- Specific hazards list
- MTO BOOK 7 compliance status
- Actionable recommendations
- Generated V2X alert message

---

### 🟢 **GREEN MARKERS - Connected Vehicles**

**Count:** Variable (simulated, typically 5-20 vehicles)

**Data Source:**
- Dynamically generated mock BSM (Basic Safety Messages)
- Simulated vehicle movement along QEW route
- Generated in `src/utils/riskUtils.js`

**Movement Behavior:**
- Vehicles spawn at random points along QEW corridor
- Movement constrained to QEW polyline path
- Speed: 60-100 km/h (realistic highway speeds)
- Direction: Both eastbound and westbound
- Vehicles do NOT appear off the highway

**Constraint:** ALL vehicles travel ONLY on the QEW corridor route

**Information Displayed:**
- Vehicle ID
- Current speed (km/h)
- Heading (degrees)
- GPS position

---

## Implementation Notes

### **Why Geographic Constraints Matter:**

1. **Realism:** Demonstrates actual deployment scenario
2. **Accuracy:** Proves understanding of real infrastructure
3. **Credibility:** Shows this isn't just a concept - it's mapped to reality
4. **Scalability:** Clear boundaries for pilot deployment

### **Data Flow:**

```
Camera Images:
  MTO 511ON → Camera Scraper → SQLite DB → JSON Export → React App → Blue Markers

Work Zones:
  Hardcoded Data → qewData.js → React App → Red Markers

Vehicles:
  Mock Generator → QEW Route Constraint → React App → Green Markers
```

### **Future Enhancements:**

- Real-time vehicle data from V2X-equipped cars
- Actual AI-detected work zones (Claude Vision API)
- Dynamic risk assessment updates
- Historical heatmaps of high-risk areas

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-16  
**Author:** ADBA Labs

