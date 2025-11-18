# QEW Innovation Corridor - Digital Twin Dashboard

**OVIN Hackathon Project | Building Path to $150K Pilot Funding**

🌐 **Live Repository:** https://github.com/adbadev1/QEW-Innovation-Corridor
🚀 **Live Demo:** https://adbadev1.github.io/QEW-Innovation-Corridor/

## 🎯 Project Overview

**Real-time digital twin** of Ontario's QEW Innovation Corridor (40km Burlington-Toronto). AI-powered traffic management system featuring work zone safety monitoring, V2X alert generation, and COMPASS camera integration.

### Challenge Addressed
**OVIN Challenge #1: Work Zone Safety**
- Real-time hazard detection from traffic camera feeds
- Automated MTO BOOK 7 compliance checking
- RSU-ready alert generation for V2I communication

## 🏗️ Architecture

```
Traffic Camera Feed → Claude Vision API → Safety Analysis → V2X Alert Generation
                                              ↓
                                    Risk Assessment + Recommendations
```

## 🚀 Hackathon Deliverable (3 Hours)

**Interactive Artifact:** Upload work zone photos → Get instant AI safety analysis

### Features
- ✅ Image upload with drag-and-drop
- ✅ AI-powered hazard detection (workers, vehicles, equipment)
- ✅ Risk scoring (1-10 scale)
- ✅ MTO compliance checking
- ✅ Automated RSU alert message generation
- ✅ Actionable recommendations

## 📊 Technical Stack

- **Frontend:** React + Vite + Tailwind CSS + Leaflet
- **AI Engine:** Google Gemini 2.0 Flash (Vision API)
- **Real Data:** 46 COMPASS traffic cameras (MTO 511ON)
- **Deployment:** GitHub Pages (live demo)
- **Future:** GCP Cloud Run + V2X-Hub integration

## 🛣️ Path to Market

### Phase 1: MVP1 (Complete) ✅
- ✅ Interactive dashboard with real QEW data
- ✅ 46 COMPASS cameras integrated
- ✅ AI-powered work zone analysis (Gemini Vision)
- ✅ Image upload for real-time safety analysis
- ✅ Proof of concept deployed

### Phase 2: OVIN Application (2 weeks)
- Integrate with MTO COMPASS camera feeds
- Deploy production prototype
- Performance metrics collection

### Phase 3: Pilot Deployment (6 months)
- 40km QEW testbed deployment
- Real V2X RSU integration
- $150K pilot funding

### Phase 4: Scale (12 months)
- Province-wide deployment
- Multi-jurisdictional licensing
- Commercial partnerships

## 📁 Project Structure

```
QEW-Innovation-Corridor/
├── src/
│   ├── App.jsx                          # Main Digital Twin Dashboard
│   ├── components/
│   │   └── WorkZoneAnalysisPanel.jsx    # Work zone analyzer
│   ├── data/
│   │   └── qewData.js                   # QEW corridor data (13 cameras)
│   └── utils/
│       └── riskUtils.js                 # Risk assessment utilities
├── artifacts/
│   └── work-zone-safety-analyzer.jsx    # Original prototype (reference)
├── docs/
│   ├── MVP_WORKFLOW.md                  # 📊 Complete MVP roadmap (Mermaid diagrams)
│   ├── DEMO_SCRIPT.md                   # Presentation guide
│   └── ARCHITECTURE.md                  # Technical architecture
├── package.json
├── vite.config.js
└── README.md
```

## 📊 MVP Roadmap

**See detailed workflow:** [docs/MVP_WORKFLOW.md](docs/MVP_WORKFLOW.md)

- **Phase 0:** ✅ Hackathon Prototype (COMPLETE)
- **Phase 1:** OVIN Application (Week 1-4)
- **Phase 2:** Production Development (Month 1-2)
- **Phase 3:** Testing & Validation (Month 3-4)
- **Phase 4:** Pilot Deployment (Month 5-6)
- **Result:** 🎉 MVP Achieved

Full timeline with Mermaid diagrams, technical architecture evolution, and success metrics available in the workflow document.

## 🎤 Demo Script

**Opening (30 sec):**
> "Every year, 70 workers die in highway work zones across North America. We built an AI system that analyzes work zone safety in real-time and prevents accidents before they happen."

**Live Demo (90 sec):**
1. Upload QEW work zone photo
2. Show AI analysis in 3 seconds
3. Display risk score + identified hazards
4. Generate V2X alert message
5. Show MTO compliance report

**Close (30 sec):**
> "This is the future of smart highway safety. We're applying for OVIN's $150K pilot program to deploy this on all 40km of the QEW testbed."

## 🔗 Resources

- [OVIN Program Guidelines](https://www.ovinhub.ca/wp-content/uploads/2025/02/OVIN-QEW-IC-Program-Guidelines-Final-Version-2024.11.18.pdf)
- [MTO COMPASS System](http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml)
- [USDOT V2X-Hub (RSU Software)](https://github.com/usdot-fhwa-OPS/V2X-Hub)
- [SAE J2735 Standard](https://www.sae.org/standards/content/j2735_202309/)

## 👥 Team

**ADBA Labs**
- Domain Expertise: Enterprise IoT, BIM, Geospatial
- Business Acumen: M&A, Go-to-Market Strategy
- Technical Stack: Python, GCP, AI/ML

## 📧 Contact

- **Email:** adbalabs0101@gmail.com
- **OVIN Program Manager:** David Harris-Koblin (dharris-koblin@oc.innovation.ca)

## 📜 License

Proprietary - ADBA Labs
Prepared for OVIN QEW Innovation Corridor Program Application

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))

### Setup
```bash
# Clone the repository
git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
cd QEW-Innovation-Corridor

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env and add your VITE_GEMINI_API_KEY

# Run development server
npm run dev
```

Open http://localhost:8200 to view the dashboard!

### Testing AI Analysis
1. Click any mock work zone on the map
2. Upload a work zone image in the side panel
3. Get real-time AI safety analysis in 2-3 seconds!

---

**Built with Claude Code CLI** | **Powered by Google Gemini 2.0 Flash**
