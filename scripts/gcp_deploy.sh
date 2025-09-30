#!/usr/bin/env bash
# Deploy CBI-V13 to Google Cloud Run (app) and create a Cloud Run Job (pipelines)
# Supports two modes:
#  1) DATABASE_URL (any Postgres)
#  2) Cloud SQL IAM Auth (no JSON key) with CLOUD_SQL_CONNECTION_NAME
#
# Required env:
#  PROJECT_ID, REGION
# Optional env:
#  REPO (Artifact Registry repo name, default: cbi-v13-repo)
#  IMAGE_NAME (default: cbi-v13)
#  ADMIN_TOKEN, REFRESH_HOURS (default 8)
#  Mode A: DATABASE_URL
#  Mode B: USE_IAM_AUTH=true, CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_NAME
set -euo pipefail

PROJECT_ID=${PROJECT_ID:?set PROJECT_ID}
REGION=${REGION:?set REGION}
REPO=${REPO:-cbi-v13-repo}
IMAGE_NAME=${IMAGE_NAME:-cbi-v13}
ADMIN_TOKEN=${ADMIN_TOKEN:-change-me}
REFRESH_HOURS=${REFRESH_HOURS:-8}

IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$IMAGE_NAME:latest"

# Enable required services
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudscheduler.googleapis.com cloudbuild.googleapis.com --project "$PROJECT_ID"

# Create repo if it doesn't exist
if ! gcloud artifacts repositories describe "$REPO" --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="CBI-V13 container repo" \
    --project="$PROJECT_ID"
fi

gcloud auth configure-docker "$REGION-docker.pkg.dev" -q

echo "Building and pushing image: $IMAGE"
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"

APP_ENV=("ADMIN_TOKEN=$ADMIN_TOKEN" "REFRESH_HOURS=$REFRESH_HOURS")
JOB_ENV=("ADMIN_TOKEN=$ADMIN_TOKEN" "REFRESH_HOURS=$REFRESH_HOURS")

if [[ "${USE_IAM_AUTH:-false}" == "true" ]]; then
  : "${CLOUD_SQL_CONNECTION_NAME:?set CLOUD_SQL_CONNECTION_NAME}"
  DB_USER=${DB_USER:-postgres}
  DB_NAME=${DB_NAME:-postgres}
  APP_ENV+=("USE_IAM_AUTH=true" "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" "DB_USER=$DB_USER" "DB_NAME=$DB_NAME")
  JOB_ENV+=("USE_IAM_AUTH=true" "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" "DB_USER=$DB_USER" "DB_NAME=$DB_NAME")
else
  : "${DATABASE_URL:?set DATABASE_URL or USE_IAM_AUTH=true}"
  APP_ENV+=("DATABASE_URL=$DATABASE_URL")
  JOB_ENV+=("DATABASE_URL=$DATABASE_URL")
fi

# Deploy app
APP_ENV_FLAGS=()
for kv in "${APP_ENV[@]}"; do APP_ENV_FLAGS+=(--set-env-vars "$kv"); done

gcloud run deploy cbi-v13-app \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  "${APP_ENV_FLAGS[@]}" \
  --project "$PROJECT_ID"

# Create or update job
JOB_ENV_FLAGS=()
for kv in "${JOB_ENV[@]}"; do JOB_ENV_FLAGS+=(--set-env-vars "$kv"); done

if gcloud run jobs describe cbi-v13-pipelines --region "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud run jobs update cbi-v13-pipelines \
    --image "$IMAGE" \
    --region "$REGION" \
    --task-timeout=3600 \
    "${JOB_ENV_FLAGS[@]}" \
    --command python --args run_all.py \
    --project "$PROJECT_ID"
else
  gcloud run jobs create cbi-v13-pipelines \
    --image "$IMAGE" \
    --region "$REGION" \
    --task-timeout=3600 \
    "${JOB_ENV_FLAGS[@]}" \
    --command python --args run_all.py \
    --project "$PROJECT_ID"
fi

echo "Triggering job once to verify..."
gcloud run jobs execute cbi-v13-pipelines --region "$REGION" --project "$PROJECT_ID" --wait

echo "Done. Check Cloud Run service URL and Job execution logs in the console."