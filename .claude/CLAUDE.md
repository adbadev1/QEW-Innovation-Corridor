# .claude/CLAUDE.md - QEW Innovation Corridor AI Development Guidelines

**Tier 0 Documentation** - Read this FIRST before any development work.

Last Updated: 2025-11-17
Project: QEW Innovation Corridor Digital Twin Dashboard
Organization: ADBA Labs
Purpose: OVIN $150K Pilot Application

---

## 🚨 CRITICAL CONFIGURATION RULES

### Port Configuration (NEVER VIOLATE)
```
✅ ALWAYS: Port 8200 for development server
❌ NEVER: Port 3000 (conflicts with React/Next.js)
```

**Universal Port Registry:** `/Users/adbalabs/config/universal_port_config.md`

If port configuration needs to change:
1. Update `vite.config.js` in this project
2. Update `/Users/adbalabs/config/universal_port_config.md`
3. Document reason in commit message

### Development Commands
```bash
npm run dev      # Start dev server (port 8200)
npm run build    # Build for production
npm run deploy   # Deploy to GitHub Pages
```

---

## 📍 GEOGRAPHIC ACCURACY STANDARDS

### CRITICAL: Production Coordinates Only

**✅ DO:**
- Use production coordinates from `src/data/qewData.js` (46 COMPASS cameras)
- Use OSRM-generated routes from `src/data/qewRoutes.js` (364 westbound, 316 eastbound waypoints)
- Verify coordinates against MTO COMPASS system
- Cross-reference with Google Maps for accuracy

**❌ NEVER:**
- Interpolate or mock coordinates
- Use approximate locations
- Guess camera positions
- Generate synthetic waypoints

**Why This Matters:**
- OVIN pilot requires ±10m accuracy for V2X RSU placement
- MTO compliance requires exact camera-to-road mapping
- Safety alerts depend on precise geolocation

### Data Sources (Source of Truth)
```javascript
// Camera locations (46 cameras, Hamilton to Mississauga)
import { COMPASS_CAMERAS } from './data/qewData.js';

// Driving routes (OSRM-generated, actual road geometry)
import { qewPathWestbound, qewPathEastbound } from './data/qewRoutes.js';
```

---

## 🎯 PROJECT CONTEXT

### Current Phase: Phase 0 Complete → Phase 1 Starting
- **Phase 0:** ✅ Hackathon prototype (3 hours, COMPLETE)
- **Phase 1:** ⏳ OVIN Application (Sprint 1, 2 weeks)
- **Phase 2:** 🔜 Production Development (Months 1-2)
- **Phase 3:** 🔜 Testing & Validation (Months 3-4)
- **Phase 4:** 🔜 Pilot Deployment (Months 5-6)

