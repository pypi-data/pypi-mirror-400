#!/usr/bin/env python3
"""
Grok Code: An agentic CLI coding assistant powered by xAI's Grok API.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Any

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.theme import Theme

from state import (
    StateManager,
    create_task_plan,
    update_task_status,
    add_task,
    get_plan_status,
    clear_task_plan,
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

VERSION = "1.2.1"
XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-4-1-fast-reasoning"  # Optimized for agentic tool calling, 2M context

# Available models
AVAILABLE_MODELS = {
    "grok-4-1-fast-reasoning": "Grok 4.1 Fast (2M context, optimized for tool use)",
    "grok-3": "Grok 3 (standard model)",
    "grok-3-fast": "Grok 3 Fast (faster, lower cost)",
    "grok-2": "Grok 2 (legacy)",
}

# Default configuration
DEFAULT_CONFIG = {
    "model": DEFAULT_MODEL,
    "skip_permissions": False,
    "theme": "default",
    "hooks": {
        "pre_tool": [],
        "post_tool": [],
        "on_error": []
    }
}

# Custom theme
CUSTOM_THEME = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "green",
    "tool": "bold blue",
    "result": "dim",
    "prompt": "bold white",
    "grok": "bold magenta",
})

# Prompt file path (relative to script location)
PROMPT_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT_FILE = PROMPT_DIR / "system_prompt.md"

# Default fallback prompt if file not found
DEFAULT_PROMPT = """You are Grok Code, an expert AI coding assistant running in a terminal.
You help users with software engineering tasks by reading, writing, and executing code.
Be concise but helpful. Use tools to understand context before making changes."""


def load_system_prompt() -> str:
    """Load system prompt from markdown file, with fallback."""
    try:
        if SYSTEM_PROMPT_FILE.exists():
            return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
        return DEFAULT_PROMPT
    except Exception:
        return DEFAULT_PROMPT


SYSTEM_PROMPT = load_system_prompt()


def load_project_memory() -> str | None:
    """Load GROK.md project memory file if it exists."""
    grok_md = Path("GROK.md")
    if grok_md.exists():
        try:
            return grok_md.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def build_system_messages() -> list[dict[str, str]]:
    """Build system messages including project memory."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    project_memory = load_project_memory()
    if project_memory:
        messages.append({
            "role": "system",
            "content": f"# Project Context (from GROK.md)\n\n{project_memory}"
        })

    return messages


def generate_grok_md() -> dict[str, Any]:
    """Generate a starter GROK.md template."""
    template = '''# Project Overview

Brief description of your project.

## Build & Test Commands

```bash
# Install dependencies
npm install  # or pip install -r requirements.txt

# Run tests
npm test  # or pytest

# Build
npm run build
```

## Architecture

Describe the key components and structure.

## Coding Standards

- Follow existing code style
- Write tests for new features
- Keep functions small and focused

## Important Files

- `src/` - Main source code
- `tests/` - Test files
- `README.md` - Documentation
'''
    try:
        grok_md = Path("GROK.md")
        if grok_md.exists():
            return {"success": False, "error": "GROK.md already exists"}

        grok_md.write_text(template, encoding="utf-8")
        return {"success": True, "message": "Created GROK.md"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_latest_session(base_path: str = ".") -> str | None:
    """Get the most recent session file."""
    sessions_dir = Path(base_path) / ".grokcode"
    if not sessions_dir.exists():
        return None

    sessions = sorted(sessions_dir.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if sessions:
        return str(sessions[0])
    return None


def read_stdin_if_pipe() -> str | None:
    """Read from stdin if it's a pipe (not a terminal)."""
    import select
    if not sys.stdin.isatty():
        # Check if there's data available
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read()
    return None


# Tool definitions for the model
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Run a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search files with grep",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Search pattern"},
                    "path": {"type": "string", "description": "Directory to search"}
                },
                "required": ["pattern"]
            }
        }
    },
    # File edit tool
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file at specific line(s). Supports replace, insert, and delete modes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to edit"},
                    "line": {"type": "integer", "description": "Line number (1-based)"},
                    "content": {"type": "string", "description": "New content for the line"},
                    "mode": {
                        "type": "string",
                        "enum": ["replace", "insert", "delete"],
                        "description": "Edit mode: replace line, insert before, or delete"
                    },
                    "end_line": {"type": "integer", "description": "End line for range operations (inclusive)"}
                },
                "required": ["path", "line", "content"]
            }
        }
    },
    # Glob/find tool
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "Find files matching a glob pattern (e.g., **/*.py, *.js)",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern to match"},
                    "path": {"type": "string", "description": "Base directory to search"}
                },
                "required": ["pattern"]
            }
        }
    },
    # Git tools
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Get git status showing changed files",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Get git diff showing changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "staged": {"type": "boolean", "description": "Show staged changes only"},
                    "file": {"type": "string", "description": "Show diff for specific file"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Show recent git commits",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of commits to show"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_add",
            "description": "Stage files for git commit",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File or directory to stage (default: .)"},
                    "all_files": {"type": "boolean", "description": "Stage all changes including deletions"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Create a git commit with staged changes",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"}
                },
                "required": ["message"]
            }
        }
    },
    # Task plan tools (Ralph Wiggum Loop)
    {
        "type": "function",
        "function": {
            "name": "create_task_plan",
            "description": "Create a new task plan with a goal and list of tasks. Use this at the start of complex multi-step work.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "The overall goal of the task plan"},
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of task descriptions"
                    }
                },
                "required": ["goal", "tasks"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": "Update a task's status. Use 'in_progress' when starting, 'done' when complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_index": {"type": "integer", "description": "Index of the task (0-based)"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "done"],
                        "description": "New status"
                    }
                },
                "required": ["task_index", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the current plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_plan_status",
            "description": "Get current task plan status and progress",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_task_plan",
            "description": "Clear the current task plan (use when all tasks complete or starting fresh)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # Web fetch tool
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch a URL and return its content. Useful for reading documentation or web pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "extract_text": {"type": "boolean", "description": "Extract text only (no HTML)"}
                },
                "required": ["url"]
            }
        }
    },
    # Ask user question tool
    {
        "type": "function",
        "function": {
            "name": "ask_user",
            "description": "Ask the user a question and wait for their response. Use when you need clarification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to ask the user"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of choices for the user"
                    }
                },
                "required": ["question"]
            }
        }
    },
    # Notebook edit tool
    {
        "type": "function",
        "function": {
            "name": "notebook_edit",
            "description": "Edit a Jupyter notebook (.ipynb) cell. Can replace, insert, or delete cells.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the .ipynb file"},
                    "cell_index": {"type": "integer", "description": "Cell index (0-based)"},
                    "content": {"type": "string", "description": "New cell content"},
                    "cell_type": {
                        "type": "string",
                        "enum": ["code", "markdown"],
                        "description": "Cell type"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["replace", "insert", "delete"],
                        "description": "Edit mode"
                    }
                },
                "required": ["path", "cell_index"]
            }
        }
    },
    # Image reading tool
    {
        "type": "function",
        "function": {
            "name": "read_image",
            "description": "Read and analyze an image file. Returns a description of the image contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the image file (png, jpg, gif, webp)"},
                    "question": {"type": "string", "description": "Optional question about the image"}
                },
                "required": ["path"]
            }
        }
    },
    # Web search tool
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information. Returns relevant results from DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum number of results (default: 5)"}
                },
                "required": ["query"]
            }
        }
    }
]

DANGEROUS_TOOLS = {"execute_command", "write_to_file", "edit_file"}
MAX_RESULT_CHARS = 8000

# Loop detection settings
LOOP_HISTORY_SIZE = 10  # Track last N tool calls
LOOP_THRESHOLD = 3  # Trigger after N identical calls
LOOP_NUDGE_MESSAGE = """You appear to be repeating the same action. Please try a different approach:
- If stuck reading files, summarize what you've learned and ask the user for guidance
- If stuck on an error, try a different solution strategy
- If the task is complete, say so clearly"""


# ==============================================================================
# TOKEN TRACKING
# ==============================================================================


