# QEW Innovation Corridor - Documentation Index

**Last Updated:** 2025-11-17
**Total Active Docs:** 13 (Tier 1: 3, Tier 2: 10)
**Organization Standard:** Per `docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md`

---

## 📚 Documentation Tiers

### Tier 0: AI Agent Instructions (Hidden)
Critical system-level documentation for AI development agents.

| File | Description | Last Modified |
|------|-------------|---------------|
| [.claude/CLAUDE.md](.claude/CLAUDE.md) | AI development guidelines (port config, geographic accuracy, project context) | 2025-11-17 |

---

### Tier 1: Essential Documentation (Root ≤8 files)
**Current: 3 files** | **Target: ≤8 files** | **Status: ✅ Within target**

Core documentation that must be read before any work.

| File | Description | Purpose | Last Modified |
|------|-------------|---------|---------------|
| [README.md](README.md) | Project overview, tech stack, demo script | First point of contact | 2025-11-17 |
| [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md) | Current project status, metrics, critical gaps, action plan | Status snapshot | 2025-11-17 |
| [SAAS_CHALLENGE_SUMMARY.md](SAAS_CHALLENGE_SUMMARY.md) | 7 critical challenges for SaaS transition | Technical roadmap | 2025-11-17 |

**Archived from Root (Tier 3 → Tier 4):**
- 11 update summary files moved to `archive/docs-deprecated-20251117/` on 2025-11-17

---

### Tier 2: Domain Documentation (docs/ ≤30 files)
**Current: 10 files** | **Target: ≤30 files** | **Status: ✅ Well within target**

Organized by subdirectory and topic.

#### Architecture & Technical (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture, component diagrams, data flow | Developers | 2025-11-15 |
| [docs/MAP_IMPLEMENTATION.md](docs/MAP_IMPLEMENTATION.md) | Leaflet map implementation details | Frontend devs | 2025-11-15 |

#### Product & Planning (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md) | Complete 6-month roadmap with Mermaid diagrams | Product, stakeholders | 2025-11-15 |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | 3-minute presentation guide for OVIN demo | Sales, leadership | 2025-11-15 |

#### Onboarding (docs/onboarding/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md) | 5-minute setup guide for new developers | New developers | 2025-11-17 |

#### Sprint Planning (docs/sprints/Sprint1/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md) | Sprint 1 plan (Nov 17-30): OVIN demo prep, 16 story points | Team, scrum | 2025-11-17 |

#### Framework & Standards (docs/adba-labs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md) | ADBA Labs organizational framework adapted for QEW | All team members | 2025-11-17 |

#### Miscellaneous (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/DOCUMENTATION_UPDATE_SUMMARY.md](docs/DOCUMENTATION_UPDATE_SUMMARY.md) | Documentation maintenance history | Documentation maintainers | 2025-11-15 |

---

### Tier 3: Sprint & Temporary Documentation (docs/sprints/, docs/temp/)
**Current: 1 file (Sprint1/)** | **Status: Active sprint documentation**

Temporary files created during sprints. Moved to Tier 4 (archive) after sprint completion.

| File | Description | Sprint | Status |
|------|-------------|--------|--------|
| [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md) | Sprint 1 backlog, daily standup notes | Sprint 1 (Nov 17-30) | 🟢 Active |

**Note:** Sprint 1 docs will be archived to `archive/sprints/Sprint1/` after Nov 30, 2025.

---

### Tier 4: Archived Documentation (archive/)
**Current: 11 files** | **Archived: 2025-11-17**

Historical documentation preserved for reference.

| Archive Directory | Contents | Archived Date | Reason |
|-------------------|----------|---------------|--------|
| [archive/docs-deprecated-20251117/](archive/docs-deprecated-20251117/) | 11 update summary files | 2025-11-17 | Cleanup for OVIN application (reduce root clutter) |

**Archived Files:**
- AI_CAMERA_DIRECTION_UPDATED.md
- CAMERA_MAP_UPDATE_SUMMARY.md
- GEMINI_SUPPORT_ADDED.md
- IMAGE_FOLDER_STRUCTURE_UPDATED.md
- INFINITE_LOOP_FIX.md
- QEW_BLUE_LINE_UPDATED.md
- QEW_CAR_ROUTES_COMPLETE.md
- QEW_CORRIDOR_UPDATE_PHASE1.md
- RED_GREEN_DOTS_ADDED.md
- VEHICLE_DISAPPEARING_FIX.md
- VEHICLE_MOVEMENT_FIXED.md

---

## 🗂️ Documentation by Category

### 🚀 Quick Start
New to the project? Start here:
1. [README.md](README.md) - Project overview
2. [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md) - 5-minute setup
3. [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md) - Current status
4. [.claude/CLAUDE.md](.claude/CLAUDE.md) - Development guidelines (if using AI tools)

### 🏗️ Architecture & Development
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [docs/MAP_IMPLEMENTATION.md](docs/MAP_IMPLEMENTATION.md) - Map implementation
- [.claude/CLAUDE.md](.claude/CLAUDE.md) - AI development guidelines
- [SAAS_CHALLENGE_SUMMARY.md](SAAS_CHALLENGE_SUMMARY.md) - Technical challenges

### 📊 Product & Planning
- [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md) - 6-month roadmap
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - Presentation guide
- [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md) - Current sprint

