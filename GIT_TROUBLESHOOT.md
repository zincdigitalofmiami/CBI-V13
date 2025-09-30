Title: Git Troubleshooting — “Nothing is showing up in Git”

Use this checklist to fix the most common causes when your IDE or terminal shows no changes or can’t see your repo files.

Quick commands (recommended)
- make git-doctor
  - Runs scripts/git_doctor.sh and prints status, remotes, branch, upstream, ignored files, and common fixes.
- make git-now
  - Stages, commits, and pushes the current repo. If 'origin' is missing, set GIT_REMOTE before running, e.g.:
    GIT_REMOTE=git@github.com:you/your-repo.git make git-now

1) Ensure you’re inside the correct folder
- pwd should be the CBI-V13 project root (where README.md and app/ exist).
- In JetBrains: Right‑click the top folder in Project View → Open in Terminal → run: ls

2) Verify the repository exists locally
- If .git folder is missing:
  - git init
  - git add .
  - git commit -m "init"

3) Add a remote and push
- git remote add origin <your-repo-url>
- git branch -M main
- git push -u origin main

4) If JetBrains IDE shows no VCS
- VCS → Enable Version Control Integration → select Git
- File → Settings → Version Control → ensure the project root is mapped to Git
- VCS → Git → Fetch/Refresh File Status

5) Fix “unsafe repository” error (common on macOS folders created by other users)
- git config --global --add safe.directory "$(pwd)"

6) Check ignored files
- Overly broad .gitignore (e.g., a single * line) can hide everything.
- Inspect repo .gitignore and global (~/.config/git/ignore or ~/.gitignore_global)
- Remove or narrow broad patterns; then run: git status --ignored

7) Detached HEAD or no upstream
- git switch -c main    # if ‘HEAD’ state
- After adding origin: git push -u origin main

8) Shallow clones / no history
- If CI created a shallow checkout: git fetch --unshallow

9) Network and auth
- If fetch/push fails:
  - Check VPN/Firewall; try another network
  - Verify remote URL: git remote -v; update with: git remote set-url origin <url>
  - For GitHub 2FA, use a Personal Access Token as password when prompted

10) Case sensitivity (macOS)
- macOS filesystems are often case-insensitive; renames that only change case may not show.
- Use git mv to rename with intermediate name, e.g., git mv File tmp && git mv tmp file

If still stuck
- Run: make git-doctor
- Copy the full output and share it; I’ll pinpoint the exact fix.