class TokenTracker:
    """Track token usage across API calls."""

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.request_count = 0

    def add_usage(self, input_tokens: int, output_tokens: int):
        """Record token usage from an API call."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.request_count += 1

    def summary(self) -> str:
        """Return a summary of token usage."""
        total = self.total_input_tokens + self.total_output_tokens
        return f"Tokens: {self.total_input_tokens} in, {self.total_output_tokens} out ({total} total)"


# ==============================================================================
# SYNTAX HIGHLIGHTING
# ==============================================================================


def detect_language(code: str) -> str:
    """Detect the programming language of a code snippet."""
    code = code.strip()

    # Check for JSON
    if code.startswith('{') and code.endswith('}'):
        try:
            json.loads(code)
            return "json"
        except json.JSONDecodeError:
            pass
    if code.startswith('[') and code.endswith(']'):
        try:
            json.loads(code)
            return "json"
        except json.JSONDecodeError:
            pass

    # Check for Python patterns
    python_patterns = [
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+',
        r'\bimport\s+\w+',
        r'\bfrom\s+\w+\s+import',
        r':\s*$',
    ]
    for pattern in python_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return "python"

    # Check for JavaScript patterns
    js_patterns = [
        r'\bfunction\s+\w+\s*\(',
        r'\bconst\s+\w+\s*=',
        r'\blet\s+\w+\s*=',
        r'\bvar\s+\w+\s*=',
        r'=>',
        r'console\.log',
    ]
    for pattern in js_patterns:
        if re.search(pattern, code):
            return "javascript"

    # Check for shell patterns
    shell_patterns = [
        r'^(ls|cd|pwd|echo|cat|grep|find|rm|cp|mv|mkdir)\s',
        r'\|\s*(grep|awk|sed|sort|head|tail)',
        r'&&|\|\|',
        r'^\s*#!.*/(ba)?sh',
    ]
    for pattern in shell_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return "bash"

    return "text"


def format_code_output(code: str, language: str = None) -> Syntax:
    """Format code with syntax highlighting."""
    if language is None:
        language = detect_language(code)
    return Syntax(code, language, theme="monokai", line_numbers=True)


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def truncate_result(result: dict[str, Any]) -> dict[str, Any]:
    """Truncate large string values to prevent token overflow."""
    truncated = {}
    for key, value in result.items():
        if isinstance(value, str) and len(value) > MAX_RESULT_CHARS:
            truncated[key] = value[:MAX_RESULT_CHARS] + f"\n... ({len(value)} chars total)"
        else:
            truncated[key] = value
    return truncated


def get_cwd_display() -> str:
    """Get a display-friendly current working directory."""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        return "~" + cwd[len(home):]
    return cwd


# ==============================================================================
# TOOL IMPLEMENTATIONS
# ==============================================================================


def read_file(path: str) -> dict[str, Any]:
    """Read file contents."""
    try:
        path = os.path.expanduser(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"success": True, "content": content}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_to_file(path: str, content: str) -> dict[str, Any]:
    """Write content to a file."""
    try:
        path = os.path.expanduser(path)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        lines = content.count('\n') + 1
        return {"success": True, "message": f"Wrote {lines} lines to {path}"}
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(path: str = ".") -> dict[str, Any]:
    """List files in directory."""
    try:
        path = os.path.expanduser(path) if path else "."
        result = subprocess.run(
            ["ls", "-la", path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_command(command: str) -> dict[str, Any]:
    """Execute a shell command."""
    try:
        result = subprocess.run(
            command, shell=True,
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return {
            "success": True,
            "output": output,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out (120s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_files(pattern: str, path: str = ".") -> dict[str, Any]:
    """Search files with grep."""
    try:
        path = os.path.expanduser(path) if path else "."
        result = subprocess.run(
            ["grep", "-rn", "--color=never", pattern, path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode in (0, 1):
            output = result.stdout if result.stdout else "No matches found."
            return {"success": True, "output": output}
        return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Search timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# GIT INTEGRATION
# ==============================================================================


def git_status() -> dict[str, Any]:
    """Get git status."""
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        return {"success": True, "output": result.stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_diff(staged: bool = False, file: str = None) -> dict[str, Any]:
    """Get git diff."""
    try:
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        if file:
            cmd.append(file)
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 and result.stderr:
            return {"success": False, "error": result.stderr.strip()}
        output = result.stdout if result.stdout else "No changes."
        return {"success": True, "output": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_log(count: int = 10) -> dict[str, Any]:
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline", "--decorate"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        output = result.stdout if result.stdout else "No commits yet."
        return {"success": True, "output": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_add(path: str = ".", all_files: bool = False) -> dict[str, Any]:
    """Stage files for commit."""
    try:
        cmd = ["git", "add"]
        if all_files:
            cmd.append("-A")
        cmd.append(path)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        return {"success": True, "message": f"Staged {path}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_commit(message: str) -> dict[str, Any]:
    """Create a git commit."""
    try:
        # Check if there's anything staged
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True, timeout=10
        )
        if status.returncode == 0:
            return {"success": False, "error": "Nothing staged to commit"}

        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        return {"success": True, "message": f"Committed: {message}", "output": result.stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_branch(create: str = None, checkout: str = None, delete: str = None) -> dict[str, Any]:
    """Manage git branches.

    Args:
        create: Create a new branch with this name
        checkout: Switch to this branch
        delete: Delete this branch
    """
    try:
        if create:
            result = subprocess.run(
                ["git", "checkout", "-b", create],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip()}
            return {"success": True, "message": f"Created and switched to branch: {create}"}

        if checkout:
            result = subprocess.run(
                ["git", "checkout", checkout],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip()}
            return {"success": True, "message": f"Switched to branch: {checkout}"}

        if delete:
            result = subprocess.run(
                ["git", "branch", "-d", delete],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip()}
            return {"success": True, "message": f"Deleted branch: {delete}"}

        # List branches
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        return {"success": True, "output": result.stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# WEB FETCH TOOL
# ==============================================================================


def web_fetch(url: str, extract_text: bool = True) -> dict[str, Any]:
    """Fetch content from a URL.

    Args:
        url: URL to fetch
        extract_text: If True, extract text only (strip HTML tags)
    """
    import urllib.request
    import urllib.error
    import html.parser

    class TextExtractor(html.parser.HTMLParser):
        """Simple HTML to text converter."""
        def __init__(self):
            super().__init__()
            self.text = []
            self.skip_tags = {'script', 'style', 'head', 'meta', 'link'}
            self.skip_depth = 0

        def handle_starttag(self, tag, attrs):
            if tag in self.skip_tags:
                self.skip_depth += 1

        def handle_endtag(self, tag):
            if tag in self.skip_tags and self.skip_depth > 0:
                self.skip_depth -= 1

        def handle_data(self, data):
            if self.skip_depth == 0:
                text = data.strip()
                if text:
                    self.text.append(text)

        def get_text(self):
            return ' '.join(self.text)

    try:
        # Add user agent to avoid blocking
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'GrokCode/1.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')

        if extract_text and response.headers.get('content-type', '').startswith('text/html'):
            extractor = TextExtractor()
            extractor.feed(content)
            content = extractor.get_text()

        # Truncate if too long
        if len(content) > MAX_RESULT_CHARS:
            content = content[:MAX_RESULT_CHARS] + f"\n... (truncated, {len(content)} chars total)"

        return {"success": True, "content": content, "url": url}
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# ASK USER TOOL
# ==============================================================================


def ask_user(question: str, options: list[str] = None) -> dict[str, Any]:
    """Ask the user a question.

    Args:
        question: The question to ask
        options: Optional list of choices
    """
    from prompt_toolkit import prompt as pt_prompt
    from rich.console import Console

    console = Console()
    console.print(f"\n[bold cyan]Question:[/bold cyan] {question}")

    if options:
        console.print("[dim]Options:[/dim]")
        for i, opt in enumerate(options, 1):
            console.print(f"  {i}. {opt}")
        console.print()

    try:
        answer = pt_prompt("Your answer: ").strip()

        # If options provided and user entered a number, convert to the option text
        if options and answer.isdigit():
            idx = int(answer) - 1
            if 0 <= idx < len(options):
                answer = options[idx]

        return {"success": True, "answer": answer}
    except (KeyboardInterrupt, EOFError):
        return {"success": False, "error": "User cancelled"}


# ==============================================================================
# NOTEBOOK EDIT TOOL
# ==============================================================================


def notebook_edit(path: str, cell_index: int, content: str = None,
                  cell_type: str = "code", mode: str = "replace") -> dict[str, Any]:
    """Edit a Jupyter notebook cell.

    Args:
        path: Path to .ipynb file
        cell_index: Cell index (0-based)
        content: New cell content (for replace/insert)
        cell_type: 'code' or 'markdown'
        mode: 'replace', 'insert', or 'delete'
    """
    try:
        path = os.path.expanduser(path)

        if not path.endswith('.ipynb'):
            return {"success": False, "error": "Not a Jupyter notebook (.ipynb)"}

        # Read existing notebook
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)

        cells = notebook.get('cells', [])

        if mode == "delete":
            if cell_index < 0 or cell_index >= len(cells):
                return {"success": False, "error": f"Cell index {cell_index} out of range (0-{len(cells)-1})"}
            del cells[cell_index]
            message = f"Deleted cell {cell_index}"

        elif mode == "insert":
            if content is None:
                return {"success": False, "error": "Content required for insert mode"}
            new_cell = {
                "cell_type": cell_type,
                "metadata": {},
                "source": content.split('\n') if content else []
            }
            if cell_type == "code":
                new_cell["execution_count"] = None
                new_cell["outputs"] = []
            cells.insert(cell_index, new_cell)
            message = f"Inserted {cell_type} cell at index {cell_index}"

        elif mode == "replace":
            if cell_index < 0 or cell_index >= len(cells):
                return {"success": False, "error": f"Cell index {cell_index} out of range (0-{len(cells)-1})"}
            if content is None:
                return {"success": False, "error": "Content required for replace mode"}
            cells[cell_index]["source"] = content.split('\n') if content else []
            if cell_type:
                cells[cell_index]["cell_type"] = cell_type
            message = f"Replaced cell {cell_index}"

        else:
            return {"success": False, "error": f"Unknown mode: {mode}"}

        # Write back
        notebook['cells'] = cells
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)

        return {"success": True, "message": message, "total_cells": len(cells)}
    except FileNotFoundError:
        return {"success": False, "error": f"Notebook not found: {path}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid notebook JSON"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# IMAGE READING TOOL
# ==============================================================================

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def read_image(path: str, question: str = None) -> dict[str, Any]:
    """Read and analyze an image file using vision API.

    Args:
        path: Path to the image file
        question: Optional question about the image
    """
    import base64
    import mimetypes

    try:
        path = os.path.expanduser(path)

        # Check file exists
        if not os.path.exists(path):
            return {"success": False, "error": f"Image not found: {path}"}

        # Check file extension
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_IMAGE_FORMATS:
            return {
                "success": False,
                "error": f"Unsupported format: {ext}. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            }

        # Read and encode image
        with open(path, "rb") as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')

        # Determine MIME type
        mime_type = mimetypes.guess_type(path)[0] or 'image/png'

        # Get file size
        file_size = len(image_data)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            return {"success": False, "error": "Image too large (max 20MB)"}

        # Return image info for the agent to use in vision call
        return {
            "success": True,
            "path": path,
            "format": ext,
            "mime_type": mime_type,
            "size_bytes": file_size,
            "base64": base64_image,
            "question": question or "Describe this image in detail.",
            "note": "Image loaded. Use this in a vision API call to analyze."
        }
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# WEB SEARCH TOOL
# ==============================================================================


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
    """
    import urllib.request
    import urllib.parse
    import urllib.error

    try:
        # Use DuckDuckGo HTML search (no API key required)
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'GrokCode/1.0 (CLI coding assistant)',
                'Accept': 'text/html'
            }
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Parse results from HTML (simple regex-based extraction)
        results = []

        # Find result blocks
        import re

        # Extract result snippets
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*(?:<[^>]*>[^<]*)*)</a>'

        titles = re.findall(result_pattern, html)
        snippets = re.findall(snippet_pattern, html)

        for i, (url, title) in enumerate(titles[:max_results]):
            # Clean up the URL (DuckDuckGo wraps URLs)
            if '//' in url:
                # Extract actual URL from DDG redirect
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = urllib.parse.unquote(url_match.group(1))

            snippet = snippets[i] if i < len(snippets) else ""
            # Clean HTML tags from snippet
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()

            results.append({
                "title": title.strip(),
                "url": url,
                "snippet": snippet[:200]
            })

        if not results:
            return {
                "success": True,
                "query": query,
                "results": [],
                "message": "No results found"
            }

        return {
            "success": True,
            "query": query,
            "result_count": len(results),
            "results": results
        }
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Network error: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# FILE EDIT TOOL
# ==============================================================================


