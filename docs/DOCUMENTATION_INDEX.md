# QEW Innovation Corridor - Documentation Index

**Last Updated:** 2025-11-20
**Total Active Docs:** 14 (Tier 1: 1, Tier 2: 13)
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
**Current: 1 file** | **Target: ≤8 files** | **Status: ✅ Within target**

Core documentation that must be read before any work.

| File | Description | Purpose | Last Modified |
|------|-------------|---------|---------------|
| [README.md](../README.md) | Project overview, tech stack, demo script | First point of contact | 2025-11-17 |

**Reorganized (2025-11-20):**
- Moved all .md files to organized subdirectories in `docs/`
- Created new subdirectories: infrastructure/, development/, reports/, status/, tools/

---

### Tier 2: Domain Documentation (docs/ ≤30 files)
**Current: 13 files** | **Target: ≤30 files** | **Status: ✅ Well within target**

Organized by subdirectory and topic.

#### 🏗️ Infrastructure & GCP (docs/infrastructure/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/infrastructure/GCP_AI_INTEGRATION_COMPLETE.md](infrastructure/GCP_AI_INTEGRATION_COMPLETE.md) | GCP + Gemini AI integration summary | Developers | 2025-11-18 |
| [docs/infrastructure/GCP_SETUP_COMPLETE.md](infrastructure/GCP_SETUP_COMPLETE.md) | GCP bucket setup and configuration | DevOps | 2025-11-19 |
| [docs/infrastructure/GCP_PROJECT_SETUP.md](infrastructure/GCP_PROJECT_SETUP.md) | Complete GCP project setup guide | DevOps | 2025-11-20 |
| [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md) | **NEW:** GCP cost analysis for 50 images/hr 24/7 | Finance, Product | 2025-11-20 |

#### 💻 Development & Implementation (docs/development/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/development/IMPLEMENTATION_GUIDE.md](development/IMPLEMENTATION_GUIDE.md) | Camera collection & AI analysis implementation | Developers | 2025-11-18 |
| [docs/development/INTEGRATION_COMPLETE.md](development/INTEGRATION_COMPLETE.md) | Integration milestone documentation | Developers | 2025-11-18 |
| [docs/development/REFACTORING_STATUS.md](development/REFACTORING_STATUS.md) | Full-stack refactor status (90% complete) | Developers | 2025-11-20 |
| [docs/development/TEST_REPORT.md](development/TEST_REPORT.md) | Full-stack integration test results | QA, Developers | 2025-11-20 |

#### 📊 Reports & Diagnostics (docs/reports/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/reports/CAMERA_465_468_DIAGNOSTIC_REPORT.md](reports/CAMERA_465_468_DIAGNOSTIC_REPORT.md) | Camera 465/468 work zone detection diagnostics | Developers, QA | 2025-11-20 |
| [docs/reports/REAL_DATA_MIGRATION_SUMMARY.md](reports/REAL_DATA_MIGRATION_SUMMARY.md) | Mock data removal and real data migration | Developers | 2025-11-18 |

#### 📈 Project Status (docs/status/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md) | Current project status, metrics, critical gaps, action plan | All stakeholders | 2025-11-17 |
| [docs/status/SAAS_CHALLENGE_SUMMARY.md](status/SAAS_CHALLENGE_SUMMARY.md) | 7 critical challenges for SaaS transition | Product, Developers | 2025-11-17 |

#### 🔧 Development Tools (docs/tools/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/tools/WORKTREE_GUIDE.md](tools/WORKTREE_GUIDE.md) | Git worktree setup for parallel Claude Code sessions | Developers | 2025-11-18 |
| [docs/tools/WORKTREE_QUICKSTART.md](tools/WORKTREE_QUICKSTART.md) | Quick reference for worktree commands | Developers | 2025-11-18 |

#### 🏛️ Architecture & Technical (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture, component diagrams, data flow | Developers | 2025-11-15 |
| [docs/MAP_IMPLEMENTATION.md](MAP_IMPLEMENTATION.md) | Leaflet map implementation details | Frontend devs | 2025-11-15 |
| [docs/COREY_ACCESS_GUIDE.md](COREY_ACCESS_GUIDE.md) | Guide for Corey's repository access | Collaborators | 2025-11-20 |
| [docs/PRODUCTION_FEATURES.md](PRODUCTION_FEATURES.md) | Production feature specifications | Product | 2025-11-20 |
| [docs/V2X_OBU_INTEGRATION.md](V2X_OBU_INTEGRATION.md) | V2X On-Board Unit integration guide | Developers | 2025-11-20 |
| [docs/VRSU_INTEGRATION.md](VRSU_INTEGRATION.md) | V2X Roadside Unit integration guide | Developers | 2025-11-20 |

