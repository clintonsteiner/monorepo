-- Database schema initialization
-- This file runs first (ordered by filename)

-- Create schema
CREATE SCHEMA IF NOT EXISTS ercot;

-- Create LMP data table
CREATE TABLE IF NOT EXISTS ercot.lmp_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    location VARCHAR(100) NOT NULL,
    lmp_value DECIMAL(10, 2),
    energy_value DECIMAL(10, 2),
    congestion_value DECIMAL(10, 2),
    loss_value DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, location)
);

-- Create index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_lmp_timestamp ON ercot.lmp_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_lmp_location ON ercot.lmp_data(location);

-- Create monitoring metadata table
CREATE TABLE IF NOT EXISTS ercot.monitor_metadata (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ercot.lmp_data IS 'Stores ERCOT LMP (Locational Marginal Pricing) data';
COMMENT ON TABLE ercot.monitor_metadata IS 'Stores monitoring job metadata and status';