def edit_file(path: str, line: int, content: str, mode: str = "replace", end_line: int = None) -> dict[str, Any]:
    """Edit a file at specific line(s).

    Args:
        path: File path to edit
        line: Line number (1-based)
        content: New content for the line(s)
        mode: 'replace', 'insert', or 'delete'
        end_line: End line for range operations (inclusive)
    """
    try:
        path = os.path.expanduser(path)
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Convert to 0-based index
        idx = line - 1
        end_idx = (end_line - 1) if end_line else idx

        if idx < 0 or idx >= len(lines):
            return {"success": False, "error": f"Line {line} out of range (file has {len(lines)} lines)"}

        if end_line and (end_idx < 0 or end_idx >= len(lines)):
            return {"success": False, "error": f"End line {end_line} out of range"}

        if mode == "replace":
            # Replace line(s)
            if end_line:
                lines[idx:end_idx + 1] = [content + "\n"]
            else:
                lines[idx] = content + "\n"
        elif mode == "insert":
            lines.insert(idx, content + "\n")
        elif mode == "delete":
            if end_line:
                del lines[idx:end_idx + 1]
            else:
                del lines[idx]
        else:
            return {"success": False, "error": f"Unknown mode: {mode}"}

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return {"success": True, "message": f"Edited {path} at line {line}"}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# GLOB/FIND TOOL
# ==============================================================================


def glob_files(pattern: str, path: str = ".") -> dict[str, Any]:
    """Find files matching a glob pattern."""
    try:
        import glob as glob_module
        path = os.path.expanduser(path) if path else "."
        full_pattern = os.path.join(path, pattern)
        matches = glob_module.glob(full_pattern, recursive=True)

        if not matches:
            return {"success": True, "output": "No matches found."}

        # Format output with relative paths
        output = "\n".join(sorted(matches))
        return {"success": True, "output": output}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# SESSION PERSISTENCE
# ==============================================================================


