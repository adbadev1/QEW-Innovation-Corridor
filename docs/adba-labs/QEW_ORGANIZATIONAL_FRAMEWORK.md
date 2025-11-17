# QEW Innovation Corridor - Organizational Framework

**Version**: 1.0
**Created**: 2025-11-17
**Purpose**: Project organization framework for QEW Innovation Corridor
**Adapted From**: [ADBA Labs SaaS Organizational Framework](../../future_city_hackathon/docs/adba-labs/SAAS_ORGANIZATIONAL_FRAMEWORK.md)
**Project Type**: Hackathon → OVIN Pilot → Production SaaS

---

## Executive Summary

This framework adapts the ADBA Labs SaaS organizational structure for the QEW Innovation Corridor project, accounting for its unique lifecycle from hackathon prototype to production deployment.

**Project Phases**:
1. **Phase 0: Hackathon Prototype** ✅ COMPLETE (3 hours)
2. **Phase 1: OVIN Application** (Week 1-4)
3. **Phase 2: Production Development** (Month 1-2)
4. **Phase 3: Testing & Validation** (Month 3-4)
5. **Phase 4: Pilot Deployment** (Month 5-6) → $150K OVIN Funding

**Target Outcomes**:
- **Documentation**: ≤30 active .md files (simpler than full SaaS)
- **Root Directory**: ≤8 essential files
- **Development Port**: 8200 (standardized per universal config)
- **Deployment**: GCP Cloud Run + V2X-Hub integration

---

## Table of Contents

