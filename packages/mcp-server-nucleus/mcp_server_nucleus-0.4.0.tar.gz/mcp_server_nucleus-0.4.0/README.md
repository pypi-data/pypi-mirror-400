# 🧠 Nucleus MCP Server

[![PyPI version](https://badge.fury.io/py/mcp-server-nucleus.svg)](https://badge.fury.io/py/mcp-server-nucleus)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The Core of Your AI Agents** — Multi-agent orchestration MCP server

`mcp-server-nucleus` connects your local "Nuclear Brain" agentic system with MCP-compatible clients like Claude Desktop, Cursor, and more.

## ✨ Features

- **16 MCP Tools** for agent orchestration
- **4 MCP Resources** for subscribable state
- **3 MCP Prompts** for pre-built orchestration
- **V2 Task Orchestration** — Priority queue, skill routing, dependency DAG
- **Local Intelligence** — Directly manipulates your `.brain/` directory
- **Event-Driven** — Emit and listen to system events
- **Zero-Knowledge Default** — Your data stays local

## 🚀 Quick Start

### Installation

> ⚠️ **Requires Python 3.10+** — If `pip3` fails, use `python3.11 -m pip` instead.

```bash
# Check your Python version first
python3 --version

# Install (use python3.11 if your default is older)
python3.11 -m pip install mcp-server-nucleus

# Verify installation
nucleus-init --help
```

**Common error:** `No matching distribution found` → Your Python is too old. Install Python 3.10+ via Homebrew: `brew install python@3.11`

### Initialize Your Brain (Smart Init!)

```bash
# Create a new .brain/ directory — auto-configures Claude Desktop!
nucleus-init

# For solo founders (minimal setup)
nucleus-init --template=solo
```

> **v0.2.2+**: Smart Init automatically detects Claude Desktop and adds the config for you!

### Configuration (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nucleus": {
      "command": "python3",
      "args": ["-m", "mcp_server_nucleus"],
      "env": {
        "NUCLEAR_BRAIN_PATH": "/path/to/your/.brain"
      }
    }
  }
}
```

Restart Claude Desktop and try: *"What's my current sprint focus?"*

### Configuration (Windsurf)

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "nucleus": {
      "command": "python3",
      "args": ["-m", "mcp_server_nucleus"],
      "env": {
        "NUCLEAR_BRAIN_PATH": "/path/to/your/.brain"
      }
    }
  }
}
```

### Configuration (Cursor)

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "nucleus": {
      "command": "python3",
      "args": ["-m", "mcp_server_nucleus"],
      "env": {
        "NUCLEAR_BRAIN_PATH": "/path/to/your/.brain"
      }
    }
  }
}
```

### ❓ Troubleshooting

**"Show me all tasks" returns nothing?**
Check your config pointer! You might be pointing to an old or temp brain.

1. **Check config:** Open `~/Library/Application Support/Claude/claude_desktop_config.json`
2. **Verify path:** Ensure `NUCLEAR_BRAIN_PATH` points to your active project (e.g., `/Users/me/my-project/.brain`)
3. **Restart:** You MUST restart Claude Desktop after any config change.

## 🛠 Available Tools

### Core Tools

| Tool | Description |
|------|-------------|
| `brain_emit_event` | Emit a new event to the ledger |
| `brain_read_events` | Read recent events |
| `brain_get_state` | Get current brain state |
| `brain_update_state` | Update brain state |
| `brain_read_artifact` | Read an artifact file |
| `brain_write_artifact` | Write to an artifact file |
| `brain_list_artifacts` | List all artifacts |
| `brain_trigger_agent` | Trigger an agent with a task |
| `brain_get_triggers` | Get all neural triggers |
| `brain_evaluate_triggers` | Evaluate trigger activation |

### V2 Task Orchestration (New in v0.3.0)

| Tool | Description |
|------|-------------|
| `brain_list_tasks` | Query tasks with filters (status, priority, skill, claimed_by) |
| `brain_get_next_task` | Get highest-priority unblocked task matching your skills |
| `brain_claim_task` | Atomically claim a task (prevents race conditions) |
| `brain_update_task` | Update task fields (status, priority, etc.) |
| `brain_add_task` | Create a new task with full V2 schema |
| `brain_escalate` | Request human help when stuck |

**V2 Task Schema (11 fields):**
```json
{
  "id": "task-abc123",
  "description": "Build landing page",
  "status": "PENDING | READY | IN_PROGRESS | BLOCKED | DONE | FAILED | ESCALATED",
  "priority": 1,
  "blocked_by": ["task-prerequisite"],
  "required_skills": ["python", "frontend"],
  "claimed_by": "agent-thread-id",
  "source": "user | synthesizer",
  "escalation_reason": null,
  "created_at": "2026-01-03T12:00:00",
  "updated_at": "2026-01-03T12:00:00"
}
```

## 📡 MCP Resources

| Resource | Description |
|----------|-------------|
| `brain://state` | Live state.json content |
| `brain://events` | Recent events stream |
| `brain://triggers` | Trigger definitions |
| `brain://context` | **Full context for cold start** — click in sidebar for instant context |

## 💬 MCP Prompts

| Prompt | Description |
|--------|-------------|
| `cold_start` | **Get instant context** — sprint, events, artifacts, workflows |
| `activate_synthesizer` | Orchestrate current sprint |
| `start_sprint` | Initialize a new sprint |

## 🎯 Common Use Cases

### 1. Run a Sprint
```
> "What's my current sprint focus?"
> "Add a task: Build landing page with priority 1"
> "Show me all priority 1 tasks"
```

### 2. Coordinate Multiple Agents
```
> "Claim the next Python task for me"
> "Mark task-abc123 as DONE"
> "List all tasks claimed by agent-1"
```

### 3. Escalate When Stuck
```
> "Escalate task-xyz with reason: Need human approval on pricing"
```
The task is released and flagged for human intervention.

### 4. Check Agent Context
```
> "Use the cold_start prompt from nucleus"
```
Instantly loads sprint, events, and artifacts.

## 🚀 Cold Start (New in v0.2.4)

Start every new session with full context:

```
> Use the cold_start prompt from nucleus
```

Or click `brain://context` in Claude Desktop's sidebar.

**What you get:**
- Current sprint name, focus, and status
- Recent events and artifacts
- Workflow detection (e.g., `lead_agent_model.md`)
- Lead Agent role assignment

## 📁 Expected `.brain/` Structure

```
.brain/
├── ledger/
│   ├── events.jsonl
│   ├── state.json
│   └── triggers.json
├── artifacts/
│   ├── research/
│   ├── strategy/
│   └── ...
└── agents/
    └── *.md
```

## ⚠️ Known Limitations

- **IDE context is separate**: Each MCP client (Claude Desktop, Cursor, Windsurf) connects to the same `.brain/` directory and shares project state. However, IDE-specific context (Cursor's codebase memory, Antigravity's conversation artifacts, etc.) remains separate per editor.
- **No cross-editor sync**: Artifacts created in one IDE's conversation don't automatically sync to another. Manual copy is required for important documents.
- **Python 3.10+ required**: Won't work with older Python versions.

## 📜 License

MIT © Nucleus Team

