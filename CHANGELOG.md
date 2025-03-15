# Changelog

All notable changes to the CLIche project will be documented in this file.

## [Unreleased]

### Added
- 🧠 Memory system improvements:
  - Added SQLite-based memory system for better reliability
  - Added `memory repair` command to fix database issues
  - Enhanced forget command with better UI and confirmation steps
  - Added range selection (e.g., "1-3") for deleting multiple memories
  - Added automatic migration from old database to new format
  - Updated documentation to reflect the simplified architecture

### Fixed
- 🛠️ Enhanced error handling in memory system:
  - Suppressed disruptive "database disk image is malformed" FTS errors from user display
  - Implemented robust error handling in both `chat` and `ask` commands
  - Added graceful fallback to LIKE search when FTS search fails
  - Improved logging of suppressed errors for debugging purposes
  - Enhanced the memory search method to handle errors more elegantly
  - Updated documentation to reflect the improved error handling capabilities

## [Pre-Release Beta]

## [1.4.0] - 2024-03-10

### Removed
- 🧹 Removed the `draw` command and Durdraw dependency:
  - Eliminated external dependency on the Durdraw repository
  - Removed all references to the draw command in documentation
  - Cleaned up imports and command registrations
  - Updated the COMMAND_TEST_LIST.md to remove draw command testing instructions
  - Simplified the codebase by removing unnecessary dependencies

### Added
- 🎨 New interactive ANSI art drawing command:
  - Added `draw` command with intuitive TUI interface
  - Implemented mouse-based drawing with color selection
  - Added multiple drawing tools (brush, eraser, fill, text)
  - Created undo/redo functionality
  - Implemented character/brush selection
  - Added canvas saving to ANSI files
  - Added keyboard shortcuts for common operations
  - Created comprehensive documentation in docs/DRAW_COMMAND_README.md
  - Integrated with Durdraw for professional drawing capabilities
  - Added both ASCII art mode (text characters) and ANSI art mode (colored blocks)
  - Implemented frame-based animation with playback controls
  - Added command options for width, height, and output file
  - Provided interface for copy/paste operations and selections
  - Added canvas resizing capabilities through command line and keyboard shortcuts
- 📝 Enhanced document generation in research and scrape commands:
  - Increased source character usage from 5,000 to 100,000 chars per source
  - Added improved prompt guidelines to preserve technical details and code examples
  - Enhanced section generation with 2,000-3,000 word targets for comprehensive coverage
  - Implemented terminal-friendly output mode with concise summaries (800-1000 words)
  - Added clear separation between terminal output and file output modes
  - Improved content preservation to maintain the depth and complexity of original sources
  - Added fallback mechanism for terminal output if summary generation fails
- 🔍 Enhanced web scraping capabilities in the `scrape` command:
  - Added `--max-pages` parameter to control the total number of pages scraped
  - Improved crawler configuration for proper multi-page content extraction
  - Enhanced content extraction algorithm to prioritize larger, more relevant chunks
  - Better debug output with detailed information about the scraping process
  - Fixed issues with depth-based link following and content accumulation
  - Implemented scaled content limits based on depth (100,000 chars × depth)
  - Added clear console messages about crawler settings and content extraction
- 🔍 Improved web scraping capabilities:
  - Increased character limit in general extractor to 1 million chars
  - Increased character limit in research command to 100K chars per page
  - Added browser-based rendering for better JavaScript content extraction
  - Implemented detailed progress output with timing information
  - Enhanced console output to match research command style
- 📚 Updated documentation for scraping and research commands
- 🗺️ Added future plans for specialized blog/medium extractor
- 🎛️ Added flexible dual command pattern:
  - Allow using commands in both flag style (--option) and subcommand style
  - Implemented in config-manager command
  - Added utility helpers for easy implementation in other commands
  - Improved command-line usability and flexibility
  - Updated documentation with usage examples
- 🧠 Enhanced memory system:
  - Added `--reset` flag to retention command for quickly resetting to indefinite memory retention
  - Fixed embedding model configuration with proper provider settings
  - Improved documentation and organization in docs/memory/
  - Added support for multiple embedding providers (Ollama, OpenAI, Anthropic, Google)
  - Added embedding model installation command for Ollama models
  - Implemented configurable retention policies (time-based and count-based)
  - Fixed ChromaDB integration for improved semantic search
  - Enhanced error handling and diagnostics
  - Added comprehensive memory system documentation
- 🧠 Improved memory system for Anthropic provider:
  - Implemented Voyage AI integration for embeddings when using Anthropic provider
  - Added dedicated configuration options for Voyage AI (`voyage_api_key` in config)
  - Created new `cliche memory set-voyage-key` command for easy configuration
  - Updated documentation with clear instructions for setting up Voyage AI
  - Added multiple Voyage models: voyage-3-lite (default), voyage-3, voyage-2
  - Implemented automatic model detection and dimension handling
  - Enhanced error handling with graceful fallbacks to hash-based embeddings
  - Added configuration status display in memory status command
  - Improved reload mechanism to ensure model changes are applied immediately

### Changed
- Refactored general extractor to use direct browser rendering
- Improved error handling and fallback mechanisms
- Enhanced content extraction quality for JavaScript-heavy sites
- Updated README.md with new draw command information and examples
- Updated CLICHE_PLAN.md to mark the drawing tool implementation as complete
- Updated config-manager command to support both --flag and subcommand styles
- ⚙️ Optimized token limits for all providers based on cost and capabilities:
  - Increased OpenAI and Anthropic limits to 20,000 tokens (balanced for cost)
  - Increased Google limit to 64,000 tokens (higher since it's more affordable)
  - Maintained DeepSeek limit at 8,192 tokens (model limitation)
  - Kept OpenRouter limit at 100,000 tokens for maximum flexibility
  - Increased Ollama limit to 100,000 tokens (for local models)

### Fixed
- Resolved browser initialization issues with crawl4ai
- Fixed character limit inconsistencies between commands
- Improved image extraction reliability
- Fixed config-manager command flags (--show, --create, --backup, etc.)

## [1.3.4] - 2025-02-27

### Enhanced
- 🖼️ Added AI-powered contextual image placement across all document commands
  - Implemented LLM-based analysis to find optimal image placement points
  - Enhanced image handling in research, generate, and write commands
  - Images now placed at contextually relevant positions in the document
  - Added fallback to evenly distributed placement when LLM suggestions unavailable
  - Replaced confusing error messages with more user-friendly notifications

## [1.3.3] - 2025-02-27

### Fixed
- 🔧 Fixed primary web crawler functionality in research command
  - Updated to use correct crawler methods (`arun`, `aprocess_html`) available in current `