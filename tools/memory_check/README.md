# CLIche Memory Storage Checker 🧠

This directory contains tools and instructions for manually checking the memory storage systems used by CLIche outside of the application itself. These tools are useful for debugging, development, and verification purposes.

## 📋 Overview of CLIche Memory Storage

CLIche uses two storage systems for memories:

1. **SQLite Database**: Located at `~/.config/cliche/memory/cliche_memories.db`
   - Primary storage for memory content and metadata
   - Used as a fallback when ChromaDB is unavailable

2. **ChromaDB**: Located at `~/.config/cliche/memory/chroma/`
   - Vector database for semantic search and similarity matching
   - Uses embeddings for efficient retrieval of relevant memories

## 🛠️ Quick Check Commands

### Checking SQLite Database

```bash
# Count all memories in SQLite
sqlite3 ~/.config/cliche/memory/cliche_memories.db "SELECT COUNT(*) FROM memories;"

# View the most recent memories
sqlite3 ~/.config/cliche/memory/cliche_memories.db "SELECT id, content, timestamp FROM memories ORDER BY timestamp DESC LIMIT 5;"

# View memory details
sqlite3 ~/.config/cliche/memory/cliche_memories.db "SELECT * FROM memories WHERE id = 'specific-memory-id';"
```

### Checking ChromaDB Storage

```bash
# View ChromaDB files and collection
ls -la ~/.config/cliche/memory/chroma/

# Check embeddings count in ChromaDB
sqlite3 ~/.config/cliche/memory/chroma/chroma.sqlite3 "SELECT COUNT(*) FROM embeddings;"

# View embedding IDs (these match memory IDs)
sqlite3 ~/.config/cliche/memory/chroma/chroma.sqlite3 "SELECT embedding_id FROM embeddings LIMIT 10;"
```

### Checking Collection Details

```bash
# View collections in ChromaDB
sqlite3 ~/.config/cliche/memory/chroma/chroma.sqlite3 "SELECT name FROM collections;"

# Check collection details
sqlite3 ~/.config/cliche/memory/chroma/chroma.sqlite3 "SELECT * FROM collection_metadata WHERE collection_id = (SELECT id FROM collections WHERE name = 'cliche_memories');"
```

## 🧪 Using the Memory Checker Script

The `check_memories.py` script provides a comprehensive check of both storage systems. It requires `colorama` and `chromadb` Python packages.

### Installation

```bash
# Install required packages
pip install colorama chromadb
```

### Usage

```bash
# Navigate to the tools directory
cd /path/to/CLIche/tools/memory_check

# Run the script
python check_memories.py
```

### What the Script Checks

- Existence of both SQLite and ChromaDB storage locations
- Number of memories in each storage system
- Details of recent memories
- ChromaDB collection information
- Sample memories from both systems

## 🔍 Common Issues and Solutions

### Dimension Mismatch in ChromaDB

If you see errors about dimension mismatches (e.g., "Embedding dimension 384 does not match collection dimensionality 768"):

1. This occurs when different embedding models are used (e.g., switching between different Ollama models)
2. CLIche now handles this automatically with fallbacks
3. If you need to reset the collection, you can delete the ChromaDB directory and it will be recreated:
   ```bash
   rm -rf ~/.config/cliche/memory/chroma
   ```

### No LLM Provider Available

If you see warnings about "No LLM provider available":

1. Check your CLIche configuration:
   ```bash
   cat ~/.config/cliche/config.json | grep "llm_provider"
   ```
2. Ensure the configured provider is properly set up
3. For Ollama, ensure the server is running:
   ```bash
   curl http://localhost:11434/api/list
   ```

### Entity Extraction Errors

If you see errors like "Failed to add relationship: 'str' object has no attribute 'id'":

1. These are related to entity extraction in the memory system
2. They don't affect basic memory storage functionality
3. The issue is documented in `docs/KNOWN_ISSUES.md`

## 📊 Expected Counts and Reconciliation

If the memory counts between SQLite and ChromaDB differ:

1. **SQLite > ChromaDB**: Normal if you've been using CLIche before the ChromaDB integration
2. **ChromaDB > SQLite**: Unusual and may indicate an issue
3. **Different IDs**: The systems should contain memories with the same IDs

To check IDs in both systems:

```bash
# Get IDs from SQLite
sqlite3 ~/.config/cliche/memory/cliche_memories.db "SELECT id FROM memories ORDER BY timestamp DESC LIMIT 10;"

# Get IDs from ChromaDB
sqlite3 ~/.config/cliche/memory/chroma/chroma.sqlite3 "SELECT embedding_id FROM embeddings LIMIT 10;"
```

## 🚀 Next Steps

After identifying any issues, you may want to:

1. Review the latest status in `docs/KNOWN_ISSUES.md`
2. Check if the issue is already being addressed
3. Contribute fixes to the CLIche project
4. Create a migration tool if needed (e.g., to move memories from SQLite to ChromaDB)

## 📚 Additional Resources

- `docs/KNOWN_ISSUES.md`: Current status of memory system issues
- `docs/README_MEMORY.md`: Documentation of the memory system
- `docs/MEMORY_SYSTEM_REDESIGN.md`: Details on the memory system architecture 