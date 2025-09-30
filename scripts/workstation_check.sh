#!/usr/bin/env bash
# Validate and (optionally) start a Google Cloud Workstation and print connection guidance.
# Usage:
#   PROJECT_ID=cbi-v14 REGION=us-central1 CLUSTER=dev-cluster CONFIG=pycharm-config WORKSTATION=chris-dev \
#   bash scripts/workstation_check.sh
set -euo pipefail

# Read env vars
PROJECT_ID=${PROJECT_ID:-}
REGION=${REGION:-}
CLUSTER=${CLUSTER:-}
CONFIG=${CONFIG:-}
WORKSTATION=${WORKSTATION:-}

red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    red "Missing required command: $1"
    exit 1
  fi
}

need gcloud

if [[ -z "$PROJECT_ID" || -z "$REGION" || -z "$CLUSTER" || -z "$CONFIG" || -z "$WORKSTATION" ]]; then
  red "Set PROJECT_ID, REGION, CLUSTER, CONFIG, WORKSTATION environment variables."
  exit 1
fi

echo "Setting project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" >/dev/null

echo "Ensuring Cloud Workstations API is enabled..."
if ! gcloud services list --enabled --filter=workstations.googleapis.com --format='value(config.name)' | grep -q workstations.googleapis.com; then
  gcloud services enable workstations.googleapis.com --project "$PROJECT_ID"
fi

echo "Checking cluster ($CLUSTER) in $REGION..."
if ! gcloud workstations clusters describe "$CLUSTER" --region "$REGION" >/dev/null 2>&1; then
  red "Cluster '$CLUSTER' not found in region '$REGION'."
  exit 1
fi

echo "Checking config ($CONFIG)..."
if ! gcloud workstations configs describe "$CONFIG" --cluster "$CLUSTER" --region "$REGION" >/dev/null 2>&1; then
  red "Config '$CONFIG' not found in cluster '$CLUSTER'."
  exit 1
fi

echo "Checking workstation ($WORKSTATION)..."
if ! gcloud workstations describe "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" >/dev/null 2>&1; then
  red "Workstation '$WORKSTATION' not found."
  exit 1
fi

STATE=$(gcloud workstations describe "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" --format='value(state)')
LINK=$(gcloud workstations describe "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" --format='value(uris[0])' || true)

echo "Current state: $STATE"
if [[ -n "$LINK" ]]; then
  echo "Console link: $LINK"
fi

if [[ "$STATE" == "STOPPED" || "$STATE" == "SUSPENDED" ]]; then
  yellow "Workstation is $STATE. Starting..."
  gcloud workstations start "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" --async
  echo "Waiting for RUNNING (this may take 1-3 minutes)..."
  for i in {1..30}; do
    sleep 6
    STATE=$(gcloud workstations describe "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" --format='value(state)')
    echo "  -> $STATE"
    [[ "$STATE" == "RUNNING" ]] && break
  done
fi

if [[ "$STATE" == "RUNNING" ]]; then
  green "Workstation is RUNNING."
  echo "Probing SSH connectivity..."
  if gcloud workstations ssh "$WORKSTATION" --cluster "$CLUSTER" --config "$CONFIG" --region "$REGION" --command 'echo ok' 2>/dev/null | grep -q '^ok$'; then
    green "SSH probe ok."
  else
    yellow "SSH probe did not return 'ok'. There may be IAM/network issues; share the SSH error if shown above."
  fi
  cat <<EOF
Next steps (JetBrains Gateway):
1) Open JetBrains Gateway
2) New Connection -> Google Cloud Workstations
3) Select project '$PROJECT_ID' and region '$REGION'
4) Choose '$WORKSTATION' (config '$CONFIG' on cluster '$CLUSTER')
5) Pick PyCharm and connect
Note: Console's "Open in IDE" may not appear for JetBrains images; using Gateway is expected.
EOF
else
  red "Workstation state is '$STATE'. If it doesn't reach RUNNING, check IAM permissions and logs in Cloud Console."
fi
