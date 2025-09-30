Title: Connect and Verify Google Cloud Workstations (JetBrains Gateway)

Overview
Use this guide and the included script to verify that your Google Cloud Workstation is up, reachable, and ready for JetBrains Gateway (PyCharm). It also includes a quick SSH probe and idle-timeout tips to prevent disconnects.

Prerequisites
- gcloud CLI installed and authenticated: gcloud auth login
- Project selected: gcloud config set project <PROJECT_ID>
- Cloud Workstations API enabled
- You already created a Workstation cluster, config, and workstation. If not, ask and I’ll provision a known‑good config for PyCharm.

Key identifiers
- PROJECT_ID: your GCP project (e.g., cbi-v14)
- REGION: region (e.g., us-central1)
- CLUSTER: workstation cluster (e.g., cbi-v14-ws)
- CONFIG: workstation config (e.g., config-abc123)
- WORKSTATION: workstation name (e.g., w-zinc-xyz)

Quick state check (recommended)
Run from your shell (replace values):
PROJECT_ID=cbi-v14 REGION=us-central1 CLUSTER=cbi-v14-ws CONFIG=config-mg5r5y45 WORKSTATION=w-zinc-mg5rb0vm \
  bash scripts/workstation_check.sh

What the script does
- Ensures Workstations API is enabled
- Verifies cluster/config/workstation
- Starts the workstation if it’s STOPPED and waits until RUNNING
- Performs an optional SSH connectivity probe (echo ok)
- Prints the correct connection instructions for JetBrains Gateway

Connect with JetBrains Gateway (PyCharm)
Important: For JetBrains, use the JetBrains Gateway “Google Cloud Workstations” provider (not a Console “Open in IDE” button, which is typically for browser editors).

Steps:
1) Start the workstation and wait for RUNNING (use the script above or gcloud start+describe loop).
2) Open JetBrains Gateway → New Connection → Google Cloud Workstations.
3) Select your Google account, Project, and Region.
4) Pick your workstation and choose PyCharm.
5) When prompted for a folder, choose your home directory (/home/USER) or /home/USER/workstations. It’s okay if it’s empty—you’ll clone the repo next inside PyCharm.
6) After connecting, in PyCharm: VCS → Get from Version Control → paste your repo URL → clone to /home/USER/workstations/CBI-V13 → Open.

Connectivity probe (diagnostic)
Use this to distinguish Gateway issues vs. workstation/IAM issues. Run when the workstation is RUNNING:

gcloud workstations ssh "$WORKSTATION" \
  --cluster "$CLUSTER" \
  --config "$CONFIG" \
  --region "$REGION" \
  --command 'echo ok'

- If it prints ok: IAM and network are fine; focus on Gateway sign‑in and selection.
- If it fails: share the error; we’ll fix IAM (roles/workstations.user), API enablement, or config.

Idle timeout tip (prevents auto‑STOP)
If your workstation flips back to STOPPED before you can connect, increase the idle timeout to 1–2 hours in the Workstation Config.
- Console: Workstations → Configs → Edit → Idle timeout → set to something like 2h.
- CLI (if supported by your gcloud version):
  gcloud workstations configs update "$CONFIG" \
    --cluster "$CLUSTER" \
    --region "$REGION" \
    --idle-timeout=7200s

After you connect
- Clone the repo via VCS → Get from Version Control… into /home/USER/workstations/CBI-V13
- Create venv and install deps:
  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
- If using Cloud SQL with IAM auth:
  export USE_IAM_AUTH=true CLOUD_SQL_CONNECTION_NAME=project:region:instance DB_USER=postgres DB_NAME=cbi
- Apply schema and run pipelines/app:
  python scripts/apply_schema.py && python run_all.py && streamlit run app/Home.py --server.port 8080 --server.address 0.0.0.0

If any step fails, copy the exact error text and I’ll resolve immediately.