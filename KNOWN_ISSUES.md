# Known Issues in CLIche

## Memory System Issues

The memory system has undergone significant improvements but still has some outstanding issues:

### 1. Embedding Provider Dimension Mismatches
- **Issue**: When switching between different memory providers (e.g., OpenAI to Anthropic), the embedding dimensions may change.
- **Root Cause**: Different embedding models have different vector dimensions (OpenAI: 1536, Voyage: 1536, Gemini: 3072).
- **Impact**: This can cause errors when searching memories created with a different provider.
- **Status**: 🔄 IN PROGRESS - Currently being addressed with dimension handling improvements.
- **Workaround**: If you switch providers, consider clearing your memories first with `cliche memory clear`.

### 2. Missing Embedding Providers
- **Issue**: Not all LLM providers have corresponding embedding providers (DeepSeek, OpenRouter)
- **Root Cause**: Integration with these providers' embedding APIs is not yet implemented
- **Impact**: When using DeepSeek or OpenRouter as your LLM provider, the memory system falls back to Ollama
- **Status**: 📝 PLANNED - Implementation will be added in future releases
- **Workaround**: You can manually set a different embedding provider with `cliche memory set-model --provider openai text-embedding-3-small`

### 3. Hash-Based Embedding Fallbacks
- **Issue**: When using Anthropic without a Voyage API key, the system falls back to hash-based embeddings.
- **Root Cause**: Voyage API key is required for proper embeddings with Anthropic.
- **Impact**: Semantic search is less accurate when using hash-based embeddings.
- **Status**: ✅ INTENDED - This is a deliberate fallback mechanism.
- **Solution**: Set up a Voyage API key with `cliche memory set-voyage-key YOUR_API_KEY`.

### 4. SQLite FTS Error Display ✅ FIXED
- **Issue**: Users would see "database disk image is malformed" errors during memory retrieval.
- **Root Cause**: SQLite FTS index corruption in some scenarios.
- **Resolution**: Added error suppression and robust fallback mechanisms. The errors no longer appear to users, and the system automatically falls back to alternative search methods (LIKE queries) when FTS fails.
- **Implementation**: Errors are now suppressed in both the `chat` and `ask` commands and logged for debugging only.
- **Additional Fix**: Improved handling directly in the `search` method of the memory system to handle errors more gracefully.

## How to Help

If you encounter any of these issues or discover new ones, please consider:

1. Setting up a Voyage API key if using Anthropic (for better semantic search)
2. Reporting specific errors with full details
3. Contributing fixes if you have the expertise

We're actively working on these issues and appreciate your patience and feedback.

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