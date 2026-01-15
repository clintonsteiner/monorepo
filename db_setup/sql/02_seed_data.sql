-- Seed data for development
-- This file runs second (ordered by filename)

-- Insert some sample metadata
INSERT INTO ercot.monitor_metadata (key, value)
VALUES
    ('last_poll_time', '2024-01-01 00:00:00+00'),
    ('monitor_status', 'initialized'),
    ('version', '1.0.0')
ON CONFLICT (key) DO NOTHING;

-- Insert sample LMP data for testing
INSERT INTO ercot.lmp_data (timestamp, location, lmp_value, energy_value, congestion_value, loss_value)
VALUES
    ('2024-01-01 12:00:00+00', 'HB_HOUSTON', 45.50, 42.00, 2.50, 1.00),
    ('2024-01-01 12:15:00+00', 'HB_HOUSTON', 46.75, 43.25, 2.25, 1.25),
    ('2024-01-01 12:30:00+00', 'HB_HOUSTON', 44.25, 41.50, 1.75, 1.00),
    ('2024-01-01 12:00:00+00', 'LZ_WEST', 38.20, 36.00, 1.50, 0.70),
    ('2024-01-01 12:15:00+00', 'LZ_WEST', 39.10, 36.80, 1.60, 0.70)
ON CONFLICT (timestamp, location) DO NOTHING;
