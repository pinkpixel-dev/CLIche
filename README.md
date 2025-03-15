# CLIche

![CLIche Logo](assets/logo.png)

A command-line interface for interacting with LLMs.

## Features

- Chat with LLMs from your terminal
- Support for multiple LLM providers (Ollama, OpenAI, Anthropic, OpenRouter)
- Memory system for storing and retrieving important information
- Professional mode for more formal responses
- System information inclusion for relevant queries
- User profile for personalized interactions

## Installation

```bash
pip install cliche-cli
```

Or install from source:

```bash
git clone https://github.com/pinkpixel-dev/cliche.git
cd cliche
pip install -e .
```

## Configuration

CLIche uses a configuration file located at `~/.config/cliche/config.json`. You can create this file manually or let CLIche create it for you on first run.

Example configuration:

```json
{
  "provider": "ollama",
  "ollama": {
    "model": "llama3",
    "base_url": "http://localhost:11434"
  },
  "openai": {
    "api_key": "your-api-key",
    "model": "gpt-4"
  },
  "anthropic": {
    "api_key": "your-api-key",
    "model": "claude-3-opus-20240229"
  },
  "openrouter": {
    "api_key": "your-api-key",
    "model": "anthropic/claude-3-opus-20240229"
  },
  "memory": {
    "enabled": true,
    "auto_memory": false,
    "data_dir": "~/.config/cliche/memory",
    "collection_name": "cliche_memories"
  }
}
```

> **Note:** If you're using Anthropic as your provider, the memory system uses Voyage AI for embeddings. You'll need to set the `VOYAGE_API_KEY` environment variable or configure it using `cliche memory set-voyage-key YOUR_API_KEY` to enable this feature. Get a key at https://docs.voyageai.com/

## Usage

### Basic Chat

```bash
cliche ask "What is the capital of France?"
```

### Professional Mode

```bash
cliche ask --professional "Write a business email to schedule a meeting."
```

### Including System Information

```bash
cliche ask --sys-info "What kind of CPU do I have?"
```

### Memory Commands

Store a memory:

```bash
cliche memory store "Python dictionaries use square brackets for accessing items."
```

Recall memories:

```bash
cliche memory recall "Python dictionaries"
```

Fix database issues:

```bash
cliche memory repair
```

Ask a question with memory context:

```bash
# Memory is now automatically used with the ask command when enabled
cliche ask "question that might benefit from memory context"
   
# To disable memory for a specific query
cliche ask --no-memory "question without memory context"
```

Toggle memory system:

```bash
cliche memory toggle on  # Enable memory system
cliche memory toggle off  # Disable memory system
```

Set user ID for memories:

```bash
cliche memory user "john_doe"
```

Check memory status:

```bash
cliche memory status
```

## Memory System

CLIche includes a built-in memory system that allows you to:

1. Store important information for later recall
```bash
cliche memory store "Important fact or information"
# or use the shorter alias
cliche remember "Important fact or information"
```

2. Recall information with semantic search
```bash
cliche memory recall "search term"
```

3. Ask questions with memory context to get more personalized answers
```bash
# Memory is now automatically used with the ask command when enabled
cliche ask "question that might benefit from memory context"

# To disable memory for a specific query
cliche ask --no-memory "question without memory context"
```

4. Toggle the memory system on or off
```bash
cliche memory toggle on|off
```

5. Set your user ID for personalized memory storage
```bash
cliche memory user "your_username"
```

6. Check the status of the memory system
```bash
cliche memory status
```

7. Automatically store important information (when auto_memory is enabled)
```bash
# Enable auto_memory
cliche memory automemory on

# Disable auto_memory
cliche memory automemory off
```

8. Configure memory retention policy
```bash
# Keep memories for 30 days
cliche memory retention --days 30

# Keep only the most recent 100 memories
cliche memory retention --max 100

# Reset to keep all memories indefinitely
cliche memory retention --reset
```

9. Repair the database if issues occur
```bash
# Fix database issues, especially for search functionality
cliche memory repair
```

For complete documentation on the memory system, see [Memory System Documentation](docs/memory/README.md).

## User Profile

The user profile feature allows CLIche to remember and use your personal information in every interaction, making responses more personalized. You can set various profile fields such as:

- **name**: Your preferred name
- **location**: Where you're located
- **role**: Your job or occupation
- **interests**: Topics you're interested in
- **preferences**: How you prefer CLIche to respond
- **goals**: What you're trying to accomplish

When profile is enabled (which it is by default), CLIche will include this information in every interaction, regardless of the query. This means it can address you by name and tailor responses to your specific context without you having to explicitly ask about it.

To manage your profile:

```bash
# Set profile fields
cliche memory profile set name "Your Name"
cliche memory profile set location "Your Location"

# Check your profile
cliche memory status

# Toggle profile on/off
cliche memory profile toggle on|off

# Clear your profile
cliche memory profile clear
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Made with ❤️ by Pink Pixel
