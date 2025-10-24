#!/usr/bin/env python3
"""
Comprehensive tests for the CSV import script.
Tests all major features including transaction handling, progress tracking, and filename column.
"""

import unittest
import sqlite3
import csv
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import csv_import module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from csv_import import CSVImporter


class TestCSVImporter(unittest.TestCase):
    """Test suite for CSVImporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test.db')
        self.importer = CSVImporter(self.db_path)
        self.importer.connect()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.importer.close()
        shutil.rmtree(self.test_dir)
        
    def create_test_csv(self, filename, headers, rows):
        """Helper to create a test CSV file."""
        csv_path = os.path.join(self.test_dir, filename)
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return csv_path
        
    def test_single_file_import(self):
        """Test importing a single CSV file."""
        csv_file = self.create_test_csv(
            'test.csv',
            ['id', 'name', 'value'],
            [['1', 'Alice', '100'], ['2', 'Bob', '200']]
        )
        
        rows = self.importer.import_csv_file(csv_file, 'test_table')
        
        self.assertEqual(rows, 2)
        
        # Verify data in database
        cursor = self.importer.cursor
        cursor.execute('SELECT COUNT(*) FROM test_table')
        self.assertEqual(cursor.fetchone()[0], 2)
        
    def test_filename_column(self):
        """Test that filename column is added and populated correctly."""
        csv_file = self.create_test_csv(
            'source.csv',
            ['id', 'name'],
            [['1', 'Alice'], ['2', 'Bob']]
        )
        
        self.importer.import_csv_file(csv_file, 'test_table')
        
        # Verify filename column exists and is populated
        cursor = self.importer.cursor
        cursor.execute('SELECT filename FROM test_table')
        filenames = [row[0] for row in cursor.fetchall()]
        
        self.assertEqual(len(filenames), 2)
        self.assertTrue(all(f == 'source.csv' for f in filenames))
        
    def test_multiple_files_same_table(self):
        """Test importing multiple CSV files into the same table."""
        csv1 = self.create_test_csv(
            'file1.csv',
            ['id', 'name'],
            [['1', 'Alice'], ['2', 'Bob']]
        )
        
        csv2 = self.create_test_csv(
            'file2.csv',
            ['id', 'name'],
            [['3', 'Charlie'], ['4', 'Diana']]
        )
        
        total = self.importer.import_multiple_files([csv1, csv2], 'combined')
        
        self.assertEqual(total, 4)
        
        # Verify data from both files
        cursor = self.importer.cursor
        cursor.execute('SELECT COUNT(*), filename FROM combined GROUP BY filename ORDER BY filename')
        results = cursor.fetchall()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (2, 'file1.csv'))
        self.assertEqual(results[1], (2, 'file2.csv'))
        
    def test_transaction_rollback_on_error(self):
        """Test that transactions are rolled back on errors."""
        csv_file = self.create_test_csv(
            'test.csv',
            ['id', 'name'],
            [['1', 'Alice'], ['2', 'Bob']]
        )
        
        # First import succeeds
        self.importer.import_csv_file(csv_file, 'test_table')
        
        # Second import of same data should fail (duplicate), and rollback
        # We'll modify to create an error scenario
        cursor = self.importer.cursor
        cursor.execute('CREATE UNIQUE INDEX idx_id ON test_table(id)')
        
        # This should fail due to duplicate IDs
        with self.assertRaises(sqlite3.IntegrityError):
            self.importer.import_csv_file(csv_file, 'test_table')
            
        # Verify original data is still there (only 2 rows, not 4)
        cursor.execute('SELECT COUNT(*) FROM test_table')
        self.assertEqual(cursor.fetchone()[0], 2)
        
    def test_table_creation_from_csv_structure(self):
        """Test that table is created with correct columns from CSV."""
        csv_file = self.create_test_csv(
            'test.csv',
            ['id', 'name', 'email', 'age'],
            [['1', 'Alice', 'alice@example.com', '28']]
        )
        
        self.importer.import_csv_file(csv_file, 'test_table')
        
        # Check table schema
        cursor = self.importer.cursor
        cursor.execute("PRAGMA table_info(test_table)")
        columns = [row[1] for row in cursor.fetchall()]
        
        self.assertIn('id', columns)
        self.assertIn('name', columns)
        self.assertIn('email', columns)
        self.assertIn('age', columns)
        self.assertIn('filename', columns)
        
    def test_empty_csv_file(self):
        """Test handling of empty CSV file."""
        csv_file = self.create_test_csv(
            'empty.csv',
            ['id', 'name'],
            []
        )
        
        rows = self.importer.import_csv_file(csv_file, 'test_table')
        self.assertEqual(rows, 0)
        
        # Verify table exists but is empty
        cursor = self.importer.cursor
        cursor.execute('SELECT COUNT(*) FROM test_table')
        self.assertEqual(cursor.fetchone()[0], 0)
        
    def test_csv_with_special_characters(self):
        """Test handling of CSV with special characters in column names."""
        csv_file = self.create_test_csv(
            'special.csv',
            ['id', 'user name', 'e-mail', 'age (years)'],
            [['1', 'Alice Smith', 'alice@example.com', '28']]
        )
        
        self.importer.import_csv_file(csv_file, 'test_table')
        
        # Check that column names were sanitized
        cursor = self.importer.cursor
        cursor.execute("PRAGMA table_info(test_table)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Spaces and hyphens should be converted to underscores
        self.assertIn('user_name', columns)
        self.assertIn('e_mail', columns)
        
    def test_large_csv_file(self):
        """Test importing a larger CSV file."""
        # Create a CSV with 1000 rows
        rows = [[str(i), f'User{i}', f'user{i}@example.com'] 
                for i in range(1000)]
        
        csv_file = self.create_test_csv(
            'large.csv',
            ['id', 'name', 'email'],
            rows
        )
        
        imported = self.importer.import_csv_file(csv_file, 'test_table')
        self.assertEqual(imported, 1000)
        
        # Verify count in database
        cursor = self.importer.cursor
        cursor.execute('SELECT COUNT(*) FROM test_table')
        self.assertEqual(cursor.fetchone()[0], 1000)


class TestTransactionHandling(unittest.TestCase):
    """Test suite specifically for transaction handling."""
    
    def test_explicit_transaction_commit(self):
        """Test that explicit transactions are used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Simulate the proper transaction handling
            try:
                conn.execute('BEGIN TRANSACTION')
                cursor.execute('CREATE TABLE test (id INTEGER)')
                cursor.execute('INSERT INTO test VALUES (1)')
                conn.commit()
                
                # Verify data was committed
                cursor.execute('SELECT * FROM test')
                self.assertEqual(cursor.fetchone()[0], 1)
                
            finally:
                conn.close()
                
    def test_transaction_rollback(self):
        """Test that transactions are rolled back on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('CREATE TABLE test (id INTEGER UNIQUE)')
            cursor.execute('INSERT INTO test VALUES (1)')
            conn.commit()
            
            try:
                conn.execute('BEGIN TRANSACTION')
                cursor.execute('INSERT INTO test VALUES (2)')
                cursor.execute('INSERT INTO test VALUES (1)')  # This will fail
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()
                
            # Verify only the first insert remains
            cursor.execute('SELECT COUNT(*) FROM test')
            self.assertEqual(cursor.fetchone()[0], 1)
            
            conn.close()


def run_tests():
    """Run all tests and display results."""
    print("="*60)
    print("Running CSV Import Script Tests")
    print("="*60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCSVImporter))
    suite.addTests(loader.loadTestsFromTestCase(TestTransactionHandling))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
