# TODAY TODO — Complete Modeling Alignment (CBI‑V13)

Goal: Finish a production‑ready, horizon‑aware modeling loop consistent with the quantitative hierarchy of soybean oil price drivers. Keep all changes safe and idempotent.

Quick run references
- Init DB: export $(grep -v '^#' .env | xargs) && make init-db
- Pipelines (full): make pipelines  # or python run_all.py
- App: make app
- Diagnostics: make diagnose

1) Data ingestion (priority: high)
- [ ] Prices: ensure curated.prices_daily has ZL=F updated (pipelines/ingest.py)
- [ ] Palm: add settlement series for Palm Oil (e.g., BMD FCPO proxy or available palm series) → raw.market_prices; derive daily close series
- [ ] FX: ensure raw.fx has DXY (or proxy), BRL/USD; confirm features.fx_trade view works
- [ ] Macro: populate features.macro minimally (DXY, WTI, 10y rates)
- [ ] Optional Weather: seed features.weather with simple drought/temp/precip anomalies if data available today

2) Feature engineering (priority: high)
- [ ] Crush proxy: compute oilshare/COSI approximation from ZL and ZM → features.key_drivers (driver='crush_proxy')
- [ ] BOPO spread: ZL − Palm with z‑score and divergence flag → features.key_drivers (driver='bopo_spread')
- [ ] DXY/BRL: normalized FX features → features.key_drivers (driver='dxy_feature','brl_usd')
- [ ] Weather anoms: placeholders if data present → features.key_drivers (driver='weather_anom')

3) Baseline and NN modeling (priority: high)
- [ ] Baseline: keep placeholder variance band, but log params to models.runs and write app.explanations with top placeholder drivers
- [ ] NN scaffold: wire ml/models.py LSTM in pipelines/models_nn.py with safe fallback if features missing
- [ ] Horizons: 7/30/90/365 day outputs to forecasts.price_baseline and forecasts.price_nn

4) Signal & econ impact (priority: medium)
- [ ] Ensure app.signals_today updated with signal, confidence (from ensemble agreement), and dollar_impact stub
- [ ] Store rationale summarizing current factor state (e.g., crush_proxy strong, BOPO diverging)

5) App surfacing (priority: medium)
- [ ] Home: confirm price + forecast band + signal present
- [ ] Strategy page: show technicals and S&D if available; leave placeholders otherwise
- [ ] Trade Intelligence: confirm policy/FX panels render even if empty

6) Verification & QA (priority: high)
- [ ] Run make diagnose (check DB/HTTPS/Git)
- [ ] SQL checks: counts in curated.prices_daily, forecasts.price_baseline, app.signals_today
- [ ] Streamlit smoke test: no errors with empty optional tables

7) Deploy (if GCP path) (priority: medium)
- [ ] make gcp-deploy (Cloud Build → Cloud Run)
- [ ] Create Job for pipelines; schedule via Cloud Scheduler (see CLOUD_RUN.md)

Notes
- Idempotency: use ON CONFLICT DO NOTHING/UPDATE on inserts
- Provider‑agnostic DB: include sslmode=require if your provider needs SSL; Cloud SQL IAM supported
- Explainability: populate app.explanations for transparency even with placeholders
