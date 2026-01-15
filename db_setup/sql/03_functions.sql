-- Database functions and procedures
-- This file runs third (ordered by filename)

-- Function to get latest LMP for a location
CREATE OR REPLACE FUNCTION ercot.get_latest_lmp(loc VARCHAR)
RETURNS TABLE (
    reading_timestamp TIMESTAMPTZ,
    location VARCHAR,
    lmp_value DECIMAL,
    energy_value DECIMAL,
    congestion_value DECIMAL,
    loss_value DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ld.timestamp,
        ld.location,
        ld.lmp_value,
        ld.energy_value,
        ld.congestion_value,
        ld.loss_value
    FROM ercot.lmp_data ld
    WHERE ld.location = loc
    ORDER BY ld.timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to update monitor metadata
CREATE OR REPLACE FUNCTION ercot.update_metadata(
    meta_key VARCHAR,
    meta_value TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO ercot.monitor_metadata (key, value, updated_at)
    VALUES (meta_key, meta_value, CURRENT_TIMESTAMP)
    ON CONFLICT (key)
    DO UPDATE SET
        value = EXCLUDED.value,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to get average LMP over time period
CREATE OR REPLACE FUNCTION ercot.get_avg_lmp(
    loc VARCHAR,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
)
RETURNS DECIMAL AS $$
DECLARE
    avg_lmp DECIMAL;
BEGIN
    SELECT AVG(lmp_value) INTO avg_lmp
    FROM ercot.lmp_data
    WHERE location = loc
      AND timestamp BETWEEN start_time AND end_time;

    RETURN COALESCE(avg_lmp, 0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ercot.get_latest_lmp IS 'Get the most recent LMP reading for a location';
COMMENT ON FUNCTION ercot.update_metadata IS 'Update or insert monitoring metadata';
COMMENT ON FUNCTION ercot.get_avg_lmp IS 'Calculate average LMP over a time period';
