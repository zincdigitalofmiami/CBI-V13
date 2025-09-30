# Review Package — TODO + Scaffolding (For Approval)

Purpose: Put the exact TODO list and scaffolding plan in one place for quick executive review and sign‑off. This compiles links, how to verify, and what decisions are needed.

Quick links
- TODAY TODO (execution checklist): TODAY_TODO.md
- Go‑Live Review & Scaffolding Plan: GO_LIVE_REVIEW.md
- Modeling Plan (driver hierarchy → features/models): MODELING_PLAN.md
- Architecture overview: ARCHITECTURE.md
- End‑to‑end steps (local + deploy): ALL_STEPS.md

What’s included
- TODO list covering data ingestion, features, modeling, signals, app surfacing, QA, and deploy.
- Scaffolding plan that reviews architecture, missing data/pipelines, blockers, and prioritization to go live safely.
- Modeling alignment with the quantitative hierarchy (weather, crush, palm substitution, macro, policy, speculation).
- How to run diagnostics and the audit tool.

How to verify (5 minutes)
1) Environment
   - export $(grep -v '^#' .env | xargs)
   - make diagnose  # repo/app/DB checks
   - python scripts/audit_status.py  # structured project audit
2) Data & pipelines
   - make init-db   # applies sql/schema.sql (idempotent)
   - make pipelines # or: python run_all.py
   - psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM curated.prices_daily;"
   - psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM forecasts.price_baseline;"
   - psql "$DATABASE_URL" -c "SELECT * FROM app.signals_today ORDER BY ds DESC LIMIT 1;"
3) App
   - make app  # streamlit run app/Home.py
   - Home shows: price chart, forecast band, signal card, parameters
   - Pages render even if optional tables are empty (safe fallbacks)

Decision & approvals checklist
- [ ] Accept the TODAY_TODO sequence as the execution plan for “today.”
- [ ] Approve the Go‑Live Scaffolding approach (focus on safe pipelines and minimal viable data first).
- [ ] Confirm deployment path (Google Cloud Run + Cloud SQL IAM, or alt). See CLOUD_RUN.md.
- [ ] Confirm signal policy thresholds/definitions and dollar‑impact assumptions.
- [ ] Approve data source priorities for next adds (FX/weather/palm/policy feeds).

Notes
- Provider‑agnostic Postgres. SSL may be required (use ?sslmode=require if your provider enforces SSL). Cloud SQL IAM auth supported.
- All schema operations are idempotent; pipelines use ON CONFLICT safeguards.
- Admin page is token‑protected (ADMIN_TOKEN). Rotate periodically.

Next steps after approval
- Execute TODAY_TODO.md in order.
- If GCP: make gcp-deploy, create Cloud Run Job for pipelines, schedule via Cloud Scheduler.
- Share live URL + confirm pipeline cadence is healthy.

Direct review questions
1) Anything you want added/removed from the TODO for Day‑1?
2) Any blocking dependencies not captured in GO_LIVE_REVIEW.md?
3) Are the Page 1–4 descriptions in README the correct product spec for this sprint?

Submitting this package
- This document exists in the repo at REVIEW_PACKAGE.md.
- To push updates any time: MSG="docs: update review package" make git-now