def generate_session_name() -> str:
    """Generate a unique session filename."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}.json"


def save_session(messages: list[dict], filepath: str) -> dict[str, Any]:
    """Save conversation messages to a file."""
    try:
        filepath = os.path.expanduser(filepath)
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        session_data = {
            "version": VERSION,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "messages": messages
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        return {"success": True, "message": f"Session saved to {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_session(filepath: str) -> dict[str, Any]:
    """Load conversation messages from a file."""
    try:
        filepath = os.path.expanduser(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        messages = session_data.get("messages", [])
        return {
            "success": True,
            "messages": messages,
            "version": session_data.get("version"),
            "saved_at": session_data.get("saved_at")
        }
    except FileNotFoundError:
        return {"success": False, "error": f"Session not found: {filepath}"}
    except json.JSONDecodeError:
        return {"success": False, "error": f"Invalid session file: {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_sessions(base_path: str = ".") -> dict[str, Any]:
    """List saved sessions in the .grokcode directory."""
    try:
        sessions_dir = Path(base_path) / ".grokcode"
        if not sessions_dir.exists():
            return {"success": True, "output": "No sessions directory found."}

        sessions = sorted(sessions_dir.glob("session_*.json"), reverse=True)
        if not sessions:
            return {"success": True, "output": "No saved sessions."}

        output_lines = []
        for s in sessions[:10]:  # Show last 10
            try:
                with open(s) as f:
                    data = json.load(f)
                    saved_at = data.get("saved_at", "unknown")
                    msg_count = len(data.get("messages", []))
                    output_lines.append(f"{s.name}  ({saved_at}, {msg_count} messages)")
            except Exception:
                output_lines.append(f"{s.name}  (unreadable)")

        return {"success": True, "output": "\n".join(output_lines)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# COMPACT / SUMMARIZATION
# ==============================================================================


def compact_messages(messages: list[dict], keep_recent: int = 4) -> dict[str, Any]:
    """Compact conversation history by summarizing older messages.

    Keeps:
    - System prompts (always)
    - Recent messages (keep_recent exchanges)
    - Summarizes older content into a single message
    """
    if len(messages) <= 1:  # Only system prompt
        return {"success": True, "messages": messages, "removed": 0}

    # Separate system messages and conversation
    system_msgs = [m for m in messages if m.get("role") == "system"]
    conversation = [m for m in messages if m.get("role") != "system"]

    if len(conversation) <= keep_recent * 2:  # Not enough to compact
        return {"success": True, "messages": messages, "removed": 0}

    # Keep recent messages
    recent = conversation[-(keep_recent * 2):]
    older = conversation[:-(keep_recent * 2)]

    # Create summary of older messages
    summary_parts = []
    for msg in older:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            summary_parts.append(f"User: {content[:100]}...")
        elif role == "assistant":
            if content:
                summary_parts.append(f"Assistant: {content[:100]}...")
        # Skip tool messages in summary

    summary = "Previous conversation summary:\n" + "\n".join(summary_parts[-10:])  # Last 10 items

    # Build compacted messages
    compacted = system_msgs.copy()
    compacted.append({"role": "user", "content": f"[Context from earlier conversation]\n{summary}"})
    compacted.extend(recent)

    return {
        "success": True,
        "messages": compacted,
        "removed": len(older),
        "message": f"Compacted {len(older)} messages into summary"
    }


# ==============================================================================
# EXPORT TRANSCRIPT
# ==============================================================================


def export_transcript(messages: list[dict], filepath: str, format: str = "markdown") -> dict[str, Any]:
    """Export conversation transcript to a file.

    Args:
        messages: List of conversation messages
        filepath: Output file path
        format: 'markdown' or 'json'
    """
    try:
        filepath = os.path.expanduser(filepath)
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        if format == "json":
            export_data = {
                "version": VERSION,
                "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "messages": messages
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
        else:  # markdown
            lines = ["# Grok Code Transcript\n"]
            lines.append(f"*Exported: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            lines.append("---\n\n")

            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")

                if role == "system":
                    continue  # Skip system prompts
                elif role == "user":
                    lines.append(f"## User\n\n{content}\n\n")
                elif role == "assistant":
                    if content:
                        lines.append(f"## Assistant\n\n{content}\n\n")
                    if msg.get("tool_calls"):
                        lines.append("*[Tool calls made]*\n\n")
                elif role == "tool":
                    lines.append(f"*Tool result: {content[:200]}...*\n\n" if len(content) > 200 else f"*Tool result: {content}*\n\n")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("".join(lines))

        return {"success": True, "message": f"Exported to {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# REWIND CONVERSATION
# ==============================================================================


def rewind_conversation(messages: list[dict]) -> dict[str, Any]:
    """Remove the last user/assistant exchange from the conversation.

    Removes everything from the last user message onwards.
    Modifies the list in place.
    """
    # Find the last user message index
    last_user_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    if last_user_idx is None:
        return {"success": False, "error": "Nothing to rewind - no user messages found"}

    # Remove everything from last user message onwards
    removed_count = len(messages) - last_user_idx
    del messages[last_user_idx:]

    return {"success": True, "message": f"Removed {removed_count} messages", "removed": removed_count}


# ==============================================================================
# OUTPUT FORMATTING
# ==============================================================================


def format_output(data: dict, format: str = "text") -> str:
    """Format output for different output modes.

    Args:
        data: Data to format
        format: 'text' or 'json'
    """
    if format == "json":
        return json.dumps(data, indent=2)
    else:
        # Text format - return content if present
        if "content" in data:
            return str(data["content"])
        return str(data)


# ==============================================================================
# TOOL FILTERING
# ==============================================================================


def filter_tools(
    tools: list[dict],
    allowed_tools: set[str] = None,
    disallowed_tools: set[str] = None
) -> list[dict]:
    """Filter tools based on whitelist or blacklist.

    Args:
        tools: List of tool schemas
        allowed_tools: If provided, only include these tools (whitelist)
        disallowed_tools: If provided, exclude these tools (blacklist)

    Returns:
        Filtered list of tool schemas
    """
    if allowed_tools:
        return [t for t in tools if t["function"]["name"] in allowed_tools]
    elif disallowed_tools:
        return [t for t in tools if t["function"]["name"] not in disallowed_tools]
    return tools


# ==============================================================================
# DOCTOR / HEALTH CHECK
# ==============================================================================


def run_doctor() -> dict[str, Any]:
    """Run health checks and return status of various components."""
    checks = {}

    # Check API key
    api_key = os.environ.get("XAI_API_KEY")
    if api_key:
        checks["api_key"] = {"status": "ok", "message": "XAI_API_KEY is set"}
    else:
        checks["api_key"] = {"status": "error", "message": "XAI_API_KEY not set"}

    # Check git
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            checks["git"] = {"status": "ok", "message": version}
        else:
            checks["git"] = {"status": "warning", "message": "Git not working properly"}
    except FileNotFoundError:
        checks["git"] = {"status": "warning", "message": "Git not installed"}
    except Exception as e:
        checks["git"] = {"status": "warning", "message": str(e)}

    # Check if in a git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            checks["git_repo"] = {"status": "ok", "message": "In a git repository"}
        else:
            checks["git_repo"] = {"status": "info", "message": "Not in a git repository"}
    except Exception:
        checks["git_repo"] = {"status": "info", "message": "Could not check git repo"}

    # Check GROK.md
    if Path("GROK.md").exists():
        checks["grok_md"] = {"status": "ok", "message": "GROK.md found"}
    else:
        checks["grok_md"] = {"status": "info", "message": "No GROK.md (run /init to create)"}

    # Check config
    config_file = Path(".grokcode") / "config.json"
    if config_file.exists():
        checks["config"] = {"status": "ok", "message": "Config file found"}
    else:
        checks["config"] = {"status": "info", "message": "Using default config"}

    # Overall success if no errors
    has_errors = any(c["status"] == "error" for c in checks.values())

    return {
        "success": not has_errors,
        "checks": checks
    }


# ==============================================================================
# CONTEXT SIZE CHECK
# ==============================================================================


def check_context_size(messages: list[dict], threshold: int = 100000) -> dict[str, Any]:
    """Check if conversation context is getting large.

    Args:
        messages: List of conversation messages
        threshold: Character count threshold for warning (rough estimate)

    Returns:
        Dict with warning status and size info
    """
    # Estimate token count (rough: ~4 chars per token)
    total_chars = sum(len(str(m.get("content", ""))) for m in messages)
    estimated_tokens = total_chars // 4

    warning = total_chars > threshold

    return {
        "warning": warning,
        "total_chars": total_chars,
        "estimated_tokens": estimated_tokens,
        "message_count": len(messages),
        "suggestion": "Consider using /compact to reduce context" if warning else None
    }


# ==============================================================================
# REVIEW DIFF
# ==============================================================================


def review_diff(diff_text: str) -> dict[str, Any]:
    """Generate a code review analysis for a git diff.

    Args:
        diff_text: The diff text to review
    """
    if not diff_text or not diff_text.strip():
        return {"success": False, "error": "No diff content to review"}

    # Parse the diff to extract key information
    lines_added = diff_text.count("\n+") - diff_text.count("\n+++")
    lines_removed = diff_text.count("\n-") - diff_text.count("\n---")

    # Extract file names
    files = []
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3].lstrip("b/"))

    analysis = {
        "files_changed": len(files),
        "files": files,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "summary": f"Changed {len(files)} file(s), +{lines_added}/-{lines_removed} lines"
    }

    return {"success": True, "analysis": analysis, "diff": diff_text}


# ==============================================================================
# EXTRACT TODOS
# ==============================================================================


def extract_todos(directory: str = ".") -> dict[str, Any]:
    """Extract TODO, FIXME, and similar comments from code files.

    Args:
        directory: Directory to search
    """
    todos = []
    patterns = ["TODO", "FIXME", "HACK", "XXX", "BUG", "NOTE"]
    pattern_regex = "|".join(patterns)

    try:
        # Use grep to find TODOs
        result = subprocess.run(
            ["grep", "-rn", "-E", f"({pattern_regex})[:\\s]", directory,
             "--include=*.py", "--include=*.js", "--include=*.ts",
             "--include=*.go", "--include=*.rs", "--include=*.java",
             "--include=*.c", "--include=*.cpp", "--include=*.h"],
            capture_output=True, text=True, timeout=30
        )

        for line in result.stdout.strip().split("\n"):
            if line:
                # Parse: filename:lineno:content
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    todos.append({
                        "file": parts[0],
                        "line": int(parts[1]) if parts[1].isdigit() else 0,
                        "content": parts[2].strip()
                    })

        return {"success": True, "todos": todos, "count": len(todos)}
    except Exception as e:
        return {"success": True, "todos": [], "count": 0, "note": str(e)}


# ==============================================================================
# SESSION PICKER
# ==============================================================================


def get_sessions_for_picker(base_path: str = ".") -> list[dict]:
    """Get sessions formatted for picker display.

    Returns list of dicts with path, name, date, preview
    """
    sessions = []
    sessions_dir = Path(base_path) / ".grokcode"

    if not sessions_dir.exists():
        return sessions

    for session_file in sorted(sessions_dir.glob("session_*.json"),
                               key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with open(session_file, "r") as f:
                data = json.load(f)

            # Get first user message as preview
            preview = ""
            for msg in data.get("messages", []):
                if msg.get("role") == "user":
                    preview = msg.get("content", "")[:50]
                    break

            sessions.append({
                "path": str(session_file),
                "name": session_file.name,
                "date": data.get("saved_at", "Unknown"),
                "preview": preview + "..." if len(preview) >= 50 else preview
            })
        except Exception:
            continue

    return sessions


# ==============================================================================
# THEMES
# ==============================================================================


THEMES = {
    "default": {
        "primary": "cyan",
        "secondary": "green",
        "error": "red",
        "warning": "yellow",
        "info": "blue",
        "dim": "dim",
    },
    "dark": {
        "primary": "bright_blue",
        "secondary": "bright_green",
        "error": "bright_red",
        "warning": "bright_yellow",
        "info": "bright_cyan",
        "dim": "bright_black",
    },
    "light": {
        "primary": "blue",
        "secondary": "green",
        "error": "red",
        "warning": "yellow",
        "info": "cyan",
        "dim": "white",
    },
    "monokai": {
        "primary": "magenta",
        "secondary": "green",
        "error": "red",
        "warning": "yellow",
        "info": "cyan",
        "dim": "bright_black",
    },
}

_current_theme = "default"


def get_current_theme() -> str:
    """Get the current theme name."""
    return _current_theme


def set_theme(theme_name: str) -> dict[str, Any]:
    """Set the current theme."""
    global _current_theme
    if theme_name not in THEMES:
        return {"success": False, "error": f"Unknown theme: {theme_name}. Available: {', '.join(THEMES.keys())}"}
    _current_theme = theme_name
    return {"success": True, "message": f"Theme set to: {theme_name}"}


def get_theme_color(color_name: str) -> str:
    """Get a color from the current theme."""
    theme = THEMES.get(_current_theme, THEMES["default"])
    return theme.get(color_name, color_name)


# ==============================================================================
# VIM MODE
# ==============================================================================


_vim_mode_enabled = False


def is_vim_mode_enabled() -> bool:
    """Check if vim mode is enabled."""
    return _vim_mode_enabled


def toggle_vim_mode() -> dict[str, Any]:
    """Toggle vim mode on/off."""
    global _vim_mode_enabled
    _vim_mode_enabled = not _vim_mode_enabled
    status = "enabled" if _vim_mode_enabled else "disabled"
    return {"success": True, "message": f"Vim mode {status}", "enabled": _vim_mode_enabled}


# ==============================================================================
# MULTILINE INPUT
# ==============================================================================


def get_multiline_keybindings():
    """Get keybindings for multiline input (Shift+Enter for newline)."""
    from prompt_toolkit.key_binding import KeyBindings

    bindings = KeyBindings()

    @bindings.add('escape', 'enter')  # Alt+Enter or Escape then Enter
    def _(event):
        """Insert newline on Alt+Enter."""
        event.current_buffer.insert_text('\n')

    @bindings.add('c-j')  # Ctrl+J
    def _(event):
        """Insert newline on Ctrl+J."""
        event.current_buffer.insert_text('\n')

    return bindings


def create_input_session(multiline: bool = False):
    """Create a prompt_toolkit session with optional multiline support."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    history_file = Path(".grokcode") / "history"
    history_file.parent.mkdir(exist_ok=True)

    kwargs = {
        "history": FileHistory(str(history_file)),
        "auto_suggest": AutoSuggestFromHistory(),
        "enable_history_search": True,
    }

    if multiline:
        kwargs["key_bindings"] = get_multiline_keybindings()
        kwargs["multiline"] = False  # We handle it with keybindings

    if is_vim_mode_enabled():
        from prompt_toolkit.editing_mode import EditingMode
        kwargs["editing_mode"] = EditingMode.VI

    return PromptSession(**kwargs)


# ==============================================================================
# GITHUB ACTION
# ==============================================================================


def generate_github_action() -> dict[str, Any]:
    """Generate a GitHub Action workflow for GrokCode."""
    return {
        "name": "GrokCode CI",
        "on": {
            "push": {"branches": ["main", "master"]},
            "pull_request": {"branches": ["main", "master"]},
        },
        "jobs": {
            "review": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v4"},
                    {"name": "Set up Python", "uses": "actions/setup-python@v5", "with": {"python-version": "3.11"}},
                    {"name": "Install GrokCode", "run": "pip install grokcode"},
                    {
                        "name": "Review Changes",
                        "env": {"XAI_API_KEY": "${{ secrets.XAI_API_KEY }}"},
                        "run": "grokcode -p 'Review the changes in this PR and provide feedback' --output-format json"
                    }
                ]
            }
        }
    }


def create_github_action_file(output_path: str = ".github/workflows/grokcode.yml") -> dict[str, Any]:
    """Create a GitHub Action workflow file."""
    try:
        import yaml
        action = generate_github_action()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(action, f, default_flow_style=False, sort_keys=False)
        return {"success": True, "message": f"Created {output_path}"}
    except ImportError:
        # Fallback without yaml
        return {"success": False, "error": "PyYAML not installed. Run: pip install pyyaml"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# CUSTOM TOOLS
# ==============================================================================


def load_custom_tools(base_path: str = ".") -> list[dict]:
    """Load custom tools from config file.

    Custom tools are defined in .grokcode/config.json under 'custom_tools' key.
    Each tool has: name, description, command, and optional parameters.
    """
    config = load_config(base_path)
    custom_tools = config.get("custom_tools", [])
    tool_schemas = []

    for tool in custom_tools:
        if not tool.get("name") or not tool.get("command"):
            continue

        schema = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", f"Custom tool: {tool['name']}"),
                "parameters": tool.get("parameters", {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "string",
                            "description": "Arguments to pass to the command"
                        }
                    }
                })
            }
        }
        tool_schemas.append(schema)

    return tool_schemas


