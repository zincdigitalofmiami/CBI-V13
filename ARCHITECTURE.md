# CBI-V13 Architecture and Scope

## Executive Summary
CBI-V13 (Crystal Ball V13) is a data-to-decisions platform for soybean oil procurement. It ingests market and macro data, engineers features, trains baseline and advanced ML models, converts outputs into procurement signals, and serves them in a Streamlit dashboard. The repo includes data pipelines, database schema, a web app, deployment automation, and docs.

Core flow: Ingestion → Processing → Features → Models → Signals → Dashboard
Primary user outcome: Clear Buy/Watch/Hold guidance with quantified dollar impact, plus market intelligence and scenario views.

## Goals and Stakeholders
- Goal: Reduce procurement cost and risk via timely intelligence and model-driven recommendations.
- Stakeholders: Procurement lead, Ops/supply chain, Data/ML team, Execs/finance.

## High-Level Architecture
- Data sources: Market prices (e.g., ZL=F), macro/policy data (NOAA, GDELT, USDA, BLS), internal CSVs, optional APIs (AlphaVantage, FRED, EIA).
- Storage: Postgres (managed; e.g., Cloud SQL for Postgres or any provider) with schemas: raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy.
- Processing: Python pipelines orchestrated by `run_all.py` and `pipelines/*`.
- Modeling: Baseline (ARIMA+exog-like) and advanced (LSTM/GRU roadmap).
- Serving: Streamlit app (`app/Home.py` and `app/pages/*`).
- Deployment: Google Cloud Run (recommended) via Cloud Build; Docker supported. Alternative providers are possible.

## Repository Structure (Key Paths)
- App: `app/Home.py`, `app/pages/`
- Pipelines: `pipelines/ingest.py`, `pipelines/features.py`, `pipelines/models_baseline.py`, `pipelines/models_nn.py`, `pipelines/econ_impact.py`
- Orchestration: `run_all.py`
- DB & schema: `db/session.py`, `sql/schema.sql`
- ML helpers: `ml/datasets.py`, `ml/models.py`, `ml/evaluate.py`
- Scripts & Ops: `scripts/apply_schema.py`, `scripts/diagnose.py`, `scripts/workstation_check.sh`, `scripts/git_now.sh`
- DevOps: `Dockerfile`, `cloudbuild.yaml`, `Makefile`, `CLOUD_RUN.md`
- Docs: `README.md`, `ALL_STEPS.md`, `GIT_TROUBLESHOOT.md`, `WORKSTATION.md`, (this) `ARCHITECTURE.md`

## Data Layer
- Engine/session: `db/session.py` via SQLAlchemy; DB config via env. Supports DATABASE_URL or Cloud SQL IAM auth.
- Schema: `sql/schema.sql` (idempotent); tables across `raw`, `curated`, `features`, `sentiment`, `forecasts`, `models`, `app`, `geo`, `ops`, `strategy`.

## Pipelines
- `ingest.py`: ZL=F via yfinance → `curated.prices_daily`.
- `features.py`: Indicators, spreads, volatility, weather/policy flags → `features.*`.
- `models_baseline.py`: Baseline forecasts → `forecasts.price_baseline`.
- `models_nn.py`: Placeholder for LSTM/GRU → `forecasts.*`.
- `econ_impact.py`: Buy/Watch/Hold + dollar impact → `app.signals_today`, `app.econ_impact`.
- Orchestration: `run_all.py` runs end-to-end. Idempotent inserts/constraints used.

## Modeling Stack
- Baseline: ARIMA(+ exog)-style, 1w/1m/3m horizons.
- Advanced roadmap: LSTM/GRU; exogenous features: extended futures, weather, policy/tariffs, sentiment.
- Quant templates (roadmap): feature engineering, cointegration/VAR, Monte Carlo, VaR.
- Generative AI RAG (concept): news → embeddings → classification → `features.sentiment_scores`.

## Streamlit App
- Pages: Health, Market Intelligence, Strategy, Trade Intelligence, Admin (token-protected).
- Outputs: current prices vs contract, Buy/Watch/Hold + confidence + dollar impact, hedge windows, risk alerts, scenarios.

## Configuration
- `config/settings.py` reading env vars: `DATABASE_URL`, `ADMIN_TOKEN`, `REFRESH_HOURS`; optional API keys.
- Cloud SQL IAM path using `USE_IAM_AUTH=true` with `CLOUD_SQL_CONNECTION_NAME`, `DB_USER`, `DB_NAME`.

## Operations & Automation
- Make targets: `help`, `init-db`, `pipelines`, `app`, `gcp-setup`, `gcp-deploy`, `workstation-check`, `diagnose`, `git-doctor`, `git-now`.
- Scripts: schema apply, diagnostics, workstation checks, and `git_now.sh` for one-shot push.
- CI/CD & containers: Dockerfile, `cloudbuild.yaml`.

## How to Run (Local)
1) `pip install -r requirements.txt`
2) `cp .env.example .env` then set `DATABASE_URL` (include `sslmode=require` if required) or set IAM envs.
3) `make init-db`
4) `python run_all.py`
5) `streamlit run app/Home.py`

## Deployment (Google Cloud Run)
- Primary path is in `CLOUD_RUN.md`:
  - Build via Cloud Build and deploy to Cloud Run
  - Use Cloud SQL (DATABASE_URL or IAM auth)
  - Use Cloud Run Jobs + Cloud Scheduler for pipelines

## Acceptance Criteria
- `curated.prices_daily` has recent ZL=F
- `forecasts.price_baseline` populated
- `app.signals_today` has current recommendation
- Streamlit app runs without errors
- Pipelines run on a cadence (Jobs or Cron)

## Roadmap
- Productionize ARIMA(+ exog) with parameter search
- Implement `models_nn.py` (LSTM/GRU) + metrics tracking in `models.*`
- Expand sources/features; add `app.pipeline_runs` table
- Integrate sentiment/RAG pipeline
- Add stress testing and hedging optimization
