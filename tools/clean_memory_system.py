#!/usr/bin/env python
"""
Memory System Cleanup Script

This script cleans up the existing memory system and prepares the codebase 
for the new implementation. It archives existing files and sets up stubs.

Made with ❤️ by Pink Pixel
"""
import os
import shutil
import sys
from pathlib import Path
import argparse

def create_directories(base_dir):
    """Create necessary directories for cleanup"""
    print(f"Creating archive directories...")
    os.makedirs(os.path.join(base_dir, "cliche/memory/_archive/stores"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "docs/_archive"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "cliche/memory/embeddings"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "cliche/memory/vector_stores"), exist_ok=True)

def archive_memory_files(base_dir):
    """Archive existing memory-related files"""
    print(f"Archiving memory core files...")
    
    # Core memory files to archive
    core_files = [
        "memory.py",
        "embeddings.py",
        "provider.py",
        "extraction.py",
        "enhanced.py",
        "categorization.py",
        "graph.py",
        "temp_memory.py",
        "memory_enhanced.py"
    ]
    
    for file in core_files:
        src = os.path.join(base_dir, f"cliche/memory/{file}")
        dst = os.path.join(base_dir, f"cliche/memory/_archive/{file}")
        if os.path.exists(src):
            print(f"  Moving {src} to {dst}")
            shutil.move(src, dst)
        else:
            print(f"  Warning: {src} not found, skipping")
    
    # Archive store files
    print(f"Archiving memory store files...")
    store_files = [
        "chroma.py",
        "sqlite.py",
        "base.py",
        "__init__.py"
    ]
    
    for file in store_files:
        src = os.path.join(base_dir, f"cliche/memory/stores/{file}")
        dst = os.path.join(base_dir, f"cliche/memory/_archive/stores/{file}")
        if os.path.exists(src):
            print(f"  Moving {src} to {dst}")
            shutil.move(src, dst)
        else:
            print(f"  Warning: {src} not found, skipping")
    
    # Archive documentation
    print(f"Archiving documentation files...")
    doc_files = [
        "README_MEMORY.md",
        "GraphMemory.md",
    ]
    
    for file in doc_files:
        src = os.path.join(base_dir, f"docs/{file}")
        dst = os.path.join(base_dir, f"docs/_archive/{file}")
        if os.path.exists(src):
            print(f"  Moving {src} to {dst}")
            shutil.move(src, dst)
        else:
            print(f"  Warning: {src} not found, skipping")

def install_stub_files(base_dir):
    """Install stub files for compatibility"""
    print(f"Installing stub files...")
    
    stubs = {
        "cliche/memory/stub_memory.py.new": "cliche/memory/stub_memory.py",
        "cliche/memory/__init__.py.new": "cliche/memory/__init__.py",
        "cliche/commands/memory.py.new": "cliche/commands/memory.py",
        "cliche/commands/remember.py.new": "cliche/commands/remember.py",
        "cliche/commands/forget.py.new": "cliche/commands/forget.py",
        "docs/KNOWN_ISSUES.md.new": "docs/KNOWN_ISSUES.md"
    }
    
    for src, dst in stubs.items():
        src_path = os.path.join(base_dir, src)
        dst_path = os.path.join(base_dir, dst)
        if os.path.exists(src_path):
            print(f"  Copying {src_path} to {dst_path}")
            shutil.copy(src_path, dst_path)
        else:
            print(f"  Warning: {src_path} not found, skipping")

def main():
    """Main function to execute cleanup"""
    parser = argparse.ArgumentParser(description="Clean up memory system")
    parser.add_argument('--base-dir', help="Base directory for CLIche project", 
                        default=".")
    parser.add_argument('--no-backup', action='store_true', 
                        help="Skip creating backup of existing files")
    parser.add_argument('--confirm', action='store_true', 
                        help="Run without confirmation")
    
    args = parser.parse_args()
    
    # Check if base directory exists
    base_dir = args.base_dir
    if not os.path.exists(os.path.join(base_dir, "cliche")):
        print(f"Error: {base_dir} does not appear to be a CLIche project directory")
        return False
    
    # Confirm with user
    if not args.confirm:
        print("This script will archive the current memory system and set up stubs.")
        print("The following files will be moved to _archive directories:")
        print("  - cliche/memory/* core files")
        print("  - cliche/memory/stores/* files")
        print("  - docs/README_MEMORY.md and GraphMemory.md")
        print("New stub files will be installed for compatibility.")
        
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cleanup cancelled.")
            return False
    
    # Create backup if requested
    backup_dir = None
    if not args.no_backup:
        timestamp = Path('timestamp').stem
        backup_dir = f"backup_memory_system_{timestamp}"
        print(f"Creating backup in {backup_dir}...")
        
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "cliche/memory"), exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "cliche/memory/stores"), exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "docs"), exist_ok=True)
        
        # Copy memory files to backup
        for file in os.listdir(os.path.join(base_dir, "cliche/memory")):
            if file.endswith(".py"):
                src = os.path.join(base_dir, f"cliche/memory/{file}")
                dst = os.path.join(backup_dir, f"cliche/memory/{file}")
                shutil.copy(src, dst)
        
        # Copy store files to backup
        if os.path.exists(os.path.join(base_dir, "cliche/memory/stores")):
            for file in os.listdir(os.path.join(base_dir, "cliche/memory/stores")):
                if file.endswith(".py"):
                    src = os.path.join(base_dir, f"cliche/memory/stores/{file}")
                    dst = os.path.join(backup_dir, f"cliche/memory/stores/{file}")
                    shutil.copy(src, dst)
        
        # Copy doc files to backup
        for file in ["README_MEMORY.md", "GraphMemory.md"]:
            src = os.path.join(base_dir, f"docs/{file}")
            if os.path.exists(src):
                dst = os.path.join(backup_dir, f"docs/{file}")
                shutil.copy(src, dst)
    
    # Create directories
    create_directories(base_dir)
    
    # Archive files
    archive_memory_files(base_dir)
    
    # Install stub files
    install_stub_files(base_dir)
    
    print("\nCleanup complete!")
    if backup_dir:
        print(f"Backup created in {backup_dir}")
    print("The memory system is now ready for reimplementation.")
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1) 