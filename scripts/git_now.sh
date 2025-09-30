#!/usr/bin/env bash
# One-command "push it now" helper.
# Usage:
#   make git-now
# or
#   GIT_REMOTE="git@github.com:you/your-repo.git" MSG="feat: first push" bash scripts/git_now.sh
set -euo pipefail

red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
note() { printf "\n== %s ==\n" "$*"; }

# Preconditions
if ! command -v git >/dev/null 2>&1; then
  red "Git is not installed or not in PATH."; exit 1;
fi

if [ ! -d .git ]; then
  note "Initializing new git repository"
  git init
fi

# Ensure we are not in a detached HEAD state
CUR_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ -z "$CUR_BRANCH" ] || [ "$CUR_BRANCH" = "HEAD" ]; then
  note "Creating/switching to main branch"
  git switch -c main 2>/dev/null || git switch main 2>/dev/null || git checkout -b main
  CUR_BRANCH=main
fi

# Stage changes
note "Staging all changes"
git add -A

# Commit if there is anything to commit
set +e
CHANGES=$(git diff --cached --name-only)
set -e
if [ -n "$CHANGES" ]; then
  MSG=${MSG:-"chore: quick push"}
  note "Committing changes: $MSG"
  git commit -m "$MSG"
else
  yellow "No staged changes to commit. Proceeding to push any existing commits."
fi

# Ensure remote origin exists
set +e
HAS_ORIGIN=$(git remote | grep -E '^origin$')
set -e
if [ -z "$HAS_ORIGIN" ]; then
  if [ -z "${GIT_REMOTE:-}" ]; then
    red "No 'origin' remote configured. Set env var GIT_REMOTE to your repo URL, e.g."
    echo "  GIT_REMOTE=git@github.com:you/your-repo.git make git-now"
    echo "  or"
    echo "  GIT_REMOTE=https://github.com/you/your-repo.git make git-now"
    exit 2
  fi
  note "Adding origin remote: $GIT_REMOTE"
  git remote add origin "$GIT_REMOTE" || git remote set-url origin "$GIT_REMOTE"
fi

# Ensure branch is main by default if unborn
BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$BRANCH" ]; then
  BRANCH=main
fi

# Set upstream if missing and push
set +e
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
RC=$?
set -e
if [ $RC -ne 0 ]; then
  note "Pushing and setting upstream to origin/$BRANCH"
  git branch -M "$BRANCH"
  git push -u origin "$BRANCH"
else
  note "Pushing to $UPSTREAM"
  git push
fi

green "Push complete."