#### 📦 Product & Planning (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/MVP_WORKFLOW.md](MVP_WORKFLOW.md) | Complete 6-month roadmap with Mermaid diagrams | Product, stakeholders | 2025-11-15 |

#### 🎓 Onboarding (docs/onboarding/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md) | 5-minute setup guide for new developers | New developers | 2025-11-17 |
| [docs/onboarding/FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md) | Complete full-stack developer setup guide (1000+ lines) | New developers | 2025-11-20 |

#### 📅 Sprint Planning (docs/sprints/Sprint1/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md) | Sprint 1 plan (Nov 17-30): OVIN demo prep, 16 story points | Team, scrum | 2025-11-17 |

#### 🏢 Framework & Standards (docs/adba-labs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md) | ADBA Labs organizational framework adapted for QEW | All team members | 2025-11-17 |

#### 📝 Miscellaneous (docs/)

| File | Description | Audience | Last Modified |
|------|-------------|----------|---------------|
| [docs/DOCUMENTATION_UPDATE_SUMMARY.md](DOCUMENTATION_UPDATE_SUMMARY.md) | Documentation maintenance history | Documentation maintainers | 2025-11-15 |

---

### Tier 3: Sprint & Temporary Documentation (docs/sprints/, docs/temp/)
**Current: 1 file (Sprint1/)** | **Status: Active sprint documentation**

Temporary files created during sprints. Moved to Tier 4 (archive) after sprint completion.

| File | Description | Sprint | Status |
|------|-------------|--------|--------|
| [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md) | Sprint 1 backlog, daily standup notes | Sprint 1 (Nov 17-30) | 🟢 Active |

**Note:** Sprint 1 docs will be archived to `archive/sprints/Sprint1/` after Nov 30, 2025.

---

### Tier 4: Archived Documentation (archive/)
**Current: 11 files** | **Archived: 2025-11-17**

Historical documentation preserved for reference.

| Archive Directory | Contents | Archived Date | Reason |
|-------------------|----------|---------------|--------|
| [archive/docs-deprecated-20251117/](../archive/docs-deprecated-20251117/) | 11 update summary files | 2025-11-17 | Cleanup for OVIN application (reduce root clutter) |

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
1. [README.md](../README.md) - Project overview
2. [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md) - 5-minute setup
3. [docs/onboarding/FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md) - Complete setup guide
4. [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md) - Current status
5. [.claude/CLAUDE.md](../.claude/CLAUDE.md) - Development guidelines (if using AI tools)

### 🏗️ Architecture & Development
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [docs/MAP_IMPLEMENTATION.md](MAP_IMPLEMENTATION.md) - Map implementation
- [docs/development/REFACTORING_STATUS.md](development/REFACTORING_STATUS.md) - Refactor status (90% complete)
- [.claude/CLAUDE.md](../.claude/CLAUDE.md) - AI development guidelines
- [docs/status/SAAS_CHALLENGE_SUMMARY.md](status/SAAS_CHALLENGE_SUMMARY.md) - Technical challenges

### 📊 Product & Planning
- [docs/MVP_WORKFLOW.md](MVP_WORKFLOW.md) - 6-month roadmap
- [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md) - Current sprint

### 💰 Infrastructure & Cost Analysis
- [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md) - **NEW:** GCP cost projections ($35-125/month)
- [docs/infrastructure/GCP_PROJECT_SETUP.md](infrastructure/GCP_PROJECT_SETUP.md) - GCP setup
- [docs/infrastructure/GCP_AI_INTEGRATION_COMPLETE.md](infrastructure/GCP_AI_INTEGRATION_COMPLETE.md) - AI integration

