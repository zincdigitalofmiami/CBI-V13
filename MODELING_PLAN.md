# Modeling Plan — Quantitative Hierarchy Alignment (CBI‑V13)

Purpose: Align CBI‑V13 modeling with the quantitative hierarchy of soybean oil price drivers and define concrete actions to reach a production‑ready multi‑horizon forecast feeding BUY/WATCH/HOLD signals.

Core takeaway: No single factor explains >45% of variance. We will use a multi‑factor, horizon‑aware approach: short‑term DL for pattern capture; medium‑term hybrid decomposition + ML; long‑term structural econometrics.

Factor hierarchy (driver → target features/tables)
- Weather (35–45%):
  - Features: precip/temperature anomalies, drought indices, ENSO signals; satellite vegetation (NDVI/SIF) proxies when available.
  - Tables: features.weather (sql/schema.sql), raw.weather (upstream), features.key_drivers.
- Crush economics & supply‑demand (30–40%):
  - Features: crush margin proxy (oilshare/COSI with ZL and ZM, or price‑based proxy), stocks‑to‑use, production/exports by region.
  - Tables: curated.supply_demand, features.technical (oilshare proxy), features.key_drivers.
- Palm oil substitution (15–25%):
  - Features: BOPO spread (ZL − Palm), correlation bands, divergence flags.
  - Tables: raw.market_prices (add palm), features.key_drivers.
- Macro/FX (15–20%):
  - Features: DXY, BRLUSD, 10y rates, WTI; carry proxies.
  - Tables: features.macro, raw.fx, view features.fx_trade.
- Biofuel policy (structural level shift):
  - Features: RD/biodiesel policy dummies; DEFCON‑style demand regime.
  - Tables: curated.policy (via curated.trade_policy_probs, curated.trade_timeline), features.key_drivers.
- Speculation/positioning (5–10%):
  - Features: CFTC managed money net; options skew; CVOL.
  - Tables: raw.market_prices (options if added), sentiment.category_scores (if used).

Modeling by horizon
- Short‑term (1–7d): DL sequence models (NBEATSX/Transformer proxy via LSTM for now) using last 5–10 days of prices + high‑freq features (FX, palm, weather updates). Target: MAPE 3–5% on holdout.
- Medium‑term (1–3m): Hybrid decomposition (CEEMDAN/VMD placeholder) + ML (GBM/LSTM) with monthly USDA/WASDE revisions, crush trends, China imports pace, weather forecasts. Target: MAPE 6–12%.
- Long‑term (6–12m): Structural econometric approach (futures‑basis, stocks‑to‑use, marketing weights) inspired by ERS methodology. Target: interpretable forecasts with documented error bands.

Implementation map (repo linkage)
- Pipelines: pipelines/ingest.py, pipelines/features.py, pipelines/models_baseline.py, pipelines/models_nn.py, pipelines/econ_impact.py.
- Schema: sql/schema.sql already includes features.weather, features.macro, curated.supply_demand, curated.trade_* and features.fx_trade view.
- App Pages: Home (signals), Sentiment, Strategy, Trade Intelligence.

Evaluation & governance
- Track runs and metrics: models.runs, models.metrics.
- Benchmarks: Random Walk (end‑of‑period), naive seasonal, walk‑forward validation. Report relative RMSE and MAPE by horizon.
- Explainability: store top_features_json in app.explanations; use SHAP/feature importances where applicable.

Milestones (today)
1) Extend ingest to pull palm and BRLUSD/ DXY (if not already), and ensure features.macro populated.
2) Compute factor placeholders in features.py: crush_proxy, bopo_spread, dxy_feature, weather_anoms (if data available), writing to features.key_drivers.
3) Baseline forecast: keep simple variance‑band placeholder but log factors in app.explanations to surface drivers on Home.
4) NN scaffold: ensure ml/models.py LSTM is used in pipelines/models_nn.py with safe fallbacks; do not break when features missing.
5) Econ impact: continue to compute signals from forecasts with confidence bands; later refine using factor regime logic.

Success criteria (acceptance)
- forecasts.price_baseline has current horizons.
- app.signals_today populated daily.
- features.key_drivers includes at least: crush_proxy, bopo_spread, dxy_feature; weather fields optional on day‑1.
- Pages render end‑to‑end with no data crashes.

Notes
- Remain provider‑agnostic for Postgres. For Cloud SQL IAM, see CLOUD_RUN.md.
- When adding new sources, ensure idempotency and ON CONFLICT safeguards.
