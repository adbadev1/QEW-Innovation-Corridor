# Git Worktree Quick Reference

## 🚀 Quick Commands

```bash
# Create new worktree
./worktree-setup.sh create <branch-name> [port]

# List all worktrees
./worktree-setup.sh list

# Remove worktree
./worktree-setup.sh remove <branch-name>

# Cleanup deleted worktrees
./worktree-setup.sh cleanup
```

## 📋 Common Examples

### Create Feature Branch Worktree
```bash
./worktree-setup.sh create feature-ml-validation 8300
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-ml-validation
npm run dev  # Runs on port 8300
```

### Create Bugfix Worktree
```bash
./worktree-setup.sh create hotfix-camera-loading 8400
cd /Users/adbalabs/QEW-Innovation-Corridor-hotfix-camera-loading
npm run dev  # Runs on port 8400
```

### Multiple Parallel Sessions
```bash
# Session 1 (Main) - Port 8200
cd /Users/adbalabs/QEW-Innovation-Corridor
npm run dev

# Session 2 (Feature A) - Port 8300
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-a
npm run dev

# Session 3 (Feature B) - Port 8400
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-b
npm run dev
```

## 🎯 Port Assignment Strategy

| Port Range | Purpose | Example |
|-----------|---------|---------|
| 8200 | Main development | Main branch (default) |
| 8300-8399 | Feature branches | feature-ml-validation |
| 8400-8499 | Bugfix branches | hotfix-camera-crash |
| 8500-8599 | Experimental branches | experiment-mapbox |

## 🔄 Workflow

### 1. Create Worktree
```bash
./worktree-setup.sh create my-feature 8300
```

### 2. Work on Feature
```bash
cd /Users/adbalabs/QEW-Innovation-Corridor-my-feature
npm run dev
# Open Claude Code in this directory
# Make changes, commit
```

### 3. Merge to Main
```bash
cd /Users/adbalabs/QEW-Innovation-Corridor
git merge my-feature
```

### 4. Cleanup
```bash
./worktree-setup.sh remove my-feature
```

## 💡 Pro Tips

- **One feature = One worktree** - Keep work isolated
- **Short-lived** - Remove worktrees after merging
- **List often** - Run `./worktree-setup.sh list` to see active worktrees
- **Different ports** - Each worktree needs unique port number
- **Share .env** - API keys are copied automatically

## 🔧 Troubleshooting

**Port already in use?**
```bash
./worktree-setup.sh create my-feature 8350  # Use different port
```

**Deleted directory manually?**
```bash
./worktree-setup.sh cleanup  # Clean git metadata
```

**Branch already checked out?**
```bash
./worktree-setup.sh list  # Find which worktree has it
./worktree-setup.sh remove existing-branch  # Remove it first
```

## 📚 Full Documentation

See [WORKTREE_GUIDE.md](./WORKTREE_GUIDE.md) for complete guide with:
- Architecture details
- Advanced workflows
- Claude Code integration
- Best practices
- Troubleshooting

---

**Ready to start?**
```bash
# Example: Create your first worktree
./worktree-setup.sh create feature-my-awesome-feature 8300
cd /Users/adbalabs/QEW-Innovation-Corridor-feature-my-awesome-feature
npm run dev
```
