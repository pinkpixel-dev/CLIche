# CLIche Memory System Cleanup Plan 🧹

## Overview

This document outlines the plan to clean up the existing memory-related code and documentation in preparation for implementing the new memory system based on mem0's architecture. The goal is to reduce confusion by clearly separating the old implementation from the new one.

## 🗂️ Files to Archive

Instead of deleting code that might contain useful logic, we'll archive it by moving it to a backup directory. This allows us to refer back to it if needed during implementation.

### Create Archive Directory

```bash
mkdir -p cliche/memory/_archive
mkdir -p docs/_archive
```

### Memory System Core Files

| File | Action | Reason |
|------|--------|--------|
| `cliche/memory/memory.py` | Archive | Main memory class to be replaced |
| `cliche/memory/embeddings.py` | Archive | Old embedding implementation |
| `cliche/memory/provider.py` | Archive | Old provider system |
| `cliche/memory/extraction.py` | Archive | Memory extraction logic |
| `cliche/memory/enhanced.py` | Archive | Enhanced memory features |
| `cliche/memory/categorization.py` | Archive | Categorization system |
| `cliche/memory/graph.py` | Archive | Old graph implementation |
| `cliche/memory/temp_memory.py` | Archive | Temporary memory implementation |
| `cliche/memory/memory_enhanced.py` | Archive | Enhanced memory implementation |

### Memory Stores

| File | Action | Reason |
|------|--------|--------|
| `cliche/memory/stores/chroma.py` | Archive | Old ChromaDB implementation |
| `cliche/memory/stores/sqlite.py` | Archive | SQLite storage implementation |
| `cliche/memory/stores/base.py` | Archive | Base class for stores |
| `cliche/memory/stores/__init__.py` | Archive | Module initialization |

### Documentation

| File | Action | Reason |
|------|--------|--------|
| `docs/README_MEMORY.md` | Archive | Old memory documentation |
| `docs/GraphMemory.md` | Archive | Graph memory documentation |
| `docs/KNOWN_ISSUES.md` | Update | Keep but update to reflect changes |

## 🔄 Files to Update

Some files need to be updated to maintain compatibility with the rest of the system during transition.

### Core Integration

| File | Action | Notes |
|------|--------|-------|
| `cliche/core.py` | Create stub | Create a temporary stub version of the new memory system |
| `cliche/commands/memory.py` | Create stub | Create a simplified version with "Coming Soon" messages |
| `cliche/commands/remember.py` | Create stub | Create a simplified version with "Coming Soon" messages |
| `cliche/commands/forget.py` | Create stub | Create a simplified version with "Coming Soon" messages |

### Module Structure

| File | Action | Notes |
|------|--------|-------|
| `cliche/memory/__init__.py` | Update | Keep exported symbols but point to stubs |
| `cliche/memory/types.py` | Keep | Can be reused in the new implementation |
| `cliche/memory/utils.py` | Keep | Can be reused in the new implementation |

## 📂 New Directory Structure

After cleanup, prepare the following structure for the new implementation:

```
cliche/
└── memory/
    ├── __init__.py           # Updated with stubs
    ├── memory.py             # Stub implementation
    ├── config.py             # New configuration
    ├── types.py              # Existing type definitions
    ├── utils.py              # Existing utilities
    ├── migration.py          # Will contain migration utilities
    ├── _archive/             # Archived files
    ├── embeddings/           # New embedding providers
    │   ├── __init__.py
    │   ├── base.py
    │   ├── factory.py
    │   ├── ollama.py
    │   ├── openai.py
    │   └── anthropic.py
    └── vector_stores/        # New vector stores
        ├── __init__.py
        ├── base.py
        ├── factory.py
        └── chroma.py
```

## 📋 Archiving Process

1. **Create Backup Directories**:
   ```bash
   mkdir -p cliche/memory/_archive/stores
   mkdir -p docs/_archive
   ```

2. **Move Files to Archive**:
   ```bash
   # Archive memory core files
   mv cliche/memory/memory.py cliche/memory/_archive/
   mv cliche/memory/embeddings.py cliche/memory/_archive/
   mv cliche/memory/provider.py cliche/memory/_archive/
   mv cliche/memory/extraction.py cliche/memory/_archive/
   mv cliche/memory/enhanced.py cliche/memory/_archive/
   mv cliche/memory/categorization.py cliche/memory/_archive/
   mv cliche/memory/graph.py cliche/memory/_archive/
   mv cliche/memory/temp_memory.py cliche/memory/_archive/
   mv cliche/memory/memory_enhanced.py cliche/memory/_archive/
   
   # Archive store files
   mv cliche/memory/stores/chroma.py cliche/memory/_archive/stores/
   mv cliche/memory/stores/sqlite.py cliche/memory/_archive/stores/
   mv cliche/memory/stores/base.py cliche/memory/_archive/stores/
   mv cliche/memory/stores/__init__.py cliche/memory/_archive/stores/
   
   # Archive documentation
   mv docs/README_MEMORY.md docs/_archive/
   mv docs/GraphMemory.md docs/_archive/
   ```

3. **Create New Directories**:
   ```bash
   mkdir -p cliche/memory/embeddings
   mkdir -p cliche/memory/vector_stores
   ```

4. **Create Stub Files**:
   - Create minimal implementation of `memory.py` that responds with "Coming Soon" messages
   - Update `__init__.py` to export the new stubs
   - Create stub versions of CLI commands for compatibility

## 🔄 Transition Steps

1. Archive old files
2. Create stub implementation
3. Update `KNOWN_ISSUES.md` to reflect changes
4. Implement new system in phases as outlined in the implementation plan

## 📝 Next Steps

After completing this cleanup, we'll be ready to start implementing the new memory system following the approach outlined in `MEMORY_IMPLEMENTATION_PLAN.md`. The first step will be creating the base classes and infrastructure.

## 📌 Note on Data

This plan doesn't delete any user data. Existing memory databases in `~/.config/cliche/memory/` will be preserved, and the migration utility (to be implemented) will allow users to migrate their memories to the new system. 