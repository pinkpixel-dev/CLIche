# CLIche Memory System Implementation Plan

## 🎯 Overview

This document outlines the detailed implementation plan for replacing CLIche's current dual-storage memory system with a new implementation based on the mem0 architecture. The new system will use ChromaDB as the single source of truth for memory storage and support multiple embedding providers through a modular, factory-based approach.

## 📚 Background

CLIche's current memory system uses a dual-storage approach:
1. SQLite for storing raw memory content
2. ChromaDB for storing vector embeddings

This has led to synchronization issues, limited embedding provider support, and inconsistent memory retrieval. The new implementation will address these problems by adopting a single-storage approach with ChromaDB, inspired by the clean architecture of the mem0 project.

## 🗂️ Directory Structure ✅

```
cliche/
└── memory/
    ├── __init__.py
    ├── memory.py            # Main Memory class ❌
    ├── config.py            # Configuration classes ✅
    ├── migration.py         # Migration utilities ❌
    ├── embeddings/          # Embedding providers
    │   ├── __init__.py      ✅
    │   ├── base.py          # Base embedding provider ✅
    │   ├── factory.py       # Factory for creating providers ✅
    │   ├── ollama.py        # Ollama embedding provider ✅
    │   ├── openai.py        # OpenAI embedding provider ❌
    │   └── anthropic.py     # Anthropic embedding provider ❌
    └── vector_stores/       # Vector stores
        ├── __init__.py      ✅
        ├── base.py          # Base vector store ✅
        ├── factory.py       # Factory for creating vector stores ✅
        └── chroma.py        # ChromaDB implementation ✅
```

## 📅 Implementation Timeline

### Phase 1: Core Infrastructure (Days 1-3) 🔄

#### Day 1: Base Classes and Interfaces ✅
1. Create directory structure ✅
2. Implement `config.py` with configuration classes ✅
3. Implement base embedding provider (`embeddings/base.py`) ✅
4. Implement base vector store (`vector_stores/base.py`) ✅

#### Day 2: Factories and ChromaDB Implementation ✅
1. Implement embedding provider factory (`embeddings/factory.py`) ✅
2. Implement vector store factory (`vector_stores/factory.py`) ✅
3. Implement ChromaDB vector store (`vector_stores/chroma.py`) ✅

#### Day 3: Embedding Providers 🔄
1. Implement Ollama embedding provider (`embeddings/ollama.py`) ✅
2. Implement OpenAI embedding provider (`embeddings/openai.py`) ❌
3. Implement Anthropic embedding provider stub (`embeddings/anthropic.py`) ❌
4. Implement Google embedding provider (`embeddings/google.py`) ❌
5. Implement Deepseek embedding provider (`embeddings/deepseek.py`) ❌
6. Implement OpenRouter embedding provider (`embeddings/openrouter.py`) ❌

### Phase 2: Core Memory Functionality (Days 4-6) ❌

#### Day 4: Memory Class Implementation ❌
1. Implement the main Memory class (`memory.py`) ❌
2. Implement initialization and configuration handling ❌
3. Implement basic memory operations (add, get, delete) ❌

#### Day 5: Advanced Memory Features ❌
1. Implement search functionality with metadata filtering ❌
2. Implement memory update operations ❌
3. Implement user profile support ❌
4. Implement status reporting ❌

#### Day 6: Migration Utility ❌
1. Implement SQLite to ChromaDB migration utility (`migration.py`) ❌
2. Add tests for migration ❌
3. Ensure backward compatibility with existing data ❌

### Phase 3: CLI Commands and Integration (Days 7-9) ❌

#### Day 7: CLI Commands ❌
1. Implement basic memory commands (status, enable, disable) ❌
2. Implement memory storage commands (remember, forget) ❌
3. Implement memory retrieval commands (recall, show) ❌

#### Day 8: Additional CLI Features ❌
1. Implement user profile management ❌
2. Implement migration command ❌
3. Add command-line options for embedding model selection ❌

#### Day 9: Integration with Chat and Ask ❌
1. Integrate memory system with chat command ❌
2. Integrate memory system with ask command ❌
3. Implement memory context retrieval for LLM interactions ❌

