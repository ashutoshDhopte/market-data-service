DROP TABLE IF EXISTS raw_responses;
CREATE TABLE IF NOT EXISTS raw_responses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,
    data TEXT NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

DROP TABLE IF EXISTS processed_prices;
CREATE TABLE IF NOT EXISTS processed_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR NOT NULL,
    price NUMERIC(20,2),
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    provider VARCHAR NOT NULL,
    raw_response_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_processed_prices_symbol_timestamp
    ON processed_prices (symbol, timestamp DESC);

DROP TABLE IF EXISTS symbol_averages;
CREATE TABLE IF NOT EXISTS symbol_averages (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR UNIQUE NOT NULL,
    moving_average NUMERIC(20,2),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

DROP TABLE IF EXISTS polling_job_configs;
CREATE TABLE IF NOT EXISTS polling_job_configs (
    id SERIAL PRIMARY KEY,
    symbols TEXT NOT NULL,
    interval INTEGER NOT NULL,
    provider VARCHAR NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);