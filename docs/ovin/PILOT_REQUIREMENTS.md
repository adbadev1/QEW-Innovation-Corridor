# QEW Innovation Corridor - Pilot Requirements

**Program**: OVIN - QEW Innovation Corridor Pilot
**Funding**: $150,000
**Duration**: 6 months
**Applicant**: ADBA Labs
**Last Updated**: 2025-11-18

---

## 📋 Executive Summary

This document outlines the infrastructure, technical, operational, and regulatory requirements for deploying the QEW Innovation Corridor AI Work Zone Safety System on Ontario's QEW highway corridor.

**Pilot Scope**:
- **Geographic**: 40km QEW corridor (Burlington Skyway to Mississauga)
- **Cameras**: 46 COMPASS traffic cameras
- **Timeline**: 6 months (infrastructure + deployment + validation)
- **Funding**: $150,000 OVIN grant

---

## 🗺️ Geographic Scope

### QEW Innovation Corridor Boundaries

**Western Boundary**: Burlington Skyway (Hamilton side)
- GPS: 43.2951°N, -79.8079°W
- Landmark: Burlington Skyway Bridge

**Eastern Boundary**: Mississauga Road (Mississauga)
- GPS: 43.558128°N, -79.607964°W
- Landmark: QEW / Mississauga Road interchange

**Total Distance**: Approximately 40 kilometers
**Highway**: Queen Elizabeth Way (QEW)
**Municipalities**: Hamilton, Burlington, Oakville, Mississauga

---

### Camera Coverage

**Total COMPASS Cameras**: 46 cameras, 50 views
**Geographic Distribution**:

| Region | Cameras | Key Locations |
|--------|---------|---------------|
| **Hamilton** | 10 | Red Hill Valley Pkwy, Centennial Pkwy, Nikola Tesla Blvd |
| **Burlington** | 15 | Burlington Skyway, Brant St, Guelph Line, Appleby Line |
| **Oakville** | 12 | Third Line, Dorval Dr, Trafalgar Rd, Ford Dr |
| **Mississauga** | 9 | Winston Churchill Blvd, Erin Mills Pkwy, Mississauga Rd |

**Camera Spacing**: Average 800m-1km between cameras
**View Types**:
- Eastbound (Toronto-bound) lanes
- Westbound (Hamilton/Fort Erie-bound) lanes
- Overhead views
- Ramp/interchange views

**Reference**: `camera_scraper/qew_cameras_hamilton_mississauga.json`

---

## 🏗️ Infrastructure Requirements

### 1. COMPASS Camera Integration

#### MTO COMPASS API Access
**Requirement**: API access to MTO 511ON traffic camera feeds

**Specifications**:
- **API Endpoint**: https://511on.ca/api/v2/get/cameras?format=json
- **Authentication**: Currently public API (may require credentials for pilot)
- **Update Frequency**: Real-time images (refresh every 30-60 seconds)
- **Image Format**: JPEG
- **Resolution**: 640x480 to 1280x720 (varies by camera)
- **Bandwidth**: ~50 images/min × 50KB/image = 2.5 MB/min = 3.6 GB/day

**MTO Coordination**:
- [ ] Submit API access request to MTO COMPASS team
- [ ] Negotiate data sharing agreement
- [ ] Obtain production API credentials (if required)
- [ ] Establish SLA for camera uptime (target: 95%)

---

### 2. GCP Cloud Infrastructure

#### Cloud Run Services (4 microservices)

**detection-agent** - YOLO Work Zone Detection
- **vCPUs**: 2
- **Memory**: 4 GB
- **Concurrency**: 80 requests
- **Scaling**: 0-10 instances (autoscale)
- **Image**: Python 3.11 + YOLO model
- **Purpose**: Pre-filter images for work zone presence

**assessment-agent** - Claude Vision API Analysis
- **vCPUs**: 1
- **Memory**: 2 GB
- **Concurrency**: 10 requests (API rate limit)
- **Scaling**: 1-5 instances
- **Image**: Python 3.11 + Anthropic SDK
- **Purpose**: Detailed safety analysis and risk scoring

**communication-agent** - V2X Alert Generation
- **vCPUs**: 1
- **Memory**: 1 GB
- **Concurrency**: 100 requests
- **Scaling**: 0-3 instances
- **Image**: Python 3.11 + SAE J2735 encoder
- **Purpose**: Generate and broadcast V2X alerts to RSUs

