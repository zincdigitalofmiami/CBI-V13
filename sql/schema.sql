-- Google Cloud SQL Postgres schema for U.S. Oil Solution Intelligence

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS curated;
CREATE SCHEMA IF NOT EXISTS features;
CREATE SCHEMA IF NOT EXISTS sentiment;
CREATE SCHEMA IF NOT EXISTS forecasts;
CREATE SCHEMA IF NOT EXISTS models;
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS geo;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS strategy;

-- raw tables
CREATE TABLE IF NOT EXISTS raw.market_prices (
    ts timestamptz,
    symbol text,
    price double precision,
    open double precision,
    high double precision,
    low double precision,
    volume double precision,
    source text
);

CREATE TABLE IF NOT EXISTS raw.policy_events (
    ts timestamptz,
    region text,
    topic text,
    text text,
    source text
);

CREATE TABLE IF NOT EXISTS raw.weather (
    ts timestamptz,
    region text,
    metric text,
    value double precision,
    source text
);

CREATE TABLE IF NOT EXISTS raw.news (
    ts timestamptz,
    title text,
    url text,
    outlet text,
    text text,
    category text
);

CREATE TABLE IF NOT EXISTS raw.fx (
    ts timestamptz,
    base text,
    quote text,
    rate double precision,
    source text
);

-- curated tables
CREATE TABLE IF NOT EXISTS curated.prices_daily (
    ds date,
    symbol text,
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    volume double precision
);

CREATE TABLE IF NOT EXISTS curated.procurement_context (
    ds date,
    basis double precision,
    crush_margin double precision,
    freight_idx double precision,
    storage_utilization double precision
);

CREATE TABLE IF NOT EXISTS curated.supply_demand (
    ds date,
    region text,
    production double precision,
    stocks double precision,
    use double precision,
    exports double precision
);

-- features tables
CREATE TABLE IF NOT EXISTS features.key_drivers (
    ts timestamptz,
    driver text,
    value double precision,
    unit text,
    status text,
    note text
);

CREATE TABLE IF NOT EXISTS features.technical (
    ds date,
    symbol text,
    rsi double precision,
    ma7 double precision,
    ma30 double precision,
    ma90 double precision,
    vol_z double precision
);

CREATE TABLE IF NOT EXISTS features.macro (
    ds date,
    dxy double precision,
    wti double precision,
    inflation double precision,
    rates10y double precision
);

CREATE TABLE IF NOT EXISTS features.weather (
    ds date,
    region text,
    drought_idx double precision,
    temp_anom double precision,
    precip_anom double precision
);

-- sentiment tables
CREATE TABLE IF NOT EXISTS sentiment.category_scores (
    ts timestamptz,
    category text,
    score double precision,
    label text,
    weight double precision,
    top_items_json jsonb
);

-- forecasts tables
CREATE TABLE IF NOT EXISTS forecasts.price_baseline (
    run_ts timestamptz,
    ds date,
    horizon_days int,
    y_hat double precision,
    y_lo double precision,
    y_hi double precision,
    model_version text
);

CREATE TABLE IF NOT EXISTS forecasts.price_nn (
    run_ts timestamptz,
    ds date,
    horizon_days int,
    y_hat double precision,
    y_lo double precision,
    y_hi double precision,
    model_version text
);

-- models tables
CREATE TABLE IF NOT EXISTS models.runs (
    run_id text,
    started_at timestamptz,
    finished_at timestamptz,
    model text,
    params_json jsonb,
    status text
);

CREATE TABLE IF NOT EXISTS models.metrics (
    run_id text,
    metric text,
    value double precision,
    horizon int
);

-- app tables
CREATE TABLE IF NOT EXISTS app.signals_today (
    ds date,
    signal text,
    confidence double precision,
    dollar_impact double precision,
    rationale text
);

CREATE TABLE IF NOT EXISTS app.parameters (
    key text PRIMARY KEY,
    value text
);

CREATE TABLE IF NOT EXISTS app.explanations (
    run_id text,
    ds date,
    top_features_json jsonb,
    reason_text text
);

CREATE TABLE IF NOT EXISTS app.econ_impact (
    scenario text,
    ds date,
    delta_price double precision,
    notes text
);

