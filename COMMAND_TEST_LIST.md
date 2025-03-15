# CLIche Command Reference

A comprehensive list of all CLIche commands, subcommands, and flags for testing and documentation purposes.

## Main Commands

### ask

Ask a question to the LLM.

```bash
# Basic usage
cliche ask "What is the capital of France?"

# With flags
cliche ask --no-memory "What is the capital of France?"
```

### chat

Chat with CLIche in a conversational way.

```bash
# Basic usage
cliche chat "Hello, how are you today?"

# With flags
cliche chat --no-memory "Tell me about yourself"
```

### code

Generate code in your chosen programming language.

```bash
# Basic usage
cliche code "Create a function to calculate fibonacci numbers" --lang python
cliche code "Create a simple web server" --lang javascript
cliche code "Build a CLI tool" --lang rust
cliche code "Calculator app" --lang javascript

# With flags
cliche code "Create a function to calculate fibonacci numbers" --lang python --path /path/to/save/file.py
```

### config

Configure CLIche settings.

```bash
# Provider settings
cliche config --provider openai
cliche config --provider anthropic
cliche config --provider google
cliche config --provider ollama
cliche config --provider deepseek
cliche config --provider openrouter

# API keys
cliche config --api-key "your-api-key"
cliche config --unsplash-key "your-unsplash-key"
cliche config --brave-key "your-brave-key"
cliche config --stability-key "your-stability-key"
cliche config --dalle-key "your-dalle-key"

# Model settings
cliche config --model "gpt-4"

# Image generation settings
cliche config --image-provider dalle
cliche config --image-provider stability
cliche config --image-model "dall-e-3"
```

### config-manager

Manage CLIche configuration files.

```bash
# View current config
cliche config-manager --show

# Create, backup, reset, or edit config
cliche config-manager --create
cliche config-manager --backup
cliche config-manager --reset
cliche config-manager --edit
```

### create

Generate ASCII or ANSI art.

```bash
# ASCII text art
cliche create --ascii "Hello"
cliche create "Cool"  # Default to ASCII text art if text provided

# ANSI art
cliche create --ansi
cliche create --ansi --index 3  # Show specific ANSI art by index

# Random art
cliche create --ascii --random  # Display random ASCII decorative art

# Font options
cliche create --ascii "Hi" --font block  # Use specific font
cliche create --list-fonts  # List available fonts

# Banner style
cliche create --banner "My Project"  # Generate a banner-style header
```

### image

Image generation and handling command.

```bash
# Generate images
cliche image -g "A serene mountain landscape at sunset"
cliche image -g "A futuristic city" -pr dalle --model dall-e-3
cliche image -g "A cat sitting on a windowsill" -pr stability
cliche image --generate "A cyberpunk cityscape"

# View images
cliche image --view path/to/image.jpg
cliche image --view path/to/image.jpg --width 120
cliche image --system-view path/to/image.jpg

# List and search images from Unsplash
cliche image -l "nature"
cliche image --search "cat"
cliche image -l -c 20 "mountains"  # List with 20 results
cliche image -l -pg 2 "ocean"  # View page 2 of results
cliche image --random "sunset beach"  # Get and display a random image

# Provider information
cliche image --list-providers
cliche image --list-models
cliche image --list-styles
cliche image --list-all

# Download images from Unsplash
cliche image --download "abc123"  # Download by Unsplash ID
cliche image --download "abc123" --width 1600 --height 900  # Custom size
```

Generated images are saved to `~/cliche/files/images/generated/` and Unsplash images to `~/cliche/files/images/unsplash/`.

### memory

Memory management commands.

#### memory status

Get memory system status.

```bash
cliche memory status
```

#### memory store

Store a new memory.

```bash
cliche memory store "Python dictionaries use square brackets for accessing items."
cliche memory store "My favorite color is blue."
cliche memory store -t "python,syntax" "Python uses indentation for code blocks."
cliche memory store -c "fact" "The capital of France is Paris."
```

#### memory recall

Recall memories matching a query.

```bash
cliche memory recall "Python dictionaries"
cliche memory recall "favorite color" --limit 10  # Limit results
cliche memory recall "programming" --json  # Output results as JSON
cliche memory recall "python" --keyword  # Use keyword search instead of semantic
```

#### memory toggle

Toggle the memory system on or off.

```bash
cliche memory toggle on
cliche memory toggle off
```

#### memory automemory

Toggle auto-memory feature on or off.

```bash
cliche memory automemory on
cliche memory automemory off
```

#### memory user

Set the user ID for memories.

```bash
cliche memory user "john_doe"
```

#### memory retention

Set memory retention policy.

```bash
cliche memory retention --days 30  # Keep memories for 30 days
cliche memory retention --max 100  # Keep only the most recent 100 memories
cliche memory retention --reset  # Reset to keep all memories indefinitely
```

#### memory set-model

Set the embedding model for memory operations.

```bash
# For Ollama
cliche memory set-model nomic-embed-text:latest
cliche memory set-model mxbai-embed-large:latest

# For OpenAI
cliche memory set-model text-embedding-3-small
cliche memory set-model text-embedding-3-large

# For Anthropic (via Voyage)
cliche memory set-model voyage-3-lite
cliche memory set-model voyage-3
```

#### memory set-voyage-key

Set the Voyage AI API key for Anthropic embeddings.