def execute_custom_tool(command: str, args: str = "") -> dict[str, Any]:
    """Execute a custom tool command."""
    try:
        full_command = f"{command} {args}".strip()
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout + result.stderr
        return {
            "success": result.returncode == 0,
            "output": output.strip(),
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# MCP (MODEL CONTEXT PROTOCOL)
# ==============================================================================


class MCPConfig:
    """Configuration for an MCP server."""

    def __init__(self, name: str, command: str, args: list[str] = None, env: dict = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env
        }


def load_mcp_config(config_path: str = ".mcp.json") -> list[MCPConfig]:
    """Load MCP server configurations from file."""
    path = Path(config_path)
    if not path.exists():
        return []

    try:
        with open(path) as f:
            data = json.load(f)

        configs = []
        for server in data.get("servers", []):
            configs.append(MCPConfig(
                name=server.get("name", "unnamed"),
                command=server.get("command", ""),
                args=server.get("args", []),
                env=server.get("env", {})
            ))
        return configs
    except Exception:
        return []


def list_mcp_tools(config_path: str = ".mcp.json") -> list[dict]:
    """List tools available from configured MCP servers.

    Note: This is a simplified implementation. Full MCP would require
    connecting to servers and querying their tool lists.
    """
    configs = load_mcp_config(config_path)
    tools = []

    for config in configs:
        # In a full implementation, we would connect to the server
        # and query its available tools via the MCP protocol
        tools.append({
            "server": config.name,
            "status": "configured",
            "note": "Connect to server to discover tools"
        })

    return tools


# ==============================================================================
# SECURE TOKEN STORAGE
# ==============================================================================

KEYRING_SERVICE = "grokcode"
KEYRING_USERNAME = "api_key"


def get_api_key_from_keyring() -> str | None:
    """Get API key from secure keyring storage."""
    try:
        import keyring
        return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except ImportError:
        return None
    except Exception:
        return None


def set_api_key_in_keyring(api_key: str) -> dict[str, Any]:
    """Store API key in secure keyring storage."""
    try:
        import keyring
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        return {"success": True, "message": "API key stored securely"}
    except ImportError:
        return {"success": False, "error": "keyring package not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_api_key_from_keyring() -> dict[str, Any]:
    """Delete API key from secure keyring storage."""
    try:
        import keyring
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        return {"success": True, "message": "API key removed from keyring"}
    except ImportError:
        return {"success": False, "error": "keyring package not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_api_key() -> str | None:
    """Get API key from environment or secure storage.

    Priority:
    1. XAI_API_KEY environment variable
    2. Secure keyring storage
    """
    # Check environment first
    api_key = os.environ.get("XAI_API_KEY")
    if api_key:
        return api_key

    # Try keyring
    return get_api_key_from_keyring()


# ==============================================================================
# SELF UPDATE
# ==============================================================================


def get_latest_version(package_name: str = "grokcode") -> str | None:
    """Get the latest version from PyPI."""
    try:
        import urllib.request
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get("info", {}).get("version")
    except Exception:
        return None


def check_for_updates() -> dict[str, Any]:
    """Check if a newer version is available."""
    current = VERSION
    latest = get_latest_version()

    if latest is None:
        return {
            "current_version": current,
            "latest_version": None,
            "update_available": False,
            "message": "Could not check for updates"
        }

    # Simple version comparison
    update_available = latest != current

    return {
        "current_version": current,
        "latest_version": latest,
        "update_available": update_available,
        "message": f"Update available: {latest}" if update_available else "You're up to date"
    }


def do_update() -> dict[str, Any]:
    """Perform self-update via pip."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "grokcode"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return {"success": True, "message": "Update successful! Restart grokcode to use new version."}
        return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# CONFIG FILE SUPPORT
# ==============================================================================


def load_config(base_path: str = ".") -> dict[str, Any]:
    """Load configuration from .grokcode/config.json, merging with defaults."""
    config = DEFAULT_CONFIG.copy()
    config["hooks"] = DEFAULT_CONFIG["hooks"].copy()

    config_file = Path(base_path) / ".grokcode" / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Merge user config with defaults
            for key, value in user_config.items():
                if key == "hooks" and isinstance(value, dict):
                    config["hooks"].update(value)
                else:
                    config[key] = value
        except (json.JSONDecodeError, Exception):
            pass  # Use defaults on error

    return config


def save_config(config: dict[str, Any], base_path: str = ".") -> dict[str, Any]:
    """Save configuration to .grokcode/config.json."""
    try:
        config_dir = Path(base_path) / ".grokcode"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        return {"success": True, "message": f"Config saved to {config_file}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_config_tui(console: "Console") -> dict[str, Any]:
    """Display an interactive config editor TUI."""
    from prompt_toolkit import prompt

    config = load_config()

    console.print("\n[bold]Configuration Editor[/bold]\n")
    console.print("[dim]Press Enter to keep current value, or type new value[/dim]\n")

    # Model selection
    console.print(f"[bold]1. Model[/bold]: {config.get('model', DEFAULT_MODEL)}")
    console.print(f"   Available: {', '.join(AVAILABLE_MODELS.keys())}")
    new_model = prompt("   New value (Enter to keep): ").strip()
    if new_model and new_model in AVAILABLE_MODELS:
        config["model"] = new_model
        console.print(f"   [success]Updated to {new_model}[/success]")
    elif new_model:
        console.print("   [warning]Invalid model, keeping current[/warning]")

    # Theme selection
    console.print(f"\n[bold]2. Theme[/bold]: {config.get('theme', 'default')}")
    console.print(f"   Available: {', '.join(THEMES.keys())}")
    new_theme = prompt("   New value (Enter to keep): ").strip()
    if new_theme and new_theme in THEMES:
        config["theme"] = new_theme
        console.print(f"   [success]Updated to {new_theme}[/success]")
    elif new_theme:
        console.print("   [warning]Invalid theme, keeping current[/warning]")

    # Skip permissions
    console.print(f"\n[bold]3. Skip Permissions[/bold]: {config.get('skip_permissions', False)}")
    skip_input = prompt("   New value (true/false, Enter to keep): ").strip().lower()
    if skip_input in ("true", "false"):
        config["skip_permissions"] = skip_input == "true"
        console.print(f"   [success]Updated to {config['skip_permissions']}[/success]")
    elif skip_input:
        console.print("   [warning]Invalid value, keeping current[/warning]")

    # Show hooks summary
    hooks = config.get("hooks", {})
    console.print("\n[bold]4. Hooks[/bold]:")
    console.print(f"   pre_tool: {len(hooks.get('pre_tool', []))} commands")
    console.print(f"   post_tool: {len(hooks.get('post_tool', []))} commands")
    console.print(f"   on_error: {len(hooks.get('on_error', []))} commands")
    console.print("   [dim](Edit .grokcode/config.json directly to modify hooks)[/dim]")

    # Save config
    console.print()
    save_choice = prompt("Save changes? (y/n): ").strip().lower()
    if save_choice == "y":
        result = save_config(config)
        return result

    return {"success": True, "message": "Changes discarded"}


# ==============================================================================
# HOOKS SYSTEM
# ==============================================================================


def run_hook(command: str, context: dict[str, str] = None) -> dict[str, Any]:
    """Run a hook command with optional context variables."""
    try:
        # Set up environment with context
        env = os.environ.copy()
        if context:
            env.update(context)

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Hook timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_hooks(hooks: list[str], context: dict[str, str] = None) -> list[dict[str, Any]]:
    """Run multiple hook commands."""
    results = []
    for hook in hooks:
        results.append(run_hook(hook, context))
    return results


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_to_file": write_to_file,
    "list_files": list_files,
    "execute_command": execute_command,
    "search_files": search_files,
    "edit_file": edit_file,
    "glob_files": glob_files,
    "git_status": git_status,
    "git_diff": git_diff,
    "git_log": git_log,
    "git_add": git_add,
    "git_commit": git_commit,
    "git_branch": git_branch,
    "web_fetch": web_fetch,
    "ask_user": ask_user,
    "notebook_edit": notebook_edit,
    "read_image": read_image,
    "web_search": web_search,
}

# Task plan tools need state manager - handled separately in execute_tool
TASK_PLAN_TOOLS = {
    "create_task_plan",
    "update_task_status",
    "add_task",
    "get_plan_status",
    "clear_task_plan",
}


# ==============================================================================
# GROK CODE AGENT
# ==============================================================================


class GrokCode:
    """The main Grok Code agent."""

    def __init__(self, skip_permissions: bool = False, model: str = None):
        self.console = Console(theme=CUSTOM_THEME)
        self.messages: list[dict[str, Any]] = []
        self.tool_call_count = 0
        self.tool_call_history: deque[str] = deque(maxlen=LOOP_HISTORY_SIZE)
        self.loop_nudge_injected = False

        # Load configuration
        self.config = load_config()

        # Apply settings (CLI args override config)
        self.skip_permissions = skip_permissions or self.config.get("skip_permissions", False)
        self.model = model or self.config.get("model", DEFAULT_MODEL)

        # Initialize state manager (Ralph Wiggum Loop)
        self.state_mgr = StateManager()

        # Initialize token tracker
        self.token_tracker = TokenTracker()

        # Check API key (env var or keyring)
        api_key = get_api_key()
        if not api_key:
            self.console.print(
                "[error]Error: XAI_API_KEY not set[/error]\n"
                "Set it with: export XAI_API_KEY='your-key'\n"
                "Or store securely with: grokcode login"
            )
            sys.exit(1)

        self.client = OpenAI(api_key=api_key, base_url=XAI_BASE_URL)

        # Initialize messages with system prompt and project memory (GROK.md)
        self.messages.extend(build_system_messages())

    def print_welcome(self):
        """Print welcome banner."""
        cwd = get_cwd_display()
        self.console.print()
        self.console.print(f"[bold magenta]╭─ Grok Code v{VERSION} ─╮[/bold magenta]")
        self.console.print(f"[dim]│ Model: {self.model}[/dim]")
        self.console.print(f"[dim]│ cwd: {cwd}[/dim]")
        self.console.print("[bold magenta]╰──────────────────────╯[/bold magenta]")
        if self.skip_permissions:
            self.console.print()
            self.console.print("[bold red]⚠ DANGER MODE: All tool permissions skipped![/bold red]")
        self.console.print()
        self.console.print("[dim]Type your request, or /help for commands.[/dim]")

    def _tool_signature(self, name: str, args: dict) -> str:
        """Create a signature string for a tool call (for loop detection)."""
        # Normalize args to detect identical calls
        sorted_args = json.dumps(args, sort_keys=True)
        return f"{name}:{sorted_args}"

    def _check_loop(self, name: str, args: dict) -> bool:
        """Check if we're in a loop. Returns True if loop detected."""
        sig = self._tool_signature(name, args)
        self.tool_call_history.append(sig)

        # Count occurrences of this exact call
        count = sum(1 for s in self.tool_call_history if s == sig)
        return count >= LOOP_THRESHOLD

    def _inject_loop_nudge(self):
        """Inject a message to help break out of the loop."""
        if not self.loop_nudge_injected:
            self.console.print("  [warning]Loop detected - nudging model[/warning]")
            self.messages.append({
                "role": "user",
                "content": LOOP_NUDGE_MESSAGE
            })
            self.loop_nudge_injected = True

    def _reset_loop_state(self):
        """Reset loop detection state (call on new user input)."""
        self.tool_call_history.clear()
        self.loop_nudge_injected = False

    def print_tool_use(self, tool_name: str, args: dict):
        """Print tool usage."""
        # Format based on tool type
        if tool_name == "read_file":
            self.console.print(f"  [tool]Read[/tool] {args.get('path', '')}")
        elif tool_name == "write_to_file":
            path = args.get('path', '')
            content = args.get('content', '')
            lines = content.count('\n') + 1
            self.console.print(f"  [tool]Write[/tool] {path} ({lines} lines)")
        elif tool_name == "list_files":
            self.console.print(f"  [tool]List[/tool] {args.get('path', '.')}")
        elif tool_name == "execute_command":
            cmd = args.get('command', '')
            if len(cmd) > 60:
                cmd = cmd[:60] + "..."
            self.console.print(f"  [tool]Run[/tool] {cmd}")
        elif tool_name == "search_files":
            pattern = args.get('pattern', '')
            self.console.print(f"  [tool]Search[/tool] {pattern}")
        # Task plan tools
        elif tool_name == "create_task_plan":
            goal = args.get('goal', '')[:40]
            task_count = len(args.get('tasks', []))
            self.console.print(f"  [tool]Plan[/tool] {goal}... ({task_count} tasks)")
        elif tool_name == "update_task_status":
            idx = args.get('task_index', '?')
            status = args.get('status', '')
            self.console.print(f"  [tool]Task[/tool] #{idx} -> {status}")
        elif tool_name == "add_task":
            desc = args.get('description', '')[:40]
            self.console.print(f"  [tool]AddTask[/tool] {desc}...")
        elif tool_name == "get_plan_status":
            self.console.print("  [tool]GetPlan[/tool]")
        elif tool_name == "clear_task_plan":
            self.console.print("  [tool]ClearPlan[/tool]")
        else:
            self.console.print(f"  [tool]{tool_name}[/tool]")

    def print_tool_result(self, result: dict, tool_name: str):
        """Print tool result compactly."""
        if not result.get("success", False):
            error = result.get("error", "Unknown error")
            self.console.print(f"    [error]Error: {error}[/error]")
            return

        # Show compact result based on tool
        if tool_name == "read_file":
            content = result.get("content", "")
            lines = content.count('\n') + 1
            self.console.print(f"    [result]({lines} lines)[/result]")
        elif tool_name == "write_to_file":
            self.console.print("    [success]Done[/success]")
        elif tool_name == "list_files":
            output = result.get("output", "")
            count = len([line for line in output.split('\n') if line.strip()])
            self.console.print(f"    [result]({count} entries)[/result]")
        elif tool_name == "execute_command":
            exit_code = result.get("exit_code", 0)
            if exit_code == 0:
                self.console.print("    [success]Exit 0[/success]")
            else:
                self.console.print(f"    [warning]Exit {exit_code}[/warning]")
        elif tool_name == "search_files":
            output = result.get("output", "")
            if "No matches" in output:
                self.console.print("    [result]No matches[/result]")
            else:
                matches = len([line for line in output.split('\n') if line.strip()])
                self.console.print(f"    [result]({matches} matches)[/result]")
        # Task plan tools
        elif tool_name in TASK_PLAN_TOOLS:
            msg = result.get("message", "Done")
            self.console.print(f"    [success]{msg}[/success]")

    def request_confirmation(self, tool_name: str, args: dict) -> bool:
        """Ask for confirmation on dangerous tools."""
        self.console.print()
        if tool_name == "write_to_file":
            path = args.get('path', '')
            content = args.get('content', '')
            # Show preview of content with syntax highlighting
            preview = content[:500] + "..." if len(content) > 500 else content
            # Detect language from file extension or content
            ext = Path(path).suffix.lower()
            ext_to_lang = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
                '.md': 'markdown', '.sh': 'bash', '.bash': 'bash',
                '.html': 'html', '.css': 'css', '.sql': 'sql',
                '.rs': 'rust', '.go': 'go', '.rb': 'ruby',
            }
            lang = ext_to_lang.get(ext, detect_language(preview))
            self.console.print(Panel(
                Syntax(preview, lang, theme="monokai", line_numbers=True),
                title=f"[yellow]Write to {path}?[/yellow]",
                border_style="yellow"
            ))
        else:
            cmd = args.get('command', '')
            self.console.print(Panel(
                Syntax(cmd, "bash", theme="monokai"),
                title="[yellow]Run command?[/yellow]",
                border_style="yellow"
            ))
        return Confirm.ask("Allow?", default=True)

    # Tools that may take longer and benefit from a spinner
    SLOW_TOOLS = {"execute_command", "web_fetch", "web_search", "search_files"}

    def execute_tool(self, name: str, args: dict) -> dict[str, Any]:
        """Execute a tool by name."""
        # Handle task plan tools (need state manager)
        if name in TASK_PLAN_TOOLS:
            try:
                if name == "create_task_plan":
                    return create_task_plan(args["goal"], args["tasks"], self.state_mgr)
                elif name == "update_task_status":
                    return update_task_status(args["task_index"], args["status"], self.state_mgr)
                elif name == "add_task":
                    return add_task(args["description"], self.state_mgr)
                elif name == "get_plan_status":
                    return get_plan_status(self.state_mgr)
                elif name == "clear_task_plan":
                    return clear_task_plan(self.state_mgr)
            except KeyError as e:
                return {"success": False, "error": f"Missing argument: {e}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Handle regular tools
        if name not in TOOL_FUNCTIONS:
            return {"success": False, "error": f"Unknown tool: {name}"}
        try:
            # Handle renamed parameter
            if name == "search_files" and "regex" in args:
                args["pattern"] = args.pop("regex")

            # Use spinner for slow tools
            if name in self.SLOW_TOOLS:
                with Progress(
                    SpinnerColumn(),
                    TextColumn(f"[dim]Running {name}...[/dim]"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    progress.add_task("running", total=None)
                    return TOOL_FUNCTIONS[name](**args)
            else:
                return TOOL_FUNCTIONS[name](**args)
        except TypeError as e:
            return {"success": False, "error": f"Invalid arguments: {e}"}

    def call_api(self):
        """Make API call to Grok."""
        try:
            # Inject plan context if available
            messages = self.messages.copy()
            plan_context = self.state_mgr.get_plan_context()
            if plan_context:
                # Find the last user message and inject context after system prompt
                # This keeps the plan visible to the model on each call
                messages = [messages[0]]  # System prompt
                messages.append({
                    "role": "system",
                    "content": plan_context
                })
                messages.extend(self.messages[1:])  # Rest of conversation

            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.1
            )
        except Exception as e:
            self.console.print(f"[error]API Error: {e}[/error]")
            return None

    def call_api_stream(self):
        """Make streaming API call to Grok."""
        try:
            # Inject plan context if available
            messages = self.messages.copy()
            plan_context = self.state_mgr.get_plan_context()
            if plan_context:
                messages = [messages[0]]  # System prompt
                messages.append({
                    "role": "system",
                    "content": plan_context
                })
                messages.extend(self.messages[1:])  # Rest of conversation

            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.1,
                stream=True
            )
        except Exception as e:
            self.console.print(f"[error]API Error: {e}[/error]")
            return None

    def process_stream(self, stream) -> tuple[str, list[dict]]:
        """Process a streaming response and return content and tool calls."""
        content = ""
        tool_calls_builder: dict[int, dict] = {}  # index -> {id, function: {name, arguments}}
        first_chunk = True

        # Show thinking spinner until first content arrives
        with Progress(
            SpinnerColumn(),
            TextColumn("[dim]Thinking...[/dim]"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task("thinking", total=None)

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Stop spinner on first content
                if first_chunk and (delta.content or delta.tool_calls):
                    first_chunk = False
                    break

            # Re-process the first chunk after spinner stops
            if not first_chunk:
                if delta.content:
                    content += delta.content
                    self.console.print(delta.content, end="")
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_builder:
                            tool_calls_builder[idx] = {
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            }
                        if tc.id:
                            tool_calls_builder[idx]["id"] = tc.id
                        if tc.function.name:
                            tool_calls_builder[idx]["function"]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls_builder[idx]["function"]["arguments"] += tc.function.arguments

        # Continue processing remaining chunks
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Accumulate text content
            if delta.content:
                content += delta.content
                # Print content as it streams
                self.console.print(delta.content, end="")

            # Accumulate tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_builder:
                        tool_calls_builder[idx] = {
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }

                    if tc.id:
                        tool_calls_builder[idx]["id"] = tc.id
                    if tc.function.name:
                        tool_calls_builder[idx]["function"]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls_builder[idx]["function"]["arguments"] += tc.function.arguments

        # Add newline after streaming content
        if content:
            self.console.print()

        # Convert builder to list
        tool_calls = [tool_calls_builder[i] for i in sorted(tool_calls_builder.keys())]

        return content, tool_calls

    def process_response(self, response) -> bool:
        """Process API response. Returns True if should continue (tools called)."""
        if not response:
            return False

        message = response.choices[0].message

        # Handle tool calls
        if message.tool_calls:
            # Add assistant message
            self.messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # Process each tool
            for tc in message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                # Check for loop before executing
                if self._check_loop(name, args):
                    self._inject_loop_nudge()
                    return True  # Re-trigger API with nudge

                self.print_tool_use(name, args)
                self.tool_call_count += 1

                # Confirmation for dangerous tools (unless skip_permissions)
                if name in DANGEROUS_TOOLS and not self.skip_permissions:
                    if not self.request_confirmation(name, args):
                        result = {"success": False, "error": "Denied by user"}
                    else:
                        result = self.execute_tool(name, args)
                else:
                    result = self.execute_tool(name, args)

                self.print_tool_result(result, name)

                # Add to messages (truncated)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(truncate_result(result))
                })

            return True

        # No tools - print text response
        content = message.content or ""
        if content:
            self.messages.append({"role": "assistant", "content": content})
            self.console.print()
            self.console.print(Markdown(content))

        return False

    def clear_context(self):
        """Clear conversation history."""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tool_call_count = 0
        self.console.print("[success]Context cleared.[/success]")

    def show_help(self):
        """Show help information."""
        help_text = """
[bold]Commands:[/bold]
  /clear       Clear conversation history
  /compact     Summarize older messages to reduce tokens
  /rewind      Undo the last exchange
  /export FILE Export conversation to markdown or JSON
  /doctor      Run health checks
  /review      Review current git diff with AI
  /todos       List TODOs/FIXMEs in codebase
  /plan        Show current task plan
  /plan clear  Clear task plan
  /tokens      Show token usage
  /init        Generate GROK.md project file
  /status      Show git status
  /diff        Show git diff
  /log         Show git log
  /branch      List git branches
  /save        Save current session
  /load FILE   Load a saved session
  /resume      Pick a session to resume
  /sessions    List saved sessions
  /theme NAME  Switch theme (default, dark, light, monokai)
  /vim         Toggle vim input mode
  /config      Edit configuration settings
  /update      Check for updates and install
  /help        Show this help
  /exit        Exit Grok Code

[bold]Tips:[/bold]
  - Create a GROK.md file with /init to give context about your project
  - Use natural language to describe what you want
  - Grok will ask for confirmation before writing files or running commands
  - For complex tasks, Grok will create a task plan to track progress
"""
        self.console.print(help_text)

    def show_doctor(self):
        """Show health check results."""
        result = run_doctor()
        self.console.print()
        self.console.print("[bold]Health Check[/bold]")
        self.console.print()

        status_icons = {
            "ok": "[green]OK[/green]",
            "warning": "[yellow]WARN[/yellow]",
            "error": "[red]ERROR[/red]",
            "info": "[dim]INFO[/dim]"
        }

        for name, check in result["checks"].items():
            icon = status_icons.get(check["status"], "?")
            self.console.print(f"  {icon}  {name}: {check['message']}")

        self.console.print()

    def show_git_status(self):
        """Show git status."""
        result = git_status()
        if result["success"]:
            self.console.print(Panel(
                result["output"] or "No changes.",
                title="[bold]Git Status[/bold]",
                border_style="blue"
            ))
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def show_git_diff(self, staged: bool = False):
        """Show git diff."""
        result = git_diff(staged=staged)
        if result["success"]:
            output = result["output"]
            if output and output != "No changes.":
                self.console.print(Panel(
                    Syntax(output, "diff", theme="monokai"),
                    title="[bold]Git Diff[/bold]" + (" (staged)" if staged else ""),
                    border_style="blue"
                ))
            else:
                self.console.print("[dim]No changes.[/dim]")
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def show_git_log(self, count: int = 10):
        """Show git log."""
        result = git_log(count=count)
        if result["success"]:
            self.console.print(Panel(
                result["output"] or "No commits yet.",
                title="[bold]Git Log[/bold]",
                border_style="blue"
            ))
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def do_save_session(self, filename: str = None):
        """Save the current session."""
        if filename is None:
            filename = generate_session_name()
        filepath = Path(".grokcode") / filename
        result = save_session(self.messages, str(filepath))
        if result["success"]:
            self.console.print(f"[success]{result['message']}[/success]")
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def do_load_session(self, filepath: str):
        """Load a saved session."""
        # Check if it's just a filename (in .grokcode dir)
        if not os.path.dirname(filepath):
            filepath = str(Path(".grokcode") / filepath)

        result = load_session(filepath)
        if result["success"]:
            self.messages = result["messages"]
            saved_at = result.get("saved_at", "unknown")
            self.console.print(f"[success]Loaded session from {saved_at} ({len(self.messages)} messages)[/success]")
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def do_list_sessions(self):
        """List saved sessions."""
        result = list_sessions()
        if result["success"]:
            output = result["output"]
            if output and "No " not in output:
                self.console.print(Panel(
                    output,
                    title="[bold]Saved Sessions[/bold]",
                    border_style="blue"
                ))
            else:
                self.console.print(f"[dim]{output}[/dim]")
        else:
            self.console.print(f"[error]{result['error']}[/error]")

    def show_plan(self):
        """Show current task plan."""
        plan = self.state_mgr.load_plan()
        if plan and plan.tasks:
            self.console.print()
            self.console.print(Panel(
                plan.summary(),
                title="[bold]Task Plan[/bold]",
                border_style="blue"
            ))
        else:
            self.console.print("[dim]No active task plan.[/dim]")

    def process_streaming_response(self) -> bool:
        """Process a streaming response. Returns True if should continue (tools called)."""
        stream = self.call_api_stream()
        if not stream:
            return False

        self.console.print()
        content, tool_calls = self.process_stream(stream)

        if tool_calls:
            # Add assistant message with tool calls
            self.messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": tool_calls
            })

            # Process each tool
            for tc in tool_calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                # Check for loop before executing
                if self._check_loop(name, args):
                    self._inject_loop_nudge()
                    return True  # Re-trigger API with nudge

                self.print_tool_use(name, args)
                self.tool_call_count += 1

                # Confirmation for dangerous tools (unless skip_permissions)
                if name in DANGEROUS_TOOLS and not self.skip_permissions:
                    if not self.request_confirmation(name, args):
                        result = {"success": False, "error": "Denied by user"}
                    else:
                        result = self.execute_tool(name, args)
                else:
                    result = self.execute_tool(name, args)

                self.print_tool_result(result, name)

                # Add to messages (truncated)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(truncate_result(result))
                })

            return True

        # No tools - just text response
        if content:
            self.messages.append({"role": "assistant", "content": content})

        return False

    def show_tokens(self):
        """Show token usage summary."""
        if self.token_tracker.request_count > 0:
            self.console.print(f"\n[dim]{self.token_tracker.summary()}[/dim]")

    def run(self):
        """Main REPL loop."""
        self.print_welcome()

        while True:
            try:
                self.console.print()
                user_input = self.console.input("[prompt]>[/prompt] ").strip()

                if not user_input:
                    continue

                # Slash commands
                cmd = user_input.lower()
                if cmd == "/clear":
                    self.clear_context()
                    continue
                if cmd == "/compact":
                    result = compact_messages(self.messages)
                    if result["success"]:
                        self.messages = result["messages"]
                        removed = result.get("removed", 0)
                        self.console.print(f"[success]Compacted conversation ({removed} messages summarized)[/success]")
                    else:
                        self.console.print(f"[error]{result.get('error', 'Compact failed')}[/error]")
                    continue
                if cmd == "/rewind":
                    result = rewind_conversation(self.messages)
                    if result["success"]:
                        self.console.print(f"[success]{result['message']}[/success]")
                    else:
                        self.console.print(f"[error]{result['error']}[/error]")
                    continue
                if cmd.startswith("/export"):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        # Default filename
                        filename = f"transcript_{time.strftime('%Y%m%d_%H%M%S')}.md"
                    else:
                        filename = parts[1].strip()
                    # Determine format from extension
                    fmt = "json" if filename.endswith(".json") else "markdown"
                    result = export_transcript(self.messages, filename, format=fmt)
                    if result["success"]:
                        self.console.print(f"[success]{result['message']}[/success]")
                    else:
                        self.console.print(f"[error]{result['error']}[/error]")
                    continue
                if cmd == "/doctor":
                    self.show_doctor()
                    continue
                if cmd == "/plan":
                    self.show_plan()
                    continue
                if cmd == "/plan clear":
                    if self.state_mgr.clear_plan():
                        self.console.print("[success]Task plan cleared.[/success]")
                    else:
                        self.console.print("[dim]No task plan to clear.[/dim]")
                    continue
                if cmd == "/help":
                    self.show_help()
                    continue
                if cmd == "/tokens":
                    self.show_tokens()
                    continue
                if cmd == "/status":
                    self.show_git_status()
                    continue
                if cmd == "/diff":
                    self.show_git_diff()
                    continue
                if cmd == "/diff --staged" or cmd == "/diff -s":
                    self.show_git_diff(staged=True)
                    continue
                if cmd == "/log":
                    self.show_git_log()
                    continue
                if cmd == "/save":
                    self.do_save_session()
                    continue
                if cmd.startswith("/save "):
                    filename = user_input[6:].strip()
                    if not filename.endswith(".json"):
                        filename += ".json"
                    self.do_save_session(filename)
                    continue
                if cmd.startswith("/load "):
                    filepath = user_input[6:].strip()
                    self.do_load_session(filepath)
                    continue
                if cmd == "/sessions":
                    self.do_list_sessions()
                    continue
                if cmd == "/init":
                    result = generate_grok_md()
                    if result["success"]:
                        self.console.print(f"[success]{result['message']}[/success]")
                    else:
                        self.console.print(f"[error]{result['error']}[/error]")
                    continue
                if cmd == "/review":
                    diff_result = git_diff()
                    if diff_result["success"] and diff_result.get("output"):
                        result = review_diff(diff_result["output"])
                        if result["success"]:
                            analysis = result["analysis"]
                            self.console.print("\n[bold]Code Review Summary[/bold]")
                            self.console.print(f"  Files changed: {analysis['files_changed']}")
                            self.console.print(f"  Lines: +{analysis['lines_added']}/-{analysis['lines_removed']}")
                            if analysis['files']:
                                self.console.print(f"  Files: {', '.join(analysis['files'][:5])}")
                            self.console.print()
                    else:
                        self.console.print("[dim]No changes to review[/dim]")
                    continue
                if cmd == "/todos":
                    result = extract_todos()
                    if result["success"]:
                        if result["todos"]:
                            self.console.print(f"\n[bold]Found {result['count']} TODOs:[/bold]")
                            for todo in result["todos"][:20]:
                                self.console.print(f"  {todo['file']}:{todo['line']}: {todo['content'][:60]}")
                            if result["count"] > 20:
                                self.console.print(f"  ... and {result['count'] - 20} more")
                        else:
                            self.console.print("[dim]No TODOs found[/dim]")
                    self.console.print()
                    continue
                if cmd == "/resume":
                    sessions = get_sessions_for_picker()
                    if sessions:
                        self.console.print("\n[bold]Available Sessions:[/bold]")
                        for i, session in enumerate(sessions[:10], 1):
                            self.console.print(f"  {i}. {session['date']} - {session['preview']}")
                        self.console.print("\nUse /load <filename> to load a session")
                    else:
                        self.console.print("[dim]No saved sessions found[/dim]")
                    self.console.print()
                    continue
                if cmd == "/branch":
                    result = git_branch()
                    if result["success"]:
                        self.console.print(result.get("output", result.get("message", "")))
                    else:
                        self.console.print(f"[error]{result['error']}[/error]")
                    continue
                if cmd.startswith("/theme"):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        self.console.print(f"Current theme: {get_current_theme()}")
                        self.console.print(f"Available: {', '.join(THEMES.keys())}")
                    else:
                        result = set_theme(parts[1].strip())
                        if result["success"]:
                            self.console.print(f"[success]{result['message']}[/success]")
                        else:
                            self.console.print(f"[error]{result['error']}[/error]")
                    continue
                if cmd == "/vim":
                    result = toggle_vim_mode()
                    self.console.print(f"[success]{result['message']}[/success]")
                    continue
                if cmd == "/config":
                    result = show_config_tui(self.console)
                    if result["success"]:
                        self.console.print(f"[success]{result['message']}[/success]")
                    else:
                        self.console.print(f"[error]{result.get('error', 'Config failed')}[/error]")
                    continue
                if cmd == "/update":
                    result = check_for_updates()
                    self.console.print(f"Current: {result['current_version']}")
                    if result.get("latest_version"):
                        self.console.print(f"Latest:  {result['latest_version']}")
                    if result.get("update_available"):
                        self.console.print(f"\n[warning]{result['message']}[/warning]")
                        if Confirm.ask("Update now?"):
                            update_result = do_update()
                            if update_result["success"]:
                                self.console.print(f"[success]{update_result['message']}[/success]")
                            else:
                                self.console.print(f"[error]{update_result['error']}[/error]")
                    else:
                        self.console.print(f"[success]{result['message']}[/success]")
                    continue
                if cmd in ("/exit", "/quit", "/q"):
                    self.show_tokens()
                    self.console.print("[dim]Goodbye![/dim]")
                    break

                # Reset loop detection for new user input
                self._reset_loop_state()

                # Add user message
                self.messages.append({"role": "user", "content": user_input})

                # Agentic loop with streaming
                should_continue = self.process_streaming_response()
                while should_continue:
                    should_continue = self.process_streaming_response()

            except KeyboardInterrupt:
                self.console.print("\n[warning]Interrupted[/warning]")
                continue
            except EOFError:
                self.show_tokens()
                self.console.print("\n[dim]Goodbye![/dim]")
                break