CREATE TABLE IF NOT EXISTS app.purchases (
    ts timestamptz,
    quantity_lbs double precision,
    price double precision,
    note text
);

-- geo tables
CREATE TABLE IF NOT EXISTS geo.nodes (
    id text,
    name text,
    type text,
    lat double precision,
    lon double precision,
    capacity double precision,
    status_json jsonb
);

CREATE TABLE IF NOT EXISTS geo.edges (
    src_id text,
    dst_id text,
    kind text,
    weight double precision,
    status_json jsonb
);

CREATE TABLE IF NOT EXISTS geo.port_metrics (
    port text,
    ts timestamptz,
    vessels_waiting int,
    avg_delay_days double precision
);

-- ops tables
CREATE TABLE IF NOT EXISTS ops.realtime (
    ts timestamptz,
    crush_margin double precision,
    freight_rate double precision,
    storage_level double precision,
    alert_text text
);

-- strategy tables
CREATE TABLE IF NOT EXISTS strategy.backtests (
    strategy text,
    metric text,
    value double precision
);

CREATE TABLE IF NOT EXISTS strategy.performance (
    ds date,
    realized_cost double precision,
    benchmark_cost double precision,
    savings_cum double precision
);


-- Idempotency constraints and indexes for ON CONFLICT support
ALTER TABLE curated.prices_daily
    ADD CONSTRAINT IF NOT EXISTS uq_prices_daily UNIQUE (ds, symbol);

ALTER TABLE features.technical
    ADD CONSTRAINT IF NOT EXISTS uq_features_technical UNIQUE (ds, symbol);

ALTER TABLE forecasts.price_baseline
    ADD CONSTRAINT IF NOT EXISTS uq_price_baseline UNIQUE (run_ts, ds, horizon_days);

ALTER TABLE forecasts.price_nn
    ADD CONSTRAINT IF NOT EXISTS uq_price_nn UNIQUE (run_ts, ds, horizon_days);

ALTER TABLE models.runs
    ADD CONSTRAINT IF NOT EXISTS pk_models_runs PRIMARY KEY (run_id);

ALTER TABLE app.explanations
    ADD CONSTRAINT IF NOT EXISTS uq_app_explanations UNIQUE (run_id, ds);


-- Trade Intelligence additions (optional, safe if absent in app)
CREATE TABLE IF NOT EXISTS curated.trade_policy_probs (
  as_of date NOT NULL,
  country text NOT NULL,
  commodity text NOT NULL,
  prob double precision NOT NULL,
  proposed_rate double precision,
  rationale text,
  PRIMARY KEY (as_of, country, commodity)
);

CREATE TABLE IF NOT EXISTS curated.trade_timeline (
  event_ts timestamptz NOT NULL,
  label text NOT NULL,
  category text,
  url text,
  importance int,
  PRIMARY KEY (event_ts, label)
);

CREATE TABLE IF NOT EXISTS raw.social_posts (
  ts timestamptz NOT NULL,
  author text,
  source text,
  text text,
  url text,
  PRIMARY KEY (ts, url)
);

CREATE TABLE IF NOT EXISTS sentiment.social_impact (
  ts timestamptz NOT NULL,
  author text,
  trade_relevance double precision,
  sentiment double precision,
  entities jsonb,
  impact_est double precision,
  PRIMARY KEY (ts, author)
);

CREATE TABLE IF NOT EXISTS curated.congress_votes (
  bill_id text PRIMARY KEY,
  chamber text,
  title text,
  scheduled_date date,
  topic text,
  prob_pass double precision,
  impact_json jsonb,
  url text
);

CREATE TABLE IF NOT EXISTS curated.country_intel (
  as_of date NOT NULL,
  country text NOT NULL,
  section text NOT NULL,
  metric text NOT NULL,
  value text,
  score double precision,
  PRIMARY KEY (as_of, country, section, metric)
);

-- View for FX trade context (safe to create/replace)
CREATE OR REPLACE VIEW features.fx_trade AS
SELECT m.ds,
       m.dxy,
       m.wti,
       m.rates10y,
       f.rate AS brl_usd
FROM features.macro m
LEFT JOIN raw.fx f ON f.ts::date = m.ds AND f.base='BRL' AND f.quote='USD';