```bash
cliche memory set-voyage-key "your-voyage-api-key"
cliche memory set-voyage-key --reset  # Remove the key from configuration
```

#### memory install

Install embedding models for Ollama.

```bash
cliche memory install  # Shows available models
cliche memory install nomic-embed-text:latest
cliche memory install mxbai-embed-large:latest
```

#### memory profile

Manage user profile.

##### memory profile set

Set a user profile field.

```bash
cliche memory profile set name "John Doe"
cliche memory profile set location "San Francisco"
cliche memory profile set role "Software Developer"
cliche memory profile set interests "AI, programming, music"
cliche memory profile set preferences "concise responses"
cliche memory profile set goals "learn new technologies"
```

##### memory profile toggle

Toggle user profile on/off.

```bash
cliche memory profile toggle on
cliche memory profile toggle off
```

##### memory profile clear

Clear the user profile.

```bash
cliche memory profile clear
```

#### memory extract

Extract facts and preferences from a conversation.

```bash
cliche memory extract "I like blue and my favorite food is pizza. I prefer working at night and I'm allergic to peanuts."
cliche memory extract --file conversation.txt  # Extract from a file
```

#### memory analyze

Analyze the memory database for patterns and insights.

```bash
cliche memory analyze  # General analysis
cliche memory analyze --category preferences  # Analysis of specific category
cliche memory analyze --topic food  # Analysis of specific topic
```

#### memory categorize

Categorize existing memories by topic and type.

```bash
cliche memory categorize  # Categorize all uncategorized memories
cliche memory categorize --recategorize  # Recategorize all memories
```

#### memory chat

Chat with your memories to get personalized responses.

```bash
cliche memory chat "What are my food preferences?"
cliche memory chat "What programming languages do I know?"
cliche memory chat "What are my travel preferences?"
```

### remember

A shorthand alias for `memory store` to store a new memory.

```bash
cliche remember "Python dictionaries use square brackets for accessing items."
cliche remember -t "python,syntax" "Python uses indentation for code blocks."
cliche remember -c "fact" "The capital of France is Paris."
```

### forget

Remove specific memories or clear all memories.

```bash
cliche forget "Python dictionaries"  # Searches for memories and prompts which to remove
cliche forget --id 12345  # Remove memory with specific ID
cliche forget --all  # Removes all memories after confirmation
cliche forget --all --confirm  # Removes all memories without confirmation
```

### models

List available models for the specified or active provider.

```bash
cliche models
```

### research

Research a topic online and generate a response or document.

```bash
# Basic usage
cliche research "History of artificial intelligence"

# With format
cliche research "Climate change impacts" --format markdown
```

### roastme

Get a snarky roast.

```bash
cliche roastme "My code never has bugs"
```

### scrape

Scrape content from a website.

```bash
# Basic usage
cliche scrape https://example.com

# With format
cliche scrape https://example.com --format json

# With images
cliche scrape https://example.com --images
```

### search

Search for files by name or file type.

```bash
# Basic usage
cliche search filename.txt

# Search by type
cliche search --type py

# Search in directory
cliche search --dir /path/to/directory
cliche search --path /path/to/directory

# Search patterns
cliche search --name "*.txt"
cliche search --name "test*" --root  # Find files starting with test from root

# Depth control
cliche search --type py --max-depth 2  # Find Python files up to 2 directories deep

# Include hidden files
cliche search --name "*.log" --hidden  # Find log files including hidden ones

# Local search
cliche search --type pdf --local  # Find PDF files in current directory

# Case sensitivity
cliche search --name "Test*" --case-sensitive

# Exclude patterns
cliche search --type py --exclude "venv"
```

### servers

List running servers and their ports, or kill server processes.

```bash
# List all running servers
cliche servers
cliche servers list

# Stop a specific server
cliche servers stop [NAME]

# Kill server processes
cliche servers --kill 12345        # Kill a specific process by PID
cliche servers --kill all          # Kill all detected server processes
cliche servers --kill nodejs       # Kill all servers of a specific type
```

### system

Display system information.

```bash
cliche system
cliche system --detailed
```

### view

View a generated file with proper formatting.

```bash
# Basic usage
cliche view filename.txt

# With format
cliche view tutorial.md --format write
cliche view game.py --format code
cliche view research_commands_in_linux.md --format docs --source research
cliche view python_async_markdown.md --format docs --source scrape

# Image control in markdown
cliche view document.md --show-images
cliche view document.md --hide-images
cliche view document.md --image-width 120
```

### write

Generate text content in various formats.

```bash
# Basic usage
cliche write "Write a short story about a robot"

# With format
cliche write "A tutorial on docker" --format markdown
cliche write "A blog post about AI" --format html

# Save to file
cliche write "Project documentation" --format markdown --path /path/to/save/file.md

# With images
cliche write "A travel guide to Paris" --format markdown --image "paris"
cliche write "A travel guide to Paris" --format markdown --image "paris" --image-count 3
cliche write "A travel guide to Paris" --format markdown --image-id "specific-unsplash-id"
cliche write "A travel guide to Paris" --format markdown --image "paris" --image-width 800
```

## Testing Workflow

1. Run each command with its basic usage
2. Test each command with various flags and options
3. Test subcommands and their options
4. Verify proper help display for all commands and subcommands
5. Test error handling with invalid inputs
6. Test integration between related commands (e.g., memory and ask)

Made with ❤️ by Pink Pixel