### 🎯 OVIN Application
- [README.md](../README.md) - Project overview for stakeholders
- [docs/MVP_WORKFLOW.md](MVP_WORKFLOW.md) - Complete roadmap
- [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md) - Current metrics
- [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md) - Budget analysis (<1% of $150K grant)
- **Future:** `docs/ovin/` (Issue #5, Sprint 1)

### 📈 Status & Metrics
- [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md) - Project status, gaps, action plan
- [docs/development/REFACTORING_STATUS.md](development/REFACTORING_STATUS.md) - Refactor progress (90%)
- [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md) - Sprint progress

### 🔧 Developer Tools
- [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md) - 5-minute setup
- [docs/onboarding/FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md) - Complete setup (1000+ lines)
- [docs/tools/WORKTREE_GUIDE.md](tools/WORKTREE_GUIDE.md) - Git worktree for parallel sessions
- [.claude/CLAUDE.md](../.claude/CLAUDE.md) - AI development guidelines
- [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md) - Project standards

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
1. [README.md](../README.md)
2. [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md)
3. [docs/onboarding/FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md)
4. [docs/ARCHITECTURE.md](ARCHITECTURE.md)
5. [.claude/CLAUDE.md](../.claude/CLAUDE.md)

**Product Manager:**
1. [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md)
2. [docs/MVP_WORKFLOW.md](MVP_WORKFLOW.md)
3. [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md)

**Finance/Budget:**
1. [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md) - Complete cost breakdown
2. [README.md](../README.md) - Budget context

**OVIN Stakeholder:**
1. [README.md](../README.md)
2. [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md)
3. [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md)

**AI Development Agent:**
1. [.claude/CLAUDE.md](../.claude/CLAUDE.md) ← **START HERE**
2. [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md)
3. [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md)
4. [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md)

### By Topic

**Setup & Installation:**
- [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md) - 5-minute setup
- [docs/onboarding/FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md) - Full setup guide

**Current Work:**
- [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md)
- [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md)
- [docs/development/REFACTORING_STATUS.md](development/REFACTORING_STATUS.md)

**Technical Details:**
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/MAP_IMPLEMENTATION.md](MAP_IMPLEMENTATION.md)
- [docs/status/SAAS_CHALLENGE_SUMMARY.md](status/SAAS_CHALLENGE_SUMMARY.md)

**Cost & Budget:**
- [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md) - **NEW:** Comprehensive cost analysis

**Project Planning:**
- [docs/MVP_WORKFLOW.md](MVP_WORKFLOW.md)
- [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md)

**OVIN Application:**
- [README.md](../README.md)
- **Future:** `docs/ovin/` directory (Issue #5)

---

## 📊 Documentation Metrics

### Current State (2025-11-20)
```
Tier 0 (AI Instructions):     1 file
Tier 1 (Essential):            1 file   (Target: ≤8)  ✅
Tier 2 (Domain):              13 files  (Target: ≤30) ✅
Tier 3 (Sprint/Temp):          1 file   (Active)      ✅
Tier 4 (Archived):            11 files  (Historical)  📦
────────────────────────────────────────────────────
Total Active Documentation:   15 files
Total Archived:               11 files
```

### Recent Changes
- **2025-11-20:** 📁 **Major reorganization** - Created subdirectories in docs/
  - Created: `docs/infrastructure/`, `docs/development/`, `docs/reports/`, `docs/status/`, `docs/tools/`
  - Moved 12 .md files from root to organized subdirectories
  - Created `docs/GCP_COST_ANALYSIS.md` - Comprehensive cost analysis
- **2025-11-20:** Created FULLSTACK_SETUP.md (1000+ lines onboarding guide)
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
- **Weekly:** State of the Nation updates (docs/status/STATE_OF_THE_NATION.md)
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

- **Framework Questions:** See [docs/adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md](adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md)
- **Setup Questions:** See [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md) or [FULLSTACK_SETUP.md](onboarding/FULLSTACK_SETUP.md)
- **Project Questions:** See [docs/status/STATE_OF_THE_NATION.md](status/STATE_OF_THE_NATION.md)
- **Cost Questions:** See [docs/GCP_COST_ANALYSIS.md](GCP_COST_ANALYSIS.md)
- **OVIN Questions:** Contact David Harris-Koblin (dharris-koblin@oc.innovation.ca)

---

**This index is maintained according to QEW_ORGANIZATIONAL_FRAMEWORK.md Section 1.7**

Last Updated: 2025-11-20
Maintained By: ADBA Labs
Project: QEW Innovation Corridor - OVIN Pilot Application

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**
