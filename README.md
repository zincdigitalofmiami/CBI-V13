Below is the full, end-to-end scope for “U.S. Oil Solution Intelligence” using Neon Postgres, full Python (including PyTorch), DataSpell for exploration, and a Streamlit web app hosted on Render with an 8-hour adjustable cron. Dark, modern, high-definition visuals, no emojis, 3D elements, mobile-responsive. New table/endpoint names (no legacy names).
Objectives and Outcomes
Business goals:
Deliver operational procurement signals (Buy/Watch/Hold) with confidence and dollar impact.
Produce price forecasts for 1w/1m/3m/12m plus volatility/risk and global trade context.
Provide scenario modeling and economic impact analysis.
Ensure explainability (“why this matters”) alongside each signal.
Non-functional:
One client URL (https), mobile responsive.
Serverless database (Neon), easy-to-operate app (Render).
All data in DB (no data in repo).
Versioned code, minimal DevOps, security by environment variables and least-privilege DB roles.
High-Level Architecture
Data store: Neon Postgres (source of truth).
App hosting: Render Web Service (Streamlit) + Render Cron for pipelines.
Pipelines: Python CLI scripts for ingest → transform → features → train → forecast → narratives.
ML stack:
Baseline: statsmodels (ARIMA/xreg).
Neural: PyTorch LSTM/GRU + optional TabNet for tabular signals.
Risk: rolling vol proxies; optional GARCH-like approximations.
Explainability: permutation/SHAP; rationale text generation templates.
Exploration: JetBrains DataSpell notebooks connected to Neon, reusing pipeline utilities.
Security: DATABASE_URL secret; optional read-only DB role for analysts; admin token for on-demand refresh.
Data Model (Neon Schemas/Tables)
raw: ingested data (as-is)
raw.market_prices(ts, symbol, price, open, high, low, volume, source)
raw.policy_events(ts, region, topic, text, source)
raw.weather(ts, region, metric, value, source)
raw.news(ts, title, url, outlet, text, category)
raw.fx(ts, base, quote, rate, source)
curated: cleaned, conformed sets
curated.prices_daily(ds, symbol, open, high, low, close, volume)
curated.procurement_context(ds, basis, crush_margin, freight_idx, storage_utilization)
curated.supply_demand(ds, region, production, stocks, use, exports)
features: model-ready features
features.key_drivers(ts, driver, value, unit, status, note)
features.technical(ds, symbol, rsi, ma7, ma30, ma90, vol_z)
features.macro(ds, dxy, wti, inflation, rates10y)
features.weather(ds, region, drought_idx, temp_anom, precip_anom)
sentiment: text-derived signals
sentiment.category_scores(ts, category, score, label, weight, top_items_json)
forecasts: model outputs
forecasts.price_baseline(run_ts, ds, horizon_days, y_hat, y_lo, y_hi, model_version)
forecasts.price_nn(run_ts, ds, horizon_days, y_hat, y_lo, y_hi, model_version)
models: run meta and metrics
models.runs(run_id, started_at, finished_at, model, params_json, status)
models.metrics(run_id, metric, value, horizon)
app: operational presentation
app.signals_today(ds, signal, confidence, dollar_impact, rationale)
app.parameters(key, value) // e.g., refresh_hours, support_level, resistance_level
app.explanations(run_id, ds, top_features_json, reason_text)
app.econ_impact(scenario, ds, delta_price, notes)
app.purchases(ts, quantity_lbs, price, note) // optional client data
geo: mapping and flows
geo.nodes(id, name, type, lat, lon, capacity, status_json)
geo.edges(src_id, dst_id, kind, weight, status_json)
geo.port_metrics(port, ts, vessels_waiting, avg_delay_days)
ops: real-time operational signals
ops.realtime(ts, crush_margin, freight_rate, storage_level, alert_text)
strategy: backtests and results
strategy.backtests(strategy, metric, value)
strategy.performance(ds, realized_cost, benchmark_cost, savings_cum)
Data Ingestion Sources and Approach
Historical CSVs (your files): bulk-loaded into raw.market_prices and curated.prices_daily for ZL history.
Market prices: Yahoo Finance (ZL=F, related symbols), Alpha Vantage (backup), FRED (macro), FX APIs.
USDA: QuickStats, WASDE, export sales (free APIs).
EIA: petroleum/biofuels metrics (API).
CFTC: weekly COT text/CSV.
Weather: NOAA/INMET/SMN basics; computed drought/temperature anomalies.
News/policy: RSS + web-scraped sources; sentiment via lightweight NLP (Hugging Face) if required; write to sentiment.category_scores.
Scheduling: cron every 8h (adjustable via app.parameters.refresh_hours). On-demand trigger via admin API or Streamlit admin page (token-protected).
Transformation and Feature Engineering
Normalize time and units; deduplicate; symbol mapping.
Compute technical features (RSI, MAs, z-scored volumes).
Compute fundamentals (crush margins, basis proxies, stocks-to-use).
Macro features (DXY, WTI, rates).
Weather risk indices per region (standardized anomalies).
Sentiment weighted scores per category.
Key drivers table updated each run for the side panel.
Modeling
Baseline (statsmodels):
ARIMA/ARIMA+exog using curated.prices_daily and features.*; outputs forecasts.price_baseline.
Neural (PyTorch):
LSTM/GRU with lookback window, exogenous features (macro, weather, sentiment, fundamentals).
Train/val/test split with rolling origin; capture uncertainty (MC dropout or residual bootstrapping).
Write outputs to forecasts.price_nn; log runs/metrics; generate explanations.
Risk/Vol:
Rolling volatility and realized vol; optional simple GARCH-like estimate; write to features.volatility_signals or ops.realtime.
Explainability:
Permutation feature importance on validation/holdout; store in app.explanations.
Rationale templates: “Driver A↑, Driver B↓, Weather stress neutral → BUY/WATCH/HOLD because …”
Scenarios and Economic Impact
Deterministic shocks (FX ±, weather stress ±, demand ±, basis ±).
Monte Carlo around residuals for 30/60/90-day distributions.
Compute dollar impact for volume and hedge ratios; write app.econ_impact.
Backtesting engine to evaluate strategies and record strategy.performance.
Web Application (Streamlit on Render)
Theming:
Dark, high-contrast, modern; custom CSS; no emojis; 3D effects (glassmorphism, glow, depth).
Plotly dark template, HD lines; pydeck for 3D globe map.
Mobile responsiveness via Streamlit layout and CSS tweaks.
Pages:
Page 1: Procurement Command Center
Large signal indicator (deep red/amber/deep green), confidence meter, dollar impact.
Price chart with purchases, 30-day forecast bands, support/resistance, volume spikes.
Real-time drivers panel (China buying, Brazil weather, crush margins, funds).
Scenario sliders (volume, hedge split, timing) + cost table; risk alerts.
Page 2: Sentiment & Market Intelligence
Weighted “mood” gauge from sentiment.category_scores.
4x4 category grid; click to expand recent sources with impact scoring.
Narrative summary every 4 hours; “changes since yesterday” bullets.
Page 3: Strategy Lab & Supply Chain Map
3D globe (pydeck) with plants, routes, weather overlays, port congestion.
Pre-built scenarios (Brazil drought, China buying, mandate +10%, tariffs) and custom sliders; distributions for 30/60/90 days.
Backtest results and actual performance vs benchmark; savings and hit rate.
Sidebar intel (margins, freight, storage, alerts, technical levels).
Admin controls:
Token-protected admin page or FastAPI service to trigger refresh/pipelines and set refresh cadence.
Pipelines (CLI Scripts)
pipelines/ingest.py
Load CSVs → raw.market_prices; upsert curated.prices_daily (ZL).
Pull APIs (Yahoo, USDA, EIA, FRED, Alpha Vantage, CFTC); write to raw.*; maintain idempotency.
pipelines/features.py
Build curated.procurement_context, features.technical, features.macro, features.weather, features.key_drivers.
pipelines/models_baseline.py
Fit ARIMA/xreg; write forecasts.price_baseline; log to models.runs/metrics.
pipelines/models_nn.py
Train/score LSTM/GRU; write forecasts.price_nn; explanations and metrics; register runs.
pipelines/econ_impact.py
Run scenarios; write app.econ_impact; update app.signals_today with signal, confidence, and rationale.
Shared utils:
db/session.py (SQLAlchemy)
io/csv_loader.py (schema inference/upsert)
ml/datasets.py (windowing, feature assembly)
ml/models.py (torch modules)
ml/evaluate.py (metrics, importance)
config/settings.py (env handling)
Dev Tooling
IDEs:
PyCharm/IntelliJ for app/pipelines.
DataSpell for notebooks using the same utils; notebooks target Neon directly.
Environments:
requirements.txt; Python 3.12.
.env locally; environment vars on Render.
Code quality:
Black/ruff optional; pre-commit hooks optional.
Logging with structured logs; pipeline logs stored in models.runs.
Deployment and Operations
Render Web Service:
Build: pip install -r requirements.txt
Start: streamlit run app/Home.py --server.port $PORT --server.address 0.0.0.0
Env vars: DATABASE_URL, API keys, ADMIN_TOKEN, REFRESH_HOURS
Render Cron (every 8h by default):
Command: pip install -r requirements.txt && python pipelines/ingest.py && python pipelines/features.py && python pipelines/models_baseline.py && python pipelines/models_nn.py && python pipelines/econ_impact.py
Adjustable via app.parameters; admin page can change cadence and trigger on-demand.
Observability:
Render logs; DB health via Neon dashboard.
models.metrics table trend; alerting later if needed.
Security and Access
Secrets via Render env vars.
Principle of least privilege:
App service user: read-only to curated/features/forecasts/app; write to app.parameters (if needed) and features.procurement_scenarios.
Pipeline service user: write to all target tables.
Optional: signed admin token to run refresh.
Handoff and Client Experience
One HTTPS link (Render URL; optional custom domain).
Mobile-responsive, fast, high-definition visuals.
Documentation:
README with setup, deploy, env, CSV onboarding, cron control, admin usage.
Data dictionary for key tables.
Ongoing ops:
You approve schema, pages, pipelines; I implement.
Feature requests/changes via a simple approval loop.
