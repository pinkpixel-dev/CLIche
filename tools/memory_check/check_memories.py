#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Storage Checker for CLIche

This script checks both memory storage systems (SQLite and ChromaDB) used by CLIche
and provides detailed information about the stored memories.
"""

import chromadb
import os
import sqlite3
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init()

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

def print_section(text):
    """Print a formatted section header."""
    print(f"\n{Fore.GREEN}{'-' * 50}")
    print(f"{Fore.GREEN}{text}")
    print(f"{Fore.GREEN}{'-' * 50}{Style.RESET_ALL}")

def print_success(text):
    """Print a success message."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print an error message."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print an info message."""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def check_sqlite_memories():
    """Check memories stored in SQLite database."""
    print_section("SQLite Memory Storage Check")
    
    db_path = os.path.expanduser("~/.config/cliche/memory/cliche_memories.db")
    
    if not os.path.exists(db_path):
        print_error(f"SQLite database not found at: {db_path}")
        return
    
    print_success(f"SQLite database found at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if memories table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        if not cursor.fetchone():
            print_error("Memories table not found in the database!")
            conn.close()
            return
        
        # Count memories
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print_success(f"SQLite contains {count} memories")
        
        if count > 0:
            # Get recent memories
            print_section("Recent Memories in SQLite")
            cursor.execute("""
                SELECT id, content, timestamp 
                FROM memories 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            
            memories = cursor.fetchall()
            for i, (mem_id, content, timestamp) in enumerate(memories, 1):
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n{Fore.YELLOW}Memory #{i}:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}ID:{Style.RESET_ALL} {mem_id}")
                print(f"{Fore.CYAN}Date:{Style.RESET_ALL} {date_str}")
                print(f"{Fore.CYAN}Content:{Style.RESET_ALL} {content[:150]}...")
        
        conn.close()
        
    except sqlite3.Error as e:
        print_error(f"SQLite error: {e}")

def check_chromadb_memories():
    """Check memories stored in ChromaDB."""
    print_section("ChromaDB Memory Storage Check")
    
    chroma_path = os.path.expanduser("~/.config/cliche/memory/chroma")
    
    if not os.path.exists(chroma_path):
        print_error(f"ChromaDB directory not found at: {chroma_path}")
        return
    
    print_success(f"ChromaDB directory found at: {chroma_path}")
    
    # Check ChromaDB SQLite file
    chroma_db = os.path.join(chroma_path, "chroma.sqlite3")
    
    if not os.path.exists(chroma_db):
        print_error(f"ChromaDB database file not found at: {chroma_db}")
        return
    
    print_success(f"ChromaDB database file found at: {chroma_db}")
    
    try:
        # Check embeddings directly in SQLite
        conn = sqlite3.connect(chroma_db)
        cursor = conn.cursor()
        
        # Check collections
        cursor.execute("SELECT name FROM collections")
        collections = cursor.fetchall()
        
        if not collections:
            print_warning("No collections found in ChromaDB")
            conn.close()
            return
        
        print_success(f"Collections found: {', '.join([c[0] for c in collections])}")
        
        # Check embeddings
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        emb_count = cursor.fetchone()[0]
        print_success(f"ChromaDB contains {emb_count} embeddings")
        
        if emb_count > 0:
            # Get embedding IDs
            cursor.execute("SELECT embedding_id FROM embeddings LIMIT 5")
            embedding_ids = [row[0] for row in cursor.fetchall()]
            print_info(f"First 5 embedding IDs: {', '.join(embedding_ids)}")
        
        conn.close()
        
        # Now try to use the ChromaDB Python API
        try:
            print_section("Checking ChromaDB via Python API")
            client = chromadb.PersistentClient(path=chroma_path)
            
            try:
                collection = client.get_collection("cliche_memories")
                print_success("Successfully connected to 'cliche_memories' collection")
                
                # Get collection info
                print_info(f"Collection metadata: {collection.metadata}")
                
                # Get all documents (this might be slow with many documents)
                results = collection.get(limit=5)
                print_success(f"Retrieved {len(results['ids'])} memories from collection")
                
                if len(results['ids']) > 0:
                    print_section("Sample Memory from ChromaDB")
                    for i in range(min(3, len(results['ids']))):
                        print(f"\n{Fore.YELLOW}Memory #{i+1}:{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}ID:{Style.RESET_ALL} {results['ids'][i]}")
                        if 'documents' in results and len(results['documents']) > i:
                            print(f"{Fore.CYAN}Content:{Style.RESET_ALL} {results['documents'][i][:150]}...")
                        if 'metadatas' in results and len(results['metadatas']) > i:
                            print(f"{Fore.CYAN}Metadata:{Style.RESET_ALL} {results['metadatas'][i]}")
                
            except Exception as e:
                print_error(f"Failed to get collection: {e}")
        
        except ImportError:
            print_error("ChromaDB Python package not installed. Can't check via API.")
        except Exception as e:
            print_error(f"Error using ChromaDB API: {e}")
    
    except sqlite3.Error as e:
        print_error(f"SQLite error when checking ChromaDB: {e}")

def main():
    """Main function to run all checks."""
    print_header("CLIche Memory Storage Checker")
    print_info("Checking all memory storage systems...")
    
    check_sqlite_memories()
    check_chromadb_memories()
    
    print_section("Summary")
    print_info("Memory check complete!")
    print_info("If you see any errors, please consult the CLIche documentation or report issues.")
    print("\n")

if __name__ == "__main__":
    main() 