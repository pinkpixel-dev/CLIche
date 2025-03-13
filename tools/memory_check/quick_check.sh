#!/bin/bash
# Quick Memory System Check for CLIche
# This script performs a quick check of both SQLite and ChromaDB memory storage

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ASCII art banner
echo -e "${CYAN}"
echo -e "   _____ _     _____ __         __  __                               "
echo -e "  / ____| |   |_   _| |        |  \/  |                              "
echo -e " | |    | |     | | | |        | \  / | ___ _ __ ___   ___  _ __ ___ "
echo -e " | |    | |     | | | |        | |\/| |/ _ \ '_ \` _ \ / _ \| '__/ __|"
echo -e " | |____| |___ _| |_| |____    | |  | |  __/ | | | | | (_) | |  \__ \\"
echo -e "  \_____|_____|_____|______|   |_|  |_|\___|_| |_| |_|\___/|_|  |___/"
echo -e "                                                                     "
echo -e "                       Storage Quick Check Tool                      "
echo -e "${NC}"

# Print section header
section() {
    echo -e "\n${BOLD}${BLUE}==== $1 ====${NC}\n"
}

# Print info
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Print success
success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Print warning
warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

# Print error
error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if SQLite is installed
check_dependencies() {
    section "Checking Dependencies"
    
    if ! command -v sqlite3 &> /dev/null; then
        error "sqlite3 command not found. Please install SQLite."
        exit 1
    else
        success "SQLite is installed."
    fi
}

# Check SQLite database
check_sqlite() {
    section "SQLite Memory Check"
    
    DB_PATH="$HOME/.config/cliche/memory/cliche_memories.db"
    
    if [ ! -f "$DB_PATH" ]; then
        error "SQLite database not found at: $DB_PATH"
        return
    fi
    
    success "SQLite database found at: $DB_PATH"
    
    # Count memories
    MEMORY_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM memories;")
    if [ $? -eq 0 ]; then
        success "SQLite contains $MEMORY_COUNT memories"
    else
        error "Failed to count memories in SQLite"
    fi
    
    # Get recent memories if any exist
    if [ "$MEMORY_COUNT" -gt 0 ]; then
        echo
        info "Recent memories in SQLite:"
        sqlite3 "$DB_PATH" "SELECT id, substr(content, 1, 50) || '...', datetime(timestamp, 'unixepoch') FROM memories ORDER BY timestamp DESC LIMIT 3;"
    fi
}

# Check ChromaDB
check_chromadb() {
    section "ChromaDB Memory Check"
    
    CHROMA_DIR="$HOME/.config/cliche/memory/chroma"
    
    if [ ! -d "$CHROMA_DIR" ]; then
        error "ChromaDB directory not found at: $CHROMA_DIR"
        return
    fi
    
    success "ChromaDB directory found at: $CHROMA_DIR"
    
    CHROMA_DB="$CHROMA_DIR/chroma.sqlite3"
    
    if [ ! -f "$CHROMA_DB" ]; then
        error "ChromaDB database file not found at: $CHROMA_DB"
        return
    fi
    
    success "ChromaDB database file found at: $CHROMA_DB"
    
    # Check collections
    COLLECTIONS=$(sqlite3 "$CHROMA_DB" "SELECT name FROM collections;")
    if [ -z "$COLLECTIONS" ]; then
        warning "No collections found in ChromaDB"
    else
        success "Collections found: $COLLECTIONS"
    fi
    
    # Count embeddings
    EMB_COUNT=$(sqlite3 "$CHROMA_DB" "SELECT COUNT(*) FROM embeddings;")
    if [ $? -eq 0 ]; then
        success "ChromaDB contains $EMB_COUNT embeddings"
    else
        error "Failed to count embeddings in ChromaDB"
    fi
    
    # Get embedding IDs if any exist
    if [ "$EMB_COUNT" -gt 0 ]; then
        echo
        info "Recent embedding IDs in ChromaDB:"
        sqlite3 "$CHROMA_DB" "SELECT embedding_id FROM embeddings LIMIT 3;"
    fi
}

# Check for mismatches
check_mismatches() {
    section "Storage Comparison"
    
    DB_PATH="$HOME/.config/cliche/memory/cliche_memories.db"
    CHROMA_DB="$HOME/.config/cliche/memory/chroma/chroma.sqlite3"
    
    if [ ! -f "$DB_PATH" ] || [ ! -f "$CHROMA_DB" ]; then
        warning "Cannot compare stores: one or both databases missing"
        return
    fi
    
    SQLITE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM memories;")
    CHROMA_COUNT=$(sqlite3 "$CHROMA_DB" "SELECT COUNT(*) FROM embeddings;")
    
    echo -e "SQLite memories:  ${YELLOW}$SQLITE_COUNT${NC}"
    echo -e "ChromaDB embeddings: ${YELLOW}$CHROMA_COUNT${NC}"
    
    if [ "$SQLITE_COUNT" -gt "$CHROMA_COUNT" ]; then
        info "SQLite has more memories than ChromaDB. This is normal if you've been using CLIche before the ChromaDB integration."
    elif [ "$CHROMA_COUNT" -gt "$SQLITE_COUNT" ]; then
        warning "ChromaDB has more embeddings than SQLite memories. This is unusual and may indicate an issue."
    else
        success "Both stores have the same number of entries."
    fi
}

# Run checks
check_dependencies
check_sqlite
check_chromadb
check_mismatches

section "Summary"
info "Quick check complete. For more detailed analysis, run:"
echo -e "  ${CYAN}python check_memories.py${NC}"
echo

# Make executable
chmod +x "$0" 