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
