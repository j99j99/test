# Test Repository

This repository contains a CSV import script with SQLite database support.

## CSV Import Script

A robust Python script for importing CSV files into SQLite databases with:
- ✅ Fixed SQLite transaction commit errors
- ✅ Progress bars for import operations
- ✅ Automatic 'filename' column tracking
- ✅ Status display after each file

See [CSV_IMPORT_README.md](CSV_IMPORT_README.md) for detailed documentation.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Import a CSV file
python csv_import.py sample_data/users.csv

# Import multiple files
python csv_import.py sample_data/*.csv --table combined_data

# Run tests
python test_csv_import.py
```