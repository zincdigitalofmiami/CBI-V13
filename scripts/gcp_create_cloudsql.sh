#!/usr/bin/env bash
# Create a new Cloud SQL for Postgres instance for CBI-V13 with IAM DB Auth enabled.
# Usage:
#   PROJECT_ID=cbi-v13 REGION=us-central1 INSTANCE=cbi-v13-sql DB_NAME=cbi ./scripts/gcp_create_cloudsql.sh
# Optional:
#   TIER=db-custom-1-3840 (or db-f1-micro for dev), PG_VERSION=POSTGRES_15
# Notes:
# - This script enables IAM database authentication and creates the database.
# - You may grant IAM DB access to a Cloud Run service account separately.
set -euo pipefail

PROJECT_ID=${PROJECT_ID:?set PROJECT_ID}
REGION=${REGION:?set REGION}
INSTANCE=${INSTANCE:-cbi-v13-sql}
DB_NAME=${DB_NAME:-cbi}
TIER=${TIER:-db-f1-micro}
PG_VERSION=${PG_VERSION:-POSTGRES_15}

# Enable API
gcloud services enable sqladmin.googleapis.com --project "$PROJECT_ID"

# Create instance (public IP)
if ! gcloud sql instances describe "$INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql instances create "$INSTANCE" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --database-version "$PG_VERSION" \
    --tier "$TIER" \
    --availability-type=zonal \
    --storage-auto-increase \
    --enable-point-in-time-recovery || true
fi

# Enable IAM DB Auth
gcloud sql instances patch "$INSTANCE" \
  --project "$PROJECT_ID" \
  --database-flags=cloudsql.iam_authentication=on

# Create database if missing
if ! gcloud sql databases describe "$DB_NAME" --instance "$INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql databases create "$DB_NAME" --instance "$INSTANCE" --project "$PROJECT_ID"
fi

# Output connection name
CONN_NAME=$(gcloud sql instances describe "$INSTANCE" --project "$PROJECT_ID" --format='value(connectionName)')
echo "Instance connection name: $CONN_NAME"
echo "Next: deploy Cloud Run with USE_IAM_AUTH=true CLOUD_SQL_CONNECTION_NAME=$CONN_NAME DB_USER=postgres DB_NAME=$DB_NAME"