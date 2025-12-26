# Tools Directory

This directory contains utility scripts for database maintenance, testing, and diagnostics.

## Available Scripts

### 1. `diagnose_database.py`
Comprehensive database diagnostic tool that checks:
- Database connection
- Table existence
- Product and category counts
- Migration status

**Usage:**
```bash
# From project root
python tools/diagnose_database.py

# Or from tools folder
cd tools
python diagnose_database.py
```

### 2. `test_db_connection.py`
Quick script to test PostgreSQL connection and verify database accessibility.

**Usage:**
```bash
python tools/test_db_connection.py
```

### 3. `test_products.py`
Checks if products exist in the database and displays active products.

**Usage:**
```bash
python tools/test_products.py
```

### 4. `backup_postgres.py`
Creates a backup of your PostgreSQL database.

**Usage:**
```bash
python tools/backup_postgres.py
```

**Configuration:**
- Backups are saved to `backups/` folder in project root
- Database settings are read from Django settings
- Set `PG_DUMP_PATH` environment variable if pg_dump is not in PATH

**Note:** Make sure PostgreSQL's `pg_dump` is installed and accessible.

## Requirements

All scripts require:
- Django project to be properly configured
- Virtual environment activated (if using one)
- Database connection settings in `settings.py`

## Notes

- All scripts automatically detect the project root when run from the `tools/` folder
- Scripts use Django settings for database configuration (no hardcoded values)
- Backups are stored in `backups/` directory (created automatically)

