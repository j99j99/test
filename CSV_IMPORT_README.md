# CSV Import Script

A robust Python script for importing CSV files into SQLite databases with progress tracking and source file tracking.

## Features

- ✅ **Proper Transaction Handling**: Fixes SQLite transaction commit errors with explicit BEGIN/COMMIT/ROLLBACK
- ✅ **Progress Bar**: Visual progress indicator using tqdm for import operations
- ✅ **Filename Tracking**: Automatically adds a 'filename' column to record the source CSV file for each row
- ✅ **Status Display**: Shows detailed status after processing each file
- ✅ **Multiple File Support**: Import single or multiple CSV files
- ✅ **Error Handling**: Graceful error handling with transaction rollback on failures

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Import a single CSV file

```bash
python csv_import.py sample_data/users.csv
```

This creates a table named `users` in `import.db` with all columns from the CSV plus a `filename` column.

### Import with custom table name

```bash
python csv_import.py sample_data/users.csv --table my_users
```

### Import multiple CSV files into one table

```bash
python csv_import.py sample_data/users.csv sample_data/products.csv --table combined_data
```

### Specify custom database

```bash
python csv_import.py sample_data/users.csv --database mydata.db
```

### CSV without headers

```bash
python csv_import.py data.csv --no-header
```

## Example Output

```
============================================================
Starting import of 3 file(s) into table: imported_data
============================================================

Processing: users.csv
  Table: imported_data
  Importing users.csv: 100%|████████████| 5/5 [00:00<00:00, 1250.00 rows/s]
  ✓ Successfully imported 5 rows
  ✓ Source file tracked in 'filename' column

Processing: products.csv
  Table: imported_data
  Importing products.csv: 100%|████████████| 6/6 [00:00<00:00, 1500.00 rows/s]
  ✓ Successfully imported 6 rows
  ✓ Source file tracked in 'filename' column

Processing: orders.csv
  Table: imported_data
  Importing orders.csv: 100%|████████████| 7/7 [00:00<00:00, 1400.00 rows/s]
  ✓ Successfully imported 7 rows
  ✓ Source file tracked in 'filename' column

============================================================
Import Summary:
  Total files processed: 3
  Successful: 3
  Failed: 0
  Total rows imported: 18
============================================================
```

## Technical Details

### Transaction Commit Error Fix

The script properly handles SQLite transactions by:
1. Explicitly beginning transactions with `BEGIN TRANSACTION`
2. Committing after successful imports with `conn.commit()`
3. Rolling back on errors with `conn.rollback()`

This prevents the common "cannot commit - no transaction is active" error.

### Filename Column

Each imported row automatically gets a `filename` column that stores the source CSV filename. This allows you to:
- Track which file each row came from
- Filter or group data by source file
- Audit data lineage

Example query:
```sql
SELECT * FROM imported_data WHERE filename = 'users.csv';
```

## Sample Data

The `sample_data/` directory contains example CSV files:
- `users.csv` - Sample user data
- `products.csv` - Sample product data
- `orders.csv` - Sample order data

## Requirements

- Python 3.6+
- tqdm (for progress bars)
- sqlite3 (included in Python standard library)
