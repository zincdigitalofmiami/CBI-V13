# Deploy CBI-V13 to Google Cloud

This guide provides complete setup for deploying CBI-V13 to Google Cloud using:
- **Cloud SQL** for PostgreSQL database with IAM authentication
- **Cloud Run** for the Streamlit web application
- **Cloud Run Jobs** for data pipeline execution
- **Cloud Build** for automated deployment

## Quick Setup

Run the automated setup script:

```bash
# Set your project ID first
export PROJECT_ID=your-project-id

# Run the setup script
./scripts/gcp_setup.sh
```

This script will:
- Enable required Google Cloud APIs
- Create Cloud SQL instance with IAM auth
- Set up Artifact Registry
- Create necessary service accounts and IAM bindings
- Generate admin token secret

## Manual Setup (Alternative)

If you prefer manual setup, follow the detailed steps below.

### Prerequisites
- Google Cloud project with billing enabled
- `gcloud` CLI authenticated: `gcloud auth login && gcloud config set project YOUR_PROJECT_ID`
- Required APIs enabled (or run the setup script)

1) Configure environment
- export PROJECT_ID=cbi-v13
- export REGION=us-central1   # pick your region
- export REPO=cbi-v13-repo

2) Create Artifact Registry repo (for container images)
- gcloud artifacts repositories create $REPO \
    --project=$PROJECT_ID \
    --repository-format=docker \
    --location=$REGION \
    --description="Container repo for CBI-V13"
- gcloud auth configure-docker $REGION-docker.pkg.dev

3) Build and push the container
- IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/cbi-v13:latest
- gcloud builds submit --tag $IMAGE

4) Deploy the Streamlit app to Cloud Run
Option A — Using DATABASE_URL (any Postgres):
- gcloud run deploy cbi-v13-app \
    --image $IMAGE \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars DATABASE_URL="<paste>" \
    --set-env-vars ADMIN_TOKEN="<token>" \
    --set-env-vars REFRESH_HOURS="8"

Option B — Using Cloud SQL IAM Auth (no DB URL):
- gcloud run deploy cbi-v13-app \
    --image $IMAGE \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars USE_IAM_AUTH=true \
    --set-env-vars CLOUD_SQL_CONNECTION_NAME="<project:region:instance>" \
    --set-env-vars DB_USER="postgres" \
    --set-env-vars DB_NAME="cbi" \
    --set-env-vars ADMIN_TOKEN="<token>" \
    --set-env-vars REFRESH_HOURS="8"
- After deploy, note the URL output (https://cbi-v13-app-xxxxx-run.app).

5) Create a Cloud Run Job for pipelines
Option A — DATABASE_URL:
- gcloud run jobs create cbi-v13-pipelines \
    --image $IMAGE \
    --region $REGION \
    --task-timeout=3600 \
    --set-env-vars DATABASE_URL="<paste>" \
    --set-env-vars ADMIN_TOKEN="<token>" \
    --set-env-vars REFRESH_HOURS="8" \
    --command python --args run_all.py

Option B — Cloud SQL IAM Auth:
- gcloud run jobs create cbi-v13-pipelines \
    --image $IMAGE \
    --region $REGION \
    --task-timeout=3600 \
    --set-env-vars USE_IAM_AUTH=true \
    --set-env-vars CLOUD_SQL_CONNECTION_NAME="<project:region:instance>" \
    --set-env-vars DB_USER="postgres" \
    --set-env-vars DB_NAME="cbi" \
    --set-env-vars ADMIN_TOKEN="<token>" \
    --set-env-vars REFRESH_HOURS="8" \
    --command python --args run_all.py
- Test run once: gcloud run jobs execute cbi-v13-pipelines --region $REGION --wait
- Check logs: Cloud Run > Jobs > Executions

6) Schedule the job every 8 hours (Cloud Scheduler)
- Create a service account for Scheduler to run the Job (once per project) or reuse default with proper permissions.
  Example (lightweight): grant roles/run.admin to your scheduler SA.
- gcloud scheduler jobs create http cbi-v13-pipelines-8h \
    --schedule "0 */8 * * *" \
    --uri "https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/cbi-v13-pipelines:run" \
    --http-method POST \
    --oauth-service-account-email <SCHEDULER_SA_EMAIL> \
    --oauth-token-scope "https://www.googleapis.com/auth/cloud-platform"

7) Apply schema and seed data
- Option A: Use pipelines (ingest creates data). Before first run, ensure schema applied:
  psql "$DATABASE_URL" -f sql/schema.sql
- Option B: Have the first Job run apply schema by adding a step in your process (manual is simpler).
- Then run job once: gcloud run jobs execute cbi-v13-pipelines --region $REGION --wait

8) Verify
- App URL should render charts and signal card
- SQL checks:
  psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM curated.prices_daily;"
  psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM forecasts.price_baseline;"
  psql "$DATABASE_URL" -c "SELECT * FROM app.signals_today ORDER BY ds DESC LIMIT 1;"

Notes
- Cloud SQL Postgres: if you move to Cloud SQL, set up a public IP with SSL or use the Cloud SQL Auth Proxy sidecar.
- Costs: Cloud Run scales to zero; Jobs run only on schedule; Artifact Registry storage minimal.
- Security: Keep DATABASE_URL and ADMIN_TOKEN as secrets (env vars). Consider Secret Manager.
