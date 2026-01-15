# Database Setup

PostgreSQL database initialization for ERCOT LMP monitoring.

## Structure

```
db_setup/
├── sql/
│   ├── 01_schema.sql      # Table definitions and indexes
│   ├── 02_seed_data.sql   # Development seed data
│   └── 03_functions.sql   # Stored procedures and functions
├── Dockerfile.db          # PostgreSQL image definition
└── BUILD                  # Pants build configuration
```

## SQL Files

SQL files are executed in alphabetical order during container initialization:

1. **01_schema.sql** - Creates tables, indexes, and schema
2. **02_seed_data.sql** - Inserts sample development data
3. **03_functions.sql** - Creates stored procedures and functions

## Usage

### Build the database image
```bash
make db-build
```

### Run the database container
```bash
make db-run
```

### Stop the database container
```bash
make db-stop
```

### Connect to the database
```bash
make db-shell
# or directly:
psql -h localhost -p 5432 -U ercot_user -d ercot_db
```

### Environment Variables

- `POSTGRES_USER`: Database user (default: ercot_user)
- `POSTGRES_PASSWORD`: Database password (default: ercot_pass)
- `POSTGRES_DB`: Database name (default: ercot_db)

## Tables

### ercot.lmp_data
Stores ERCOT LMP (Locational Marginal Pricing) data.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| timestamp | TIMESTAMPTZ | Time of reading |
| location | VARCHAR(100) | Location code |
| lmp_value | DECIMAL(10,2) | Total LMP value |
| energy_value | DECIMAL(10,2) | Energy component |
| congestion_value | DECIMAL(10,2) | Congestion component |
| loss_value | DECIMAL(10,2) | Loss component |
| created_at | TIMESTAMPTZ | Record creation time |

### ercot.monitor_metadata
Stores monitoring job metadata and status.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| key | VARCHAR(100) | Metadata key (unique) |
| value | TEXT | Metadata value |
| updated_at | TIMESTAMPTZ | Last update time |

## Functions

### ercot.get_latest_lmp(location)
Get the most recent LMP reading for a location.

```sql
SELECT * FROM ercot.get_latest_lmp('HB_HOUSTON');
```

### ercot.update_metadata(key, value)
Update or insert monitoring metadata.

```sql
SELECT ercot.update_metadata('last_poll_time', NOW()::TEXT);
```

### ercot.get_avg_lmp(location, start_time, end_time)
Calculate average LMP over a time period.

```sql
SELECT ercot.get_avg_lmp(
    'HB_HOUSTON',
    '2024-01-01 00:00:00+00',
    '2024-01-01 23:59:59+00'
);
```

## Development

### Adding New SQL Files

1. Create a new `.sql` file in `sql/` directory
2. Use numeric prefix for ordering (e.g., `04_new_feature.sql`)
3. SQL files execute in alphabetical order
4. Rebuild the image: `make db-build`

### Modifying Schema

For development, you can modify SQL files and rebuild:
```bash
make db-stop
make db-clean
make db-build
make db-run
```

For production, use proper database migrations instead of recreating.
