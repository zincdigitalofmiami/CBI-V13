#!/bin/bash
# Google Cloud Setup Script for CBI-V13
# Run this script to set up the complete Google Cloud infrastructure

set -euo pipefail

# Configuration - Update these values for your project
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
ZONE=${ZONE:-"us-central1-a"}
INSTANCE_NAME=${INSTANCE_NAME:-"cbi-v13-sql"}
DB_NAME=${DB_NAME:-"cbi_v13"}
DB_USER=${DB_USER:-"postgres"}
SERVICE_ACCOUNT_NAME=${SERVICE_ACCOUNT_NAME:-"cbi-v13-runner"}
REPO_NAME=${REPO_NAME:-"cbi-v13-repo"}

echo "Setting up CBI-V13 on Google Cloud Platform..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudsql.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    compute.googleapis.com

# Create service account for Cloud Run
echo "Creating service account: $SERVICE_ACCOUNT_NAME..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1; then
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --description="Service account for CBI-V13 Cloud Run services" \
        --display-name="CBI-V13 Runner"
fi

# Grant necessary roles to the service account
echo "Granting IAM roles to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create Artifact Registry repository
echo "Creating Artifact Registry repository: $REPO_NAME..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION >/dev/null 2>&1; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="CBI-V13 container images"
fi

# Create Cloud SQL instance
echo "Creating Cloud SQL instance: $INSTANCE_NAME..."
if ! gcloud sql instances describe $INSTANCE_NAME >/dev/null 2>&1; then
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=20GB \
        --database-flags=cloudsql.iam_authentication=on

    # Create database
    echo "Creating database: $DB_NAME..."
    gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME

    # Create database user with IAM authentication
    echo "Creating database user: $DB_USER..."
    gcloud sql users create $DB_USER \
        --instance=$INSTANCE_NAME \
        --type=cloud_iam_service_account

    # Grant database access to the service account
    echo "Granting database access to service account..."
    gcloud sql users create "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --instance=$INSTANCE_NAME \
        --type=cloud_iam_service_account
else
    echo "Cloud SQL instance $INSTANCE_NAME already exists."
fi

# Create admin token secret in Secret Manager
echo "Creating admin token secret..."
if ! gcloud secrets describe admin-token >/dev/null 2>&1; then
    echo -n "$(openssl rand -hex 32)" | gcloud secrets create admin-token --data-file=-
fi

echo ""
echo "✅ Google Cloud setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with:"
echo "   CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo ""
echo "2. Apply the database schema:"
echo "   python scripts/apply_schema.py"
echo ""
echo "3. Deploy using Cloud Build:"
echo "   gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "4. Or deploy manually:"
echo "   make gcp-deploy"
echo ""
echo "Cloud SQL connection name: $PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "Service account: ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Artifact Registry: $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"