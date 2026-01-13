# ForgeCodeCLI

An agentic, file-aware command-line tool that lets you manage and modify your codebase using natural language — powered by LLMs.

It acts as a safe, deterministic AI agent that can read files, create directories, and write code only through explicit tools, not raw hallucination.

## Features

- Agentic workflow (LLM decides actions, CLI executes them)
- File-aware (read, list, create, write files & directories)
- Secure API key storage (no env vars required after setup)
- Deterministic and rule-based execution
- Interactive CLI experience
- Built to support multiple LLM providers (Gemini first)

## Installation

Requires Python 3.9+

```bash
pip install forgecodecli
```

## Quick Start

### Initialize (one-time setup)

```bash
forgecodecli init
```

You will be prompted to:
- Select an LLM provider
- Enter your API key (stored securely)

### Start the agent

```bash
forgecodecli
```

You are now in interactive agent mode. Example commands:

```
create a folder src/app and add a main.py file that prints hello
read the README.md file
list all files in the src directory
quit
```

Or press `Ctrl + C` to exit.

## Reset Configuration

To remove all configuration and API keys:

```bash
forgecodecli reset
```

## Security

- API keys are stored using the system keyring
- No API keys are written to config files or environment variables
- Config files contain only non-sensitive metadata

## How It Works

1. You enter a natural language command
2. The LLM decides the next valid action
3. ForgeCodeCLI executes the action safely
4. The agent responds with the result

The agent is strictly limited to predefined tools, ensuring predictable and safe behavior.

## Supported Actions

- `read_file`
- `list_files`
- `create_dir`
- `write_file`

No action outside these tools is permitted.

## Status

This project is in active development.

**Current version supports:**
- Gemini LLM
- Interactive agent mode

**Planned features:**
- Multiple LLM providers
- Model switching
- Streaming responses
- Session memory

## License

MIT License

## Author

Built by Sudhanshu






