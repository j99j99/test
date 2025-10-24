#!/usr/bin/env python3
"""
CSV Import Script with SQLite Database Support

This script imports CSV files into a SQLite database with the following features:
- Proper transaction handling to prevent commit errors
- Progress bar for import operations
- Automatic 'filename' column to track source files
- Status display after each file is processed
"""

import sqlite3
import csv
import os
import sys
from pathlib import Path
from tqdm import tqdm


class CSVImporter:
    """Handles CSV file imports into SQLite database."""
    
    def __init__(self, db_path):
        """Initialize the importer with database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def create_table_from_csv(self, table_name, csv_file, has_header=True):
        """Create a table based on CSV structure with filename column.
        
        Args:
            table_name: Name of the table to create
            csv_file: Path to the CSV file
            has_header: Whether the CSV has a header row
            
        Returns:
            List of column names
        """
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            if has_header:
                headers = next(reader)
                # Sanitize column names
                columns = [col.strip().replace(' ', '_').replace('-', '_') 
                          for col in headers]
            else:
                # Count columns from first row
                first_row = next(reader)
                columns = [f'column_{i}' for i in range(len(first_row))]
                
        # Add filename column to track source
        columns.append('filename')
        
        # Create table with TEXT columns and filename column
        column_defs = ', '.join([f'"{col}" TEXT' for col in columns])
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({column_defs})'
        
        self.cursor.execute(create_sql)
        
        return columns[:-1]  # Return columns without filename
        
    def import_csv_file(self, csv_file, table_name=None, has_header=True):
        """Import a single CSV file into the database.
        
        Args:
            csv_file: Path to the CSV file
            table_name: Name of the table (defaults to filename without extension)
            has_header: Whether the CSV has a header row
            
        Returns:
            Number of rows imported
        """
        csv_path = Path(csv_file)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
            
        # Default table name from filename
        if table_name is None:
            table_name = csv_path.stem.replace('-', '_').replace(' ', '_')
            
        # Get the base filename for the filename column
        source_filename = csv_path.name
        
        print(f"\nProcessing: {source_filename}")
        print(f"  Table: {table_name}")
        
        # Create table structure
        columns = self.create_table_from_csv(table_name, csv_file, has_header)
        
        # Count total rows for progress bar
        with open(csv_file, 'r', encoding='utf-8') as f:
            total_rows = sum(1 for _ in f)
            if has_header:
                total_rows -= 1  # Exclude header
                
        # Import data with proper transaction handling
        rows_imported = 0
        
        try:
            # Begin transaction explicitly
            self.conn.execute('BEGIN TRANSACTION')
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                if has_header:
                    next(reader)  # Skip header
                    
                # Prepare INSERT statement with filename column
                placeholders = ', '.join(['?' for _ in range(len(columns) + 1)])
                insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
                
                # Use progress bar for import
                for row in tqdm(reader, total=total_rows, 
                               desc=f"  Importing {source_filename}", 
                               unit=" rows"):
                    # Add filename to the row
                    row_with_filename = row + [source_filename]
                    self.cursor.execute(insert_sql, row_with_filename)
                    rows_imported += 1
                    
            # Commit transaction - this is the critical fix for transaction errors
            self.conn.commit()
            
            # Display status after processing
            print(f"  ✓ Successfully imported {rows_imported} rows")
            print(f"  ✓ Source file tracked in 'filename' column")
            
        except Exception as e:
            # Rollback on error
            self.conn.rollback()
            print(f"  ✗ Error importing {source_filename}: {str(e)}")
            raise
            
        return rows_imported
        
    def import_multiple_files(self, csv_files, table_name=None):
        """Import multiple CSV files into the same table.
        
        Args:
            csv_files: List of CSV file paths
            table_name: Name of the table (defaults to 'imported_data')
            
        Returns:
            Total number of rows imported
        """
        if not csv_files:
            print("No CSV files to import")
            return 0
            
        if table_name is None:
            table_name = 'imported_data'
            
        total_rows = 0
        successful = 0
        failed = 0
        
        print(f"\n{'='*60}")
        print(f"Starting import of {len(csv_files)} file(s) into table: {table_name}")
        print(f"{'='*60}")
        
        for csv_file in csv_files:
            try:
                rows = self.import_csv_file(csv_file, table_name)
                total_rows += rows
                successful += 1
            except Exception as e:
                print(f"Failed to import {csv_file}: {e}")
                failed += 1
                
        # Final summary
        print(f"\n{'='*60}")
        print(f"Import Summary:")
        print(f"  Total files processed: {len(csv_files)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total rows imported: {total_rows}")
        print(f"{'='*60}\n")
        
        return total_rows
        

def main():
    """Main entry point for the CSV import script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import CSV files into SQLite database with progress tracking'
    )
    parser.add_argument('csv_files', nargs='+', help='CSV file(s) to import')
    parser.add_argument('--database', '-d', default='import.db',
                       help='SQLite database file (default: import.db)')
    parser.add_argument('--table', '-t', help='Table name (default: derived from filename)')
    parser.add_argument('--no-header', action='store_true',
                       help='CSV files do not have header row')
    
    args = parser.parse_args()
    
    # Create importer
    importer = CSVImporter(args.database)
    
    try:
        importer.connect()
        
        if len(args.csv_files) == 1:
            # Single file import
            importer.import_csv_file(args.csv_files[0], args.table, 
                                    not args.no_header)
        else:
            # Multiple files import
            importer.import_multiple_files(args.csv_files, args.table)
            
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    finally:
        importer.close()
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
