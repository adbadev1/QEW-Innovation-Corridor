# GCP Project Setup - QEW Innovation Corridor

**Project Created:** 2025-11-17
**Project ID:** `qew-innovation-pilot`
**Project Number:** 843899919832
**Project Name:** QEW Innovation Corridor Pilot
**Status:** ✅ ACTIVE

---

## ✅ Completed Steps

### 1. Project Creation ✅
```bash
gcloud projects create qew-innovation-pilot \
  --name="QEW Innovation Corridor Pilot" \
  --set-as-default
```

**Result:**
- Project ID: `qew-innovation-pilot`
- Project Number: `843899919832`
- Status: ACTIVE
- Default project set to `qew-innovation-pilot`

### 2. Billing Enabled ✅
```bash
gcloud billing projects link qew-innovation-pilot \
  --billing-account=018099-521D2C-05208A
```

**Result:**
- Billing Account: AEC-MVP-PRODUCTION (018099-521D2C-05208A)
- Status: billingEnabled = true
- All paid APIs now available

### 3. Required APIs Enabled ✅
```bash
gcloud services enable \
  run.googleapis.com \
  compute.googleapis.com \
  pubsub.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

**Enabled Services:**
- ✅ Cloud Run (backend services)
- ✅ Compute Engine
- ✅ Pub/Sub (message queue)
- ✅ BigQuery (data warehouse)
- ✅ Cloud Storage (image storage)
- ✅ Vertex AI (ML models)
- ✅ Artifact Registry (Docker images)
- ✅ Cloud Scheduler (cron jobs)
- ✅ Cloud Logging
- ✅ Cloud Monitoring

### 4. Team Collaborators Added ✅
```bash
# Corey Barron - Full Development Access
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey.barron.123@gmail.com" \
  --role="roles/editor"

gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey.barron.123@gmail.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey.barron.123@gmail.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey.barron.123@gmail.com" \
  --role="roles/bigquery.admin"
```

**Corey's IAM Roles:**
- ✅ `roles/editor` - Create/modify resources
- ✅ `roles/run.admin` - Deploy Cloud Run services
- ✅ `roles/storage.admin` - Manage Cloud Storage buckets
- ✅ `roles/bigquery.admin` - Manage BigQuery datasets

**Current IAM Members:**
| User | Email | Roles |
|------|-------|-------|
| Owner | adbalabs0101@gmail.com | `roles/owner` |
| Developer | corey.barron.123@gmail.com | `roles/editor`, `roles/run.admin`, `roles/storage.admin`, `roles/bigquery.admin` |

---

## ⏳ Optional Next Steps

### 1. Enable Billing (REQUIRED) - ✅ COMPLETED

**Option A: Via Web Console (Recommended)**
1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=qew-innovation-pilot
2. Select a billing account or create a new one
3. Link billing account to `qew-innovation-pilot`

**Option B: Via gcloud CLI**
```bash
# List available billing accounts
gcloud billing accounts list

# Link billing account to project
gcloud billing projects link qew-innovation-pilot \
  --billing-account=BILLING_ACCOUNT_ID
```

**Why Needed:**
- Cloud Run, Compute Engine, and other services require billing
- Free tier available for initial development
- Estimated cost: $50-200/month (Phase 2 development)

---

### 2. Enable Required APIs

**After billing is enabled, run:**
```bash
# Set active project
gcloud config set project qew-innovation-pilot

# Enable all required APIs
gcloud services enable \
  run.googleapis.com \
  compute.googleapis.com \
  pubsub.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# Verify enabled services
gcloud services list --enabled
```

**Required Services:**
- `run.googleapis.com` - Cloud Run (backend services)
- `compute.googleapis.com` - Compute Engine (if needed)
- `pubsub.googleapis.com` - Pub/Sub (message queue)
- `bigquery.googleapis.com` - BigQuery (data warehouse)
- `storage.googleapis.com` - Cloud Storage (image storage)
- `aiplatform.googleapis.com` - Vertex AI (ML models)
- `artifactregistry.googleapis.com` - Artifact Registry (Docker images)
- `cloudscheduler.googleapis.com` - Cloud Scheduler (cron jobs)
- `logging.googleapis.com` - Cloud Logging
- `monitoring.googleapis.com` - Cloud Monitoring

---

### 3. Add Collaborators (IAM)

**Add Corey as Project Editor:**
```bash
# Replace with Corey's email
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey@example.com" \
  --role="roles/editor"
