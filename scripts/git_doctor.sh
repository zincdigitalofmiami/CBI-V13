#!/usr/bin/env bash
# Quick Git diagnostics for "nothing is showing up in git" issues.
# Usage: bash scripts/git_doctor.sh
set -euo pipefail

red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

note() { printf "\n== %s ==\n" "$*"; }

if ! command -v git >/dev/null 2>&1; then
  red "Git is not installed or not in PATH."; exit 1;
fi

note "Git version"
git --version || true

note ".git directory present?"
if [ -d .git ]; then
  green ".git exists"
else
  red ".git missing. Initialize the repo: git init && git add . && git commit -m 'init'"
  exit 0
fi

note "Current directory"
pwd

echo
note "Repository status"
set +e
git status --porcelain=v1 --branch
STATUS_CODE=$?
set -e
if [ $STATUS_CODE -ne 0 ]; then
  red "git status failed. If you see 'unsafe repository', run: git config --global --add safe.directory '$(pwd)'"
fi

note "Remotes"
if git remote -v | sed 's/[[:space:]].*//' | uniq | grep -q .; then
  git remote -v
else
  yellow "No remotes configured. Add one: git remote add origin <your-repo-url>"
fi

note "Current branch"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(unknown)")
echo "$BRANCH"
if [ "$BRANCH" = "HEAD" ]; then
  yellow "You are in a detached HEAD state. Create/switch branch: git switch -c main"
fi

note "Upstream tracking"
set +e
UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
RC=$?
set -e
if [ $RC -ne 0 ]; then
  yellow "No upstream set. After adding origin, run: git push -u origin $(git branch --show-current)"
else
  echo "$UPSTREAM"
fi

note "Fetch test"
if git remote -v | grep -q origin; then
  set +e
  git fetch --dry-run origin
  RC=$?
  set -e
  if [ $RC -ne 0 ]; then
    yellow "Fetch failed. Check network/VPN and that the remote URL is correct."
  fi
fi

note "Ignored files check (top-level)"
# Show if current directory is ignored by any rule
if git check-ignore -v . >/dev/null 2>&1; then
  red "This directory is ignored by .gitignore or global gitignore. Check .gitignore and ~/.config/git/ignore."
  git check-ignore -v . || true
fi

note "Untracked files (first 100)"
# Show first 100 untracked for visibility
UNTRACKED=$(git ls-files --others --exclude-standard | head -n 100)
if [ -z "$UNTRACKED" ]; then
  yellow "No untracked files detected. If you expected changes, ensure you are in the correct folder and files are saved."
else
  echo "$UNTRACKED"
fi

note "Common fixes"
cat <<'EOF'
1) Initialize repo if missing:
   git init && git add . && git commit -m "init"
2) Add remote and push:
   git remote add origin <url>
   git branch -M main
   git push -u origin main
3) If IDE shows nothing, map the project to Git:
   JetBrains: VCS -> Enable Version Control Integration -> Git
4) If "unsafe repository" error:
   git config --global --add safe.directory "$(pwd)"
5) If fetch/push blocked:
   - Check VPN/Firewall; try another network
   - Verify remote URL: git remote set-url origin <url>
6) If files are ignored unexpectedly:
   - Inspect .gitignore in repo and global (~/.config/git/ignore)
   - Remove overly broad patterns (like *)
EOF

green "Git doctor finished."
