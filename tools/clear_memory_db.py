#!/usr/bin/env python3
"""
Clear Memory Database Tool

This script clears the memory database to allow for fresh testing of the enhanced memory system.
It will remove all memories but keep the database structure intact.

Made with ❤️ by Pink Pixel
"""
import os
import sys
import sqlite3
import argparse
import shutil
from pathlib import Path
from datetime import datetime

def clear_memory_database(data_dir=None, backup=True, confirm=False):
    """
    Clear the memory database
    
    Args:
        data_dir: Directory containing the memory database
        backup: Whether to create a backup before clearing
        confirm: Whether to skip confirmation prompt
        
    Returns:
        Success status
    """
    # Determine data directory
    if not data_dir:
        data_dir = Path.home() / ".config" / "cliche" / "memory"
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        print(f"Memory data directory {data_dir} does not exist.")
        return False
    
    # Find database files
    db_files = []
    for file in os.listdir(data_dir):
        if file.endswith(".db"):
            db_files.append(os.path.join(data_dir, file))
    
    if not db_files:
        print(f"No database files found in {data_dir}.")
        return False
    
    # Confirm clearing
    if not confirm:
        print(f"Found {len(db_files)} database files:")
        for db_file in db_files:
            print(f"  - {db_file}")
        
        response = input("Are you sure you want to clear these databases? (y/N): ")
        if response.lower() != "y":
            print("Operation cancelled.")
            return False
    
    # Create backup if requested
    if backup:
        backup_dir = os.path.join(data_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        for db_file in db_files:
            backup_file = os.path.join(backup_dir, os.path.basename(db_file))
            shutil.copy2(db_file, backup_file)
        
        print(f"Created backup in {backup_dir}")
    
    # Clear databases
    for db_file in db_files:
        try:
            # Connect to database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Clear tables
            for table in tables:
                table_name = table[0]
                if table_name != "sqlite_sequence" and not table_name.startswith("sqlite_"):
                    cursor.execute(f"DELETE FROM {table_name};")
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            print(f"Cleared database {db_file}")
        except Exception as e:
            print(f"Error clearing database {db_file}: {str(e)}")
            return False
    
    print("All memory databases have been cleared successfully.")
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Clear CLIche memory database")
    parser.add_argument("--data-dir", help="Memory data directory (default: ~/.config/cliche/memory)")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup before clearing")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    data_dir = args.data_dir
    backup = not args.no_backup
    confirm = args.yes
    
    success = clear_memory_database(data_dir, backup, confirm)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 