### Phase 4: Testing and Refinement (Days 10-12) 🔄

#### Day 10: Testing 🔄
1. Write unit tests for all components 🔄
   - Created test_memory_infrastructure.py ✅
   - Need more comprehensive test suite ❌
2. Write integration tests for the memory system ❌
3. Create test fixtures and helper utilities ❌

#### Day 11: Documentation and Examples ❌
1. Document all classes and methods ❌
2. Create usage examples ❌
3. Update user documentation ❌

#### Day 12: Final Refinements ❌
1. Address any issues found during testing ❌
2. Optimize performance ❌
3. Prepare for release ❌

## 💻 Detailed Implementation Steps

### 1. Configuration System ✅

1. Create dataclasses for configuration: ✅
   - `BaseEmbeddingConfig`, `OllamaEmbeddingConfig`, `OpenAIEmbeddingConfig` ✅
   - `VectorStoreConfig` ✅
   - `MemoryConfig` ✅

2. Implement methods to load and save configuration from/to JSON ✅

3. Set up default values that work out of the box ✅

### 2. Embedding Providers 🔄

1. Create base embedding provider with abstract methods: ✅
   - `embed(text, action)`: Generate embeddings for text ✅
   - `get_dimensions()`: Return dimensions of embeddings ✅
   - `download_model(model_name)`: Download a model if needed ✅

2. Implement Ollama embedding provider: ✅
   - Support for local Ollama server ✅
   - Auto-download models if not present ✅
   - Handle different model dimensions ✅

3. Implement OpenAI embedding provider: ❌
   - API key management ❌
   - Support for different models (text-embedding-3-small, text-embedding-3-large) ❌
   - Error handling for API limitations ❌

4. Implement factory pattern for creating providers dynamically ✅

### 3. Vector Stores ✅

1. Create base vector store with abstract methods: ✅
   - `add(content, embedding, metadata, memory_id)`: Add a memory ✅
   - `search(query_embedding, limit, filter_metadata, min_similarity)`: Search for memories ✅
   - `get(memory_id)`: Retrieve a memory by ID ✅
   - `delete(memory_id)`: Delete a memory ✅
   - `update(memory_id, content, embedding, metadata)`: Update a memory ✅
   - `count(filters)`: Count memories ✅

2. Implement ChromaDB vector store: ✅
   - Support for both local and remote ChromaDB ✅
   - Proper dimension handling ✅
   - Metadata filtering with ChromaDB where clauses ✅
   - Error handling for ChromaDB-specific issues ✅

3. Implement factory pattern for creating vector stores dynamically ✅

### 4. Memory Class ❌

1. Implement the main Memory class: ❌
   - Configuration handling ❌
   - Component initialization ❌
   - Proper error handling ❌

2. Implement memory operations: ❌
   - `add(content, metadata)`: Add a memory ❌
   - `search(query, limit, filters, min_similarity)`: Search memories ❌
   - `get(memory_id)`: Retrieve a memory ❌
   - `delete(memory_id)`: Delete a memory ❌
   - `update(memory_id, content, metadata)`: Update a memory ❌
   - `count(filters)`: Count memories ❌
   - `status()`: Get system status ❌

3. Implement user profile handling: ❌
   - Profile-specific collections ❌
   - Profile switching ❌

### 5. Migration Utility ❌

1. Implement SQLite to ChromaDB migration: ❌
   - Read memories from SQLite ❌
   - Generate embeddings for each memory ❌
   - Store in ChromaDB ❌
   - Handle errors gracefully ❌

2. Add command-line interface for migration ❌

3. Implement progress reporting ❌

### 6. CLI Commands ❌

1. Implement system commands: ❌
   - `status`: Show memory system status ❌
   - `enable`: Enable memory system ❌
   - `disable`: Disable memory system ❌
   - `set-profile`: Set user profile ❌

2. Implement memory management commands: ❌
   - `remember`: Add a memory ❌
   - `recall`: Search memories ❌
   - `forget`: Delete a memory ❌
   - `show`: Show a memory ❌

3. Implement migration command: ❌
   - `migrate`: Migrate memories from SQLite to ChromaDB ❌

