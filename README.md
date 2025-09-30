# CBI-V13: Crystal Ball Intelligence Platform

**Soybean Oil Market Intelligence & Procurement Decision Support System**

Crystal Ball V13 (CBI-V13) is an AI-powered platform that provides real-time market intelligence, price forecasting, and procurement recommendations for soybean oil trading and procurement decisions.

## 🚀 Quick Start

### Deploy to Google Cloud (Recommended)
```bash
# Set your Google Cloud project
export PROJECT_ID=your-project-id

# One-command setup (enables APIs, sets up Cloud SQL/Artifact Registry/IAM)
./scripts/gcp_setup.sh

# Deploy via Cloud Build to Cloud Run
make gcp-deploy
```

For full Cloud Run + Cloud SQL guidance (including IAM auth and Jobs scheduling), see CLOUD_RUN.md.

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database settings (Postgres). If your provider enforces SSL, include ?sslmode=require.

# Set up database (applies sql/schema.sql)
make init-db

# Run pipelines (end-to-end)
make pipelines

# Start web app (Streamlit dashboard)
make app
```

## 📊 Features

### Procurement Command Center
- **Real-time Signals**: BUY/WATCH/HOLD recommendations with confidence scores
- **Price Forecasting**: 7-day to 365-day forecasts using ARIMA and neural networks
- **Economic Impact**: Dollar impact calculations for procurement decisions

### Market Intelligence
- **Sentiment Analysis**: News and policy impact scoring
- **Technical Indicators**: RSI, moving averages, volatility measures
- **Supply Chain Mapping**: Geographic visualization of key nodes and disruptions

### Strategy Lab
- **Scenario Modeling**: "What if" analysis for droughts, tariffs, demand changes
- **Backtesting**: Historical performance of different procurement strategies
- **Risk Assessment**: VaR calculations and hedge recommendations

## 🖥️ Dashboard Pages

Current pages (app/pages):
- Health: Connection checks, row counts, and latest records; tips for DATABASE_URL vs Cloud SQL IAM.

- Page 1 — Procurement Command Center (Chris’s Daily Decision Page):
  - Traffic Light Signal System (giant circular indicator):
    - RED: "HOLD - Volatility >8% or price >$0.65/lb"
    - YELLOW: "WATCH - Decision zone, check scenarios"
    - GREEN: "BUY NOW - Optimal window detected"
  - Confidence meter (0–100% based on neural network agreement)
  - Dollar impact display: e.g., "Buying today vs waiting: +$47,000 cost" or "- $23,000 savings"
  - Live Price Intelligence (main chart + overlays):
    - ZL futures with last 5 purchase points, AI next-30-day forecast band, key support/resistance
    - Volume spikes correlated with China buying
  - Real-time drivers side panel: China overnight buying, Brazil weather, crush margins, fund positioning
  - Procurement Scenarios: sliders for need-in-30-days, harvest pressure, 50/50 hedge; output table + risk alerts

- Page 2 — Sentiment & Market Intelligence:
  - Market Mood Ring (semi-circle gauge): Extremely Bearish ← Neutral → Extremely Bullish
  - Weighted inputs: News sentiment (40%), Fund positioning (30%), Technicals (20%), Weather (10%)
  - 16-Category News Grid (4x4) with drilldowns and impact scores
  - Narrative Intelligence (auto-updated every 4 hours) with key changes since yesterday

- Page 3 — Strategy (Chris’s Business Intelligence Page):
  - Optimal Procurement Windows: calendar heatmap + seasonal patterns; overlays for WASDE, OPEX, FND
  - Contract Strategy Optimizer: current mix (e.g., 40/30/30), comparison (spot vs 30/90-day), basis/storage implications
  - Industry Intelligence (4 columns): Key Players, Pricing Trends, Recent Developments, Market Structure
  - Deep Dive Analytics Tabs:
    1) U.S. Production & Storage (map + weekly crush/utilization table)
    2) Global Supply & Demand (stacked S&D + trade flow diagram)
    3) Soy Complex Value Chain (interactive flow + profitability calc)
    4) Food & Industrial Demand (restaurant metrics, competing oils, biodiesel curve)
  - Strategy Tools (sidebar): quick calculators, performance metrics, AI strategy suggestions

- Page 4 — Geopolitical & Trade Intelligence (context only — Command Center owns the signal):
  - Tariff Threat Matrix: probability and proposed rate by country/commodity
  - Trump Feed Impact: trade-keyword parsing, historical correlation, alerting (e.g., HIGH RISK windows)
  - Policy Timeline and Congressional Trade Votes: upcoming votes, pass probabilities, impact assessment
  - Country Snapshots: US–China, Brazil, India/Pakistan, EU/UK key metrics
  - FX & Macro Panel: BRL/USD, DXY, WTI, rates (features.fx_trade)
  - Trade War Alerts: DEFCON level, flash updates, historical patterns, action items

- Admin (protected by ADMIN_TOKEN): Parameters (e.g., refresh cadence), manual pipeline triggers.

## 🏗️ Architecture

### Core Pipeline

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
