# Git Worktree Guide - Parallel Claude Code Sessions

This guide explains how to use git worktrees to run multiple Claude Code sessions in parallel on the QEW Innovation Corridor project.

## Why Git Worktrees?

Git worktrees allow you to:
- **Work on multiple features simultaneously** - No need to stash changes or switch branches
- **Run multiple dev servers** - Each worktree runs on a different port
- **Parallel Claude Code sessions** - Multiple Claude instances working on different tasks
- **Independent testing** - Test features in isolation without affecting main development

## Architecture

```
/Users/adbalabs/
├── QEW-Innovation-Corridor/              # Main worktree (port 8200) - MAIN BRANCH
├── QEW-Innovation-Corridor-camera-fix/   # Worktree #1 (port 8300) - camera-fix branch
├── QEW-Innovation-Corridor-ml-validation/# Worktree #2 (port 8400) - ml-validation branch
└── QEW-Innovation-Corridor-v2x-alerts/   # Worktree #3 (port 8500) - v2x-alerts branch
```

Each directory is a complete working copy with:
- Independent dev server (different port)
- Independent node_modules
- Independent .env configuration
- Same git repository (shared .git)

## Quick Start

### 1. Create a New Worktree

```bash
./worktree-setup.sh create <branch-name> [port]
```

**Example - Create worktree for ML validation feature:**
```bash
./worktree-setup.sh create feature-ml-validation 8300
```

This will:
1. Create new branch `feature-ml-validation` (or checkout existing)
2. Create directory `/Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation`
3. Copy `.env` file and update port to 8300
4. Run `npm install`
5. Ready for Claude Code!

### 2. Start Working in New Worktree

```bash
# Navigate to new worktree
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation

# Start dev server (runs on port 8300)
npm run dev

# Open new Claude Code session in this directory
# Now you can work on ML validation while main branch continues separately!
```

### 3. List All Worktrees

```bash
./worktree-setup.sh list
```

Output:
```
Git Worktrees:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/Users/adbalabs/QEW-Innovation-Corridor              50f2bc2 [main]
/Users/adbalabs/QEW-Innovation-Corridor-ml-validation a1b2c3d [feature-ml-validation]
/Users/adbalabs/QEW-Innovation-Corridor-camera-fix    d4e5f6g [bugfix-camera-loading]
```

### 4. Remove Worktree When Done

```bash
./worktree-setup.sh remove feature-ml-validation
```

This will:
1. Remove the worktree directory
2. Ask if you want to delete the branch (optional)

## Common Workflows

### Workflow 1: Multiple Feature Development

**Scenario:** Working on 3 features simultaneously with 3 Claude sessions

```bash
# Main branch - ongoing work
cd /Users/adbalabs/QEW-Innovation-Corridor
npm run dev  # Port 8200

# Feature 1 - ML validation panel
./worktree-setup.sh create feature-ml-validation 8300
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation
npm run dev  # Port 8300

# Feature 2 - Camera collection improvements
./worktree-setup.sh create feature-camera-improvements 8400
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-camera-improvements
npm run dev  # Port 8400

# Feature 3 - V2X RSU integration
./worktree-setup.sh create feature-v2x-rsu 8500
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-v2x-rsu
npm run dev  # Port 8500
```

Now you have:
- **4 dev servers running** (ports 8200, 8300, 8400, 8500)
- **4 Claude Code sessions** (one per directory)
- **Independent development** on each feature

### Workflow 2: Hotfix While Feature in Progress

**Scenario:** Working on large feature, urgent bug needs fixing

```bash
# Current: Working on ML validation in main worktree
# Emergency: Production bug in camera loading

# Create hotfix worktree
./worktree-setup.sh create hotfix-camera-crash 8300
cd /Users/adbalabs/QEW-Innovation-Corridor-hotfix-camera-crash

# Open new Claude Code session
# Fix bug, test, commit
git add .
git commit -m "Fix camera crash on missing metadata"

# Merge hotfix to main
cd /Users/adbalabs/QEW-Innovation-Corridor
git merge hotfix-camera-crash

# Continue with ML validation feature (no context lost!)
```

### Workflow 3: Testing Different Approaches

**Scenario:** Try two different implementations to compare

```bash
# Approach 1: Use Leaflet for maps
./worktree-setup.sh create experiment-leaflet 8300

# Approach 2: Use MapBox for maps
./worktree-setup.sh create experiment-mapbox 8400

# Test both simultaneously on different ports
# Keep the better implementation
```

## Port Management

Default ports for each worktree:
- **Main worktree:** 8200 (default Vite port from .env)
- **Worktree 1:** 8300 (specified in create command)
- **Worktree 2:** 8400 (specified in create command)
- **Worktree 3:** 8500 (specified in create command)

Each worktree's `.env` file is automatically updated with the specified port:
```
VITE_PORT=8300
```

## Claude Code Integration

### Opening Multiple Claude Sessions

1. **Terminal 1 - Main Branch:**
   ```bash
   cd /Users/adbalabs/QEW-Innovation-Corridor
   claude code
   # Works on main branch (port 8200)
   ```

2. **Terminal 2 - Feature Branch:**
   ```bash
   cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation
   claude code
   # Works on feature-ml-validation branch (port 8300)
   ```

