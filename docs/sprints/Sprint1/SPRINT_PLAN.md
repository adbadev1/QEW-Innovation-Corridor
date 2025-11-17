# Sprint 1 Plan: OVIN Demo Preparation & Application

**Sprint Duration**: 2025-11-17 to 2025-11-30 (14 days)
**Sprint Goal**: Complete OVIN demo preparation and submit Client Intake Form

---

## 📊 Sprint Goals

### Primary Goals (P1 - Must Complete)
1. ✅ Complete hackathon demo preparation (all Tier 1 tasks)
2. ⏳ Submit OVIN Client Intake Form
3. ⏳ Create OVIN application documentation structure

### Secondary Goals (P2 - Should Complete)
1. ⏳ Prepare OVIN pitch deck
2. ⏳ Create onboarding documentation
3. ⏳ Archive expired documentation

### Stretch Goals (P3 - Nice to Have)
1. ⏳ Add Claude Vision API integration
2. ⏳ Deploy to GitHub Pages
3. ⏳ Record demo video

---

## 📋 Sprint Backlog (GitHub Issues)

### **Priority 1 (P1) - Critical for Demo** [Story Points: 4]

#### Issue #1: Complete Camera Images (8 missing)
**Label**: `P1`, `type:data`, `area:cameras`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Download missing 8 camera images to achieve 100% QEW coverage (46/46 cameras).

**Current**: 38/46 camera images (83%)
**Target**: 46/46 camera images (100%)

**Tasks**:
- [ ] Run camera scraper for missing 8 cameras
- [ ] Verify all 46 images in public/camera_images/
- [ ] Test dashboard loads all camera popups
- [ ] Commit new images to git

**Files**:
- camera_scraper/download_camera_images.py
- public/camera_images/

**Time Estimate**: 15 minutes actual work, 1 day buffer for testing
```

#### Issue #2: Archive Documentation (Tier 3 → Tier 4)
**Label**: `P1`, `type:docs`, `area:docs`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Archive 11 update summary files per QEW_ORGANIZATIONAL_FRAMEWORK.md guidelines.

**Current**: 12 .md files in root
**Target**: ≤8 .md files in root

**Tasks**:
- [ ] Create archive/docs-deprecated-20251117/
- [ ] Move 11 update summary files (*_UPDATED.md, *_SUMMARY.md, *_FIXED.md, *_ADDED.md, *_COMPLETE.md)
- [ ] Verify root doc count ≤8
- [ ] Update DOCUMENTATION_INDEX.md (create if needed)
- [ ] Commit with git mv to preserve history

**Files to Archive**:
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

**Time Estimate**: 10 minutes actual work, 1 day buffer
```

#### Issue #3: Create Environment Configuration Template
**Label**: `P1`, `type:config`, `area:devops`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Create .env.example to document all environment variables.

**Current**: No .env.example file
**Target**: Complete environment variable template

**Tasks**:
- [ ] Create .env.example with all config options
- [ ] Document Claude API key variable
- [ ] Document port configuration
- [ ] Document feature flags
- [ ] Add .env to .gitignore (if not already)
- [ ] Test that .env.example has correct format
- [ ] Commit .env.example

**Template Structure**:
```bash
# Service Ports
VITE_PORT=8200

# Claude API
VITE_CLAUDE_API_KEY=your-api-key-here

# Feature Flags
VITE_ENABLE_REAL_AI_ANALYSIS=false
```

**Time Estimate**: 5 minutes actual work, 1 day buffer
```

#### Issue #4: Deploy to GitHub Pages
**Label**: `P1`, `type:deployment`, `area:devops`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Deploy production build to GitHub Pages for public demo URL.

**Current**: Local dev server only (http://localhost:8200)
**Target**: Public URL (https://adbadev1.github.io/QEW-Innovation-Corridor/)

**Tasks**:
- [ ] Run npm run build (test production build)
- [ ] Fix any build errors
- [ ] Run npm run deploy
- [ ] Verify deployment at GitHub Pages URL
- [ ] Update README.md with live demo URL
- [ ] Test all features work on deployed version
- [ ] Commit README update

**Files**:
- package.json (gh-pages script)
- vite.config.js (base path)
- README.md (add live URL)

**Time Estimate**: 15 minutes actual work, 1 day buffer for troubleshooting
```

---

### **Priority 2 (P2) - OVIN Application** [Story Points: 8]

#### Issue #5: Create OVIN Documentation Structure
**Label**: `P2`, `type:docs`, `area:ovin`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Create docs/ovin/ directory with all application templates.

**Tasks**:
- [ ] mkdir -p docs/ovin
- [ ] Create APPLICATION_CHECKLIST.md
- [ ] Create FIPPA_COMPLIANCE.md
- [ ] Create MTO_BOOK_7_COMPLIANCE.md
- [ ] Create PILOT_REQUIREMENTS.md
- [ ] Create BUDGET_BREAKDOWN.md
- [ ] Add placeholder content to each file
- [ ] Commit all new docs

**Reference**: STATE_OF_THE_NATION.md Section 5.3 (Compliance Documentation)

