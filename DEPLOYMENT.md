# CBI-V13 Deployment Guide

Complete deployment guide for the Crystal Ball V13 soybean oil intelligence platform.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  Cloud Run Jobs │    │   Cloud SQL     │
│   Dashboard     │◄──►│   (Pipelines)   │◄──►│   PostgreSQL    │
│   (Cloud Run)   │    │                 │    │   (IAM Auth)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Cloud Build    │    │ Cloud Scheduler │    │ Artifact Registry│
│  (CI/CD)        │    │ (Every 8hrs)    │    │ (Images)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Deployment

### 1. Prerequisites
- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated

### 2. One-Command Setup
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Run automated setup
./scripts/gcp_setup.sh
```

### 3. Deploy
```bash
# Deploy using Cloud Build
make gcp-deploy

# Or manually
gcloud builds submit --config cloudbuild.yaml
```

## Manual Setup (Alternative)

If you need more control, follow these detailed steps:

### 1. Enable APIs
```bash
gcloud services enable \
    cloudsql.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### 2. Create Cloud SQL Instance
```bash
# Create instance with IAM auth
gcloud sql instances create cbi-v13-sql \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --database-flags=cloudsql.iam_authentication=on

# Create database
gcloud sql databases create cbi_v13 --instance=cbi-v13-sql
```

### 3. Set up Service Account
```bash
# Create service account
gcloud iam service-accounts create cbi-v13-runner \
    --description="CBI-V13 Cloud Run services" \
    --display-name="CBI-V13 Runner"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:cbi-v13-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

### 4. Build and Deploy
```bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/cbi-v13

# Deploy service
gcloud run deploy cbi-v13-app \
    --image gcr.io/$PROJECT_ID/cbi-v13 \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account cbi-v13-runner@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars USE_IAM_AUTH=true \
    --set-env-vars CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:us-central1:cbi-v13-sql \
    --set-env-vars DB_NAME=cbi_v13
```

## Environment Variables

The application uses these environment variables:

### Database Configuration (Choose one)
```bash
# Option A: Direct connection string
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db?sslmode=require

# Option B: Google Cloud SQL with IAM
USE_IAM_AUTH=true
CLOUD_SQL_CONNECTION_NAME=project:region:instance
DB_USER=postgres
DB_NAME=cbi_v13
```

### Application Settings
```bash
ADMIN_TOKEN=your-secret-token
REFRESH_HOURS=8
```

### Optional API Keys
```bash
ALPHAVANTAGE_API_KEY=your-key
FRED_API_KEY=your-key
EIA_API_KEY=your-key
USDA_API_KEY=your-key
CFTC_API_KEY=your-key
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Set up Database
```bash
# Apply schema
make init-db

# Or manually
psql "$DATABASE_URL" -f sql/schema.sql
```

### 4. Run Application
```bash
# Run pipelines
make pipelines

# Start Streamlit app
make app
```

## Pipeline Architecture

The system runs these pipelines in sequence:

1. **Ingest** (`pipelines/ingest.py`)
   - Fetches market data from Yahoo Finance
   - Stores in `curated.prices_daily`

2. **Features** (`pipelines/features.py`)
   - Computes technical indicators
   - Stores in `features.technical`

3. **Baseline Models** (`pipelines/models_baseline.py`)
   - Runs ARIMA forecasts
   - Stores in `forecasts.price_baseline`

4. **Neural Network Models** (`pipelines/models_nn.py`)
   - Placeholder for LSTM/GRU models
   - Stores in `forecasts.price_nn`

5. **Economic Impact** (`pipelines/econ_impact.py`)
   - Generates buy/sell/hold signals
   - Stores in `app.signals_today`

## Monitoring and Troubleshooting

### Health Checks
```bash
# Run diagnostics
make diagnose

# Check database connectivity
python scripts/diagnose.py
```

### View Logs
```bash
# Cloud Run service logs
gcloud logs read --service=cbi-v13-app --region=us-central1

# Cloud Run job logs
gcloud logs read --job=cbi-v13-pipelines --region=us-central1
```

### Database Queries
```sql
-- Check data freshness
SELECT ds, symbol, close FROM curated.prices_daily ORDER BY ds DESC LIMIT 5;

-- Check forecasts
SELECT ds, y_hat FROM forecasts.price_baseline ORDER BY run_ts DESC, ds LIMIT 5;

-- Check signals
SELECT * FROM app.signals_today ORDER BY ds DESC LIMIT 1;
```

## Cost Optimization

- **Cloud Run**: Scales to zero, pay per request
- **Cloud SQL**: Use smallest tier (db-f1-micro) for development
- **Cloud Build**: Free tier includes 120 build-minutes/day
- **Artifact Registry**: Minimal storage costs

Estimated monthly cost for light usage: $20-50

## Security Best Practices

1. **Database**: Use IAM authentication instead of passwords
2. **Secrets**: Store sensitive values in Secret Manager
3. **Network**: Use VPC connector for private database access
4. **IAM**: Follow principle of least privilege
5. **Monitoring**: Enable Cloud Logging and monitoring

## Support

For issues:
1. Check the Health page in the web app
2. Run `make diagnose` for system checks
3. Review Cloud Run logs
4. Verify environment variables and IAM permissions