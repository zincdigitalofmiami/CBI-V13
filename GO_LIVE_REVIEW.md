# Go-Live Review Scaffold

Purpose: Provide a complete, structured review of the current system and a safe, prioritized plan to reach a local go-live aligned with the README page layout. This is a working document — update checkboxes as we proceed.

Last updated: 2025-09-30 10:15 local

---

## 1) Executive Summary
- Objective: Identify architectural/planning issues, missing data/pipelines, and blockers preventing go-live; then prioritize a safe path to load essential data and power the local dashboard (Pages 0–4).
- Scope: Streamlit app (Home + pages 0–4), Postgres schema, pipelines (ingest → features → models → econ impact), GCP deployment path (Cloud Run + Cloud SQL), and operations.

---

## 2) Current State Snapshot (from repo)
- App pages present:
  - [x] 0 — Health (app/pages/0_🩺_Health.py)
  - [x] 1 — Sentiment & Market Intelligence (app/pages/1_📊_Sentiment_&_Market_Intelligence.py)
  - [x] 2 — Strategy (app/pages/2_🗺️_Strategy_Lab_&_Supply_Chain_Map.py)
  - [x] 3 — Admin (app/pages/3_🔧_Admin.py)
  - [x] 4 — Geopolitical & Trade Intelligence (app/pages/4_🌐_Trade_Intelligence.py)
- Pipelines present:
  - [x] pipelines/ingest.py (ZL=F daily prices → curated.prices_daily + params)
  - [x] pipelines/features.py (technical/macro placeholders → features.*)
  - [x] pipelines/models_baseline.py (baseline forecasts → forecasts.price_baseline)
  - [x] pipelines/models_nn.py (placeholder)
  - [x] pipelines/econ_impact.py (signals → app.signals_today, app.econ_impact)
- DB/Schema:
  - [x] sql/schema.sql with schemas: raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy
  - [x] Trade Intelligence additive tables already defined (curated.trade_policy_probs, curated.trade_timeline, curated.congress_votes, curated.country_intel, raw.social_posts, sentiment.social_impact, features.fx_trade view)
- Ops/Tooling:
  - [x] Makefile targets: init-db, pipelines, app, gcp-setup, gcp-deploy, diagnose, git-now
  - [x] Diagnostics script: scripts/diagnose.py

---

## 3) Architectural/Planning Issues (to review)
- [ ] Environment configuration clarity (DATABASE_URL vs Cloud SQL IAM) and SSL requirements
- [ ] Missing minimal seed data for non-core pages (Trade Intelligence, Strategy analytics) leads to empty UIs
- [ ] Baseline model is placeholder (variance band) — acceptable for demo, but document expectations
- [ ] Lack of automated pipeline scheduling in dev (Cloud Scheduler or local cron) — manual runs only
- [ ] Monitoring/logging for pipeline runs (no app.pipeline_runs table exposed yet)
- [ ] Page filenames vs sidebar text for exact naming (cosmetic)

---

## 4) Why We Haven’t Gone Live (likely blockers)
- [ ] Database connectivity or SSL mode mismatches across environments
- [ ] Schema not applied to target database
- [ ] No initial data ingested; charts render empty
- [ ] No scheduled job to keep data fresh
- [ ] Expectations mismatch between README page data and currently ingested sources

---

## 5) Data Gaps (minimum viable for Pages 0–4)
- Prices (ZL=F): curated.prices_daily — REQUIRED
- Features: features.technical — REQUIRED for Strategy visuals
- Forecasts: forecasts.price_baseline — REQUIRED for Home signal context
- Signals: app.signals_today — REQUIRED for Command Center signal card
- Trade Intelligence seeds: curated.trade_policy_probs, curated.trade_timeline, curated.congress_votes, curated.country_intel — NICE TO HAVE to avoid empty grids
- Macro/FX: features.macro + raw.fx (for features.fx_trade view) — NICE TO HAVE for FX chart

---