**api-gateway** - FastAPI Backend
- **vCPUs**: 1
- **Memory**: 2 GB
- **Concurrency**: 80 requests
- **Scaling**: 1-5 instances
- **Image**: Python 3.11 + FastAPI
- **Purpose**: REST API for dashboard and external integrations

---

#### Pub/Sub Message Queue

**Topics**:
1. `compass-camera-feeds` - Incoming camera images
2. `work-zone-detections` - YOLO detection results
3. `risk-assessments` - Claude Vision analysis results
4. `rsu-broadcasts` - V2X alert messages

**Message Retention**: 7 days
**Throughput**: 1 message/sec/camera = 46 msg/sec = 4M msg/day
**Storage**: ~10 GB/month (with image data)

---

#### BigQuery Data Warehouse

**Datasets**:

**camera_feeds** - Camera metadata and image references
- `camera_id`, `view_id`, `location`, `gps`, `timestamp`, `image_url`
- Retention: 12 months
- Size estimate: 50M rows/year, ~5 GB

**work_zones** - Detected work zones
- `detection_id`, `camera_id`, `timestamp`, `confidence`, `bbox`, `elements`
- Retention: 24 months
- Size estimate: 100K rows/year, ~500 MB

**risk_assessments** - AI safety analysis
- `assessment_id`, `work_zone_id`, `risk_score`, `violations`, `hazards`, `recommendations`
- Retention: 24 months
- Size estimate: 100K rows/year, ~2 GB

**v2x_alerts** - Broadcast alert history
- `alert_id`, `assessment_id`, `priority`, `message`, `broadcast_time`, `rsu_id`
- Retention: 12 months
- Size estimate: 50K rows/year, ~200 MB

**Total Storage**: ~8 GB/year

---

#### Cloud Storage Buckets

**gs://qew-camera-images** - Camera image archive
- **Purpose**: Short-term image storage (0-24 hours)
- **Lifecycle**: Auto-delete after 1 day
- **Size**: 2.5 MB/min × 1440 min/day = 3.6 GB/day → 3.6 GB max (rolling)

**gs://qew-ml-models** - ML model artifacts
- **Purpose**: YOLO weights, model checkpoints
- **Size**: ~500 MB
- **Lifecycle**: Retained indefinitely

**gs://qew-v2x-alerts** - Alert archive
- **Purpose**: V2X message logs (JSON)
- **Size**: ~10 MB/month
- **Lifecycle**: Retained 12 months

**Total Storage**: ~4 GB active, ~120 MB/year growth

---

### 3. V2X / RSU Integration

#### Roadside Units (RSUs)

**Requirement**: Access to existing RSUs on QEW corridor for V2X alert broadcast

**OVIN RSU Network**:
- **Deployment**: OVIN has installed RSUs along QEW corridor (exact locations TBD)
- **Standard**: SAE J2735 (Dedicated Short-Range Communications - DSRC)
- **Frequency**: 5.9 GHz DSRC band
- **Range**: ~300m radius per RSU
- **Message Types**: TravelerInformation, RoadSideAlert

**Integration Method**:
- **Option A**: Direct integration via V2X-Hub API (preferred)
- **Option B**: Message relay through OVIN central system
- **Option C**: MQTT broker for message distribution

**Requirements**:
- [ ] Identify RSU locations along QEW
- [ ] Obtain RSU API credentials (V2X-Hub)
- [ ] Test message broadcast capability
- [ ] Establish latency SLA (target: <5 sec from detection to broadcast)