3. **Terminal 3 - Another Feature:**
   ```bash
   cd /Users/adbalabs/QEW-Innovation-Corridor-camera-improvements
   claude code
   # Works on feature-camera-improvements branch (port 8400)
   ```

### Coordinating Multiple Claude Sessions

**Example task delegation:**

**Claude Session 1 (Main):** "Monitor all other branches and integrate completed features"
**Claude Session 2 (ML Validation):** "Implement ML Vision Model Validation Panel with real-time analysis"
**Claude Session 3 (Camera):** "Fix camera loading race conditions and improve error handling"
**Claude Session 4 (V2X):** "Integrate V2X RSU broadcast system with MTO BOOK 7 compliance"

Each Claude instance works independently, commits to their branch, and you merge when ready.

## Git Operations Across Worktrees

### Committing in Worktrees

Each worktree commits independently:

```bash
# In worktree 1
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation
git add .
git commit -m "Add ML validation panel"

# In worktree 2
cd /Users/adbalabs/QEW-Innovation-Corridor-camera-improvements
git add .
git commit -m "Fix camera race condition"
```

### Merging Features Back to Main

```bash
# Switch to main worktree
cd /Users/adbalabs/QEW-Innovation-Corridor

# Merge feature branch
git merge feature-ml-validation

# If conflicts, resolve and commit
git add .
git commit -m "Merge ML validation feature"

# Feature is now in main, can remove worktree
./worktree-setup.sh remove feature-ml-validation
```

### Syncing Changes from Main to Feature Branch

```bash
# In feature worktree
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation

# Get latest from main
git fetch origin main
git merge origin/main

# Or rebase to keep linear history
git rebase origin/main
```

## Best Practices

### 1. One Feature = One Worktree
Create a worktree for each distinct feature or bugfix.

### 2. Short-Lived Worktrees
Remove worktrees after merging features to keep workspace clean.

### 3. Port Consistency
Use consistent port numbering:
- 8200: Main development
- 8300-8399: Feature branches
- 8400-8499: Bugfix branches
- 8500-8599: Experimental branches

### 4. Regular Cleanup
Periodically run cleanup:
```bash
./worktree-setup.sh cleanup
```

### 5. Shared .env Secrets
When creating worktrees, sensitive .env values are copied from main.
Update them in each worktree if needed:
```bash
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation
nano .env  # Update API keys if testing different credentials
```

### 6. Independent node_modules
Each worktree has its own `node_modules`:
- Install dependencies independently
- Different dependency versions if needed
- No conflicts between worktrees

## Troubleshooting

### Error: "Fatal: Could not create worktree"

**Cause:** Uncommitted changes in current worktree

**Solution:** Commit or stash changes first
```bash
git add .
git commit -m "WIP: Current progress"
# Or
git stash
```

### Error: "Port already in use"

**Cause:** Another dev server running on same port

**Solution:** Use different port number
```bash
./worktree-setup.sh create my-feature 8350  # Different port
```

### Worktree Directory Deleted Manually

**Problem:** Deleted worktree directory without using `remove` command

**Solution:** Cleanup git metadata
```bash
./worktree-setup.sh cleanup
```

### Branch Already Checked Out

**Error:** "Branch is already checked out at ..."

**Cause:** Branch already in use by another worktree

**Solution:** Use different branch name or remove existing worktree
```bash
./worktree-setup.sh list  # Find which worktree has the branch
./worktree-setup.sh remove existing-branch  # Remove it
```

## Advanced Usage

### Custom Branch from Specific Commit

```bash
# Create worktree from specific commit
git worktree add -b hotfix-v1.0 /Users/adbalabs/QEW-Innovation-Corridor-hotfix-v1.0 abc123f
```

### Temporary Worktree for Testing

```bash
# Create, test, and remove in one workflow
./worktree-setup.sh create temp-test 8600
cd /Users/adbalabs/QEW-Innovation-Corridor-temp-test
npm run dev
# Test feature...
cd /Users/adbalabs/QEW-Innovation-Corridor
./worktree-setup.sh remove temp-test
```

### Sharing Worktrees Across Projects

Each project can have its own worktree setup:
```bash
# QEW Innovation Corridor
cd /Users/adbalabs/QEW-Innovation-Corridor
./worktree-setup.sh create feature-x 8300

# Other Project
cd /Users/adbalabs/other-project
./worktree-setup.sh create feature-y 9300
```

## Summary

Git worktrees enable **truly parallel development** with multiple Claude Code sessions:

✅ **Independent workspaces** - No branch switching
✅ **Concurrent development** - Multiple features at once
✅ **Isolated testing** - Different ports per worktree
✅ **Fast context switching** - Just `cd` to different directory
✅ **Clean git history** - Each feature on separate branch

**Next Steps:**
1. Create your first worktree: `./worktree-setup.sh create my-feature 8300`
2. Start dev server: `cd /Users/adbalabs/QEW-Innovation-Corridor-my-feature && npm run dev`
3. Open Claude Code in new worktree directory
4. Work on feature independently!

---

**Need Help?**
- List all worktrees: `./worktree-setup.sh list`
- View script help: `./worktree-setup.sh`
- Git worktree docs: `git worktree --help`
