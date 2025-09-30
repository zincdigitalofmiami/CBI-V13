# CBI-V13: Crystal Ball Intelligence Platform

Soybean Oil Market Intelligence & Procurement Decision Support

CBI-V13 is an AI-driven platform that ingests market, policy, and macro data; engineers features; trains baseline and advanced models; and serves BUY/WATCH/HOLD procurement guidance with quantified dollar impact via a Streamlit dashboard. The stack targets Google Cloud Run for the app and Cloud SQL for Postgres (with optional IAM auth). Postgres provider is agnostic; SSL may be required depending on provider.

Table of Contents
- Overview
- System Architecture
- Repository Structure
- Environment & Configuration
- Quick Start
- Local Development
- Data Pipelines
- Dashboard Pages
- Admin & Operations
- Deployment (Google Cloud Run)
- Troubleshooting
- FAQ
- Security & Secrets
- Roadmap
- License

Overview
- Primary Outcome: Clear daily action — Should I buy today or wait? — with confidence and dollar impact.
- Users: Procurement lead (primary), Ops/Supply Chain, Finance/Exec, Data/ML.
- Core Flow: Ingestion → Processing → Features → Models → Signals → Dashboard.

System Architecture
- Data Sources: Market prices (ZL=F, etc.), macro/FX, policy and congressional data, curated CSVs/APIs.
- Storage: Postgres with schemas: raw, curated, features, sentiment, forecasts, models, app, geo, ops, strategy.
- Processing: Python pipelines (pipelines/*) orchestrated by run_all.py.
- Modeling: Baseline ARIMA(+ exog) and advanced NN roadmap (LSTM/GRU/TabNet/GARCH).
- Serving: Streamlit app (app/Home.py, app/pages/*).
- Deployment: Google Cloud Run + Cloud SQL (IAM optional) using Cloud Build. Dockerfile provided.

Repository Structure
- app/Home.py — Streamlit entrypoint (Command Center)
- app/pages/ — Additional pages (Health, Sentiment & Market Intelligence, Strategy, Admin, Trade Intelligence)
- pipelines/ — ingest.py, features.py, models_baseline.py, models_nn.py, econ_impact.py
- db/session.py — SQLAlchemy engine (supports DATABASE_URL or Cloud SQL IAM)
- sql/schema.sql — Idempotent schema for all domains
- config/settings.py — Environment configuration
- ml/ — Reusable model/data helpers
- scripts/ — Setup, deploy, diagnostics, and Git helpers
- Makefile — Common tasks (init-db, pipelines, app, gcp-setup, gcp-deploy, diagnose, git-now)
- Docs — README.md, ALL_STEPS.md, CLOUD_RUN.md, ARCHITECTURE.md, WORKSTATION.md, DEPLOYMENT.md

Environment & Configuration
- Required
  - DATABASE_URL: SQLAlchemy Postgres URL (include sslmode=require if your provider needs SSL)
  - or USE_IAM_AUTH=true with Cloud SQL variables: CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_NAME
  - ADMIN_TOKEN: Token for Admin page
  - REFRESH_HOURS: Pipeline refresh cadence (e.g., 8)
- Optional API Keys
  - ALPHAVANTAGE_API_KEY, FRED_API_KEY, NOAA, etc. (only if you enable related ingestions)
- Local .env
  - cp .env.example .env and fill values; export to shell when running locally

Quick Start
Google Cloud (Recommended)
```bash
export PROJECT_ID=your-project-id
./scripts/gcp_setup.sh
make gcp-deploy
```
See CLOUD_RUN.md for Cloud SQL IAM, Jobs, and Scheduler.

Local Development
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env (DATABASE_URL, ADMIN_TOKEN, REFRESH_HOURS). If SSL is required, add ?sslmode=require.
make init-db   # applies sql/schema.sql
make pipelines # run end-to-end (or python run_all.py)
make app       # launch Streamlit locally
```

Data Pipelines
- Orchestration: run_all.py (calls all stages)
- Stages
  - pipelines/ingest.py: Loads ZL=F daily prices to curated.prices_daily; upserts app.parameters.refresh_hours
  - pipelines/features.py: Computes technical/macro placeholders into features.*
  - pipelines/models_baseline.py: Writes forecasts.price_baseline
  - pipelines/models_nn.py: Placeholder for NN outputs to forecasts.price_nn
  - pipelines/econ_impact.py: Computes app.signals_today and app.econ_impact
- Schema Guarantees
  - sql/schema.sql is safe to re-apply; uses IF NOT EXISTS and unique constraints for idempotency

Dashboard Pages (app/pages)
- 1 — Procurement Command Center (Chris's Daily Decision Page)
  - Top Section: Traffic Light Signal System
    - Giant circular indicator (takes up 1/3 of screen width) showing:
      - RED: "HOLD - Volatility >8% or price >$0.65/lb"
      - YELLOW: "WATCH - Decision zone, check scenarios"
      - GREEN: "BUY NOW - Optimal window detected"
    - Confidence meter below signal (0-100% based on neural network agreement)
    - Dollar impact display: "Buying today vs waiting: +$47,000 cost" or "-$23,000 savings"
  - Middle Section: Live Price Intelligence
    - Main chart (60% width): ZL futures with overlay of:
      - Your last 5 purchase points (green dots)
      - AI-predicted next 30 days (blue gradient showing confidence bands)
      - Critical levels (resistance at $0.62, support at $0.58)
      - Volume spikes that correlate with China buying
    - Side panel (40% width): Real-time drivers
      - China overnight buying: "Active - 15 cargoes"
      - Brazil weather: "Dry spell continuing - Mato Grosso"
      - Crush margins: "$42/ton (profitable, buying likely)"
      - Fund positioning: "Managed money adding longs"
  - Bottom Section: Procurement Scenarios
    - Interactive sliders for Chris to test:
      - "What if I need 500,000 lbs in 30 days?"
      - "What if I wait for harvest pressure?"
      - "What if I hedge 50% now, 50% later?"
    - Output table showing cost implications of each scenario
    - Risk alerts: "Warning: Tank storage 78% full" or "ADM Decatur maintenance in 14 days"
  - Data Sources Powering This Page:
    - zl_data (real-time prices)
    - procurement_signals (AI recommendations)
    - china_crushing_margins (demand indicator)
    - storage_capacity (operational constraints)
    - cftc_cot_reports (fund positioning)
- 2 — Sentiment & Market Intelligence
  - Top Section: Market Mood Ring
    - Sentiment gauge (semicircle, like a speedometer):
      - Far left: "Extremely Bearish"
      - Center: "Neutral"
      - Far right: "Extremely Bullish"
    - Current reading based on weighted average of:
      - News sentiment (40%)
      - Fund positioning (30%)
      - Technical indicators (20%)
      - Weather concerns (10%)
  - Middle Section: 16-Category News Grid
    - Heat map grid (4x4 tiles), each tile shows:
      - China Demand: "🔴 Negative - Herd recovery slower"
      - Brazil Infrastructure: "🟢 Positive - BR-163 flowing"
      - US Policy: "🟡 Neutral - RFS unchanged"
      - Biofuels: "🟢 Positive - SAF demand growing"
      - Palm Oil: "🔴 Negative - Indonesia flooding"
      - Trade Wars: "🟡 Neutral - No new tariffs"
      - Weather: "🔴 Negative - La Niña developing"
      - Processing: "🟢 Positive - All plants operational" (... and 8 more categories)
    - Click any tile → Drops down showing actual news items with impact scores
  - Bottom Section: Narrative Intelligence
    - AI-generated summary (updates every 4 hours): "Market is cautiously bullish due to Chinese buying interest, but Brazil's harvest is 65% complete and pressuring basis. Funds added 12,000 long positions this week. Weather premium is minimal with good conditions in South America."
    - Key changes from yesterday (bullet points):
      - "✓ China bought 10 cargoes overnight vs 3 yesterday"
      - "⚠ Brazil harvest pace accelerated to 8% weekly"
      - "✓ Biodiesel mandate proposal gained Senate support"
  - Data Sources Powering This Page:
    - social_sentiment (Twitter/Reddit scraping)
    - google_trends (search volume spikes)
    - cftc_cot_reports (fund sentiment)
    - news_articles (NLP-processed news)
    - All policy/regulation tables for context
- 3 — Strategy (Chris's Business Intelligence Page)
  - Top Section: Procurement Best Practices & Timing
    - Left Panel: Optimal Procurement Windows
      - Calendar heat map showing best buying days historically:
        - Deep green: Best days (typically Tuesday/Wednesday)
        - Red: Worst days (typically Monday morning, Friday afternoon)
      - Overlays showing WASDE report dates, options expiration, first notice days
      - Seasonal patterns graph:
        - 5-year average price by month
        - Harvest pressure periods highlighted
        - Chinese buying seasons marked
        - Your historical purchase timing overlaid
    - Right Panel: Contract Strategy Optimizer
      - Current recommendations:
        - "Lock 40% on next dip below $0.58"
        - "Stay spot market for 30% (volatility play)"
        - "Forward contract 30% for Q2 2025"
      - Contract comparison table:
        - Spot vs 30-day vs 90-day forward pricing
        - Historical basis patterns
        - Storage cost implications
  - Middle Section: Industry Intelligence
    - Four-column layout:
      - Column 1: Key Players
        - Your competitors' activity:
          - "Sysco locked Q1 supply last week"
          - "Restaurant Depot seeking 500K lbs"
          - "US Foods went spot market"
        - Processor intelligence:
          - ADM: "Running full, selling Q2"
          - Bunge: "Maintenance planned March"
          - Cargill: "Expanding crush capacity"
      - Column 2: Pricing Trends
        - Basis tracker: Local basis vs CBOT
        - Quality premiums: Refined vs crude
        - Regional differentials: IL vs IA vs IN pricing
        - Transportation impact: Rail vs truck economics
      - Column 3: Recent Developments
        - Last 7 days critical changes:
          - "EPA considering B40 mandate"
          - "Argentina strike resolved"
          - "China cancelled 5 cargoes"
          - "Mississippi barge rates +20%"
        - Each item tagged with impact: HIGH/MEDIUM/LOW
      - Column 4: Market Structure
        - Futures curve: Contango vs backwardation
        - Spreads: Soy/corn, soy/meal, oil share
        - Technical setup: Support/resistance levels
        - Options positioning: Large open interest strikes
  - Bottom Section: Deep Dive Analytics
    - Tab 1: U.S. Production & Storage
      - Interactive US map showing:
        - Soybean production by state (colored by yield)
        - Crushing capacity (bubble size)
        - Storage utilization (fill percentage)
        - Click state → Detailed breakdown
      - Table: Weekly crush rates, oil yield, capacity utilization
    - Tab 2: Global Supply & Demand
      - Stacked bar chart: World soybean oil S&D
        - Production: US, Brazil, Argentina, Others
        - Consumption: China, India, US, EU, Others
        - Ending stocks trend line
      - Trade flow diagram: Animated arrows showing monthly trade flows between major countries
    - Tab 3: Soy Complex Value Chain
      - Interactive flowchart:
        - Soybeans → Crushing → Oil (18%) + Meal (80%) + Hulls (2%)
        - Oil → Food use (70%), Biodiesel (25%), Industrial (5%)
        - Price relationships and margins at each step
      - Profitability calculator: Input soybean price → See oil/meal values
    - Tab 4: Food & Industrial Demand
      - Restaurant industry health:
        - Same-store sales growth
        - New restaurant openings
        - QSR vs casual dining trends
      - Competing oils market share:
        - Pie chart: Soy vs Palm vs Canola vs Sunflower
        - Substitution triggers (price differentials)
      - Biodiesel demand curve: RFS mandates, state programs, voluntary use
  - Right Sidebar: Strategy Tools
    - Quick Calculators:
      - Storage cost calculator (days held × rate)
      - Hedge ratio optimizer
      - Basis convergence tracker
      - Forward curve analyzer
    - Your Performance Metrics:
      - Average purchase price vs market: -2.1%
      - Best decision this month: "Bought pre-WASDE"
      - Worst decision: "Missed harvest low"
      - YTD procurement savings: $247,000
    - AI Strategy Suggestions:
      - "Consider December calls at $0.60 strike"
      - "Basis widening suggests wait 2 weeks"
      - "Technical breakout likely above $0.615"
  - Data Sources for Strategy Page:
    - All processor operation tables (capacity, schedules)
    - usda_wasde_complete (supply/demand balance)
    - export_sales_weekly (demand signals)
    - crush_weekly (processing economics)
    - food_manufacturing, restaurant_sales (end-use demand)
    - inter_commodity_spreads (soy complex relationships)
    - Historical patterns from all price tables
- 4 — Geopolitical & Trade Intelligence
  - Top Section: Trump Trade Policy Dashboard
    - Left Panel: Tariff Threat Matrix
      - Heat map grid showing tariff probability by country/commodity:
        - China soybeans: 85% probability, 25% proposed rate
        - Brazil imports: 45% probability, 10% proposed rate
        - Canada canola: 30% probability, 15% proposed rate
        - Mexico products: 60% probability, 20% proposed rate
      - Timeline: Key dates for trade decisions, Congress votes, implementation
    - Center: Trump Twitter/Truth Social Feed Impact
      - Live sentiment analyzer of Trump's posts:
        - Real-time parsing for trade-related keywords
        - Historical correlation: "China tweet = -3% average move"
        - Alert system: "HIGH RISK: Trump speaking at 2 PM on trade"
      - Prediction model: "67% chance of trade announcement this week based on pattern analysis"
    - Right Panel: Congressional Trade Votes
      - Upcoming votes on trade legislation:
        - Farm Bill amendments
        - China competition bills
        - USMCA modifications
      - Vote predictions based on member positions
      - Impact assessment: Effect on soy oil if passed
  - Middle Section: Global Trade Relations
    - Four-Column Country Intelligence:
      - Column 1: US-China Relations
        - Current status: "Phase One holding, Phase Two dead"
        - Purchase commitments: "China at 67% of target"
        - Retaliation risk: "HIGH if tech sanctions increase"
        - Key indicators:
          - Taiwan tensions meter
          - Technology restrictions impact
          - Agricultural purchase tracking
      - Column 2: Brazil Competition
        - Brazil-China deals: "New 10-year agreement pending"
        - Currency advantage: "Real at 5.2, giving 8% edge"
        - Infrastructure progress: "Northern Arc 70% complete"
        - Market share war: US 28% vs Brazil 55% of China imports
      - Column 3: India/Pakistan Dynamics
        - Import duties: Current rates and proposed changes
        - Palm vs soy battle: Policy shifts favoring which oil
        - GMO stance: Approval status affecting US exports
        - Domestic production: Self-sufficiency goals
      - Column 4: EU/UK Regulations
        - Deforestation rules: "EUDR blocking 30% of Brazil supply"
        - Sustainability premiums: "+$40/ton for certified"
        - Ukraine conflict impact: Sunflower oil disruption
        - Brexit effects: UK separate trade deals
  - Bottom Section: Deep Dive Intelligence Tabs
    - Tab 1: Tariff Scenario Modeling
      - Interactive calculator:
        - Slide to adjust: "China retaliatory tariff %" (0-50%)
        - See impact on: US export volumes, basis, domestic prices
        - Historical examples: 2018 tariff war impact replay
      - Mitigation strategies:
        - "If 25% tariff imposed: Domestic basis drops $0.80/bu"
        - "Biodiesel demand could absorb 40% of surplus"
    - Tab 2: Trade Flow Disruption Map
      - Animated global map showing:
        - Normal trade flows (green arrows)
        - Disrupted flows under tariffs (red arrows)
        - Alternative routing (yellow arrows)
        - Click country → See detailed trade balance
    - Tab 3: Political Intelligence
      - Key decision makers:
        - Agriculture Secretary: Position on exports
        - Trade Representative: Current negotiations
        - Senate Ag Committee: Member positions
        - House Ways & Means: Tariff proposals
      - Lobbying activity:
        - ASA (American Soybean Association) positions
        - Food manufacturer concerns
        - Biodiesel coalition priorities
    - Tab 4: Currency & Competitive Position
      - Real-time FX impact:
        - Dollar index vs commodity currencies
        - Brazil Real giving advantage/disadvantage
        - Argentina peso chaos impact
        - China Yuan policy effects
      - Competitive matrix:
        - US vs Brazil vs Argentina production costs
        - Shipping differentials to key markets
        - Quality premiums by origin
  - Right Sidebar: Trade War Alerts
    - Risk Dashboard:
      - DEFCON-style threat level (1-5)
      - Current: "LEVEL 3 - Elevated Risk"
      - Key triggers being monitored
    - Flash Updates (last 24 hours):
      - "Trump mentioned agriculture in speech"
      - "China state media criticizes US policy"
      - "Brazil signs new export agreement"
      - "India considering import duty change"
    - Historical Patterns:
      - "Trade wars in election years: 73% chance"
      - "Average price impact of tariffs: -12%"
      - "Time to recover from trade war: 18 months"
    - Action Items for Chris:
      - "Consider domestic-only suppliers as backup"
      - "Lock prices before January policy risk"
      - "Monitor Brazil basis for arbitrage"
  - Data Sources for Geopolitical Page:
    - china_trade_relations (tariff tracking)
    - us_china_phase_deals (agreement status)
    - brazil_china_agreements (competition intelligence)
    - india_import_policies (market access)
    - congressional_ag_committee (political positions)
    - farm_bill_negotiations (policy direction)
    - usd_index, brl_real, cny_yuan (currency wars)
    - News sentiment analysis for Trump impact
    - All policy and regulation tables

Admin & Operations
- Makefile Targets
  - init-db — apply schema to DATABASE_URL
  - pipelines — run full pipeline chain
  - app — start Streamlit
  - gcp-setup — provision GCP infra (APIs, Cloud SQL, Artifact Registry)
  - gcp-deploy — build & deploy via Cloud Build to Cloud Run
  - diagnose — run repo/app diagnostics
  - git-now — stage, commit, push (uses scripts/git_now.sh)
- Diagnostics
  - python scripts/diagnose.py prints environment, Git, network, DB reachability (with hints for SSL/Cloud SQL IAM)

Deployment (Google Cloud Run)
- Cloud Build
  - make gcp-deploy builds container and deploys to Cloud Run
- Database Options
  - DATABASE_URL (any Postgres) — include sslmode=require if needed
  - Cloud SQL IAM — set USE_IAM_AUTH=true and CLOUD_SQL_CONNECTION_NAME, DB_USER, DB_NAME
- Jobs & Scheduling
  - Cloud Run Jobs for pipelines; schedule via Cloud Scheduler (see CLOUD_RUN.md)

Troubleshooting
- Database not reachable
  - Ensure DATABASE_URL is set (or USE_IAM_AUTH=true with Cloud SQL vars)
  - Some providers require ?sslmode=require in the URL
- Ingestion or pipelines fail
  - Rerun make pipelines; check logs; ensure outbound internet and symbols are valid
- Empty charts
  - Verify curated.prices_daily and forecasts.price_baseline have rows; run pipelines
- Git issues
  - make git-now or bash scripts/git_doctor.sh

FAQ
- Do I need Google Cloud? No; you can run locally or on any host. README emphasizes Cloud Run because it’s a solid default.
- Which Postgres? Any managed Postgres is fine. If SSL is enforced, include sslmode=require. Cloud SQL IAM is supported.
- Where do signals come from? From model outputs (forecasts + econ impact), not heuristics embedded in pages.

Security & Secrets
- Store secrets (DATABASE_URL, ADMIN_TOKEN, API keys) as environment variables.
- Consider Google Secret Manager for production.
- Admin page is token‑protected; rotate ADMIN_TOKEN periodically.

Roadmap
- Harden baseline ARIMA(+ exog) with parameter search and monitoring
- Implement LSTM/GRU in models_nn.py and persist to forecasts.price_nn
- Expand ingestions (FX, weather, policy feeds) and enrich features
- Add app.pipeline_runs logging and surface status on Admin page
- Integrate sentiment/RAG pipeline and alerting

License
This project is licensed under the MIT License. See LICENSE for details.