### Sprint 1 Focus (Nov 17 - Nov 30, 2025)
1. Complete OVIN Client Intake Form
2. Create OVIN documentation structure
3. Prepare pitch deck for Steering Committee
4. Deploy public demo to GitHub Pages ✅
5. **CRITICAL:** Implement real work zone detection (Issue #4)

---

## 🏗️ ARCHITECTURE OVERVIEW

### Tech Stack
- **Frontend:** React 18.3 + Vite 5.4
- **UI:** Tailwind CSS 3.4
- **Maps:** Leaflet 1.9 + React-Leaflet 4.2
- **Charts:** Recharts 2.12
- **AI Engine:** Claude 3.5 Sonnet (Vision API)
- **Deployment:** GitHub Pages
- **Future Backend:** GCP Cloud Run + PostgreSQL + Redis

### Component Structure
```
src/
├── App.jsx                          # Main dashboard (Digital Twin)
├── components/
│   ├── WorkZoneAnalysisPanel.jsx    # AI analysis panel
│   ├── TrafficMap.jsx               # Leaflet map (future)
│   └── MetricsDashboard.jsx         # Charts panel (future)
├── data/
│   ├── qewData.js                   # Camera locations (46 cameras)
│   └── qewRoutes.js                 # OSRM routes (680 waypoints)
├── utils/
│   ├── riskUtils.js                 # Risk scoring algorithms
│   └── claudeVision.js              # Claude Vision API (future)
└── services/
    └── workZoneDetection.js         # AI detection service (Issue #4)
```

---

## 🔬 CRITICAL ISSUE #4: Real Work Zone Detection

**This is THE transformative task for SaaS product.**

### Current (Demo Only - NOT ACCEPTABLE):
```javascript
// Hardcoded simulations in App.jsx
const WORK_ZONES = [
  { id: 'WZ_001', lat: 43.3850, lon: -79.7400, riskScore: 8 }
];
```

### Target (Production SaaS - REQUIRED):
```javascript
// AI-detected work zones from camera feeds
async function detectWorkZonesFromCameras() {
  const cameras = await fetchCOMPASSCameraFeeds();

  for (const camera of cameras) {
    const image = await camera.getLatestFrame();
    const analysis = await claudeVisionAPI.analyzeWorkZone(image);

    if (analysis.hasWorkZone && analysis.riskScore >= 5) {
      addWorkZoneMarker({
        camera_id: camera.id,
        lat: camera.lat,
        lon: camera.lon,
        riskScore: analysis.riskScore,
        detected: analysis.detectedElements,
        timestamp: Date.now()
      });
    }
  }
}
```

**User Requirement:** "We don't want 3 work zone simulations positioned on actual QEW route, we want the model to recognize the real work zones as we build the SaaS Solution"

---

## 🎨 COMPONENT DEVELOPMENT PATTERNS

### State Management
```javascript
// Use React hooks for local state
const [workZones, setWorkZones] = useState([]);
const [cameras, setCameras] = useState(COMPASS_CAMERAS);
const [vehicles, setVehicles] = useState([]);

// Future: Consider Zustand for global state when complexity grows
```

### Leaflet Map Integration
```javascript
// Always wrap in MapContainer
<MapContainer center={[43.4, -79.7]} zoom={10} style={{ height: '100vh' }}>
  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
  {cameras.map(cam => (
    <Marker key={cam.id} position={[cam.lat, cam.lon]} />
  ))}
</MapContainer>
```

### Claude Vision API Pattern (Future)
```javascript
// src/utils/claudeVision.js
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: import.meta.env.VITE_CLAUDE_API_KEY
});

export async function analyzeWorkZone(imageBase64) {
  const message = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20250219',
    max_tokens: 2000,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'base64', data: imageBase64 } },
        { type: 'text', text: WORK_ZONE_ANALYSIS_PROMPT }
      ]
    }]
  });

  return JSON.parse(message.content[0].text);
}
```

---

## 🧪 TESTING STANDARDS

### Pre-Commit Checklist
- [ ] Dev server starts on port 8200
- [ ] All 46 cameras visible on map
- [ ] Vehicle animations smooth (10 vehicles)
- [ ] Work zone markers clickable with popups
- [ ] Right panel displays AI analysis
- [ ] No console errors
- [ ] Mobile responsive (test at 375px width)

### Production Build Testing
```bash
npm run build
npm run preview  # Test production build locally
```

### GitHub Pages Deployment
```bash
npm run deploy   # Builds + deploys to gh-pages branch
```

**Live Demo:** https://adbadev1.github.io/QEW-Innovation-Corridor/

---

## 📊 DATA FLOW ARCHITECTURE

### Current (Phase 0 - Demo)
```
Static Data → React State → Leaflet Map → User Interaction
    ↓
qewData.js (46 cameras)
qewRoutes.js (680 waypoints)
mockWorkZones (3 hardcoded)
```

### Target (Phase 2 - Production)
```
MTO COMPASS API → Camera Feeds (1fps) → Claude Vision API
                                              ↓
                                    Work Zone Detection
                                              ↓
                                    PostgreSQL Database
                                              ↓
                              React Dashboard (WebSocket updates)
                                              ↓
                                    V2X-Hub RSU Broadcast
```

---

## 🔐 SECURITY & COMPLIANCE

### API Keys (NEVER COMMIT)
```bash
# Use .env file (in .gitignore)
VITE_CLAUDE_API_KEY=your-api-key-here

# Access in code:
const apiKey = import.meta.env.VITE_CLAUDE_API_KEY;
```

### FIPPA Compliance (Ontario Privacy)
- No personally identifiable information (PII) in camera feeds
- Automatic face/plate blurring (future requirement)
- Data retention: 30 days maximum
- Audit logs for all access

### MTO BOOK 7 Compliance (Work Zone Safety)
- 47 safety rules to automate
- Risk scoring algorithm: `src/utils/riskUtils.js`
- Compliance checking: future feature in Issue #4

---

## 🚫 NEVER DO THIS

1. **Port Changes:**
   - ❌ Never use port 3000 (conflicts with other ADBA Labs projects)
   - ❌ Never change port without updating universal config

2. **Geographic Data:**
   - ❌ Never mock or interpolate coordinates
   - ❌ Never use placeholder locations
   - ❌ Never trust unverified data sources

3. **Git Commits:**
   - ❌ Never commit `.env` files
   - ❌ Never commit `node_modules/`
   - ❌ Never commit API keys or secrets
   - ❌ Never force push to main branch

4. **Code Quality:**
   - ❌ Never use `var` (use `const`/`let`)
   - ❌ Never leave `console.log()` in production
   - ❌ Never hardcode URLs (use environment variables)

5. **Work Zones (CRITICAL):**
   - ❌ Never add more hardcoded work zones
   - ❌ Never simulate work zone data in production
   - ✅ Always use AI-detected real work zones (Issue #4)

---

## 📝 COMMIT MESSAGE STANDARDS

### Format
```
<type>(<scope>): <description>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `deploy`: Deployment changes

### Examples
```bash
git commit -m "feat(ai): Add Claude Vision API integration for Issue #4

- Implement analyzeWorkZone() function
- Process camera feeds at 1fps
- Return structured JSON with risk scores
- Add error handling and fallback to mock data

Closes #4"
```

```bash
git commit -m "config: Update port to 8200 per universal standards

Per /Users/adbalabs/config/universal_port_config.md
- Updated vite.config.js server.port
- Avoids conflict with port 3000 projects"
```

---

## 🎯 OVIN APPLICATION CONTEXT

### Funding Target
- **Amount:** $150,000 CAD
- **Duration:** 6 months
- **Testbed:** QEW Innovation Corridor (40km, Burlington to Toronto)

### Key Contacts
- **Program Manager:** David Harris-Koblin (dharris-koblin@oc.innovation.ca)
- **Organization:** Ontario Vehicle Innovation Network (OVIN)
- **Website:** https://www.ovinhub.ca/

### Application Requirements (Sprint 1)
1. ✅ Client Intake Form (Issue #6, 2 days)
2. ✅ Pitch Deck (Issue #7, 3 days)
3. ✅ Technical Architecture (docs/ARCHITECTURE.md)
4. ✅ Budget Breakdown (docs/ovin/BUDGET_BREAKDOWN.md)
5. ✅ Compliance Documentation (MTO BOOK 7, FIPPA)
6. ✅ Live Demo (GitHub Pages) ✅
7. ✅ Real work zone detection capability (Issue #4, P1 CRITICAL)

---

## 🔗 ESSENTIAL FILES TO READ

### Tier 1 (Essential - Root)
- `README.md` - Project overview
- `STATE_OF_THE_NATION.md` - Current status, metrics, action plan
- `SAAS_CHALLENGE_SUMMARY.md` - 7 critical challenges

### Tier 2 (Domain - docs/)
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/MVP_WORKFLOW.md` - Complete 6-month roadmap with Mermaid diagrams
- `docs/DEMO_SCRIPT.md` - 3-minute presentation guide
- `docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md` - Project standards
- `docs/sprints/Sprint1/SPRINT_PLAN.md` - Current sprint tasks
- `docs/onboarding/QUICK_START.md` - 5-minute setup guide

### Critical Data Files
- `src/data/qewData.js` - 46 COMPASS camera locations
- `src/data/qewRoutes.js` - 680 OSRM waypoints (actual road geometry)
- `camera_scraper/qew_cameras_hamilton_mississauga.json` - Camera metadata

---

## 🚀 QUICK START FOR AI AGENTS

```bash
# 1. Verify environment
pwd  # Should be: /Users/adbalabs/QEW-Innovation-Corridor

# 2. Check dependencies
npm install  # Install if needed

# 3. Start dev server
npm run dev  # Opens http://localhost:8200

# 4. Before any code changes, read:
cat .claude/CLAUDE.md                              # This file (you are here)
cat STATE_OF_THE_NATION.md                         # Current project status
cat docs/sprints/Sprint1/SPRINT_PLAN.md            # Current sprint
cat docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md # Project standards

# 5. Check current issue status
gh issue list --label P1  # Priority 1 issues
```

---

## 📚 ADDITIONAL RESOURCES

### MTO/OVIN Resources
- [OVIN Program Guidelines](https://www.ovinhub.ca/wp-content/uploads/2025/02/OVIN-QEW-IC-Program-Guidelines-Final-Version-2024.11.18.pdf)
- [MTO COMPASS System](http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml)
- [MTO BOOK 7 (Work Zone Safety)](https://www.library.mto.gov.on.ca/SydneyPLUS/TechPubs/Portal/tp/tvWelcome.aspx)

### Technical Standards
- [SAE J2735 (V2X Messages)](https://www.sae.org/standards/content/j2735_202309/)
- [USDOT V2X-Hub (RSU Software)](https://github.com/usdot-fhwa-OPS/V2X-Hub)
- [Leaflet Documentation](https://leafletjs.com/reference.html)
- [Claude Vision API](https://docs.anthropic.com/en/docs/vision)

### Development Tools
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

---

## 🏁 READY TO START DEVELOPING?

1. ✅ Read this file (you just did!)
2. ✅ Check `STATE_OF_THE_NATION.md` for current status
3. ✅ Review `docs/sprints/Sprint1/SPRINT_PLAN.md` for tasks
4. ✅ Look at GitHub Issues: `gh issue list`
5. 🚀 Start coding!

**Questions?** Check `docs/onboarding/QUICK_START.md` or `docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md`

---

**Last Updated:** 2025-11-17
**Project Phase:** Phase 1 (OVIN Application)
**Sprint:** Sprint 1 (Nov 17 - Nov 30, 2025)
**Critical Path:** Issue #4 (Real Work Zone Detection)

🤖 **Built with [Claude Code](https://claude.com/claude-code)**
