# DeepSeeker

AI-powered CLI agent with HITL guardrails for code assistance and automation.

<p align="center">
  <img src="https://raw.githubusercontent.com/ErosolarAI/deepseeker/main/assets/mq9_reaper_nsa_style.png" alt="DeepSeeker - MQ-9 Reaper HITL Model" width="600"/>
</p>

[![PyPI version](https://badge.fury.io/py/deepseeker.svg)](https://badge.fury.io/py/deepseeker)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multi-Provider Support**: DeepSeek, OpenAI, Anthropic
- **Tool Use**: Bash, Read, Write, Edit, Glob, Grep
- **HITL Guardrails**: MQ-9 Reaper model for operation safety
- **Streaming Responses**: Real-time output with tool execution display
- **Interactive Shell**: Slash commands, history, auto-completion

## Installation

```bash
pip install deepseeker
```

## Quick Start

```bash
# Interactive mode
deepseekpy

# Quick query
deepseekpy -q "explain this code"

# Set API key
deepseekpy --key YOUR_DEEPSEEK_API_KEY
```

## API Key Setup

On first launch, you'll be prompted to enter your API key:

```
No DEEPSEEK API key found
Get your key from: https://platform.deepseek.com/api-keys
Enter DEEPSEEK_API_KEY: sk-...
```

Keys are stored securely in `~/.agi/secrets.json` (mode 0600).

## HITL Guardrails (MQ-9 Reaper Model)

Operations are classified by risk level:

| Level | Approval | Examples |
|-------|----------|----------|
| ROUTINE | Auto-approved | `ls`, `git status`, file reads |
| ELEVATED | Logged | File writes, git operations |
| CRITICAL | 1 confirmation | `sudo` operations, system changes |
| LETHAL | 2 confirmations + 5s delay | `rm -rf /`, disk writes |

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/model [provider]` | Switch AI provider |
| `/tools` | List available tools |
| `/guardrails` | Show guardrails status |
| `/secrets` | Manage API keys |
| `/exit` | Exit |

## Tools

- **Bash**: Execute shell commands
- **Read**: Read files with line numbers
- **Write**: Create/overwrite files
- **Edit**: Precise text replacement
- **Glob**: Find files by pattern
- **Grep**: Search file contents

## API Error Handling

DeepSeeker detects and handles API errors:

- **Invalid Key**: Prompts for new key
- **Rate Limited**: Shows wait message
- **Frozen Account**: Displays support info
- **Quota Exceeded**: Shows billing link

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Bo Shang <bo@shang.software>