**Time Estimate**: 1 hour actual work, 1 day buffer
```

#### Issue #6: Draft OVIN Client Intake Form
**Label**: `P2`, `type:docs`, `area:ovin`
**Story Points**: 2 (2 days)
**Assignee**: @adbadev1
**Description**:
```
Draft complete OVIN Client Intake Form for submission.

**Contact**: David Harris-Koblin (dharris-koblin@oc.innovation.ca)

**Tasks**:
- [ ] Download intake form template from OVIN website
- [ ] Fill out company information (ADBA Labs)
- [ ] Describe project (use README.md + ARCHITECTURE.md)
- [ ] Document technology readiness (TRL 7-9)
- [ ] Specify funding request ($150,000)
- [ ] Provide 6-month timeline
- [ ] Attach supporting documents (architecture, demo screenshots)
- [ ] Review for completeness
- [ ] Get internal approval
- [ ] Schedule submission

**Reference**: MVP_WORKFLOW.md Phase 1

**Time Estimate**: 2 hours drafting, 1 day review/approval
```

#### Issue #7: Prepare OVIN Pitch Deck
**Label**: `P2`, `type:docs`, `area:ovin`
**Story Points**: 3 (3 days)
**Assignee**: @adbadev1
**Description**:
```
Create 10-15 slide pitch deck for OVIN Steering Committee.

**Tasks**:
- [ ] Slide 1: Cover (logo, title)
- [ ] Slide 2: Problem statement (70 workers die annually)
- [ ] Slide 3: Solution overview (AI work zone safety)
- [ ] Slide 4: Live demo screenshot
- [ ] Slide 5: Technical architecture diagram
- [ ] Slide 6: COMPASS integration
- [ ] Slide 7: V2X communication
- [ ] Slide 8: MTO compliance (BOOK 7, FIPPA)
- [ ] Slide 9: Pilot plan (6 months, 40km)
- [ ] Slide 10: Budget breakdown ($150K)
- [ ] Slide 11: Team credentials (ADBA Labs)
- [ ] Slide 12: Market opportunity ($5M ARR Year 3)
- [ ] Slide 13: Competitive advantages
- [ ] Slide 14: Timeline (Gantt chart from MVP_WORKFLOW.md)
- [ ] Slide 15: Close (call to action)
- [ ] Export as PDF
- [ ] Practice presentation (3-5 minutes)

**Tools**: Google Slides or PowerPoint
**Reference**: DEMO_SCRIPT.md, STATE_OF_THE_NATION.md Section "Competitive Advantages"

**Time Estimate**: 3 hours design, 1 day review/practice
```

#### Issue #8: Create .claude/CLAUDE.md
**Label**: `P2`, `type:docs`, `area:architecture`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Create Tier 0 AI agent instructions per framework guidelines.

**Tasks**:
- [ ] mkdir -p .claude
- [ ] Create CLAUDE.md with QEW-specific development guidelines
- [ ] Document port configuration rules
- [ ] Document geographic accuracy standards
- [ ] Document data sources (qewData.js, qewRoutes.js)
- [ ] Document component patterns
- [ ] Document testing procedures
- [ ] Commit .claude/CLAUDE.md

**Reference**: QEW_ORGANIZATIONAL_FRAMEWORK.md Section 1.1 (Tier 0)

**Template**:
```markdown
# .claude/CLAUDE.md

## Configuration Rules (CRITICAL)
- Port: ALWAYS use 8200 (NEVER 3000)
- Update /Users/adbalabs/config/universal_port_config.md for changes

## Geographic Accuracy
- ALWAYS use production coordinates from qewData.js
- NEVER interpolate or mock coordinates
```

**Time Estimate**: 30 minutes actual work, 1 day buffer
```

#### Issue #9: Create DOCUMENTATION_INDEX.md
**Label**: `P2`, `type:docs`, `area:docs`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Create master index of all project documentation.

**Tasks**:
- [ ] List all Tier 1 docs (root .md files)
- [ ] List all Tier 2 docs (docs/ subdirectories)
- [ ] Organize by category (Architecture, API, Operations, OVIN, etc.)
- [ ] Add brief description for each doc
- [ ] Use relative links
- [ ] Add last updated date
- [ ] Commit DOCUMENTATION_INDEX.md

**Reference**: QEW_ORGANIZATIONAL_FRAMEWORK.md Section 1.7

**Format**:
```markdown
# Documentation Index

**Last Updated**: 2025-11-17
**Total Active Docs**: 30

## Essential (Tier 1)
- [README.md](README.md) - Project overview
- [STATE_OF_THE_NATION.md](STATE_OF_THE_NATION.md) - Current status

## Architecture (Tier 2)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
```

**Time Estimate**: 15 minutes actual work, 1 day buffer
```

---

### **Priority 3 (P3) - Enhanced Features** [Story Points: 4]

#### Issue #10: Add Claude Vision API Integration
**Label**: `P3`, `type:feature`, `area:ai`
**Story Points**: 2 (2 days)
**Assignee**: @adbadev1
**Description**:
```
Integrate live Claude Vision API for real-time work zone analysis.

**Current**: Simulated risk analysis data
**Target**: Live AI-powered analysis