## 6) Pipelines Incomplete or Pending Enhancements
- [ ] features.py: enrich with macro/FX and simple weather indices (optional for first go-live)
- [ ] models_baseline.py: upgrade to ARIMA(+exog) (next sprint)
- [ ] models_nn.py: implement LSTM short-term model (next sprint)
- [ ] Ingestion for FX/BRL and DXY (optional quick add)

---

## 7) Where We Got Off Course (observations)
- Overly broad scope earlier (logistics and deep geo layers) vs. immediate need for command signal and core market data
- Non-essential provider scripts (e.g., deprecated Neon provisioning) created confusion (now deprecated in repo)
- Documentation updates outpaced data readiness in DB, leading to pages expecting data not yet populated

---

## 8) Prioritized Safe Path to Local Go-Live (no destructive changes)
1. Configure env and apply schema
   - [ ] Ensure DATABASE_URL (add `?sslmode=require` if needed) or Cloud SQL IAM vars
   - [ ] `make init-db` to apply sql/schema.sql
2. Load essential data
   - [ ] `python pipelines/ingest.py` (ZL=F only)
   - [ ] `python pipelines/features.py` (technical placeholders)
   - [ ] `python pipelines/models_baseline.py`
   - [ ] `python pipelines/econ_impact.py`
3. Seed minimal Trade Intelligence rows (optional but recommended)
   - [ ] Upsert 4–8 rows into curated.trade_policy_probs
   - [ ] Add 3–5 items in curated.trade_timeline within next 30 days
   - [ ] Add 2–3 curated.congress_votes sample rows
   - [ ] Add 2–3 curated.country_intel snapshot rows
4. Launch dashboard locally
   - [ ] `make app` → verify Pages 0–4 render per README layout
5. Schedule refresh (dev)
   - [ ] Local cron or Cloud Run Job + Scheduler to run `python run_all.py` every 8 hours
6. Review & sign-off
   - [ ] Validate acceptance criteria (below) and record in this document

---

## 9) Safe Data & Risk Controls
- Use dev database; never run destructive `DROP`/`TRUNCATE` in pipelines
- All inserts are idempotent (unique constraints; ON CONFLICT DO NOTHING)
- Feature-flag any new ingestions with env vars (disabled by default)
- Keep ADMIN_TOKEN secret; do not print sensitive envs in logs

---

## 10) Acceptance Criteria (Local Go-Live)
- [ ] curated.prices_daily has recent ZL=F
- [ ] forecasts.price_baseline populated for 7/30/90/365 horizons
- [ ] app.signals_today has latest signal row
- [ ] Home page renders price + forecast band + signal card
- [ ] Health page row counts > 0 for core tables
- [ ] Strategy page shows at least technical chart; optional performance placeholders
- [ ] Trade Intelligence page shows non-empty placeholders (or friendly guidance)

---

## 11) Operational Readiness
- [ ] Makefile targets used: init-db, pipelines, app, diagnose
- [ ] Optional: audit target (see below) run and JSON attached
- [ ] Scheduling path chosen (local cron vs GCP Job)

---

## 12) RACI (Draft)
- Responsible: Eng (pipelines/data), App (pages wiring)
- Accountable: Product/Owner (go-live decision)
- Consulted: Data/ML for modeling roadmap; Infra for Cloud SQL/Run
- Informed: Finance/Exec

---

## 13) Artifacts to Produce
- Audit JSON output (scripts/audit_status.py → audit_status.json)
- Screenshots of Pages 0–4 rendering locally
- SQL row-count checks pasted here

---

## 14) Quick Commands
```bash
# 1) Apply schema
export $(grep -v '^#' .env | xargs)
make init-db

# 2) Pipelines (essential)
python pipelines/ingest.py && \
python pipelines/features.py && \
python pipelines/models_baseline.py && \
python pipelines/econ_impact.py

# 3) Launch app
make app

# 4) Optional audit
make audit
```

---

## 15) Notes
- This document is the authoritative checklist for local go-live readiness.
- Do not expand scope until all acceptance criteria are checked.
