# CLIche Memory System 🧠

## Overview

The CLIche Memory System provides persistent memory capabilities for the CLIche assistant, allowing it to remember information across sessions and provide more contextually relevant responses. The system uses a simple SQLite-based storage for reliability and consistent operation across all environments.

## Key Features

- ✅ **Persistent Memory Storage**: Store memories across sessions
- 🔍 **Full-Text Search**: Find memories based on content
- 📋 **Memory Management**: Commands for storing, recalling, and forgetting memories
- 🧑‍💼 **User Profiles**: Store personalized information to customize responses
- ⚙️ **Configurable Retention**: Control how long memories are kept
- 🛠️ **Database Repair**: Fix database issues with a simple command
- 🔄 **Robust Error Handling**: Graceful error suppression and failover mechanisms

## Architecture

The memory system consists of several key components:

1. **SQLite Database**: Stores memory content with full-text search capabilities
2. **Memory Manager**: Coordinates memory operations
3. **CLI Interface**: Provides user-friendly commands

```
CLIche Memory System Architecture
┌─────────────────┐     ┌─────────────────┐
│    User Input   │────▶│  Memory System  │
└─────────────────┘     └────────┬────────┘
                               │
               
               │                             │
      ┌────────▼─────────────────┐    ┌─────▼────────────┐
      │  SQLite Database with    │    │ Memory Manager   │
      │  Full-Text Search (FTS5) │    │                  │
      └──────────────────────────┘    └──────────────────┘
```

## Configuration

Memory system settings are stored in the main CLIche configuration file at `~/.config/cliche/config.json` under the `memory` section:

```json
{
  "memory": {
    "enabled": true,
    "auto_memory": true,
    "user_id": "username",
    "retention_days": 30,
    "max_memories": 0
  }
}
```

Key configuration options:
- `enabled`: Turn the entire memory system on/off
- `auto_memory`: Automatically store important information
- `user_id`: Unique identifier for the user
- `retention_days`: How long to keep memories (0 = forever)
- `max_memories`: Maximum number of memories to store (0 = unlimited)

## Storage Location

Memory data is stored in:
- `~/.config/cliche/memory/` - Main data directory
- `~/.config/cliche/memory/cliche_memories.db` - SQLite database for memories and metadata

## Error Handling

The memory system includes sophisticated error handling to ensure a seamless user experience:

### FTS Error Suppression
- Errors from the SQLite FTS (Full-Text Search) system are suppressed from user display
- Common errors like "database disk image is malformed" are handled gracefully
- The system automatically falls back to alternative search methods (LIKE queries) when FTS fails
- Errors are logged for debugging purposes but hidden from users
- Implemented in both `chat` and `ask` commands for consistent behavior

### Error Recovery Strategy
1. First attempt: Precise FTS5 search with error handling
2. Fallback: LIKE-based search if FTS fails
3. Last resort: If all searches fail, continue without memories

This multi-tiered approach ensures that even if parts of the memory system encounter issues, the overall functionality remains intact without disrupting the user experience.

## CLI Commands

### Basic Operations

```bash
# Store a memory
cliche memory store "Important information to remember"
cliche remember "This is an alias for the store command"

# Recall memories
cliche memory recall "search query"
cliche memory recall "search query" --limit 10

# Forget memories
cliche memory forget "search query"
cliche forget "This is an alias for the forget command"

# Repair the database (fixes corrupted FTS index)
cliche memory repair
```

### Configuration Commands

```bash
# Check memory status
cliche memory status

# Toggle auto-memory on/off
cliche memory automemory on
cliche memory automemory off

# Set user ID
cliche memory user "your_username"

# Set retention policy
cliche memory retention --days 30
cliche memory retention --max 1000
cliche memory retention --reset  # Keep all memories indefinitely
```

## Debugging

If you encounter issues with the memory system, you can:

1. Check the status with `cliche memory status`
2. Verify configuration with `cliche config-manager --show`
3. Examine log files in `~/.config/cliche/logs/`
4. Repair the database with `cliche memory repair`

## Troubleshooting

### Common Issues

1. **"Database disk image is malformed" Error**
   - This can occur if the FTS index is corrupted
   - The error is now suppressed from being displayed to users
   - The system automatically falls back to LIKE-based search
   - Run `cliche memory repair` to rebuild the index if performance is impacted

2. **Performance Issues**
   - SQLite can be slower with very large memory collections
   - Consider setting retention limits with `cliche memory retention`

3. **Multiple User Profiles**
   - Each user ID has a separate set of memories
   - Switch between profiles with `cliche memory user "username"`

## SQLite Database Structure

The memory system uses SQLite with the following schema:

1. `memories` table - Stores the actual memory content and metadata
2. `tags` table - Stores tags associated with memories
3. `memory_fts` virtual table - FTS5 index for fast text-based searching

This structure provides efficient storage and retrieval while maintaining simplicity and reliability.

---

For developers interested in the implementation details of the memory system, please refer to the code in `cliche/utils/memory.py`. 