**Tasks**:
- [ ] Install @anthropic-ai/sdk
- [ ] Create src/utils/claudeVision.js
- [ ] Implement analyzeWorkZone() function
- [ ] Add image-to-base64 conversion
- [ ] Structured JSON output (risk score, hazards, compliance, recommendations)
- [ ] Error handling and fallback to simulated data
- [ ] Add loading state UI
- [ ] Test with sample work zone images
- [ ] Commit implementation

**API Call**:
```javascript
const message = await anthropic.messages.create({
  model: 'claude-3-5-sonnet-20250219',
  max_tokens: 2000,
  messages: [{
    role: 'user',
    content: [
      { type: 'image', source: { type: 'base64', data: imageBase64 } },
      { type: 'text', text: 'Analyze work zone safety...' }
    ]
  }]
});
```

**Reference**: STATE_OF_THE_NATION.md Task 3.1

**Time Estimate**: 2 hours coding, 1 day testing
```

#### Issue #11: Add Image Upload UI
**Label**: `P3`, `type:feature`, `area:frontend`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Add image upload functionality for interactive demo.

**Current**: No upload capability
**Target**: Upload work zone photo → get AI analysis

**Tasks**:
- [ ] Add file input to WorkZoneAnalysisPanel.jsx
- [ ] Implement handleImageUpload() function
- [ ] Connect to Claude Vision API
- [ ] Show loading spinner during analysis
- [ ] Display results in existing UI
- [ ] Add error handling
- [ ] Test with various image formats
- [ ] Commit implementation

**UI Component**:
```jsx
<input
  type="file"
  accept="image/*"
  onChange={handleImageUpload}
  className="..."
/>
{uploading && <p>Analyzing with Claude AI...</p>}
```

**Reference**: STATE_OF_THE_NATION.md Task 3.2

**Time Estimate**: 1 hour coding, 1 day testing
```

#### Issue #12: Record Demo Video
**Label**: `P3`, `type:docs`, `area:marketing`
**Story Points**: 1 (1 day)
**Assignee**: @adbadev1
**Description**:
```
Record 3-minute demo video for OVIN application.

**Tasks**:
- [ ] Set up screen recording (OBS, QuickTime, or Loom)
- [ ] Practice demo script 3 times
- [ ] Record full 3-minute demo
- [ ] Edit video (trim, add intro/outro)
- [ ] Add captions/subtitles
- [ ] Export as MP4 (1080p)
- [ ] Upload to YouTube (unlisted)
- [ ] Add video link to README.md
- [ ] Share with OVIN program manager

**Script**: docs/DEMO_SCRIPT.md

**Time Estimate**: 30 minutes recording, 1 hour editing
```

---

## 📊 Sprint Metrics

**Total Story Points**: 16
**Velocity Target**: 12-16 points (realistic for 2 weeks)
**Bug Budget**: ≤2 P1 bugs
**Code Coverage**: Maintain current (no tests yet, but document testing plan)

---

## 📅 Daily Standup Notes

### Day 1: 2025-11-17 (Sprint Start)
**Completed**:
- ✅ Hackathon prototype complete
- ✅ STATE_OF_THE_NATION.md report generated
- ✅ QEW_ORGANIZATIONAL_FRAMEWORK.md created
- ✅ Sprint 1 planning started

**Today**:
- Create all GitHub issues for Sprint 1 tasks
- Set up docs/onboarding/ structure
- Set up docs/sprints/Sprint1/ structure

**Blockers**: None

---

### Day 2: 2025-11-18 (Planned)
**Plan**:
- Complete Issue #2 (Archive documentation)
- Complete Issue #3 (Create .env.example)
- Start Issue #1 (Complete camera images)

**Blockers**: TBD

---

### Day 3: 2025-11-19 (Planned)
**Plan**:
- Complete Issue #1 (Complete camera images)
- Complete Issue #4 (Deploy to GitHub Pages)
- Start Issue #5 (Create OVIN docs structure)

**Blockers**: TBD

---

## 🎯 Definition of Done

### For Each Issue:
- [ ] Code written and tested locally
- [ ] All tasks in issue description checked off
- [ ] Code committed with descriptive message
- [ ] Pushed to GitHub
- [ ] Issue closed in GitHub
- [ ] Sprint plan updated (this file)

### For Sprint Completion:
- [ ] All P1 issues completed
- [ ] At least 80% of P2 issues completed
- [ ] Demo ready for presentation
- [ ] OVIN Client Intake Form submitted
- [ ] GitHub Pages deployed
- [ ] Documentation cleanup complete
- [ ] Sprint retrospective conducted

---

## 🚀 Next Sprint Preview (Sprint 2)

**Tentative Start**: 2025-12-01
**Focus**: OVIN application follow-up and enhanced features

**Planned Tasks**:
- BDM meeting with David Harris-Koblin
- Full OVIN proposal drafting
- Budget breakdown finalization
- RAQS consultant partnership
- Enhanced AI features (if time permits)

---

**Sprint Status**: 🟢 IN PROGRESS
**Last Updated**: 2025-11-17
**Sprint Lead**: ADBA Labs Team

---

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**
