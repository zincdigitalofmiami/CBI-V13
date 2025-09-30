# CBI-V13
Crystal Ball V13
Project Crystal Ball (CBI-V13) — Model & Pipeline Design
📐 Core Pipeline Architecture

Ingestion → Processing → Features → Models → Signals → Dashboard

Ingestion

CSV uploads (ZL, ZS, ZC, etc.) → gs://cbi-v13-futures-data

Public datasets (NOAA, GDELT, FEC, BLS, USDA, etc.) → raw.*

Scrapers/APIs for soybean oil procurement reports, policy events, and industry intelligence

Processing

raw → staging → curated cleaning + schema enforcement

Data enrichment: basis, spreads, weather overlays, policy flags

Features

features.market_signals (futures + spreads + vol surfaces)

features.weather_supply_impact (US Midwest + Brazil/Argentina forecasts)

features.china_demand_composite (hog herd, crushing margins, state reserves)

features.tariff_risk_matrix (tariffs, WTO disputes, quotas, retaliation probability)

features.sentiment_scores (news/NLP with bullish/bearish classification)

🤖 Models in the Stack
1. BigQuery ML — Baseline Forecasting

Model: ARIMA_PLUS_XREG

Inputs:

Target = ZL price series (raw.zl_data.Last)

External regressors = weather indices, crush margins, USD/BRL

Purpose:

Quick, low-latency forecasts for 1w/1m/3m horizons

Used for smoke tests and procurement “sanity signals”

2. Vertex AI — Advanced ML Models

Model Types:

LSTM / GRU (time series) → nonlinear price forecasting with multiple exogenous features

TabNet → tabular deep learning for procurement decision optimization

GARCH/HAR models (custom jobs) → volatility/risk forecasting

Inputs:

Extended futures (ZL, ZS, ZC, palm, sunflower)

Weather forecasts (NOAA, ECMWF, INMET, SMN)

Policy/tariff events (GDELT, WTO, USTR)

Sentiment scores (EmbeddingGemma / FinancialBERT sentiment)

Purpose:

Capture nonlinear interactions (e.g., USD ↑ + Brazil drought + biodiesel mandate = ZL spike)

Scenario stress tests and Monte Carlo simulation

3. StaryNet — Quant Templates

Role: Orchestration + Auto-feature pipelines

Capabilities:

Time-series feature engineering (lags, seasonality, spreads)

Scenario testing (cointegration, VAR, Monte Carlo)

Portfolio/risk modeling (hedging strategies, procurement VaR)

Purpose:

“Quant-in-a-box” to reduce wiring complexity

Plugs into BigQuery + Vertex outputs

4. Generative AI RAG (Cloud SQL + Vertex AI Embeddings)

Role: News/Geopolitical Sentiment → Signals

Pipeline:

News scrapers (policy, weather, ESG, strikes, tariffs, biofuel mandates) → Cloud SQL

Embeddings generated → semantic search (RAG)

Vertex AI → classify relevance (soybean oil vs noise)

Output = features.sentiment_scores with (relevance, bullish/bearish, conviction, half-life)

Purpose:

Power the “24/7 Digital Watchtower”

Convert unstructured text into procurement-relevant signals

📊 Dashboard Outputs (Chris’s View)

Procurement Command Center

Current wholesale soybean oil vs contract

Buy/Wait/Hold signals (w/ dollar impact)

Next 30 days recommended hedge windows

Business Health Monitor

Restaurant industry demand index (QSR expansion, sales trends)

Competitive oil spreads (soy vs palm, sunflower, canola)

Margin optimization: oil costs vs SoyMAX/StableMAX pricing power

Risk & Operations

Supply chain alerts (strikes, port congestion, freight bottlenecks)

Biofuel mandates & policy shifts (RFS, LCFS, SAF, Indonesia B40)

ESG/deforestation enforcement risks (EUDR deadlines, exemptions)

Scenario Explorer

“What if Brazil harvest down 20%?” → price impact

“What if tariffs escalate?” → procurement cost forecast

“What if SAF demand spikes?” → oil demand uplift

🧭 What’s Noise vs What Stays

Keep: Procurement-driven intelligence (oil prices, crush spreads, tariffs, weather, biofuels, logistics, demand).

Drop/Noise: Pure technical trading charts (RSI/MACD), over-detailed academic analysis, excessive crop minutiae.

Principle: Every chart answers:

Should I buy oil today or wait?

What’s threatening my supply chain this month?

How is customer demand trending?

Where can I optimize costs/margins?

✅ So the models stack like this:

BQML ARIMA_PLUS_XREG → fast baselines (cheap, explainable).

Vertex AI (LSTM/GRU/TabNet/GARCH) → heavy nonlinear modeling & risk.

StaryNet → orchestration + quant templates (stress tests, cointegration).

GenAI RAG → turn unstructured global news/events into procurement signals.


---

# U.S. Oil Solution Intelligence (Neon + Streamlit + Pipelines)

For a complete end-to-end checklist of every action, see ALL_STEPS.md.

This repository contains a minimal, production‑ready scaffold for the U.S. Oil Solution Intelligence platform using:
- Neon Postgres (source of truth)
- Streamlit app (Render Web Service)
- Python pipelines (Render Cron) for ingest → features → models → forecasts → econ impact
- Stats/ML stack stubs (statsmodels/Torch placeholders)

No data is stored in the repo; all data lives in the database.

## Quick Start (Local)
1) Python 3.12 and dependencies
- Create a virtual environment and install deps
  - pip install -r requirements.txt
- Copy .env.example to .env and set DATABASE_URL (Neon) and ADMIN_TOKEN

2) Create DB schema (Neon)
- Apply sql/schema.sql to your Neon database (via psql or console)