```

**Recommended IAM Roles:**

| User | Role | Permissions |
|------|------|-------------|
| You (Owner) | `roles/owner` | Full control |
| Corey | `roles/editor` | Create/modify resources, no billing |
| Service Account | `roles/run.admin` | Deploy Cloud Run services |
| Service Account | `roles/pubsub.admin` | Manage Pub/Sub |
| Service Account | `roles/storage.admin` | Manage Cloud Storage |

**Additional Roles (as needed):**
```bash
# Cloud Run Admin (for deployments)
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey@example.com" \
  --role="roles/run.admin"

# Storage Admin (for camera images)
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey@example.com" \
  --role="roles/storage.admin"

# BigQuery Admin (for data warehouse)
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="user:corey@example.com" \
  --role="roles/bigquery.admin"
```

---

### 4. Create Service Account

**For CI/CD and automated deployments:**
```bash
# Create service account
gcloud iam service-accounts create qew-deployer \
  --display-name="QEW Deployment Service Account" \
  --project=qew-innovation-pilot

# Grant necessary roles
gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="serviceAccount:qew-deployer@qew-innovation-pilot.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding qew-innovation-pilot \
  --member="serviceAccount:qew-deployer@qew-innovation-pilot.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key (KEEP SECURE!)
gcloud iam service-accounts keys create ~/qew-deployer-key.json \
  --iam-account=qew-deployer@qew-innovation-pilot.iam.gserviceaccount.com

# IMPORTANT: Add to .gitignore
echo "qew-deployer-key.json" >> .gitignore
```

---

## 📋 Planned GCP Resources

### Cloud Run Services (Phase 2)

| Service | Purpose | CPU | Memory | Instances |
|---------|---------|-----|--------|-----------|
| `detection-agent` | YOLO work zone detection | 2 vCPU | 4 GB | 1-10 |
| `assessment-agent` | Claude Vision API | 1 vCPU | 2 GB | 1-5 |
| `communication-agent` | V2X alert generation | 1 vCPU | 1 GB | 1-3 |
| `api-gateway` | FastAPI backend | 1 vCPU | 2 GB | 1-5 |

**Estimated Cost:**
- Cloud Run: $100-150/month
- Pub/Sub: $10-20/month
- BigQuery: $20-40/month
- Cloud Storage: $10-20/month
- **Total: $140-230/month**

### Pub/Sub Topics

```bash
# Create Pub/Sub topics
gcloud pubsub topics create compass-camera-feeds
gcloud pubsub topics create work-zone-detections
gcloud pubsub topics create risk-assessments
gcloud pubsub topics create rsu-broadcasts

# Create subscriptions
gcloud pubsub subscriptions create detection-sub \
  --topic=compass-camera-feeds

gcloud pubsub subscriptions create assessment-sub \
  --topic=work-zone-detections

gcloud pubsub subscriptions create communication-sub \
  --topic=risk-assessments
```

### Cloud Storage Buckets

```bash
# Create storage buckets
gcloud storage buckets create gs://qew-camera-images \
  --location=northamerica-northeast1 \
  --uniform-bucket-level-access

gcloud storage buckets create gs://qew-ml-models \
  --location=northamerica-northeast1 \
  --uniform-bucket-level-access

gcloud storage buckets create gs://qew-v2x-alerts \
  --location=northamerica-northeast1 \
  --uniform-bucket-level-access
```

### BigQuery Datasets

```bash
# Create BigQuery datasets
bq mk --dataset \
  --location=northamerica-northeast1 \
  qew-innovation-pilot:camera_feeds

bq mk --dataset \
  --location=northamerica-northeast1 \
  qew-innovation-pilot:work_zones

bq mk --dataset \
  --location=northamerica-northeast1 \
  qew-innovation-pilot:risk_assessments

bq mk --dataset \
  --location=northamerica-northeast1 \
  qew-innovation-pilot:v2x_alerts
```

---

## 🔐 Environment Configuration

**Update `.env` file:**
```bash
# GCP Configuration
GCP_PROJECT_ID=qew-innovation-pilot
GCP_PROJECT_NUMBER=843899919832
GCP_REGION=northamerica-northeast1
GCP_ZONE=northamerica-northeast1-a

# Cloud Run Service URLs (after deployment)
DETECTION_AGENT_URL=https://detection-agent-HASH-nn.a.run.app
ASSESSMENT_AGENT_URL=https://assessment-agent-HASH-nn.a.run.app
COMMUNICATION_AGENT_URL=https://communication-agent-HASH-nn.a.run.app
API_GATEWAY_URL=https://api-gateway-HASH-nn.a.run.app

