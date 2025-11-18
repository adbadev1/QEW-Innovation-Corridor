#!/bin/bash
#
# Git Worktree Manager for QEW Innovation Corridor
# Enables running multiple Claude Code sessions in parallel
#
# Usage:
#   ./worktree-setup.sh create <branch-name> [port]
#   ./worktree-setup.sh list
#   ./worktree-setup.sh remove <branch-name>
#   ./worktree-setup.sh cleanup
#

set -e

PROJECT_NAME="QEW-Innovation-Corridor"
WORKTREE_BASE_DIR="/Users/adbalabs"
MAIN_WORKTREE="${WORKTREE_BASE_DIR}/${PROJECT_NAME}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function: Create new worktree
create_worktree() {
    local branch_name=$1
    local port=${2:-8300}  # Default to port 8300 if not specified

    if [ -z "$branch_name" ]; then
        echo -e "${RED}Error: Branch name required${NC}"
        echo "Usage: $0 create <branch-name> [port]"
        exit 1
    fi

    local worktree_path="${WORKTREE_BASE_DIR}/${PROJECT_NAME}-${branch_name}"

    # Check if worktree already exists
    if [ -d "$worktree_path" ]; then
        echo -e "${RED}Error: Worktree already exists at ${worktree_path}${NC}"
        exit 1
    fi

    echo -e "${BLUE}Creating worktree for branch: ${branch_name}${NC}"

    # Check if branch exists
    if git show-ref --verify --quiet refs/heads/${branch_name}; then
        echo -e "${YELLOW}Branch '${branch_name}' exists, checking out...${NC}"
        git worktree add "${worktree_path}" "${branch_name}"
    else
        echo -e "${YELLOW}Branch '${branch_name}' doesn't exist, creating new branch...${NC}"
        git worktree add -b "${branch_name}" "${worktree_path}"
    fi

    # Copy .env file if it exists
    if [ -f "${MAIN_WORKTREE}/.env" ]; then
        echo -e "${BLUE}Copying .env file...${NC}"
        cp "${MAIN_WORKTREE}/.env" "${worktree_path}/.env"

        # Update port in .env
        if grep -q "VITE_PORT" "${worktree_path}/.env"; then
            sed -i.bak "s/VITE_PORT=.*/VITE_PORT=${port}/" "${worktree_path}/.env"
            rm "${worktree_path}/.env.bak"
        else
            echo "VITE_PORT=${port}" >> "${worktree_path}/.env"
        fi
    fi

    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    cd "${worktree_path}"
    npm install

    echo ""
    echo -e "${GREEN}✓ Worktree created successfully!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Branch:${NC}     ${branch_name}"
    echo -e "${BLUE}Path:${NC}       ${worktree_path}"
    echo -e "${BLUE}Dev Port:${NC}   ${port}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. cd ${worktree_path}"
    echo -e "  2. npm run dev  (will run on port ${port})"
    echo -e "  3. Open new Claude Code session in this directory"
    echo ""
}

# Function: List all worktrees
list_worktrees() {
    echo -e "${BLUE}Git Worktrees:${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    git worktree list
    echo ""
}

# Function: Remove worktree
remove_worktree() {
    local branch_name=$1

    if [ -z "$branch_name" ]; then
        echo -e "${RED}Error: Branch name required${NC}"
        echo "Usage: $0 remove <branch-name>"
        exit 1
    fi

    local worktree_path="${WORKTREE_BASE_DIR}/${PROJECT_NAME}-${branch_name}"

    if [ ! -d "$worktree_path" ]; then
        echo -e "${RED}Error: Worktree doesn't exist at ${worktree_path}${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Removing worktree: ${worktree_path}${NC}"
    git worktree remove "${worktree_path}"

    echo -e "${GREEN}✓ Worktree removed${NC}"

    # Ask if user wants to delete the branch
    read -p "Delete branch '${branch_name}'? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -D "${branch_name}"
        echo -e "${GREEN}✓ Branch deleted${NC}"
    fi
}

# Function: Cleanup prunable worktrees
cleanup_worktrees() {
    echo -e "${BLUE}Cleaning up removed worktrees...${NC}"
    git worktree prune
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main command dispatcher
case "${1}" in
    create)
        create_worktree "${2}" "${3}"
        ;;
    list)
        list_worktrees
        ;;
    remove)
        remove_worktree "${2}"
        ;;
    cleanup)
        cleanup_worktrees
        ;;
    *)
        echo "Git Worktree Manager for QEW Innovation Corridor"
        echo ""
        echo "Usage:"
        echo "  $0 create <branch-name> [port]  - Create new worktree (default port: 8300)"
        echo "  $0 list                          - List all worktrees"
        echo "  $0 remove <branch-name>          - Remove worktree"
        echo "  $0 cleanup                       - Cleanup prunable worktrees"
        echo ""
        echo "Examples:"
        echo "  $0 create feature-ml-validation 8300"
        echo "  $0 create bugfix-camera-loading 8400"
        echo "  $0 list"
        echo "  $0 remove feature-ml-validation"
        exit 1
        ;;
esac
