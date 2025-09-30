# CBI-V13: Crystal Ball Intelligence Platform

Soybean Oil Market Intelligence & Procurement Decision Support

CBI-V13 is an AI-driven platform that ingests market, policy, and macro data; engineers features; trains baseline and advanced models; and serves BUY/WATCH/HOLD procurement guidance with quantified dollar impact via a Streamlit dashboard. The stack targets Google Cloud Run for the app and Cloud SQL for Postgres (with optional IAM auth). Postgres provider is agnostic; SSL may be required depending on provider.

Table of Contents
- Overview
- System Architecture
- Repository Structure
- Environment & Configuration
- Quick Start
- Local Development
- Data Pipelines
- Dashboard Pages
- Admin & Operations
- Deployment (Google Cloud Run)
- Troubleshooting
- FAQ
- Security & Secrets
- Roadmap
- License

Overview
- Primary Outcome: Clear daily action — Should I buy today or wait? — with confidence and dollar impact.
- Users: Procurement lead (primary), Ops/Supply Chain, Finance/Exec, Data/ML.
- Core Flow: Ingestion → Processing → Features → Models → Signals → Dashboard.

System Architecture
- Data Sources: Market prices (ZL=F, etc.), macro/FX, policy and congressional data, curated CSVs/APIs.
- Storage: Postgres with schemas: raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy.
- Processing: Python pipelines (pipelines/*) orchestrated by run_all.py.
- Modeling: Baseline ARIMA(+ exog) and advanced NN roadmap (LSTM/GRU/TabNet/GARCH).
- Serving: Streamlit app (app/Home.py, app/pages/*).
- Deployment: Google Cloud Run + Cloud SQL (IAM optional) using Cloud Build. Dockerfile provided.

Repository Structure
- app/Home.py — Streamlit entrypoint (Command Center)
- app/pages/ — Additional pages (Health, Sentiment & Market Intelligence, Strategy, Admin, Trade Intelligence)
- pipelines/ — ingest.py, features.py, models_baseline.py, models_nn.py, econ_impact.py
- db/session.py — SQLAlchemy engine (supports DATABASE_URL or Cloud SQL IAM)
- sql/schema.sql — Idempotent schema for all domains
- config/settings.py — Environment configuration
- ml/ — Reusable model/data helpers
- scripts/ — Setup, deploy, diagnostics, and Git helpers
- Makefile — Common tasks (init-db, pipelines, app, gcp-setup, gcp-deploy, diagnose, git-now)
- Docs — README.md, ALL_STEPS.md, CLOUD_RUN.md, ARCHITECTURE.md, WORKSTATION.md, DEPLOYMENT.md

Environment & Configuration
- Required
  - DATABASE_URL: SQLAlchemy Postgres URL (include sslmode=require if your provider needs SSL)
  - or USE_IAM_AUTH=true with Cloud SQL variables: CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_NAME
  - ADMIN_TOKEN: Token for Admin page
  - REFRESH_HOURS: Pipeline refresh cadence (e.g., 8)
- Optional API Keys
  - ALPHAVANTAGE_API_KEY, FRED_API_KEY, NOAA, etc. (only if you enable related ingestions)
- Local .env
  - cp .env.example .env and fill values; export to shell when running locally

Quick Start
Google Cloud (Recommended)
```bash
export PROJECT_ID=your-project-id
./scripts/gcp_setup.sh
make gcp-deploy
```
See CLOUD_RUN.md for Cloud SQL IAM, Jobs, and Scheduler.

Local Development
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env (DATABASE_URL, ADMIN_TOKEN, REFRESH_HOURS). If SSL is required, add ?sslmode=require.
make init-db   # applies sql/schema.sql
make pipelines # run end-to-end (or python run_all.py)
make app       # launch Streamlit locally
```

Data Pipelines
- Orchestration: run_all.py (calls all stages)
- Stages
  - pipelines/ingest.py: Loads ZL=F daily prices to curated.prices_daily; upserts app.parameters.refresh_hours
  - pipelines/features.py: Computes technical/macro placeholders into features.*
  - pipelines/models_baseline.py: Writes forecasts.price_baseline
  - pipelines/models_nn.py: Placeholder for NN outputs to forecasts.price_nn
  - pipelines/econ_impact.py: Computes app.signals_today and app.econ_impact
- Schema Guarantees
  - sql/schema.sql is safe to re-apply; uses IF NOT EXISTS and unique constraints for idempotency

Dashboard Pages (app/pages)
- 0 — Health
  - Connection checks, row counts, latest records; tips for DATABASE_URL vs Cloud SQL IAM.
- 1 — Procurement Command Center (Chris’s Daily Decision Page)
  - Traffic Light Signal System (giant circular indicator)
    - RED: "HOLD - Volatility >8% or price >$0.65/lb"
    - YELLOW: "WATCH - Decision zone, check scenarios"
    - GREEN: "BUY NOW - Optimal window detected"
  - Confidence meter (0–100% based on model agreement)
  - Dollar impact display (e.g., "Buying today vs waiting: +$47,000 cost" or "-$23,000 savings")
  - Live Price Intelligence (ZL futures, last 5 purchase points, AI 30‑day band, support/resistance)
  - Real-time drivers: China buying, Brazil weather, crush margins, fund positioning
  - Procurement Scenarios: sliders (needs, harvest pressure, 50/50 hedge) + risk alerts
- 2 — Sentiment & Market Intelligence
  - Market Mood Ring gauge; weighted inputs: News 40%, Funds 30%, Technicals 20%, Weather 10%
  - 16‑Category News Grid with drilldowns and impact scores
  - Narrative Intelligence updated every 4 hours with key changes vs yesterday
- 3 — Strategy (Business Intelligence)
  - Procurement windows (calendar heatmap + seasonal patterns; overlays: WASDE, OPEX, FND)
  - Contract Strategy Optimizer (mix, spot vs 30/90‑day, basis/storage implications)
  - Industry Intelligence columns: Key Players, Pricing Trends, Recent Developments, Market Structure
  - Deep‑Dive Tabs: US Production & Storage; Global S&D; Soy Complex Value Chain; Food & Industrial Demand
  - Strategy Tools: calculators, performance metrics, AI suggestions
- 4 — Geopolitical & Trade Intelligence
  - Tariff Threat Matrix (probability, proposed rates)
  - Trump Feed Impact (keyword parsing, historical correlation, risk alerts)
  - Policy Timeline and Congressional Votes (probabilities, impacts)
  - Country Snapshots (US‑China, Brazil, India/Pakistan, EU/UK)
  - FX & Macro Panel (BRL/USD, DXY, WTI, rates)
  - Trade War Alerts (DEFCON, flash updates, historical patterns, action items)
- Admin (protected)
  - Manage parameters (e.g., refresh cadence), manual pipeline triggers

Admin & Operations
- Makefile Targets
  - init-db — apply schema to DATABASE_URL
  - pipelines — run full pipeline chain
  - app — start Streamlit
  - gcp-setup — provision GCP infra (APIs, Cloud SQL, Artifact Registry)
  - gcp-deploy — build & deploy via Cloud Build to Cloud Run
  - diagnose — run repo/app diagnostics
  - git-now — stage, commit, push (uses scripts/git_now.sh)
- Diagnostics
  - python scripts/diagnose.py prints environment, Git, network, DB reachability (with hints for SSL/Cloud SQL IAM)

Deployment (Google Cloud Run)
- Cloud Build
  - make gcp-deploy builds container and deploys to Cloud Run
- Database Options
  - DATABASE_URL (any Postgres) — include sslmode=require if needed
  - Cloud SQL IAM — set USE_IAM_AUTH=true and CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_NAME
- Jobs & Scheduling
  - Cloud Run Jobs for pipelines; schedule via Cloud Scheduler (see CLOUD_RUN.md)

Troubleshooting
- Database not reachable
  - Ensure DATABASE_URL is set (or USE_IAM_AUTH=true with Cloud SQL vars)
  - Some providers require ?sslmode=require in the URL
- Ingestion or pipelines fail
  - Rerun make pipelines; check logs; ensure outbound internet and symbols are valid
- Empty charts
  - Verify curated.prices_daily and forecasts.price_baseline have rows; run pipelines
- Git issues
  - make git-now or bash scripts/git_doctor.sh

FAQ
- Do I need Google Cloud? No; you can run locally or on any host. README emphasizes Cloud Run because it’s a solid default.
- Which Postgres? Any managed Postgres is fine. If SSL is enforced, include sslmode=require. Cloud SQL IAM is supported.
- Where do signals come from? From model outputs (forecasts + econ impact), not heuristics embedded in pages.

Security & Secrets
- Store secrets (DATABASE_URL, ADMIN_TOKEN, API keys) as environment variables.
- Consider Google Secret Manager for production.
- Admin page is token‑protected; rotate ADMIN_TOKEN periodically.

Roadmap
- Harden baseline ARIMA(+ exog) with parameter search and monitoring
- Implement LSTM/GRU in models_nn.py and persist to forecasts.price_nn
- Expand ingestions (FX, weather, policy feeds) and enrich features
- Add app.pipeline_runs logging and surface status on Admin page
- Integrate sentiment/RAG pipeline and alerting

License
This project is licensed under the MIT License. See LICENSE for details.
