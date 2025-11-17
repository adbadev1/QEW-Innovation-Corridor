# QEW Innovation Corridor - Quick Start Guide

**Time to Setup**: 5 minutes
**Prerequisites**: Node.js 18+, npm, git

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Clone Repository (30 seconds)
```bash
git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
cd QEW-Innovation-Corridor
```

### Step 2: Install Dependencies (2 minutes)
```bash
npm install
```

### Step 3: Start Dev Server (30 seconds)
```bash
npm run dev
```

### Step 4: Open Dashboard (immediate)
```
Browser automatically opens to: http://localhost:8200

If not, manually navigate to: http://localhost:8200
```

---

## ✅ Verify Installation

You should see:
- ✅ Leaflet map centered on QEW corridor (Burlington to Toronto)
- ✅ Blue markers (COMPASS cameras) - 38+ cameras
- ✅ Red markers (work zones) - 3 work zones
- ✅ Green markers (vehicles) - 10 simulated vehicles moving
- ✅ Right panel with AI Traffic Analyst

---

## 🎯 Next Steps

### For Demo Preparation
1. Review [DEMO_SCRIPT.md](../DEMO_SCRIPT.md) - Complete 3-minute presentation guide
2. Check [STATE_OF_THE_NATION.md](../../STATE_OF_THE_NATION.md) - Current project status

### For Development
1. Review [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical architecture
2. Review [QEW_ORGANIZATIONAL_FRAMEWORK.md](../adba-labs/QEW_ORGANIZATIONAL_FRAMEWORK.md) - Project standards
3. Check [Sprint 1 Plan](../sprints/Sprint1/SPRINT_PLAN.md) - Current sprint tasks

### For OVIN Application
1. Review [MVP_WORKFLOW.md](../MVP_WORKFLOW.md) - 6-month roadmap
2. Create docs/ovin/ directory (see Sprint 1 tasks)

---

## 🛠️ Common Commands

```bash
# Development
npm run dev          # Start dev server (port 8200)
npm run build        # Build for production
npm run preview      # Preview production build

# Deployment
npm run deploy       # Deploy to GitHub Pages

# Git workflow
git status           # Check changes
git add .            # Stage all changes
git commit -m "..."  # Commit with message
git push             # Push to GitHub
```

---

## 🔧 Configuration

### Port Configuration
- **Dev Server**: Port 8200 (standardized per [universal_port_config.md](/Users/adbalabs/config/universal_port_config.md))
- **Never use**: Port 3000 (conflicts with React/Next.js)

### Environment Variables (Optional)
```bash
# Copy template
cp .env.example .env

# Edit with your API keys (optional for demo)
# - VITE_CLAUDE_API_KEY (for live AI analysis)
```

---

## 📁 Project Structure

```
QEW-Innovation-Corridor/
├── src/
│   ├── App.jsx                    # Main Digital Twin Dashboard
│   ├── components/                # Reusable components
│   ├── data/                      # QEW data (cameras, routes)
│   └── utils/                     # Utilities (risk scoring)
├── docs/
│   ├── ARCHITECTURE.md            # Technical architecture
│   ├── DEMO_SCRIPT.md             # Presentation guide
│   ├── MVP_WORKFLOW.md            # Complete roadmap
│   ├── onboarding/                # Onboarding guides (you are here)
│   ├── sprints/                   # Sprint planning
│   └── adba-labs/                 # Framework documentation
├── public/
│   └── camera_images/             # Real COMPASS camera images
├── package.json                   # Dependencies
├── vite.config.js                 # Vite configuration (port 8200)
└── README.md                      # Project overview
```

---

## 🐛 Troubleshooting

### Port 8200 Already in Use
```bash
# Find what's using port 8200
lsof -i :8200

# Kill the process
kill -9 <PID>

# Or use a different port
npm run dev -- --port 8201
```

### Module Not Found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Map Not Showing
- Check browser console for errors
- Verify internet connection (Leaflet tiles need internet)
- Try hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

---

## 📚 Additional Resources

### Documentation
- [README.md](../../README.md) - Project overview
- [STATE_OF_THE_NATION.md](../../STATE_OF_THE_NATION.md) - Current status
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical details

### External Resources
- [OVIN Program](https://www.ovinhub.ca/)
- [MTO COMPASS](http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml)
- [Leaflet Docs](https://leafletjs.com/)
- [React Docs](https://react.dev/)

---

## 🆘 Getting Help

**GitHub Issues**: https://github.com/adbadev1/QEW-Innovation-Corridor/issues

**Contact**: adbalabs0101@gmail.com

**OVIN Program Manager**: David Harris-Koblin (dharris-koblin@oc.innovation.ca)

---

**Ready to start developing!** 🚀

Check out [Sprint 1 Plan](../sprints/Sprint1/SPRINT_PLAN.md) for current tasks.
