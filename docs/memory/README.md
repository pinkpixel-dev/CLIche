# CLIche Memory System 🧠

## Overview

The CLIche Memory System provides persistent memory capabilities for the CLIche assistant, allowing it to remember information across sessions and provide more contextually relevant responses. The system uses modern embedding techniques and vector storage to enable semantic search and retrieval of memories.

## Key Features

- ✅ **Persistent Memory Storage**: Store memories across sessions
- 🔍 **Semantic Search**: Find memories based on meaning, not just keywords
- 🤖 **Multiple Embedding Providers**: Support for different embedding models
  - Ollama (local, free): `nomic-embed-text`, `mxbai-embed-large`
  - OpenAI: `text-embedding-3-small`, `text-embedding-3-large`
  - Anthropic: `claude-3-embedding`
  - Google/Vertex AI: `textembedding-gecko`, `text-embedding-004`
- 📋 **Memory Management**: Commands for storing, recalling, and forgetting memories
- 🧑‍💼 **User Profiles**: Store personalized information to customize responses
- ⚙️ **Configurable Retention**: Control how long memories are kept

## Architecture

The memory system consists of several key components:

1. **Embeddings**: Converts text into vector representations
2. **Vector Store**: Stores and retrieves vectors efficiently
3. **Memory Manager**: Coordinates memory operations
4. **CLI Interface**: Provides user-friendly commands

```
CLIche Memory System Architecture
┌─────────────────┐     ┌─────────────────┐
│    User Input   │────▶│  Memory System  │
└─────────────────┘     └────────┬────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
      ┌────────▼─────┐  ┌──────▼───────┐  ┌───▼──────────┐
      │  Embeddings  │  │ Vector Store │  │ Memory       │
      │  Provider    │  │ (ChromaDB)   │  │ Manager      │
      └──────────────┘  └──────────────┘  └──────────────┘
```

## Configuration

Memory system settings are stored in the main CLIche configuration file at `~/.config/cliche/config.json` under the `memory` section:

```json
{
  "memory": {
    "enabled": true,
    "auto_memory": true,
    "user_id": "username",
    "embedding": {
      "provider": "ollama",
      "model": "nomic-embed-text:latest",
      "dimensions": 768
    },
    "retention_days": 30,
    "max_memories": 0
  }
}
```

Key configuration options:
- `enabled`: Turn the entire memory system on/off
- `auto_memory`: Automatically store important information
- `user_id`: Unique identifier for the user
- `embedding`: Configuration for the embedding provider
- `retention_days`: How long to keep memories (0 = forever)
- `max_memories`: Maximum number of memories to store (0 = unlimited)

## Storage Location

Memory data is stored in:
- `~/.config/cliche/memory/` - Main data directory
- `~/.config/cliche/memory/chroma/` - ChromaDB vector database
- `~/.config/cliche/memory/cliche_memories.db` - SQLite database (for metadata)

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

# Set embedding model
cliche memory set-model nomic-embed-text:latest
cliche memory set-model text-embedding-3-small --provider openai

# Install Ollama embedding models
cliche memory install nomic-embed-text:latest

# Set retention policy
cliche memory retention --days 30
cliche memory retention --max 1000
cliche memory retention --reset  # Keep all memories indefinitely
```

## Embedding Models

The memory system supports different embedding models through various providers:

### Ollama (Local)
- `nomic-embed-text:latest` - Smaller model (768 dimensions)
- `mxbai-embed-large:latest` - Larger model (1024 dimensions)

### OpenAI
- `text-embedding-3-small` - Efficient model (1536 dimensions)
- `text-embedding-3-large` - Higher quality model (3072 dimensions)
- `text-embedding-ada-002` - Legacy model (1536 dimensions)

### Anthropic
- `claude-3-embedding` - High quality model (~3072 dimensions)

### Google/Vertex AI
- `textembedding-gecko` - Base model (768 dimensions)
- `text-embedding-004` - Gemini model (768 dimensions)

## Implementation Details

For developers interested in the internal workings of the memory system, please refer to:
- [Memory Implementation](./MEMORY_IMPLEMENTATION.md)
- [ChromaDB Implementation](./CHROMA_IMPLEMENTATION.md)
- [Embeddings Implementation](./EMBEDDINGS_IMPLEMENTATION.md)
- [Memory System Redesign](./MEMORY_SYSTEM_REDESIGN.md)

## Debugging

If you encounter issues with the memory system, you can:

1. Check the status with `cliche memory status`
2. Verify configuration with `cliche config-manager --show`
3. Examine log files in `~/.config/cliche/logs/`
4. Use the tools in `tools/memory_check/` to manually inspect the memory storage

## Troubleshooting

### Common Issues

1. **Embedding Model Not Found**
   - For Ollama models, run `cliche memory install MODEL_NAME` to install
   - Check that Ollama server is running with `ollama list`

2. **API Key Issues**
   - Ensure API keys are correctly set in config for OpenAI/Anthropic/Google
   - Use `cliche config --provider openai --api-key YOUR_KEY` to set

3. **Dimension Mismatch Errors**
   - This can occur if you change embedding models. Run `cliche memory rebuild` to fix.

4. **Performance Issues**
   - ChromaDB indexing can be slow with large memory collections
   - Consider setting retention limits with `cliche memory retention` 