# Pub/Sub Topics
PUBSUB_CAMERA_FEEDS=compass-camera-feeds
PUBSUB_DETECTIONS=work-zone-detections
PUBSUB_ASSESSMENTS=risk-assessments
PUBSUB_BROADCASTS=rsu-broadcasts

# Cloud Storage Buckets
GCS_CAMERA_IMAGES=qew-camera-images
GCS_ML_MODELS=qew-ml-models
GCS_V2X_ALERTS=qew-v2x-alerts

# BigQuery Datasets
BQ_CAMERA_FEEDS=camera_feeds
BQ_WORK_ZONES=work_zones
BQ_RISK_ASSESSMENTS=risk_assessments
BQ_V2X_ALERTS=v2x_alerts
```

---

## 🚀 Deployment Workflow

### Local Development
```bash
# Set active project
gcloud config set project qew-innovation-pilot

# Authenticate
gcloud auth login
gcloud auth application-default login

# Run locally
npm run dev  # Frontend (port 8200)
# Backend services run in Cloud Run (Phase 2)
```

### Deploy to Cloud Run (Phase 2)
```bash
# Build and deploy detection agent
cd backend/detection-agent
gcloud run deploy detection-agent \
  --source . \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=qew-innovation-pilot

# Deploy assessment agent
cd ../assessment-agent
gcloud run deploy assessment-agent \
  --source . \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=qew-innovation-pilot

# Deploy communication agent
cd ../communication-agent
gcloud run deploy communication-agent \
  --source . \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=qew-innovation-pilot

# Deploy API gateway
cd ../api-gateway
gcloud run deploy api-gateway \
  --source . \
  --region northamerica-northeast1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=qew-innovation-pilot
```

---

## 📊 Monitoring & Logging

**Cloud Logging:**
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" \
  --project=qew-innovation-pilot \
  --limit=50

# Stream logs
gcloud logging tail --project=qew-innovation-pilot
```

**Cloud Monitoring:**
- Dashboard: https://console.cloud.google.com/monitoring?project=qew-innovation-pilot
- Metrics: CPU, Memory, Request Count, Latency
- Alerts: Set up for high error rates, latency spikes

---

## 🔗 Useful Links

**Project Console:**
- Main: https://console.cloud.google.com/home/dashboard?project=qew-innovation-pilot
- Billing: https://console.cloud.google.com/billing/linkedaccount?project=qew-innovation-pilot
- IAM: https://console.cloud.google.com/iam-admin/iam?project=qew-innovation-pilot
- Cloud Run: https://console.cloud.google.com/run?project=qew-innovation-pilot
- Pub/Sub: https://console.cloud.google.com/cloudpubsub?project=qew-innovation-pilot
- BigQuery: https://console.cloud.google.com/bigquery?project=qew-innovation-pilot
- Storage: https://console.cloud.google.com/storage?project=qew-innovation-pilot

**Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Pub/Sub: https://cloud.google.com/pubsub/docs
- BigQuery: https://cloud.google.com/bigquery/docs
- IAM: https://cloud.google.com/iam/docs

---

## 📝 Notes

**Current Phase:** Phase 1 (OVIN Application)
- Frontend: GitHub Pages ✅
- Backend: Not deployed yet (Phase 2)
- GCP Project: ✅ Created, billing enabled, APIs activated
- Team Access: ✅ Corey added with full development permissions

**Setup Status:**
- ✅ Project created (qew-innovation-pilot)
- ✅ Billing enabled (AEC-MVP-PRODUCTION)
- ✅ 10+ APIs enabled (Cloud Run, Pub/Sub, BigQuery, Storage, etc.)
- ✅ Team collaborator added (Corey Barron)
- ⏳ Backend services (Phase 2 - after OVIN approval)
- ⏳ Service account for CI/CD (when needed)

**Next Milestone:** Deploy backend services to Cloud Run (Phase 2)

**OVIN Funding:** $150K over 6 months
- 20% ($30K) allocated for GCP infrastructure
- Estimated monthly cost: $140-230/month

**Security:**
- All API keys in `.env` (not committed)
- Service account keys stored securely
- IAM roles follow principle of least privilege
- Billing account shared with AEC-MVP-PRODUCTION

**Team Access:**
- Corey can now access project via: https://console.cloud.google.com/home/dashboard?project=qew-innovation-pilot
- Authenticate with: `gcloud config set project qew-innovation-pilot`

---

**Last Updated:** 2025-11-17 (Billing enabled, APIs activated, Corey added)
**Created By:** ADBA Labs
**Project Phase:** Phase 1 (OVIN Application)
**Ready for:** Phase 2 backend deployment

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**