3) Seed minimal data and run pipelines
- Ensure DATABASE_URL is set
- Run:
  - python pipelines/ingest.py
  - python pipelines/features.py
  - python pipelines/models_baseline.py
  - python pipelines/models_nn.py
  - python pipelines/econ_impact.py

4) Launch app
- streamlit run app/Home.py

## Deployment on Google Cloud (Recommended single provider)
- Use Cloud Run for the app, Cloud Run Jobs for pipelines, and Cloud Scheduler for cadence.
- Database options:
  - Cloud SQL for Postgres with IAM Database Authentication (no service account JSON key required)
  - Any Postgres via DATABASE_URL (e.g., Neon)
- Environment variables for Cloud SQL IAM Auth mode:
  - USE_IAM_AUTH=true
  - CLOUD_SQL_CONNECTION_NAME=project:region:instance
  - DB_USER=postgres
  - DB_NAME=cbi (or your db)
  - ADMIN_TOKEN, REFRESH_HOURS, API keys as needed
- See CLOUD_RUN.md for exact gcloud commands (both DATABASE_URL and IAM Auth modes).

## Deployment (Render)
- Create a Render Web Service
  - Build Command: pip install -r requirements.txt
  - Start Command: streamlit run app/Home.py --server.port $PORT --server.address 0.0.0.0
  - Environment variables:
    - DATABASE_URL (Neon connection string)
    - ADMIN_TOKEN
    - REFRESH_HOURS (default 8)
    - API keys as needed (ALPHAVANTAGE_API_KEY, FRED_API_KEY, etc.)
- Create a Render Cron Job (every 8h by default)
  - Command:
    pip install -r requirements.txt && \
    python pipelines/ingest.py && \
    python pipelines/features.py && \
    python pipelines/models_baseline.py && \
    python pipelines/models_nn.py && \
    python pipelines/econ_impact.py

## Deployment without Render (Neon-only DB, local or low-cost hosting)
- Neon is your managed Postgres. It does not host the app server.
- To avoid Render costs, use one of these:
  - Local/VPS: run the Streamlit app and cron yourself; see NEON_ONLY.md
  - Fly.io or Railway: low-cost/free tiers; see NEON_ONLY.md for a minimal Dockerfile and steps
- Pipelines can be scheduled with cron (locally/VPS) or each platform’s scheduler; use python run_all.py

## Repository Layout
- app/
  - Home.py (Procurement Command Center)
  - pages/
    - 1_📊_Sentiment_&_Market_Intelligence.py
    - 2_🗺️_Strategy_Lab_&_Supply_Chain_Map.py
    - 3_🔧_Admin.py (token‑protected refresh, cadence)
- pipelines/
  - ingest.py (Yahoo Finance baseline; CSV loader utility in io/)
  - features.py (technical features)
  - models_baseline.py (placeholder baseline forecasts)
  - models_nn.py (placeholder NN forecasts + explanations)
  - econ_impact.py (signal + dollar impact)
- ml/
  - datasets.py, models.py, evaluate.py (stubs for reuse)
- db/
  - session.py (SQLAlchemy engine/session)
- config/
  - settings.py (env handling)
- io/
  - csv_loader.py (bulk CSV loader)
- sql/
  - schema.sql (all schemas and tables)
- requirements.txt, .env.example

## Data Model (Postgres)
Schema and tables are defined in sql/schema.sql per the approved spec:
- raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy

## Security
- Secrets only via environment variables; no credentials in code
- Principle of least privilege: separate DB roles for app (read‑mostly) and pipelines (writer)

## Admin & Scheduling
- Admin page in Streamlit (token‑protected) can:
  - Update refresh cadence (app.parameters.refresh_hours)
  - Trigger pipelines on‑demand (ingest → features → models → econ)
- Render Cron executes the same pipeline chain every REFRESH_HOURS (default 8)

## Theming & UX
- Dark, modern theme with custom CSS and Plotly dark template
- Mobile‑responsive layout via Streamlit
- 3D map (pydeck) on Strategy Lab page

## One-shot pipeline run
- After setting DATABASE_URL and applying schema:
  - python run_all.py
- Or with Makefile:
  - make pipelines

## Notes
- Baseline and NN pipelines currently implement lightweight placeholder logic to write forecasts and signals. Replace with full ARIMA/xreg and LSTM/GRU training as data and modeling choices are finalized.
- All tables use IF NOT EXISTS creates; apply migrations as schemas evolve.


## Repo/App Connection Diagnostics
- Quick CLI check: `make diagnose` (or `python scripts/diagnose.py`). This tests Python deps, Git remote/fetch, DNS/HTTPS, DB connectivity (DATABASE_URL or Cloud SQL IAM), and filesystem permissions. It prints human status lines and a JSON block with details and hints (e.g., add `?sslmode=require` for Neon).
- In the UI: open the Health page in Streamlit: Pages → System Health & Connections. It shows DB mode, row counts, and latest records. If DB is unreachable, verify your environment variables.

Common fixes
- Neon: ensure your DATABASE_URL ends with `?sslmode=require`.
- Cloud SQL IAM: set `USE_IAM_AUTH=true` and provide `CLOUD_SQL_CONNECTION_NAME`, `DB_USER`, and `DB_NAME`.
- Git remote issues: run `git remote -v`; if empty, add your origin: `git remote add origin <url>`.
- Network: corporate VPNs/firewalls can block Git/HTTPS; try another network or allowlist github.com and neon.tech.



## Git Troubleshooting
- If your IDE or terminal shows nothing in Git, run: `make git-doctor`
- See GIT_TROUBLESHOOT.md for a step-by-step checklist to fix remotes, branches, ignored files, and common macOS/JetBrains issues.