**Reference**: [USDOT V2X-Hub Documentation](https://github.com/usdot-fhwa-OPS/V2X-Hub)

---

## 💻 Technical Requirements

### Frontend Dashboard (React)

**Current Status**: ✅ Deployed on GitHub Pages
**URL**: https://adbadev1.github.io/QEW-Innovation-Corridor/
**Stack**: React + Vite + Leaflet + Recharts

**Pilot Enhancements**:
- [ ] Connect to live GCP API Gateway (replace simulated data)
- [ ] WebSocket for real-time updates
- [ ] MTO BOOK 7 violation drill-down view
- [ ] Historical trend charts (risk scores over time)
- [ ] Admin panel for configuration

---

### AI/ML Models

#### YOLO Object Detection (Pre-filter)

**Purpose**: Fast detection of work zone presence
**Model**: YOLOv8 or YOLOv9
**Training Data**: 1000+ labeled work zone images
**Classes**: Worker, Vehicle, Cone, Barrier, Sign, Equipment
**Accuracy Target**: ≥90% work zone detection
**Latency**: <500ms per image

**Training Requirements**:
- [ ] Collect 1000 QEW work zone images
- [ ] Label images with bounding boxes
- [ ] Train YOLO model on GCP Vertex AI
- [ ] Export to ONNX for Cloud Run deployment

---

#### Claude Vision API (Detailed Analysis)

**Purpose**: Detailed work zone safety assessment
**Model**: Claude 3.5 Sonnet (Vision)
**API**: Anthropic API (https://www.anthropic.com/)
**Prompt Engineering**: MTO BOOK 7 compliance checking
**Accuracy Target**: ≥85% risk score accuracy (±1 point)
**Latency**: 2-4 seconds per analysis

**API Usage**:
- **Volume**: ~10K images/month (work zones only, after YOLO filter)
- **Cost**: $0.015/image × 10K = $150/month (covered by OVIN budget)
- **Rate Limit**: 50 requests/min (sufficient for real-time processing)

**Requirements**:
- [ ] Obtain Anthropic API key
- [ ] Configure rate limiting and retry logic
- [ ] Set up prompt templates for BOOK 7 compliance
- [ ] Implement structured output parsing (JSON)

---

### Security Requirements

#### Authentication & Authorization

**GCP IAM (Identity and Access Management)**:
- Service accounts for each Cloud Run service
- Least privilege principle (minimal permissions)
- No public access to backend APIs
- Frontend uses API Gateway with API key

**API Security**:
- API keys for dashboard → gateway communication
- OAuth 2.0 for admin panel (future)
- Rate limiting (1000 req/hour per client)
- DDoS protection via Cloud Armor

#### Encryption

- **In Transit**: TLS 1.3 for all API calls
- **At Rest**: AES-256 for BigQuery and Cloud Storage
- **API Keys**: Stored in Google Secret Manager
- **Credentials**: Never committed to git (use .env)

#### Compliance

- **FIPPA**: See FIPPA_COMPLIANCE.md
- **PIPEDA**: Federal privacy law (applies to private data)
- **SOC 2 Type II**: GCP is certified (inherited compliance)
- **ISO 27001**: GCP is certified (inherited compliance)

---

## 📅 Pilot Timeline (6 Months)

### Month 1: Infrastructure Setup

**Week 1-2: GCP Environment**
- [ ] Create GCP project (`qew-innovation-pilot`)
- [ ] Enable billing and APIs
- [ ] Set up Cloud Run services (4 microservices)
- [ ] Configure Pub/Sub topics (4 topics)
- [ ] Create BigQuery datasets (4 datasets)
- [ ] Set up Cloud Storage buckets (3 buckets)
- [ ] Configure IAM roles and service accounts

**Week 3-4: COMPASS Integration**
- [ ] Obtain MTO COMPASS API credentials
- [ ] Implement camera feed ingestion service
- [ ] Test image download from all 46 cameras
- [ ] Verify camera uptime and reliability
- [ ] Set up monitoring and alerting

---

### Month 2: AI Model Development

**Week 5-6: YOLO Training**
- [ ] Collect 1000 QEW work zone images
- [ ] Label images (bounding boxes for workers, vehicles, barriers)
- [ ] Train YOLOv8 model on Vertex AI
- [ ] Achieve ≥90% detection accuracy
- [ ] Deploy to Cloud Run detection-agent

**Week 7-8: Claude Vision Integration**
- [ ] Set up Anthropic API access
- [ ] Design MTO BOOK 7 compliance prompt
- [ ] Test on 100 sample work zone images
- [ ] Tune risk score algorithm
- [ ] Deploy to Cloud Run assessment-agent

---

### Month 3: V2X Integration

**Week 9-10: RSU Connectivity**
- [ ] Identify RSU locations on QEW
- [ ] Obtain V2X-Hub API credentials
- [ ] Implement SAE J2735 message encoding
- [ ] Test message broadcast to 1 RSU
- [ ] Verify message reception (OBU or test device)

**Week 11-12: Alert Generation**
- [ ] Implement communication-agent service
- [ ] Connect to Pub/Sub risk-assessments topic
- [ ] Generate V2X alerts for high-risk work zones
- [ ] Broadcast to all QEW RSUs
- [ ] Monitor broadcast success rate (target: ≥95%)

---

### Month 4: Dashboard Integration

**Week 13-14: Backend API**
- [ ] Develop FastAPI Gateway service
- [ ] Expose RESTful endpoints (GET /work-zones, GET /alerts)
- [ ] Implement WebSocket for real-time updates
- [ ] Deploy to Cloud Run api-gateway
- [ ] Test API performance (target: <100ms latency)

**Week 15-16: Frontend Updates**
- [ ] Connect React dashboard to GCP API
- [ ] Replace simulated data with live work zones
- [ ] Add historical trend charts
- [ ] Implement violation drill-down view
- [ ] Deploy updated dashboard to GitHub Pages

---

### Month 5: Testing & Validation

**Week 17-18: Functional Testing**
- [ ] End-to-end testing (camera → AI → V2X → dashboard)
- [ ] Load testing (46 cameras at 1fps = 46 req/sec)
- [ ] Latency testing (target: <5 sec detection → alert)
- [ ] Accuracy testing (100 manual inspections vs AI)
- [ ] Security penetration testing

**Week 19-20: Field Validation**
- [ ] Partner with MTO for ground truth comparison
- [ ] Deploy MTO inspectors to 10 work zones
- [ ] Compare AI risk scores with human assessments
- [ ] Tune algorithm based on feedback
- [ ] Achieve ≥85% accuracy (±1 point risk score)

---

### Month 6: Production Deployment & Reporting

**Week 21-22: Production Launch**
- [ ] Deploy to all 46 QEW cameras
- [ ] Enable real-time monitoring (24/7)
- [ ] Configure alerting and paging
- [ ] Train MTO operators on dashboard usage
- [ ] Go-live celebration! 🎉

**Week 23-24: Documentation & Handoff**
- [ ] Write final pilot report
- [ ] Document lessons learned
- [ ] Prepare expansion roadmap (provincial deployment)
- [ ] Present findings to OVIN Steering Committee
- [ ] Submit application for Scale-Up funding

---

## 📊 Success Metrics

### Technical Performance

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Camera Uptime** | ≥95% | Monitor API success rate |
| **AI Detection Accuracy** | ≥90% | Ground truth comparison (1000 images) |
| **Risk Score Accuracy** | ±1 point | MTO Inspector comparison (100 work zones) |
| **Latency (Detection → Alert)** | <5 seconds | End-to-end timing logs |
| **V2X Broadcast Success** | ≥95% | RSU delivery confirmation |
| **Dashboard Availability** | ≥99% | Uptime monitoring (Pingdom) |
| **API Response Time** | <100ms | P95 latency from logs |
| **False Positive Rate** | <10% | Precision measurement |
| **False Negative Rate** | <5% | Recall measurement |

---

### Business Outcomes

| Outcome | Target | Measurement Method |
|---------|--------|-------------------|
| **Work Zone Incidents** | -20% reduction | MTO incident reports (before/after) |
| **MTO Adoption** | Pilot approved for expansion | OVIN Steering Committee vote |
| **Municipal Interest** | 3 cities inquire about licensing | Sales pipeline tracking |
| **Media Coverage** | 5 news articles | Press clippings |
| **Academic Partnerships** | 1 university collaboration | LOI signed |

---

### Regulatory Compliance

| Requirement | Target | Validation Method |
|-------------|--------|------------------|
| **FIPPA Compliance** | 100% (zero violations) | IPC audit (if requested) |
| **MTO BOOK 7 Knowledge** | ≥85% accuracy | Comparison with human inspectors |
| **V2X Standards (SAE J2735)** | 100% compliant | Third-party RSU testing |
| **Data Residency** | 100% Canadian data | GCP region verification |
| **Privacy Breaches** | Zero incidents | Incident log review |

---

## 🤝 Stakeholder Coordination

### MTO (Ministry of Transportation Ontario)

**Key Contacts**:
- **COMPASS Operations**: Camera feed access, uptime coordination
- **Highway Standards**: BOOK 7 compliance validation
- **District Offices**: Work zone violation follow-up
- **Emergency Operations**: Critical alert escalation

**Engagement Plan**:
- Monthly progress meetings
- Quarterly accuracy audits
- Annual compliance review
- Co-author case study for industry publication

---

### OVIN (Ontario Vehicle Innovation Network)

**Key Contact**: David Harris-Koblin (dharris-koblin@oc.innovation.ca)

**Reporting Requirements**:
- Monthly progress reports
- Quarterly financial reporting
- Final pilot report (Month 6)
- Steering Committee presentation

**Deliverables**:
- Technical documentation
- Source code repository (GitHub)
- Performance metrics dashboard
- Lessons learned document
- Scale-up proposal

---

### Municipal Partners (Optional)

**Potential Collaborators**:
- City of Burlington
- City of Oakville
- City of Mississauga
- City of Hamilton

**Value Proposition**:
- Extend system to municipal work zones (arterial roads)
- License SaaS platform for local deployments
- Joint grant applications (MUNI-OVIN program)

---

## 💰 Resource Requirements

### Personnel

| Role | Time Commitment | Responsibilities |
|------|----------------|------------------|
| **Project Manager** | 50% (3 months FTE) | Overall coordination, OVIN reporting |
| **Backend Developer** | 100% (6 months FTE) | GCP infrastructure, API development |
| **AI/ML Engineer** | 100% (4 months FTE) | YOLO training, Claude integration |
| **Frontend Developer** | 50% (2 months FTE) | React dashboard updates |
| **QA/Test Engineer** | 50% (2 months FTE) | Testing, validation, field trials |
| **DevOps Engineer** | 25% (1.5 months FTE) | CI/CD, monitoring, security |

**Total**: 18.5 person-months

---

### Infrastructure

**GCP Monthly Costs** (covered by OVIN $150K):
- Cloud Run: $100-150
- Pub/Sub: $10-20
- BigQuery: $20-40
- Cloud Storage: $10-20
- Network Egress: $50-100
- **Total**: $190-330/month × 6 months = **$1,140-1,980**

**Claude API Costs**:
- $150/month × 6 months = **$900**

**Total Infrastructure**: **~$2,880** (6-month pilot)

---

### Professional Services

- **Legal Review** (FIPPA, contracts): $5,000
- **RAQS Consultant** (OVIN requirement): $10,000
- **MTO Compliance Audit**: $3,000
- **Third-Party Security Assessment**: $5,000
- **Total**: **$23,000**

---

**See BUDGET_BREAKDOWN.md for detailed budget allocation.**

---

## 🚀 Post-Pilot Roadmap

### Month 7-9: Provincial Expansion

- Extend to all Ontario 400-series highways (401, 404, 427, DVP, Gardiner)
- Integrate 200+ additional COMPASS cameras
- Scale GCP infrastructure (horizontal scaling)
- Negotiate province-wide MTO contract

### Month 10-12: Municipal Licensing

- Launch SaaS platform for municipal deployments
- Onboard 3 pilot cities (Burlington, Oakville, Mississauga)
- Develop self-service deployment toolkit
- Build sales and support team

### Year 2: Multi-Jurisdictional Expansion

- BC Ministry of Transportation (Sea-to-Sky Highway)
- Alberta Transportation (QEII Highway, Deerfoot Trail)
- Quebec MTQ (Autoroute 20, 40)
- Partnerships with US DOTs (Michigan, New York)

**Revenue Target**: $5M ARR by Year 3

---

## 📚 References

- [OVIN Program Guidelines](https://www.ovinhub.ca/wp-content/uploads/2025/02/OVIN-QEW-IC-Program-Guidelines-Final-Version-2024.11.18.pdf)
- [MTO COMPASS System](http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml)
- [V2X-Hub Documentation](https://github.com/usdot-fhwa-OPS/V2X-Hub)
- [SAE J2735 Standard](https://www.sae.org/standards/content/j2735_202309/)
- [Google Cloud Platform](https://cloud.google.com/)
- [Anthropic Claude API](https://www.anthropic.com/api)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Owner**: ADBA Labs
**Status**: Ready for OVIN Submission

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