### 7. Integration with Chat and Ask ❌

1. Implement memory context retrieval for LLM interactions: ❌
   - Search for relevant memories ❌
   - Format as context messages ❌
   - Add to prompt ❌

2. Update chat and ask commands to use memory: ❌
   - Add option to enable/disable memory ❌
   - Add option to control number of memories to include ❌

## 🧪 Testing Strategy 🔄

### Unit Tests 🔄

1. Test embedding providers: 🔄
   - Test embedding generation ✅
   - Test dimension consistency ✅
   - Test error handling ❌

2. Test vector stores: 🔄
   - Test memory operations (add, get, search, delete, update) ✅
   - Test metadata filtering ❌
   - Test error handling ❌

3. Test Memory class: ❌
   - Test configuration handling ❌
   - Test memory operations ❌
   - Test user profile handling ❌

### Integration Tests ❌

1. Test full memory system: ❌
   - Add memories ❌
   - Search memories ❌
   - Delete memories ❌
   - Update memories ❌

2. Test migration: ❌
   - Test migration from SQLite to ChromaDB ❌
   - Test error handling ❌

3. Test CLI commands: ❌
   - Test all memory commands ❌
   - Test integration with chat and ask ❌

## 📋 Dependencies

The new memory system will depend on the following packages:

1. **Core Dependencies**:
   - `chromadb`: For vector storage
   - `numpy`: For vector operations
   - `typer`: For CLI commands
   - `pydantic` or `dataclasses`: For configuration

2. **Embedding Provider Dependencies**:
   - `ollama`: For Ollama embeddings
   - `openai`: For OpenAI embeddings
   - `anthropic`: For Anthropic (future support)
   - `google-generativeai`: For Google embeddings
   - Additional libraries for other providers

## 🚀 Performance Considerations

1. **Embedding Generation**:
   - Cache embeddings where possible
   - Use appropriate models for different use cases
   - Handle embedding in background for large content

2. **ChromaDB**:
   - Configure for appropriate performance/accuracy tradeoff
   - Use efficient filtering for metadata
   - Consider indices for frequently used metadata fields

3. **Memory Usage**:
   - Handle large collections gracefully
   - Implement pagination for large result sets
   - Monitor memory usage

## 🔄 Migration Strategy

The migration from the old dual-storage system to the new ChromaDB-only system will follow these steps:

1. **Preparation**:
   - Identify all SQLite databases
   - Verify ChromaDB accessibility
   - Ensure embedding providers are available

2. **Data Migration**:
   - Read memories from SQLite
   - Generate new embeddings for each memory
   - Store in ChromaDB with original IDs
   - Preserve all metadata

3. **Verification**:
   - Verify memory count
   - Verify memory content
   - Test search functionality

4. **Fallback Plan**:
   - Keep SQLite databases as backup
   - Implement rollback functionality
   - Document manual recovery steps

## 📊 Progress Tracking

Implementation progress:

1. Phase 1: Core Infrastructure - 75% complete ✅🔄
   - Directory structure ✅
   - Configuration system ✅
   - Base classes and interfaces ✅
   - ChromaDB implementation ✅
   - Ollama provider implementation ✅
   - Other providers implementation 🔄

2. Phase 2: Core Memory Functionality - 0% complete ❌
   - Memory class ❌
   - Advanced features ❌
   - Migration utility ❌

3. Phase 3: CLI Commands and Integration - 0% complete ❌
   - CLI commands ❌
   - Additional features ❌
   - Integration ❌

4. Phase 4: Testing and Refinement - 15% complete 🔄
   - Basic infrastructure tests ✅
   - Comprehensive testing ❌
   - Documentation ❌
   - Final refinements ❌

Overall progress: ~30% complete

## 🏁 Conclusion

This implementation plan provides a comprehensive roadmap for replacing CLIche's current memory system with a new, improved version based on the mem0 architecture. By following this plan, the transition to a single-storage approach with multiple embedding provider support will be smooth and well-structured.

The new memory system will offer significant improvements in reliability, flexibility, and usability, making CLIche a more powerful tool for users. 