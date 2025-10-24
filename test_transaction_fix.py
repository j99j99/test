#!/usr/bin/env python3
"""
Test script to demonstrate the transaction commit error fix.

This script shows:
1. The OLD way (with transaction errors)
2. The NEW way (with proper transaction handling)
"""

import sqlite3
import csv
import tempfile
import os

def demonstrate_bad_transaction_handling():
    """Demonstrates the OLD way that causes transaction errors."""
    print("="*60)
    print("BAD EXAMPLE: Without proper transaction handling")
    print("="*60)
    
    # Create a temporary database and CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        csv_file = f.name
        writer = csv.writer(f)
        writer.writerow(['id', 'name'])
        writer.writerow(['1', 'Alice'])
        writer.writerow(['2', 'Bob'])
    
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('CREATE TABLE test (id TEXT, name TEXT)')
        
        # Import without explicit transaction management
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                cursor.execute('INSERT INTO test VALUES (?, ?)', row)
        
        # This MIGHT fail with "cannot commit - no transaction is active"
        # if autocommit is on or transaction state is unclear
        try:
            conn.commit()
            print("✓ Commit succeeded (but this is unreliable)")
        except Exception as e:
            print(f"✗ Commit failed: {e}")
            print("  This happens when transaction state is unclear!")
            
    finally:
        conn.close()
        os.unlink(csv_file)
        os.unlink(db_file)
    
    print()


def demonstrate_good_transaction_handling():
    """Demonstrates the NEW way with proper transaction handling."""
    print("="*60)
    print("GOOD EXAMPLE: With proper transaction handling (THE FIX)")
    print("="*60)
    
    # Create a temporary database and CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        csv_file = f.name
        writer = csv.writer(f)
        writer.writerow(['id', 'name'])
        writer.writerow(['1', 'Alice'])
        writer.writerow(['2', 'Bob'])
    
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('CREATE TABLE test (id TEXT, name TEXT)')
        
        try:
            # THE FIX: Explicitly begin transaction
            conn.execute('BEGIN TRANSACTION')
            print("✓ Transaction explicitly started")
            
            # Import data
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    cursor.execute('INSERT INTO test VALUES (?, ?)', row)
            
            print("✓ Data inserted")
            
            # THE FIX: Explicitly commit transaction
            conn.commit()
            print("✓ Transaction committed successfully")
            print("  This ALWAYS works because transaction state is explicit!")
            
        except Exception as e:
            # THE FIX: Rollback on error
            conn.rollback()
            print(f"✗ Error occurred: {e}")
            print("✓ Transaction rolled back")
            raise
            
    finally:
        conn.close()
        os.unlink(csv_file)
        os.unlink(db_file)
    
    print()


def main():
    """Run demonstrations."""
    print("\n" + "="*60)
    print("TRANSACTION COMMIT ERROR DEMONSTRATION")
    print("="*60)
    print()
    
    demonstrate_bad_transaction_handling()
    demonstrate_good_transaction_handling()
    
    print("="*60)
    print("KEY FIXES IN csv_import.py:")
    print("="*60)
    print("1. Explicit BEGIN TRANSACTION before imports")
    print("2. Explicit COMMIT after successful imports")  
    print("3. Explicit ROLLBACK on errors")
    print("4. Try/except blocks for proper error handling")
    print("="*60)
    print()


if __name__ == '__main__':
    main()