### 🎯 OVIN Application
- [README.md](README.md) - Project overview for stakeholders
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - 3-minute pitch
- [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md) - Complete roadmap
- [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md) - Current metrics
- **Future:** `docs/ovin/` (Issue #5, Sprint 1)

### 📈 Status & Metrics
- [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md) - Project status, gaps, action plan
- [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md) - Sprint progress

### 🔧 Developer Tools
- [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md) - Setup guide
- [.claude/CLAUDE.md](.claude/CLAUDE.md) - AI development guidelines
- [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md) - Project standards

---

## 📁 Special Directories

### camera_scraper/
Python-based camera image collection system (separate documentation set).

| File | Description | Purpose |
|------|-------------|---------|
| camera_scraper/docs/README.md | Camera scraper overview | System documentation |
| camera_scraper/docs/EXECUTIVE_SUMMARY.md | High-level summary | Stakeholder communication |
| camera_scraper/docs/SETUP_GUIDE.md | Setup instructions | Developer onboarding |
| camera_scraper/docs/GUI_README.md | GUI tool documentation | Camera collection tool |
| camera_scraper/docs/IMPLEMENTATION_PLAN.md | Implementation roadmap | Development planning |

**Note:** Camera scraper docs are self-contained and not part of main project documentation hierarchy.

---

## 🔍 Finding Documentation

### By Role

**New Developer:**
1. [README.md](README.md)
2. [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md)
3. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. [.claude/CLAUDE.md](.claude/CLAUDE.md)

**Product Manager:**
1. [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md)
2. [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md)
3. [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md)

**OVIN Stakeholder:**
1. [README.md](README.md)
2. [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
3. [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md)

**AI Development Agent:**
1. [.claude/CLAUDE.md](.claude/CLAUDE.md) ← **START HERE**
2. [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md)
3. [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md)
4. [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md)

### By Topic

**Setup & Installation:**
- [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md)

**Current Work:**
- [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md)
- [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md)

**Technical Details:**
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/MAP_IMPLEMENTATION.md](docs/MAP_IMPLEMENTATION.md)
- [SAAS_CHALLENGE_SUMMARY.md](SAAS_CHALLENGE_SUMMARY.md)

**Project Planning:**
- [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md)
- [docs/sprints/Sprint1/SPRINT_PLAN.md](docs/sprints/Sprint1/SPRINT_PLAN.md)

**OVIN Application:**
- [README.md](README.md)
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- **Future:** `docs/ovin/` directory (Issue #5)

---

## 📊 Documentation Metrics

### Current State (2025-11-17)
```
Tier 0 (AI Instructions):     1 file
Tier 1 (Essential):            3 files  (Target: ≤8)  ✅
Tier 2 (Domain):              10 files  (Target: ≤30) ✅
Tier 3 (Sprint/Temp):          1 file   (Active)      ✅
Tier 4 (Archived):            11 files  (Historical)  📦
────────────────────────────────────────────────────
Total Active Documentation:   14 files
Total Archived:               11 files
```

### Recent Changes
- **2025-11-17:** Archived 11 update summary files (Tier 1 → Tier 4)
- **2025-11-17:** Created .claude/CLAUDE.md (Tier 0)
- **2025-11-17:** Created Sprint 1 plan (Tier 3)
- **2025-11-17:** Created QEW_ORGANIZATIONAL_FRAMEWORK.md (Tier 2)
- **2025-11-17:** Created STATE_OF_THE_NATION.md (Tier 1)
- **2025-11-17:** Created SAAS_CHALLENGE_SUMMARY.md (Tier 1)

---

## 🎯 Upcoming Documentation (Sprint 1)

### Planned (Issue #5: Create OVIN Documentation Structure)
```
docs/ovin/
├── APPLICATION_CHECKLIST.md      # OVIN application checklist
├── FIPPA_COMPLIANCE.md            # Ontario privacy compliance
├── MTO_BOOK_7_COMPLIANCE.md       # Work zone safety rules
├── PILOT_REQUIREMENTS.md          # 6-month pilot specs
└── BUDGET_BREAKDOWN.md            # $150K budget details
```

### Future Documentation Needs
- API documentation (when backend is built)
- User manual (for operators)
- Deployment guide (GCP Cloud Run)
- V2X integration guide (RSU configuration)
- Testing documentation (when tests are added)

---

## 🔄 Documentation Maintenance

### Update Schedule
- **Daily:** Sprint plan updates (docs/sprints/Sprint1/SPRINT_PLAN.md)
- **Weekly:** State of the Nation updates (STATE_OF_THE_NATION.md)
- **Monthly:** README.md updates (as features evolve)
- **Per Sprint:** Archive completed sprint docs (Tier 3 → Tier 4)

### Archive Process
1. Complete sprint → Move docs from `docs/sprints/SprintN/` to `archive/sprints/SprintN/`
2. Obsolete updates → Move from root to `archive/docs-deprecated-YYYYMMDD/`
3. Update this index after any archival

### Documentation Standards
- **Format:** Markdown (.md files only)
- **Naming:** UPPER_SNAKE_CASE.md (except root README.md)
- **Location:** Per tier guidelines in QEW_ORGANIZATIONAL_FRAMEWORK.md
- **Ownership:** All team members can update, Product Owner approves structure

---

## 📞 Documentation Questions?

- **Framework Questions:** See [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md)
- **Setup Questions:** See [docs/onboarding/QUICK_START.md](docs/onboarding/QUICK_START.md)
- **Project Questions:** See [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md)
- **OVIN Questions:** Contact David Harris-Koblin (dharris-koblin@oc.innovation.ca)

---

**This index is maintained according to QEW_ORGANIZATIONAL_FRAMEWORK.md Section 1.7**

Last Updated: 2025-11-17
Maintained By: ADBA Labs
Project: QEW Innovation Corridor - OVIN Pilot Application

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**