1. [Documentation Management](#1-documentation-management)
2. [Configuration Management](#2-configuration-management)
3. [Project Structure](#3-project-structure)
4. [Development Workflow](#4-development-workflow)
5. [OVIN Application Preparation](#5-ovin-application-preparation)
6. [Pilot Deployment Strategy](#6-pilot-deployment-strategy)
7. [Maintenance & Evolution](#7-maintenance--evolution)

---

## 1. Documentation Management

### 1.1 Four-Tier Documentation Hierarchy

#### Tier 0: AI Agent Instructions
**Location**: `.claude/`
**Max Files**: 2-3
**Expiration**: Never (update in place)

**Purpose**: Instructions for Claude Code and other AI development agents

**Required Files**:
- `CLAUDE.md` - QEW-specific development guidelines
- `MCP_CONTEXT.md` - Model Context Protocol rules (if needed)

**QEW-Specific Guidelines**:
```markdown
# .claude/CLAUDE.md

## Configuration Rules (CRITICAL)

**Port Configuration**:
- Frontend (Vite): Port 8200 (NEVER use 3000 - conflicts)
- See: /Users/adbalabs/config/universal_port_config.md
- All port changes must update universal config

## QEW Project Standards

**Geographic Accuracy**:
- ALWAYS use production coordinates from qewData.js
- Real interchange locations, not interpolated
- Update qewData.js, never hardcode coordinates

**Data Sources**:
- MTO COMPASS cameras (qew_cameras_hamilton_mississauga.json)
- OSRM car routes (qewRoutes.js)
- Real camera images (public/camera_images/)

**Component Patterns**:
- Reusable components in src/components/
- Utilities in src/utils/
- Data in src/data/
```

---

#### Tier 1: Essential Project Documentation
**Location**: `/` (repository root)
**Max Files**: ≤8
**Expiration**: Never (update in place)

**Current QEW Files**:
1. `README.md` - Project overview, live repository link
2. `DOCUMENTATION_INDEX.md` - Master index (create if needed)
3. `.gitignore` - Git ignore rules
4. `LICENSE` - Software license (proprietary ADBA Labs)

**Optional (add if needed)**:
5. `QUICK_START.md` - Fast 5-minute setup
6. `CONTRIBUTING.md` - Contribution guidelines
7. `SECURITY.md` - Security policy
8. `CHANGELOG.md` - Version history

---

#### Tier 2: Domain Documentation
**Location**: `docs/`
**Max Files**: ≤30
**Expiration**: Review every 90 days

**Current QEW Structure**:
```
docs/
├── adba-labs/              # ADBA Labs framework docs
│   └── QEW_ORGANIZATIONAL_FRAMEWORK.md (this file)
├── ARCHITECTURE.md         # Technical architecture
├── DEMO_SCRIPT.md          # Hackathon demo guide
└── MVP_WORKFLOW.md         # Complete MVP roadmap with Mermaid diagrams
```

**Recommended Additions**:
```
docs/
├── adba-labs/
├── architecture/
│   └── V2X_INTEGRATION.md  # V2X-Hub RSU integration
├── api/
│   └── CLAUDE_VISION_API.md  # Claude Vision implementation
├── operations/
│   ├── STARTUP_PROCEDURES.md
│   └── DEPLOYMENT_GUIDE.md
├── ovin/
│   ├── APPLICATION_CHECKLIST.md
│   ├── PILOT_REQUIREMENTS.md
│   └── COMPLIANCE.md  # FIPPA, MTO BOOK 7
└── sprints/
    ├── Sprint1/
    └── Sprint2/
```

---

#### Tier 3: Temporary/Sprint Documentation
**Location**: `/` (root, temporary) or `docs/sprints/SprintN/`
**Max Files**: ≤10 active at once
**Expiration**: Archive after 2 weeks

**Naming Convention**: `TYPE_YYYYMMDD_description.md`

**Examples**:
- `SPRINT_20251117_camera_integration.md`
- `SESSION_20251118_v2x_alerts.md`
- `ANALYSIS_20251120_risk_scoring.md`

**Lifecycle**:
1. **Create**: With date in filename
2. **Active**: During sprint or session
3. **Archive**: Move to `archive/docs-deprecated-YYYYMMDD/` after completion
4. **Never Delete**: Use `git mv` to preserve history

---

#### Tier 4: Archived Documentation
**Location**: `archive/docs-deprecated-YYYYMMDD/`
**Expiration**: Never (preserve git history)

**Purpose**: Historical documentation for reference

**Archive when**:
- Sprint completed (2 weeks after sprint end)
- Feature superseded
- Document replaced by newer version

---

### 1.2 Documentation Lifecycle Rules

#### Golden Rules

1. **NEVER DELETE DOCUMENTATION** - Always use `git mv` to archive
2. **Update README first** - README is the project front door
3. **Link everything** - Use relative links in markdown
4. **Date temporary docs** - Always include YYYYMMDD in temporary filenames

#### Decision Tree

```
New Documentation Needed?
│
├─ Is this for OVIN application?
│  ├─ Yes → docs/ovin/
│  └─ No → Continue
│
├─ Is this code-required or planning-required?
│  ├─ Code-Required → docs/ (Tier 2)
│  └─ Planning-Required → root with date (Tier 3)
│
├─ What's the lifespan?
│  ├─ Permanent → Tier 1 or 2
│  ├─ Sprint → Tier 3 (2-week expiration)
│  └─ Session → Tier 3 (1-week expiration)
│
└─ Could this be a code comment or README section?
   ├─ Yes → Use that instead
   └─ No → Create new doc in appropriate tier
```

---

## 2. Configuration Management

### 2.1 Port Configuration (Critical)

**QEW Project Ports**:
- **Frontend (Vite)**: 8200 ✅ ACTIVE
- **Future Backend**: 8201 (reserved)
- **Future Services**: 8202-8209 (reserved for QEW expansion)

**Universal Config Integration**:

All QEW port changes MUST update:
```
/Users/adbalabs/config/universal_port_config.md
```

**vite.config.js Pattern**:
```javascript
// ✅ CORRECT - Port 8200 per universal_port_config.md
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8200,  // QEW standard port
    open: true
  }
})

// ❌ WRONG - Never use 3000 (conflicts with React/Next.js)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000  // DON'T DO THIS
  }
})
```

**Verification**:
```bash
# Check port in use
lsof -i :8200

# Should show:
# COMMAND   PID     USER
# node      12345   adbalabs
```

---

### 2.2 Environment Configuration

**Development**: `.env` (gitignored)
**Production**: Cloud Run environment variables
**Example**: `.env.example` (committed to git)

**QEW Environment Variables**:
```bash
# .env.example

# ─────────────────────────────────────────────────────────
# Service Ports
# ─────────────────────────────────────────────────────────
VITE_PORT=8200
VITE_API_PORT=8201  # Future backend

# ─────────────────────────────────────────────────────────
# Claude API (for Vision analysis)
# ─────────────────────────────────────────────────────────
CLAUDE_API_KEY=your-anthropic-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20250219

# ─────────────────────────────────────────────────────────
# Google Cloud
# ─────────────────────────────────────────────────────────
GOOGLE_CLOUD_PROJECT=qew-innovation-corridor
GOOGLE_API_KEY=your-gcp-api-key-here

# ─────────────────────────────────────────────────────────
# MTO COMPASS Integration (Future)
# ─────────────────────────────────────────────────────────
MTO_COMPASS_API_URL=https://511on.ca/api/v1
MTO_COMPASS_API_KEY=your-mto-api-key-here

# ─────────────────────────────────────────────────────────
# V2X-Hub RSU (Future Pilot)
# ─────────────────────────────────────────────────────────
V2X_HUB_HOST=localhost
V2X_HUB_PORT=8080
V2X_RSU_ENABLED=false

# ─────────────────────────────────────────────────────────
# Feature Flags
# ─────────────────────────────────────────────────────────
ENABLE_REAL_CAMERA_FEEDS=false
ENABLE_V2X_ALERTS=false
ENABLE_AI_ANALYSIS=true
```

---

### 2.3 Data Source Configuration

**Geographic Data** (src/data/qewData.js):
```javascript
// ✅ CORRECT - Production coordinates from real interchanges
export const COMPASS_CAMERAS = [
  { id: 'CAM_QEW_403', name: 'QEW @ Highway 403',
    lat: 43.3300, lon: -79.8000, status: 'active' },
  { id: 'CAM_QEW_GUELPH', name: 'QEW @ Guelph Line',
    lat: 43.3400, lon: -79.7900, status: 'active' },
  // ... 13 total cameras at real locations
];

// ❌ WRONG - Interpolated or mock coordinates
export const COMPASS_CAMERAS = [
  { id: 'CAM_1', lat: 43.4848 + Math.random(), lon: -79.5975 }
];
```

**Route Data** (src/data/qewRoutes.js):
- **qewPathWestbound**: 364 waypoints (Hamilton → Toronto)
- **qewPathEastbound**: 316 waypoints (Toronto → Hamilton)
- Source: OSRM routing service (OpenStreetMap)

---

## 3. Project Structure

### 3.1 Current Directory Structure

```
QEW-Innovation-Corridor/
├── .claude/                          # Tier 0: AI instructions
│   └── CLAUDE.md                     # (Create if needed)
│
├── README.md                         # Tier 1: Essential docs
├── LICENSE
├── .gitignore
├── vite.config.js                    # Vite config (port 8200)
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── index.html
│
├── docs/                             # Tier 2: Domain docs
│   ├── adba-labs/
│   │   └── QEW_ORGANIZATIONAL_FRAMEWORK.md
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md
│   └── MVP_WORKFLOW.md
│
├── src/                              # Application source
│   ├── App.jsx                       # Main Digital Twin Dashboard
│   ├── components/
│   │   └── WorkZoneAnalysisPanel.jsx
│   ├── data/
│   │   ├── qewData.js                # QEW corridor data (13 cameras)
│   │   └── qewRoutes.js              # OSRM car routes (both directions)
│   └── utils/
│       └── riskUtils.js              # Risk assessment utilities
│
├── artifacts/                        # Original prototype artifacts
│   └── work-zone-safety-analyzer.jsx
│
├── public/                           # Static assets
│   ├── camera_images/                # Real COMPASS camera images
│   └── camera_scraper/               # Camera database exports
│
├── camera_scraper/                   # Python camera scraper tools
├── ai_camera_direction/              # AI camera direction analyzer
│
└── archive/                          # Tier 4: Archived docs (future)
```

---

### 3.2 Recommended Additions

**For OVIN Application Phase**:
```
QEW-Innovation-Corridor/
├── .env.example                      # Environment variables template
├── QUICK_START.md                    # 5-minute setup guide
├── docs/
│   ├── ovin/
│   │   ├── APPLICATION_CHECKLIST.md
│   │   ├── PILOT_REQUIREMENTS.md
│   │   └── COMPLIANCE.md
│   └── operations/
│       ├── STARTUP_PROCEDURES.md
│       └── DEPLOYMENT_GUIDE.md
```

**For Production Phase**:
```
├── backend/                          # Future backend service
│   ├── src/
│   │   ├── core/
│   │   │   └── config.py             # Configuration management
│   │   ├── api/
│   │   ├── services/
│   │   └── integrations/
│   └── requirements.txt
├── tests/                            # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── deployment/
    ├── Dockerfile
    ├── cloudbuild.yaml
    └── terraform/
```

---

## 4. Development Workflow

### 4.1 Daily Development Cycle

**Morning Sign-On** (Future - CLI tool):
```bash
# Check system health
npm run dev  # Should start on port 8200

# Verify in browser
open http://localhost:8200

# Check git status
git status
```

**Development**:
1. Create feature branch: `git checkout -b feature/issue-number-description`
2. Make changes
3. Test locally on port 8200
4. Commit with descriptive message
5. Push to GitHub

**Evening Sign-Off**:
```bash
# Commit day's work
git add .
git commit -m "feat: description of work

Details of what was accomplished today

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin <branch-name>
```

---

### 4.2 Git Workflow

#### Branch Naming

```
<type>/<issue-number>-<short-description>

Examples:
feature/23-v2x-alert-generation
fix/45-camera-image-loading
docs/67-ovin-application-guide
refactor/89-risk-utilities
```

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Testing
- `chore` - Maintenance, dependencies
- `style` - UI/styling changes

**Scopes** (QEW-specific):
- `map` - Map visualization
- `cameras` - COMPASS camera integration
- `work-zones` - Work zone analysis
- `v2x` - V2X alert generation
- `risk` - Risk assessment
- `config` - Configuration
- `docs` - Documentation

**Examples**:
```
feat(v2x): Add RSU alert message generation

Implemented generateV2XAlert() utility that:
- Converts risk scores to SAE J2735 priority levels
- Generates speed reduction recommendations
- Formats alerts for V2X-Hub broadcast

Issue: #23

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
fix(cameras): Resolve camera image loading paths

Fixed issue where camera images failed to load in production.
Changed from relative to absolute paths using import.meta.env.BASE_URL.

Fixes #45

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 5. OVIN Application Preparation

### 5.1 OVIN Program Requirements

**Key Dates**:
- Application Deadline: TBD (check OVIN website)
- Pilot Start: 6 months after approval
- Pilot Duration: 12 months
- Funding: Up to $150K

**Deliverables Required**:
1. **Technical Demonstration** - Working prototype ✅
2. **Business Plan** - Go-to-market strategy
3. **Technical Architecture** - System design ✅
4. **Compliance Documentation** - FIPPA, MTO BOOK 7
5. **Test Plan** - 40km QEW testbed validation
6. **Budget** - Detailed cost breakdown

---

### 5.2 Application Checklist

**Create**: `docs/ovin/APPLICATION_CHECKLIST.md`

```markdown
# OVIN Application Checklist

## Technical Demonstration
- [x] Hackathon prototype complete
- [x] Interactive artifact (work zone analyzer)
- [x] Real COMPASS camera integration
- [ ] Claude Vision API live integration
- [ ] V2X alert generation demo
- [ ] Performance metrics collection

## Business Documentation
- [ ] Company profile (ADBA Labs)
- [ ] Team qualifications
- [ ] Market analysis
- [ ] Revenue projections
- [ ] Commercialization plan

## Technical Documentation
- [x] System architecture (ARCHITECTURE.md)
- [x] MVP workflow (MVP_WORKFLOW.md)
- [ ] V2X integration design
- [ ] Scalability analysis
- [ ] Security assessment

## Compliance
- [ ] FIPPA compliance plan (no PII collection)
- [ ] MTO BOOK 7 compliance checking
- [ ] Privacy impact assessment
- [ ] Data retention policy

## Testing & Validation
- [ ] Test plan for 40km corridor
- [ ] Success metrics definition
- [ ] Performance benchmarks
- [ ] Safety validation protocol

## Budget & Timeline
- [ ] Detailed budget breakdown ($150K)
- [ ] 6-month pilot timeline
- [ ] Resource allocation plan
- [ ] Risk mitigation strategy
```

---

### 5.3 Compliance Documentation

**FIPPA Compliance** (Freedom of Information and Protection of Privacy Act):

**Create**: `docs/ovin/FIPPA_COMPLIANCE.md`

Key Points:
- **No PII Collection**: System analyzes traffic, not individuals
- **Anonymized Data**: Vehicle tracking uses random IDs, no license plates
- **Data Minimization**: Only collect necessary data (coordinates, speed, heading)
- **Retention Policy**: 24-hour rolling window, then anonymize
- **Public Disclosure**: All data sources publicly available (MTO COMPASS)

**MTO BOOK 7 Compliance** (Highway Work Zone Safety):

**Create**: `docs/ovin/MTO_BOOK_7_COMPLIANCE.md`

Automated Checks:
- Worker proximity to active lanes (<2m = high risk)
- Barrier configuration (single vs double)
- Advance warning signage distance
- Speed reduction recommendations
- Equipment sight line obstruction

---

## 6. Pilot Deployment Strategy

### 6.1 Deployment Phases

**Phase 1: Local Development** ✅ CURRENT
- Local Vite dev server (port 8200)
- Mock data and simulations
- Manual camera scraping

**Phase 2: Cloud Deployment** (Month 1-2)
- Deploy frontend to Vercel/Netlify
- Set up GCP Cloud Run backend
- Integrate Claude Vision API
- Connect to MTO COMPASS feeds

**Phase 3: V2X Integration** (Month 3-4)
- Deploy V2X-Hub on QEW RSUs
- Test RSU alert broadcasts
- Validate SAE J2735 message format
- Performance testing

**Phase 4: Pilot Launch** (Month 5-6)
- 40km QEW corridor activation
- Real-time monitoring
- Data collection for OVIN reporting
- Iterative improvements

---

### 6.2 GCP Cloud Run Deployment

**Architecture**:
```
Internet
  ↓
Cloud Load Balancer
  ↓
Cloud Run Service (Frontend) - Port 8080
  ↓
Cloud Run Service (Backend) - Port 8000
  ↓
├─ Claude API (Vision analysis)
├─ MTO COMPASS API (camera feeds)
├─ Firestore (data storage)
└─ V2X-Hub (RSU integration)
```

**Deployment Script** (Future):
```bash
#!/bin/bash
# deploy-qew-frontend.sh

# Build production frontend
npm run build

# Deploy to Cloud Run
gcloud run deploy qew-digital-twin \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10
```

---

### 6.3 Monitoring & Analytics

**Key Metrics**:
- **System Health**: Uptime, latency, error rates
- **Work Zone Detection**: Detection accuracy, false positives
- **Risk Scoring**: Score distribution, high-risk alerts
- **V2X Performance**: Alert delivery time, RSU coverage
- **Camera Availability**: COMPASS feed uptime, image quality

**Tools**:
- **Google Cloud Monitoring**: Infrastructure metrics
- **Custom Dashboards**: Work zone analytics
- **Logging**: Cloud Logging for debugging
- **Alerts**: PagerDuty/email for critical issues

---

## 7. Maintenance & Evolution

### 7.1 Monthly Documentation Review

**Schedule**: First Monday of each month

**Process**:
1. Review all Tier 3 docs (temporary/sprint)
2. Archive completed sprints (2 weeks old)
3. Update README if project goals changed
4. Check DOCUMENTATION_INDEX.md accuracy
5. Update MVP_WORKFLOW.md with progress

**Archive Command**:
```bash
# Archive old sprint docs
git mv SPRINT_20251117_camera_integration.md \
      archive/sprints-deprecated-$(date +%Y%m%d)/

# Commit archival
git commit -m "docs: Archive Sprint 1 documentation (completed 2025-11-30)"
```

---

### 7.2 Quarterly Framework Review

**Schedule**: End of each quarter (March, June, September, December)

**QEW-Specific Checklist**:
- [ ] Documentation ≤30 active files
- [ ] Port 8200 compliance (no hardcoded 3000)
- [ ] Geographic data accuracy (real coordinates)
- [ ] Camera integration working
- [ ] OVIN application progress on track
- [ ] GitHub repository public and up-to-date
- [ ] README reflects current project state

---

### 7.3 Framework Evolution

**When to Update**:
- Move from hackathon to production
- Add backend service (port 8201)
- Integrate new data sources
- Team size changes
- New OVIN requirements

**How to Evolve**:
1. Create GitHub issue proposing change
2. Update this framework document
3. Update implementation (code, config, docs)
4. Document in commit message
5. Update README if user-visible

---

## Appendix A: Quick Reference

### Essential Commands

```bash
# Development
npm run dev                    # Start dev server (port 8200)
npm run build                  # Build for production
npm run preview                # Preview production build

# Git workflow
git status                     # Check current changes
git add .                      # Stage all changes
git commit -m "type: message"  # Commit with message
git push origin <branch>       # Push to GitHub

# Port management
lsof -i :8200                  # Check what's using port 8200
```

### Configuration Checklist

Before committing:
- [ ] Port 8200 in vite.config.js
- [ ] Universal config updated if port changed
- [ ] No hardcoded coordinates (use qewData.js)
- [ ] No API keys committed (.env in .gitignore)
- [ ] Images in public/ directory
- [ ] Routes use qewRoutes.js data

### File Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Permanent docs | `SCREAMING_SNAKE_CASE.md` | `ARCHITECTURE.md` |
| Temporary docs | `TYPE_YYYYMMDD_description.md` | `SPRINT_20251117_cameras.md` |
| Components | `PascalCase.jsx` | `WorkZoneAnalysisPanel.jsx` |
| Utilities | `camelCase.js` | `riskUtils.js` |
| Data | `camelCase.js` | `qewData.js` |

---

## Appendix B: OVIN Resources

### Official Links
- **OVIN Program**: https://www.ovinhub.ca/
- **QEW Innovation Corridor**: https://www.ovinhub.ca/qew-innovation-corridor/
- **MTO COMPASS**: http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml
- **V2X-Hub (USDOT)**: https://github.com/usdot-fhwa-OPS/V2X-Hub
- **SAE J2735**: https://www.sae.org/standards/content/j2735_202309/

### Contact
- **OVIN Program Manager**: David Harris-Koblin (dharris-koblin@oc.innovation.ca)
- **ADBA Labs**: adbalabs0101@gmail.com
- **GitHub**: https://github.com/adbadev1/QEW-Innovation-Corridor

---

## Appendix C: Related Documents

### Internal ADBA Labs
- **SaaS Framework**: `/Users/adbalabs/future_city_hackathon/docs/adba-labs/SAAS_ORGANIZATIONAL_FRAMEWORK.md`
- **Universal Port Config**: `/Users/adbalabs/config/universal_port_config.md`

### QEW Project Docs
- **README**: [Project Overview](../../README.md)
- **Architecture**: [Technical Architecture](../ARCHITECTURE.md)
- **Demo Script**: [Hackathon Demo Guide](../DEMO_SCRIPT.md)
- **MVP Workflow**: [Complete Roadmap](../MVP_WORKFLOW.md)

---

**Document Status**: ✅ Complete
**Version**: 1.0
**Last Updated**: 2025-11-17
**Maintained By**: ADBA Labs - QEW Project Team

**Next Steps**:
1. ✅ Hackathon prototype complete
2. Create `.claude/CLAUDE.md` with QEW-specific guidelines
3. Create `DOCUMENTATION_INDEX.md` master index
4. Create `.env.example` environment template
5. Prepare OVIN application documentation (docs/ovin/)
6. Monthly documentation review (archive old sprints)

---

**Questions?** Create an issue in the GitHub repository or contact ADBA Labs.
