# Known Issues in CLIche

## Memory System Redesign in Progress

The memory system is currently being completely redesigned based on the mem0 architecture. During this transition period, all memory-related functionality will display "Coming Soon" messages.

### 🔄 Changes in Progress

- **Status**: ⚠️ UNDER RECONSTRUCTION - The memory system is being rebuilt from the ground up.
- **Expected Completion**: The new memory system will be implemented in phases over the coming weeks.
- **Impact**: Memory-related commands (`remember`, `memory`, `forget`) will not function until the new system is in place.
- **Temporary Solution**: All memory commands will remain accessible but will display notices about the upcoming changes.

### 📝 Overview of the Redesign

The current dual-storage memory system (SQLite + ChromaDB) is being replaced with a more robust, single-storage approach using ChromaDB exclusively. Key improvements include:

1. **Single Vector Store**: Using ChromaDB as the sole storage engine
2. **Multi-Provider Support**: Built-in support for multiple embedding providers (Ollama, OpenAI, etc.)
3. **Enhanced Reliability**: More consistent memory storage and retrieval
4. **Improved Metadata**: Better handling of memory metadata and filtering

### 📅 Implementation Timeline

The new memory system will be implemented in phases:

1. **Phase 1**: Core infrastructure (embeddings, vector stores)
2. **Phase 2**: Core memory functionality
3. **Phase 3**: CLI commands and integration
4. **Phase 4**: Testing and refinement

## Other Issues

### 1. Entity Extraction Issues (Will be Addressed in the Redesign)
- **Issue**: Entity extraction fails with errors like "Failed to add relationship: 'str' object has no attribute 'id'".
- **Root Cause**: The entity extraction system is trying to access an 'id' attribute on a string object.
- **Status**: 🔄 WILL BE FIXED - This issue will be resolved in the new memory implementation.

### 2. LLM Provider Configuration Issues (Will be Addressed in the Redesign)
- **Issue**: The system reports "No LLM provider available" and falls back to basic extraction methods.
- **Root Cause**: Either no LLM provider is configured, or the configured provider isn't being properly accessed.
- **Impact**: Reduced quality of memory extraction, entity detection, and metadata.
- **Status**: 🔄 WILL BE FIXED - This issue will be resolved in the new memory implementation.

## Technical Details

The complete redesign plan can be found in these documentation files:

- `MEMORY_SYSTEM_REDESIGN.md` - Overview of the new system design
- `MEMORY_IMPLEMENTATION_PLAN.md` - Detailed implementation timeline
- `EMBEDDINGS_IMPLEMENTATION.md` - Embedding provider architecture
- `CHROMA_IMPLEMENTATION.md` - ChromaDB integration details
- `MEMORY_IMPLEMENTATION.md` - Memory class implementation 