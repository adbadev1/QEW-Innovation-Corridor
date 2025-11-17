# QEW Innovation Corridor - Access Guide for Corey Barron

**Welcome to the team!** This guide contains everything you need to get started with the QEW Innovation Corridor project.

**Your Email:** corey.barron.123@gmail.com
**Role:** Developer (Full Development Access)
**Added:** 2025-11-17

---

## 🔐 GCP Project Access

### Project Details

| Property | Value |
|----------|-------|
| **Project Name** | QEW Innovation Corridor Pilot |
| **Project ID** | `qew-innovation-pilot` |
| **Project Number** | 843899919832 |
| **Region** | northamerica-northeast1 (Canada - Montreal) |
| **Billing Account** | AEC-MVP-PRODUCTION |
| **Status** | ✅ ACTIVE |

### Your IAM Roles

You have been granted the following permissions:

| Role | Description | What You Can Do |
|------|-------------|-----------------|
| `roles/editor` | Project Editor | Create, modify, and delete most resources (no billing control) |
| `roles/run.admin` | Cloud Run Admin | Deploy and manage Cloud Run services |
| `roles/storage.admin` | Storage Admin | Create and manage Cloud Storage buckets |
| `roles/bigquery.admin` | BigQuery Admin | Create and manage BigQuery datasets and tables |

**Full Permissions Summary:**
- ✅ Deploy Cloud Run services
- ✅ Create/manage Pub/Sub topics and subscriptions
- ✅ Create/manage Cloud Storage buckets
- ✅ Create/manage BigQuery datasets
- ✅ View and modify project resources
- ✅ Deploy code to production
- ❌ Modify billing settings (owner only)
- ❌ Change IAM permissions (owner only)

---

## 🚀 Getting Started

### Step 1: Install Google Cloud SDK

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### Step 2: Authenticate with Google Cloud

```bash
# Login with your Google account (corey.barron.123@gmail.com)
gcloud auth login

# Set the project as default
gcloud config set project qew-innovation-pilot

# Verify authentication
gcloud auth list

# Verify project access
gcloud projects describe qew-innovation-pilot
```

**Expected Output:**
```
projectId: qew-innovation-pilot
name: QEW Innovation Corridor Pilot
projectNumber: '843899919832'
lifecycleState: ACTIVE
```

### Step 3: Set Up Application Default Credentials

```bash
# Required for local development with GCP APIs
gcloud auth application-default login
```

### Step 4: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
cd QEW-Innovation-Corridor

# Install frontend dependencies
npm install

# Start dev server (port 8200)
npm run dev
```

---

## 🏗️ Project Architecture

### Current State (Phase 1 - OVIN Application)

**Frontend:**
- React + Vite + Tailwind CSS
- Deployed to GitHub Pages
- **Live Demo:** https://adbadev1.github.io/QEW-Innovation-Corridor/
- Port: 8200 (local development)

**Backend:**
- Not deployed yet (Phase 2)
- GCP infrastructure ready
- All APIs enabled

### Planned Architecture (Phase 2 - Production)

```
┌─────────────────┐
│  MTO COMPASS    │ (Camera feeds)
│  46 Cameras     │
└────────┬────────┘
         │ HTTP/RTSP
         ▼
┌─────────────────────────────────────────┐
│         GCP Cloud Run Services          │
│   Project: qew-innovation-pilot         │
│─────────────────────────────────────────│
│  ┌───────────────┐  ┌─────────────────┐│
│  │detection-agent│  │assessment-agent ││
│  │(YOLO ML)     │  │(Claude Vision)  ││
│  │2 vCPU, 4 GB  │  │1 vCPU, 2 GB     ││
│  └───────┬───────┘  └────────┬────────┘│
│          │                    │         │
│          ▼                    ▼         │
│  ┌──────────────────────────────────┐  │
│  │        Pub/Sub Topics            │  │
│  │  - compass-camera-feeds          │  │
│  │  - work-zone-detections          │  │
│  │  - risk-assessments              │  │
│  │  - rsu-broadcasts                │  │
│  └──────────────────────────────────┘  │
│          │                               │
│          ▼                               │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │communication │  │  api-gateway    │ │
│  │agent (V2X)   │  │  (FastAPI)      │ │
│  │1 vCPU, 1 GB  │  │  1 vCPU, 2 GB   │ │
│  └──────────────┘  └─────────┬───────┘ │
└────────────────────────────────┼─────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │ React Frontend │
                        │ (GitHub Pages) │
                        └────────────────┘
