Title: ALL STEPS — End-to-End Setup, Run, Deploy, Verify, and Troubleshoot

Overview
This document provides a complete, sequential checklist to take this repository from zero to a working system locally and in production on Render, using a managed Postgres database. It is intentionally verbose so you can follow it line-by-line.

Note: If you are deploying on Google Cloud, see CLOUD_RUN.md for a full Cloud Run + Cloud SQL (IAM auth supported) guide. The steps below remain valid for local use; deployment differs per provider.

Sections
- A. Prerequisites
- B. Local Environment Setup
- C. Database Setup (Postgres)
- D. Apply Schema
- E. First Data Ingestion and Pipeline Run
- F. Launch the Streamlit App Locally
- G. Verification Checks (Local)
- H. Deploy to Render (Web Service)
- I. Set Up Render Cron Job (Pipelines)
- J. Verification Checks (Render)
- K. Admin Operations
- L. Troubleshooting
- M. Rollbacks and Idempotency
- N. Next Enhancements (optional)

A. Prerequisites
- Python 3.12 installed
- A Postgres database (managed service recommended; connection string ready)
- psql CLI installed (optional but recommended for quick checks)
- Render account (if deploying)

B. Local Environment Setup
1) Clone and enter the repo
- git clone <your-repo-url>
- cd CBI-V13

2) Create and activate a virtual environment
- python3.12 -m venv .venv
- source .venv/bin/activate  # Windows: .venv\Scripts\activate

3) Install dependencies
- pip install -r requirements.txt

4) Create your environment file
- cp .env.example .env
- Edit .env and set:
  - DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db>?sslmode=require
  - ADMIN_TOKEN=<a-strong-random-token>
  - REFRESH_HOURS=8  # or your preference
  - (Optional API keys) ALPHAVANTAGE_API_KEY, FRED_API_KEY, etc.

C. Database Setup (Postgres)
- Ensure your Postgres instance is available and you have the connection string.
- The app uses SQLAlchemy with psycopg2 driver per .env.example format.

D. Apply Schema
Option 1: Using Makefile
- export $(grep -v '^#' .env | xargs)  # load env vars into the shell (macOS/Linux)
- make init-db

Option 2: Using psql directly
- psql "$DATABASE_URL" -f sql/schema.sql

What this does
- Creates schemas: raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy
- Creates required tables
- Adds idempotency and primary key constraints so repeated runs do not duplicate data

E. First Data Ingestion and Pipeline Run
Option 1: One-shot
- python run_all.py

Option 2: Stage-by-stage
- python pipelines/ingest.py
- python pipelines/features.py
- python pipelines/models_baseline.py
- python pipelines/models_nn.py
- python pipelines/econ_impact.py

Notes
- Ingestion downloads ~5 years of daily data for ZL=F via yfinance and writes curated.prices_daily
- Features computes simple technical indicators (placeholders)
- Models write baseline and NN placeholder forecasts
- Econ impact writes app.signals_today and app.econ_impact

F. Launch the Streamlit App Locally
- streamlit run app/Home.py
- Open the provided local URL (usually http://localhost:8501)

G. Verification Checks (Local)
From terminal (requires psql):
- psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM curated.prices_daily;"
- psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM forecasts.price_baseline;"
- psql "$DATABASE_URL" -c "SELECT * FROM app.signals_today ORDER BY ds DESC LIMIT 1;"
In the app Home page, you should see
- Price series chart for ZL=F
- Baseline forecast band
- Signal card with confidence and dollar impact
- Parameters JSON including refresh_hours

H. Deploy to Render (Web Service)
1) Create a new Web Service
- Type: Web Service
- Runtime: Python (native)
- Build Command: pip install -r requirements.txt
- Start Command: streamlit run app/Home.py --server.port $PORT --server.address 0.0.0.0

2) Environment variables (Render → Settings → Environment)
- DATABASE_URL = your Postgres connection string (include sslmode if your provider requires it)
- ADMIN_TOKEN = your token
- REFRESH_HOURS = 8 (or preferred)
- Optional API keys as needed

3) Auto deploy from main branch (recommended)
- Connect repo → enable auto-deploy on push

I. Set Up Render Cron Job (Pipelines)
Option A: Use render.yaml (recommended)
- This repo includes render.yaml with a cron job:
  - schedule: every 8 hours
  - command: pip install -r requirements.txt && python run_all.py
- If your repo is connected, Render will offer to create this Cron Job.

Option B: Create Cron Job manually in Render
- Type: Cron Job
- Schedule: 0 */8 * * *  (every 8 hours)
- Command:
  pip install -r requirements.txt && \
  python run_all.py
- Copy the same Environment variables from the Web Service.

J. Verification Checks (Render)
- Web Service → Logs: confirm app starts, binds to a port without DB errors
- Cron Job → Logs: confirm successful pipeline run (look for JSON status lines and no tracebacks)
- Use psql or a SQL client to verify tables populated as in local checks
- Visit your Render Web Service URL to see the dashboard

K. Admin Operations
- App pages include an Admin page (token protected)
- Use ADMIN_TOKEN to access protected operations
- You can update refresh cadence (app.parameters.refresh_hours)
- You can trigger pipelines on demand (if wired in your environment)

L. Troubleshooting
Common issues and fixes
- Database not reachable in app
  - Ensure DATABASE_URL is set in Render and locally
  - Include sslmode=require if your provider enforces SSL
  - Check db/session.py uses SQLAlchemy URL with +psycopg2 (matches .env.example)
- Ingestion fails (yfinance)
  - Retry; ensure outbound internet allowed in your environment
  - If symbol changes, run: python pipelines/ingest.py --symbol ZL=F
- Duplicate rows or constraint errors
  - Schema includes UNIQUE constraints; ON CONFLICT DO NOTHING is used in pipelines
  - Re-apply sql/schema.sql if constraints were missing
- Cron Job fails
  - Open Render → Job → Logs; find the first traceback; fix env or code then redeploy
- App blank/empty
  - Check logs; verify tables have data; run pipelines again

M. Rollbacks and Idempotency
- Render Web Service
  - Use Render’s rollback to previous successful deploy
- Pipelines
  - Safe to rerun; inserts are idempotent where applicable
- Schema
  - sql/schema.sql is safe to re-apply; it uses IF NOT EXISTS and ADD CONSTRAINT IF NOT EXISTS

N. Next Enhancements (optional)
- Replace baseline forecast with statsmodels ARIMA(+ exog)
- Wire in LSTM/GRU in models_nn.py using ml/models.py
- Add more symbols and macro features in pipelines
- Add logging table app.pipeline_runs to track run status
- Integrate external APIs (AlphaVantage, FRED, NOAA, EIA) for richer features

End of ALL STEPS
