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

EXAMPLE: 
# Crystal Ball Soybean Oil Futures Platform – Budget-Friendly, Scheduled AI Agent Solution

## Objectives
- Institutional-grade procurement signals and intelligence.
- Cap cloud spend at **$300/month** (optimize for GCP pricing).
- No real-time processing; batch updates every 8 hours or on app open.
- Maintain all best practices: raw → staging → curated → features → forecasts (no bypassing).
- Dashboard with actionable signals, scenario toggles, sentiment, and confidence.

---

## 1. Cost-Control Principles

- **Batch, not streaming/real-time:** All data/ML jobs run on a schedule or when user requests.
- **Small compute footprints:** Use serverless and preemptible resources where possible.
- **BigQuery:** Partitioned tables, scheduled queries, cap scanned data.
- **Vertex AI:** Use custom training only as needed; leverage BQML for quick wins.
- **Cloud Run:** Scale-to-zero; run scrapers/APIs only during update windows.
- **Disable unused endpoints/services.**
- **Monitor billing:** Set up GCP budget alerts (`$300` cap) and billing dashboard.

---

## 2. Data Ingestion

### 2.1. Scheduled Data Loads
- **Cloud Storage:** Drop new CSVs as usual.
- **Cloud Functions (or Cloud Run):**  
  - Trigger every 8 hours (via Cloud Scheduler) or on-demand via API from app.
  - Ingest CSVs, run scrapers, and call APIs.
- **APIs:** Use only during scheduled/batch runs (Yahoo Finance, USDA, EIA, etc.).

---

## 3. Data Transformation

- **BigQuery:** 
  - Raw tables for ingest.
  - Batch Dataform SQL transformations to staging, curated, features tables.
  - Schedule transformations every 8 hours or on-demand.

---

## 4. Machine Learning

### 4.1. Quick Wins (Low-Cost)
- **BigQuery ML:**  
  - Train ARIMA_PLUS_XREG and other models directly in BQML.
  - Schedule retraining every 8 hours.
  - Low cost, no external compute.

### 4.2. Advanced ML (Budget-Conscious)
- **Vertex AI:**  
  - Use only for features that need deep learning (LSTMs, NLP models).
  - Run custom jobs only during scheduled batch windows.
  - Limit data size and training epochs to control cost.
  - Consider preemptible instances for custom training.

### 4.3. Sentiment Analysis
- **NLP via Vertex AI or Hugging Face:**  
  - Process news articles in batch (not continuous).
  - Store sentiment scores in features.sentiment_scores.

---

## 5. Forecast Output

- **Forecasts written to forecasts.* BigQuery tables.**
- **No streaming—only batch inserts after scheduled/model runs.**
- **Tables are sacred: only models write here.**

---

## 6. Dashboard Integration

- **Dashboard fetches forecasts/features from BigQuery.**
- **On app open:**  
  - Option to trigger data ingest + ML pipeline (on-demand).
  - User sees latest available signals.
- **Charts:** ApexCharts/Recharts/Plotly for prices, volatility, forecasts, sentiment.
- **Signals:** BUY/WATCH/WAIT, with rationale and confidence.
- **Scenario Toggles:**  
  - Select and re-run pipeline with toggled parameters (on-demand).

---

## 7. MLOps & Scheduling

- **Vertex AI Pipelines + Cloud Scheduler:**  
  - Pipelines run every 8 hours or when triggered by app/API.
  - Automate entire workflow: ingest → transform → train → forecast → deploy.
- **Monitoring:**  
  - Use Vertex AI Model Monitoring, but check drift/accuracy only after each scheduled run.
  - Set up email/SMS billing alerts for $300 threshold.

---

## 8. Security & IAM

- **Principle of least privilege:**  
  - Restrict access to buckets, BigQuery, Vertex AI, Cloud Run.
- **Disable public endpoints.**
- **Monitor usage and access logs.**

---

## 9. Cost Estimation Tips

- **BigQuery:**  
  - Use partitioned tables, minimize scanned data.
  - Scheduled queries, avoid on-demand ad-hoc queries.
- **Vertex AI:**  
  - Limit custom training jobs, use BQML where possible.
  - Use preemptible machines for custom training.
- **Cloud Run/Functions:**  
  - Scale-to-zero, only run on schedule or on-demand.
- **Cloud Storage:**  
  - Minimal cost for batch data.

---

## 10. Implementation Checklist

- [ ] Cloud Scheduler batch trigger for pipeline (every 8 hours).
- [ ] On-demand API trigger for pipeline (from app/dashboard).
- [ ] Batch ingestion agents (Cloud Run/Functions).
- [ ] Dataform batch transformations.
- [ ] BQML scheduled model training.
- [ ] Vertex AI custom jobs—only as needed, batch run.
- [ ] Sentiment batch processing.
- [ ] Forecasts written to BigQuery.
- [ ] Dashboard fetches latest batch forecasts.
- [ ] Budget alerts enabled.
- [ ] Security/IAM reviewed.

---

## Example: Scheduled Pipeline Trigger

1. **Cloud Scheduler:**  
   - Cron: Every 8 hours  
   - Triggers Cloud Function or Cloud Run job to start pipeline.

2. **On App Open:**  
   - App calls API endpoint to trigger pipeline immediately.

3. **Pipeline Flow:**  
   - Ingest data (CSV, scrapers, APIs)
   - Transform (Dataform)
   - Train models (BQML, Vertex AI as needed)
   - Write forecasts to BigQuery
   - Dashboard pulls new data

---

## Notes

- **No real-time updates**: All updates are batch, every 8 hours or manual trigger.
- **$300/month cap**: If bill approaches limit, reduce job frequency (e.g., every 12 or 24 hours), limit data processed, or pause advanced ML jobs.
- **Can later upgrade to more frequent or real-time if budget increases.**

---

_Contact: Project Crystal Ball Engineering Team / U.S. Oil Solutions Lead_