```

**Data Storage:**
- **Cloud Storage:**
  - `gs://qew-camera-images` - Camera frames
  - `gs://qew-ml-models` - YOLO models
  - `gs://qew-v2x-alerts` - Alert archives

- **BigQuery:**
  - `camera_feeds` dataset
  - `work_zones` dataset
  - `risk_assessments` dataset
  - `v2x_alerts` dataset

---

## 📊 Enabled GCP Services

You have access to the following enabled APIs:

| Service | Purpose | Console Link |
|---------|---------|--------------|
| Cloud Run | Backend services | [Console](https://console.cloud.google.com/run?project=qew-innovation-pilot) |
| Compute Engine | VM instances (if needed) | [Console](https://console.cloud.google.com/compute?project=qew-innovation-pilot) |
| Pub/Sub | Message queue | [Console](https://console.cloud.google.com/cloudpubsub?project=qew-innovation-pilot) |
| BigQuery | Data warehouse | [Console](https://console.cloud.google.com/bigquery?project=qew-innovation-pilot) |
| Cloud Storage | Object storage | [Console](https://console.cloud.google.com/storage?project=qew-innovation-pilot) |
| Vertex AI | ML models | [Console](https://console.cloud.google.com/vertex-ai?project=qew-innovation-pilot) |
| Artifact Registry | Docker images | [Console](https://console.cloud.google.com/artifacts?project=qew-innovation-pilot) |
| Cloud Scheduler | Cron jobs | [Console](https://console.cloud.google.com/cloudscheduler?project=qew-innovation-pilot) |
| Cloud Logging | Logs | [Console](https://console.cloud.google.com/logs?project=qew-innovation-pilot) |
| Cloud Monitoring | Metrics & alerts | [Console](https://console.cloud.google.com/monitoring?project=qew-innovation-pilot) |

---

## 🔗 Quick Links

### GCP Console
- **Main Dashboard:** https://console.cloud.google.com/home/dashboard?project=qew-innovation-pilot
- **IAM & Admin:** https://console.cloud.google.com/iam-admin/iam?project=qew-innovation-pilot
- **Billing:** https://console.cloud.google.com/billing/linkedaccount?project=qew-innovation-pilot

### Project Resources
- **GitHub Repo:** https://github.com/adbadev1/QEW-Innovation-Corridor
- **Live Demo:** https://adbadev1.github.io/QEW-Innovation-Corridor/
- **GitHub Issues:** https://github.com/adbadev1/QEW-Innovation-Corridor/issues

### Documentation
- **Project Setup:** [docs/GCP_PROJECT_SETUP.md](GCP_PROJECT_SETUP.md)
- **Quick Start:** [docs/onboarding/QUICK_START.md](onboarding/QUICK_START.md)
- **Architecture:** [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Sprint Plan:** [docs/sprints/Sprint1/SPRINT_PLAN.md](sprints/Sprint1/SPRINT_PLAN.md)
- **AI Guidelines:** [.claude/CLAUDE.md](../.claude/CLAUDE.md)

---

## 🛠️ Common Tasks

### Deploy a Cloud Run Service

```bash
# Navigate to backend service directory (Phase 2)
cd backend/detection-agent

# Deploy to Cloud Run
gcloud run deploy detection-agent \
  --source . \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=qew-innovation-pilot

# Get service URL
gcloud run services describe detection-agent \
  --region northamerica-northeast1 \
  --format 'value(status.url)'
```

### Create Pub/Sub Topic

```bash
# Create a topic
gcloud pubsub topics create compass-camera-feeds

# Create a subscription
gcloud pubsub subscriptions create detection-sub \
  --topic=compass-camera-feeds

# Publish a test message
gcloud pubsub topics publish compass-camera-feeds \
  --message='{"camera_id": "CAM_001", "timestamp": 1234567890}'

# Pull messages
gcloud pubsub subscriptions pull detection-sub --auto-ack
```

### Create Cloud Storage Bucket

```bash
# Create a bucket
gcloud storage buckets create gs://qew-camera-images \
  --location=northamerica-northeast1 \
  --uniform-bucket-level-access

# Upload a file
gcloud storage cp local-image.jpg gs://qew-camera-images/

# List files
gcloud storage ls gs://qew-camera-images/

# Download a file
gcloud storage cp gs://qew-camera-images/image.jpg ./downloaded-image.jpg
```

### Create BigQuery Dataset

```bash
# Create dataset
bq mk --dataset \
  --location=northamerica-northeast1 \
  qew-innovation-pilot:camera_feeds

# Create table
bq mk --table \
  qew-innovation-pilot:camera_feeds.detections \
  camera_id:STRING,timestamp:TIMESTAMP,image_url:STRING

# Query data
bq query --use_legacy_sql=false \
  'SELECT * FROM `qew-innovation-pilot.camera_feeds.detections` LIMIT 10'
```

### View Logs

```bash
# Stream all logs
gcloud logging tail --project=qew-innovation-pilot

# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" \
  --project=qew-innovation-pilot \
  --limit=50

# Filter by service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=detection-agent" \
  --limit=20
```

---

## 📁 Project Structure

```
QEW-Innovation-Corridor/
├── .claude/
│   └── CLAUDE.md                      # AI development guidelines
├── docs/
│   ├── ARCHITECTURE.md                # Technical architecture
│   ├── DEMO_SCRIPT.md                 # Presentation guide
│   ├── MVP_WORKFLOW.md                # 6-month roadmap
│   ├── GCP_PROJECT_SETUP.md           # GCP setup guide
│   ├── COREY_ACCESS_GUIDE.md          # This file
│   ├── adba-labs/
│   │   └── QEW_ORGANIZATIONAL_FRAMEWORK.md
│   ├── onboarding/
│   │   └── QUICK_START.md             # 5-minute setup
│   └── sprints/
│       └── Sprint1/
│           └── SPRINT_PLAN.md         # Current sprint
├── src/
│   ├── App.jsx                        # Main dashboard
│   ├── components/
│   ├── data/
│   │   ├── qewData.js                 # 46 camera locations
│   │   └── qewRoutes.js               # OSRM routes
│   ├── services/                      # API clients (future)
│   └── utils/
│       └── riskUtils.js               # Risk scoring
├── backend/                           # Phase 2 (not created yet)
│   ├── detection-agent/
│   ├── assessment-agent/
│   ├── communication-agent/
│   └── api-gateway/
├── public/
│   └── camera_images/                 # 88 camera images
├── .env.example                       # Environment template
├── package.json
├── vite.config.js                     # Port 8200
└── README.md
```

---

## 🎯 Current Sprint Tasks

**Sprint 1 (Nov 17-30, 2025) - 16 Story Points**

### Your Potential Tasks:

**Priority 1 (Critical):**
- [ ] **Issue #4** - Implement Real Work Zone Detection (3 days)
  - This is THE critical feature for SaaS
  - Backend infrastructure using GCP Cloud Run
  - See updated issue for full GCP architecture

**Priority 2 (Important):**
- [ ] **Issue #5** - Create OVIN Documentation Structure (1 day)
- [ ] **Issue #6** - Draft OVIN Client Intake Form (2 days)
- [ ] **Issue #7** - Prepare OVIN Pitch Deck (3 days)

**Priority 3 (Nice to Have):**
- [ ] **Issue #10** - Claude Vision API Integration (2 days)
- [ ] **Issue #11** - Image Upload UI (1 day)
- [ ] **Issue #12** - Record Demo Video (1 day)

**View all issues:** https://github.com/adbadev1/QEW-Innovation-Corridor/issues

---

## ⚙️ Environment Configuration

### Local Development

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update with your credentials:
```bash
# GCP Configuration
GCP_PROJECT_ID=qew-innovation-pilot
GCP_PROJECT_NUMBER=843899919832
GCP_REGION=northamerica-northeast1
GCP_ZONE=northamerica-northeast1-a

# Claude API (get from https://console.anthropic.com/)
VITE_CLAUDE_API_KEY=your-api-key-here
VITE_CLAUDE_MODEL=claude-3-5-sonnet-20250219

# Service Ports
VITE_PORT=8200

# Feature Flags
VITE_ENABLE_REAL_AI_ANALYSIS=false
VITE_ENABLE_VISION_API=false
```

### GCP Service Account (Optional - for CI/CD)

If you need a service account for automated deployments:

```bash
# Create service account
gcloud iam service-accounts create qew-deployer \
  --display-name="QEW Deployment Service Account"

# Grant roles
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="serviceAccount:qew-deployer@qew-innovation-pilot.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Create key (KEEP SECURE!)
gcloud iam service-accounts keys create ~/qew-deployer-key.json \
  --iam-account=qew-deployer@qew-innovation-pilot.iam.gserviceaccount.com

# Use in CI/CD
export GOOGLE_APPLICATION_CREDENTIALS=~/qew-deployer-key.json
```

---

## 💰 Cost Awareness

**Monthly Estimated Costs:**
- Cloud Run: $100-150
- Pub/Sub: $10-20
- BigQuery: $20-40
- Cloud Storage: $10-20
- **Total: $140-230/month**

**Budget:**
- OVIN funding: $150K over 6 months
- Infrastructure allocation: $30K (20%)
- Monthly budget: ~$5K available

**Best Practices:**
- Use Cloud Run autoscaling (scale to zero when idle)
- Set up budget alerts in GCP Console
- Monitor costs regularly
- Use BigQuery partitioning for cost efficiency

---

## 🐛 Troubleshooting

### Authentication Issues

```bash
# Revoke and re-authenticate
gcloud auth revoke
gcloud auth login

# Check active account
gcloud auth list

# Switch accounts
gcloud config set account corey.barron.123@gmail.com
```

### Permission Denied

If you get permission errors:
1. Verify you're using the correct project: `gcloud config get-value project`
2. Check your IAM roles: `gcloud projects get-iam-policy qew-innovation-pilot`
3. Contact project owner if you need additional permissions

### Port 8200 Already in Use

```bash
# Find what's using port 8200
lsof -i :8200

# Kill the process
kill -9 <PID>

# Or use a different port
npm run dev -- --port 8201
```

---

## 📞 Contacts

**Project Owner:**
- Email: adbalabs0101@gmail.com

**OVIN Program Manager:**
- Name: David Harris-Koblin
- Email: dharris-koblin@oc.innovation.ca
- Organization: Ontario Vehicle Innovation Network (OVIN)

**GitHub:**
- Issues: https://github.com/adbadev1/QEW-Innovation-Corridor/issues
- Discussions: Use GitHub Issues for technical questions

---

## 📚 Learning Resources

**GCP Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Pub/Sub: https://cloud.google.com/pubsub/docs
- BigQuery: https://cloud.google.com/bigquery/docs
- Cloud Storage: https://cloud.google.com/storage/docs

**Project Documentation:**
- OVIN Program: https://www.ovinhub.ca/
- MTO COMPASS: http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml
- Claude Vision API: https://docs.anthropic.com/en/docs/vision
- V2X-Hub: https://github.com/usdot-fhwa-OPS/V2X-Hub

---

## ✅ Getting Started Checklist

- [ ] Install Google Cloud SDK
- [ ] Authenticate with gcloud (`gcloud auth login`)
- [ ] Set project (`gcloud config set project qew-innovation-pilot`)
- [ ] Verify access (`gcloud projects describe qew-innovation-pilot`)
- [ ] Clone repository
- [ ] Install npm dependencies (`npm install`)
- [ ] Start dev server (`npm run dev`)
- [ ] Access GCP Console
- [ ] Review Sprint 1 tasks
- [ ] Pick up Issue #4 or another task
- [ ] Join the team! 🚀

---

**Welcome aboard!** If you have any questions, reach out to the project owner or open a GitHub issue.

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**
**Last Updated:** 2025-11-17
**Project Phase:** Phase 1 (OVIN Application)