# ==============================================================================
# MAIN
# ==============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Grok Code: An agentic CLI coding assistant powered by xAI's Grok API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  grok-code                              Start interactive session
  grok-code "fix the bug in main.py"       Run with prompt (shorthand)
  grok-code -p "fix the bug in main.py"    Run with prompt (explicit)
  grok-code -c                             Continue last session
  grok-code -r session_123.json            Resume specific session
  grok-code --dangerously-skip-permissions  Skip all tool confirmations
"""
    )
    parser.add_argument(
        "prompt_positional",
        nargs="?",
        default=None,
        metavar="PROMPT",
        help="Prompt to send (shorthand for -p)"
    )
    parser.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        help="Skip all permission prompts for dangerous tools (use with caution!)"
    )
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        dest="prompt_flag",
        help="Initial prompt to send (runs non-interactively if provided)"
    )
    parser.add_argument(
        "-c", "--continue",
        action="store_true",
        dest="continue_session",
        help="Continue the most recent session"
    )
    parser.add_argument(
        "-r", "--resume",
        type=str,
        default=None,
        help="Resume a specific session file"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Maximum number of agent turns (default: unlimited)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    parser.add_argument(
        "--verbose", "--debug",
        action="store_true",
        dest="verbose",
        default=False,
        help="Enable verbose/debug output"
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format for non-interactive mode (default: text)"
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        default=None,
        help="Override the system prompt"
    )
    parser.add_argument(
        "--append-system-prompt",
        type=str,
        default=None,
        dest="append_system_prompt",
        help="Append additional context to the system prompt"
    )
    parser.add_argument(
        "--allowedTools",
        type=str,
        default=None,
        dest="allowed_tools",
        help="Comma-separated list of allowed tools (whitelist)"
    )
    parser.add_argument(
        "--disallowedTools",
        type=str,
        default=None,
        dest="disallowed_tools",
        help="Comma-separated list of disallowed tools (blacklist)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Grok Code v{VERSION}"
    )
    args = parser.parse_args()

    # Merge positional and flag prompt (flag takes precedence)
    args.prompt = args.prompt_flag if args.prompt_flag else args.prompt_positional

    return args


def handle_update_command():
    """Handle 'grokcode update' subcommand."""
    console = Console(theme=CUSTOM_THEME)
    console.print("\n[bold]Checking for updates...[/bold]")

    result = check_for_updates()
    console.print(f"Current version: {result['current_version']}")

    if result.get("latest_version"):
        console.print(f"Latest version:  {result['latest_version']}")

    if result.get("update_available"):
        console.print(f"\n[warning]{result['message']}[/warning]")
        if Confirm.ask("Update now?"):
            console.print("[dim]Updating...[/dim]")
            update_result = do_update()
            if update_result["success"]:
                console.print(f"[success]{update_result['message']}[/success]")
            else:
                console.print(f"[error]{update_result['error']}[/error]")
                sys.exit(1)
    else:
        console.print(f"[success]{result['message']}[/success]")


def handle_login_command():
    """Handle 'grokcode login' subcommand."""
    from prompt_toolkit import prompt as pt_prompt
    console = Console(theme=CUSTOM_THEME)

    console.print("\n[bold]Store xAI API Key[/bold]")
    console.print("[dim]Your API key will be stored securely in your system keychain.[/dim]\n")

    # Check if key already exists
    existing_key = get_api_key_from_keyring()
    if existing_key:
        console.print("[warning]An API key is already stored.[/warning]")
        if not Confirm.ask("Replace it?"):
            console.print("[dim]Cancelled.[/dim]")
            return

    try:
        api_key = pt_prompt("Enter your xAI API key: ", is_password=True)
        if not api_key or not api_key.strip():
            console.print("[error]No API key provided.[/error]")
            sys.exit(1)

        result = set_api_key_in_keyring(api_key.strip())
        if result["success"]:
            console.print(f"[success]{result['message']}[/success]")
        else:
            console.print(f"[error]{result['error']}[/error]")
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled.[/dim]")


def handle_logout_command():
    """Handle 'grokcode logout' subcommand."""
    console = Console(theme=CUSTOM_THEME)

    existing_key = get_api_key_from_keyring()
    if not existing_key:
        console.print("[dim]No stored API key found.[/dim]")
        return

    if Confirm.ask("Remove stored API key?"):
        result = delete_api_key_from_keyring()
        if result["success"]:
            console.print(f"[success]{result['message']}[/success]")
        else:
            console.print(f"[error]{result['error']}[/error]")
    else:
        console.print("[dim]Cancelled.[/dim]")


def main():
    """Entry point."""
    # Handle subcommands before argparse
    if len(sys.argv) > 1:
        subcommand = sys.argv[1]
        if subcommand == "update":
            handle_update_command()
            return
        elif subcommand == "login":
            handle_login_command()
            return
        elif subcommand == "logout":
            handle_logout_command()
            return

    args = parse_args()

    # Handle --list-models
    if args.list_models:
        console = Console(theme=CUSTOM_THEME)
        console.print("\n[bold]Available Models:[/bold]\n")
        for model_id, description in AVAILABLE_MODELS.items():
            marker = " [green](default)[/green]" if model_id == DEFAULT_MODEL else ""
            console.print(f"  [cyan]{model_id}[/cyan]{marker}")
            console.print(f"    {description}\n")
        return

    try:
        agent = GrokCode(
            skip_permissions=args.dangerously_skip_permissions,
            model=args.model
        )

        # Handle -c (continue last session)
        if args.continue_session:
            latest = get_latest_session()
            if latest:
                agent.do_load_session(latest)
                agent.console.print(f"[dim]Continuing from {Path(latest).name}[/dim]")
            else:
                agent.console.print("[warning]No previous session found.[/warning]")

        # Handle -r (resume specific session)
        if args.resume:
            agent.do_load_session(args.resume)

        # Handle stdin piping
        if args.prompt == "-":
            stdin_content = read_stdin_if_pipe()
            if stdin_content:
                args.prompt = stdin_content.strip()
            else:
                args.prompt = None

        if args.prompt:
            # Non-interactive mode with initial prompt (streaming)
            agent.print_welcome()
            agent.console.print(f"\n[prompt]>[/prompt] {args.prompt}")
            agent.messages.append({"role": "user", "content": args.prompt})

            # Use streaming for non-interactive mode too
            should_continue = agent.process_streaming_response()
            while should_continue:
                should_continue = agent.process_streaming_response()

            # Show token usage
            agent.show_tokens()
        else:
            # Interactive mode
            agent.run()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[warning]Interrupted[/warning]")
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Fatal error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
