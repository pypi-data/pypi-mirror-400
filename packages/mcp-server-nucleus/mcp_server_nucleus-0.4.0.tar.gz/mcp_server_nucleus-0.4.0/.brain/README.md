# 🧠 Nuclear Brain

This folder is managed by [Nucleus MCP Server](https://github.com/LKGargProjects/mcp-server-nucleus).

## Structure

```
.brain/
├── ledger/          # System state and task queue
│   ├── state.json   # Current sprint/focus
│   ├── tasks.json   # V2 task orchestration
│   └── events.jsonl # Event log
├── memory/          # Persistent context
│   └── context.md   # Project context for agents
└── agents/          # Agent definitions (optional)
```

## Quick Commands

In Claude Desktop (or your MCP client), try:

- "What is my current focus?"
- "Show me all tasks"
- "Add a task: Build landing page"
- "Claim the next task for me"

## Learn More

- [GitHub](https://github.com/LKGargProjects/mcp-server-nucleus)
- [PyPI](https://pypi.org/project/mcp-server-nucleus/)
