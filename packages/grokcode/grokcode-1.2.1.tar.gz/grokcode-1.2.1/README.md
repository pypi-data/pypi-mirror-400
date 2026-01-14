# Grok Code

An agentic CLI coding assistant powered by xAI's Grok API.

## Features

- **Agentic Loop**: Multi-turn conversations with automatic tool use
- **18 Built-in Tools**: File operations, git, search, web fetch, notebooks
- **25 Slash Commands**: Session management, git integration, theming
- **Secure Storage**: API keys stored in system keychain
- **Streaming**: Real-time response output
- **Task Planning**: Ralph Wiggum Loop for complex tasks

## Installation

### pip (recommended)

```bash
pip install grokcode
```

### From source

```bash
git clone https://github.com/maximus242/grokcode.git
cd grokcode
pip install -e .
```

### Homebrew (macOS/Linux)

```bash
brew install maximus242/tap/grokcode
```

### Standalone binaries

Download from [GitHub Releases](https://github.com/maximus242/grokcode/releases):
- `grokcode-linux-x64` - Linux (x64)
- `grokcode-macos-arm64` - macOS (Apple Silicon)
- `grokcode-macos-x64` - macOS (Intel)
- `grokcode-windows-x64.exe` - Windows

## Setup

### Option 1: Environment variable

```bash
export XAI_API_KEY='your-api-key'
```

### Option 2: Secure storage

```bash
grokcode login
```

Get your API key from [xAI Console](https://console.x.ai/).

## Usage

### Interactive mode

```bash
grokcode
```

### With prompt

```bash
grokcode "fix the bug in main.py"
grokcode -p "add tests for the user module"
```

### Continue session

```bash
grokcode -c                    # Continue last session
grokcode -r session_123.json   # Resume specific session
```

### Non-interactive

```bash
grokcode -p "list all TODO comments" --output-format json
cat file.py | grokcode -p "review this code"
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/clear` | Clear conversation |
| `/compact` | Summarize old messages |
| `/config` | Edit configuration |
| `/doctor` | Health checks |
| `/status` | Git status |
| `/diff` | Git diff |
| `/save` | Save session |
| `/theme` | Switch theme |
| `/update` | Check for updates |
| `/exit` | Exit |

## Tools

The agent can use these tools automatically:

- **File**: `read_file`, `write_to_file`, `edit_file`, `list_files`, `glob_files`
- **Search**: `search_files` (grep-style)
- **Shell**: `execute_command`
- **Git**: `git_status`, `git_diff`, `git_log`, `git_add`, `git_commit`, `git_branch`
- **Web**: `web_fetch`
- **Notebook**: `notebook_edit`
- **Interactive**: `ask_user`

## Configuration

Create `.grokcode/config.json`:

```json
{
  "model": "grok-4-1-fast-reasoning",
  "theme": "default",
  "hooks": {
    "pre_tool": [],
    "post_tool": [],
    "on_error": []
  }
}
```

### Project memory

Create `GROK.md` in your project root:

```markdown
# Project Overview

Brief description of your project.

## Build Commands

npm install && npm test
```

## CLI Options

```
grokcode [PROMPT] [OPTIONS]

Options:
  -p, --prompt TEXT          Initial prompt
  -c, --continue             Continue last session
  -r, --resume FILE          Resume specific session
  -m, --model MODEL          Model to use
  --max-turns N              Max agent turns
  --system-prompt TEXT       Override system prompt
  --allowedTools TOOLS       Whitelist tools
  --disallowedTools TOOLS    Blacklist tools
  --output-format FORMAT     json or text
  --verbose                  Debug output
  --dangerously-skip-permissions  Skip confirmations
  --version                  Show version
```

## Subcommands

```bash
grokcode update   # Check for updates
grokcode login    # Store API key securely
grokcode logout   # Remove stored API key
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest test_grok_code.py -v

# Run with coverage
pytest --cov=grok_code --cov-report=term-missing
```

## License

MIT

## Credits

- Powered by [xAI Grok API](https://x.ai/)
