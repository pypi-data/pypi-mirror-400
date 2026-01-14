# MuukTest Repair MCP

MCP server for analyzing and repairing E2E test failures (Playwright, Cypress, Selenium, etc).

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)

## Configuration

### VS Code / GitHub Copilot

Open User MCP Configuration (`Cmd+Shift+P` → "MCP: Open User Configuration"):

```json
{
  "inputs": [
    {
      "id": "muuk_key",
      "type": "promptString",
      "description": "Muuk Key available at MuukTest account",
      "password": true
    }
  ],
  "servers": {
    "muuk-test-repair": {
      "command": "uvx",
      "args": ["muuk-test-repair-mcp"],
      "env": {
        "MUUK_KEY": "${input:muuk_key}",
      }
    }
  }
}
```

### Claude Desktop

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "muuk-test-repair": {
      "command": "uvx",
      "args": ["muuk-test-repair-mcp"],
      "env": {
        "MUUK_KEY": "your-api-key",
      }
    }
  }
}
```

## Usage

Ask your AI agent:

```
Analyze the test failure in my project.
The test file is in ./test-files/ and failure data is in ./failure-data/
```

## Required Parameters

| Parameter | Description |
|-----------|-------------|
| `workspace_path` | Absolute path to project root (agent provides this automatically) |
| `test_file_path` | Path to test file or directory |
| `failure_info_path` | Path to failure info JSON |
| `dom_elements_path` | Path to DOM elements JSON |
| `screenshot_path` | Path to failure screenshot |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MUUK_KEY` | Your MuukTest key |

## Available AI Presets

- `claude` (default)
- `openai`
- `gemini`

## Troubleshooting

### "The command uvx needed to run muuk-test-repair was not found"

VS Code can't find `uvx` in the PATH. Run in terminal:

```bash
which uvx
```

Then add the path to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export PATH="$PATH:/path/from/which/uvx"
```

Restart VS Code after making changes.
