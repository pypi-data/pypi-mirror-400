#!/usr/bin/env python3
"""CLI commands for mcp-server-nucleus."""

import os
import json
import sys
import argparse
from pathlib import Path

# ============================================================================
# TEMPLATE: DEFAULT (Full structure)
# ============================================================================
DEFAULT_STATE = {
    "version": "1.0.0",
    "current_sprint": {
        "name": "Sprint 1",
        "focus": "Getting Started with Nucleus",
        "started_at": None
    },
    "top_3_leverage_actions": [
        "Set up your first agent",
        "Configure triggers",
        "Connect to Claude Desktop"
    ]
}

DEFAULT_TRIGGERS = {
    "version": "1.0.0",
    "triggers": [
        {
            "event_type": "task_completed",
            "target_agent": "synthesizer",
            "emitter_filter": None
        },
        {
            "event_type": "research_done",
            "target_agent": "architect",
            "emitter_filter": ["researcher"]
        }
    ]
}

SAMPLE_AGENT = '''# {agent_name} Agent

## Role
Define what this agent does.

## Responsibilities
- Task 1
- Task 2

## Triggers
Activated when: [define trigger conditions]

## Output Format
Describe expected output format.
'''

# ============================================================================
# ONBOARDING: Instructional Seed Tasks
# ============================================================================
import time

def get_default_tasks():
    """Generate instructional seed tasks with current timestamps."""
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    return [
        {
            "id": "onboard-1",
            "description": "Welcome! Ask your AI: 'What is my current focus?'",
            "status": "READY",
            "priority": 1,
            "blocked_by": [],
            "required_skills": [],
            "claimed_by": None,
            "source": "nucleus-init",
            "escalation_reason": None,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "onboard-2",
            "description": "Try: 'Show me all tasks' to see your task queue",
            "status": "PENDING",
            "priority": 2,
            "blocked_by": ["onboard-1"],
            "required_skills": [],
            "claimed_by": None,
            "source": "nucleus-init",
            "escalation_reason": None,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "onboard-3",
            "description": "Create your first real task: 'Add a task: [your task here]'",
            "status": "PENDING",
            "priority": 3,
            "blocked_by": ["onboard-2"],
            "required_skills": [],
            "claimed_by": None,
            "source": "nucleus-init",
            "escalation_reason": None,
            "created_at": now,
            "updated_at": now
        }
    ]

BRAIN_README = '''# 🧠 Nuclear Brain

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
'''

# ============================================================================
# TEMPLATE: SOLO (Minimal structure for solo founders)
# ============================================================================
SOLO_STATE = {
    "version": "1.0.0",
    "mode": "solo",
    "current_focus": "Getting started with Nucleus",
    "tasks": []
}

SOLO_THREAD_REGISTRY = '''# Thread Registry

> **Protocol:** Agents check this file on activation to know their role.
> **Stable Anchor:** Thread ID (UUID) never changes, even when IDE renames the thread.

---

## Active Threads

| Thread ID | Role | Focus |
|:----------|:-----|:------|
| *(Add your threads here)* | | |

---

## How to Use

1. **Find your thread ID** in your IDE's artifact path (e.g., `.gemini/antigravity/brain/<thread-id>/`)
2. **Add a row** to the table above with your role
3. **Agent self-identifies** on next activation by reading this registry

---

## Example

| Thread ID | Role | Focus |
|:----------|:-----|:------|
| `7c654df4-b83e-...` | Lead Systems Architect | Infrastructure, MCP |
| `853a0b7e-9052-...` | Synthesizer | Product work, orchestration |
'''

SOLO_CONTEXT = '''# Project Context

> This file provides context to all AI agents working on your project.

## Company/Project
- **Name:** [Your Project Name]
- **Description:** [What you're building]

## Technical Stack
- **Backend:** 
- **Frontend:** 
- **Database:** 

## Current Priorities
1. 
2. 
3. 
'''


def init_brain_default(brain_path: Path) -> bool:
    """Initialize with default (full) template."""
    dirs = [
        brain_path / "ledger",
        brain_path / "artifacts" / "research",
        brain_path / "artifacts" / "strategy",
        brain_path / "agents",
        brain_path / "memory",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  📁 Created {d}")
    
    (brain_path / "ledger" / "state.json").write_text(
        json.dumps(DEFAULT_STATE, indent=2)
    )
    print(f"  📄 Created ledger/state.json")
    
    (brain_path / "ledger" / "triggers.json").write_text(
        json.dumps(DEFAULT_TRIGGERS, indent=2)
    )
    print(f"  📄 Created ledger/triggers.json")
    
    (brain_path / "ledger" / "events.jsonl").write_text("")
    print(f"  📄 Created ledger/events.jsonl")
    
    # Seed instructional tasks
    (brain_path / "ledger" / "tasks.json").write_text(
        json.dumps(get_default_tasks(), indent=2)
    )
    print(f"  ✅ Created ledger/tasks.json (3 onboarding tasks)")
    
    # In-brain README
    (brain_path / "README.md").write_text(BRAIN_README)
    print(f"  📖 Created README.md")
    
    (brain_path / "agents" / "synthesizer.md").write_text(
        SAMPLE_AGENT.format(agent_name="Synthesizer")
    )
    print(f"  🤖 Created agents/synthesizer.md")
    
    (brain_path / "memory" / "context.md").write_text(
        "# Project Context\n\nDescribe your project here.\n"
    )
    print(f"  📝 Created memory/context.md")
    
    return True


def init_brain_solo(brain_path: Path) -> bool:
    """Initialize with solo (minimal) template."""
    dirs = [
        brain_path / "ledger",
        brain_path / "meta",
        brain_path / "memory",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  📁 Created {d}")
    
    (brain_path / "ledger" / "state.json").write_text(
        json.dumps(SOLO_STATE, indent=2)
    )
    print(f"  📄 Created ledger/state.json (solo mode)")
    
    (brain_path / "meta" / "thread_registry.md").write_text(SOLO_THREAD_REGISTRY)
    print(f"  📋 Created meta/thread_registry.md")
    
    (brain_path / "memory" / "context.md").write_text(SOLO_CONTEXT)
    print(f"  📝 Created memory/context.md")
    
    # Seed instructional tasks
    (brain_path / "ledger" / "tasks.json").write_text(
        json.dumps(get_default_tasks(), indent=2)
    )
    print(f"  ✅ Created ledger/tasks.json (3 onboarding tasks)")
    
    # In-brain README
    (brain_path / "README.md").write_text(BRAIN_README)
    print(f"  📖 Created README.md")
    
    return True

import shutil
from datetime import datetime


def init_brain(path: str = ".brain", template: str = "default"):
    """Initialize a new .brain directory structure."""
    brain_path = Path(path)
    
    if brain_path.exists():
        # Count files to detect active brain
        file_count = len(list(brain_path.rglob("*")))
        
        if file_count > 10:
            # This looks like an active brain - extra protection
            print(f"⚠️  {path}/ contains {file_count} files!")
            print(f"   This looks like an ACTIVE brain with real content.")
            print(f"   Overwriting is NOT recommended.")
            print()
            response = input("Type 'BACKUP-AND-OVERWRITE' to confirm (or anything else to abort): ")
            if response != 'BACKUP-AND-OVERWRITE':
                print("✅ Aborted. Your brain is safe.")
                return False
        else:
            print(f"⚠️  Directory {path} already exists.")
            response = input("Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return False
        
        # ALWAYS backup before overwrite
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(f"{path}.backup.{timestamp}")
        print(f"📦 Creating backup at {backup_path}...")
        shutil.copytree(brain_path, backup_path)
        print(f"   ✅ Backup complete ({file_count} items saved)")
        
        # Now safe to remove old brain
        shutil.rmtree(brain_path)
    
    print(f"🧠 Initializing Nuclear Brain at {path}/ (template: {template})...")
    
    # Route to template-specific init
    if template == "solo":
        init_brain_solo(brain_path)
    else:
        init_brain_default(brain_path)
    
    print(f"\n✅ Nuclear Brain initialized!")
    
    # Generate config and auto-configure
    abs_path = str(brain_path.absolute())
    nucleus_config = {
        "command": "python3",
        "args": ["-m", "mcp_server_nucleus"],
        "env": {"NUCLEAR_BRAIN_PATH": abs_path}
    }
    
    # Attempt auto-configuration for Claude Desktop
    claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    auto_configured = False
    
    if claude_config_path.exists():
        try:
            print(f"\n🔍 Found Claude Desktop config...")
            backup_path = claude_config_path.with_suffix(".json.bak")
            if not backup_path.exists():
                import shutil
                shutil.copy2(claude_config_path, backup_path)
                print(f"  📦 Created backup at {backup_path}")
            
            with open(claude_config_path, 'r') as f:
                config_data = json.load(f)
            
            if "mcpServers" not in config_data:
                config_data["mcpServers"] = {}
            
            if "nucleus" not in config_data["mcpServers"]:
                config_data["mcpServers"]["nucleus"] = nucleus_config
                
                with open(claude_config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                print(f"  ✅ Auto-configured 'nucleus' in Claude Desktop settings!")
                auto_configured = True
            else:
                print(f"  ℹ️  'nucleus' already configured in Claude Desktop.")
                auto_configured = True
                
        except Exception as e:
            print(f"  ⚠️  Could not auto-configure: {e}")

    if not auto_configured:
        config_snippet = f'''"nucleus": {{
    "command": "python3",
    "args": ["-m", "mcp_server_nucleus"],
    "env": {{
      "NUCLEAR_BRAIN_PATH": "{abs_path}"
    }}
  }}'''
        
        print(f"\n" + "="*60)
        print(f"📋 COPY THIS into your AI client's config:")
        print(f"="*60)
        print()
        print(config_snippet)
        print()
        print(f"="*60)
        print(f"\n📍 Config file locations:")
        print(f"   Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json")
        print(f"   Cursor:         ~/.cursor/mcp.json") 
        print(f"   Windsurf:       ~/.codeium/windsurf/mcp_config.json")
    
    print(f"\n" + "="*60)
    print(f"🚀 NEXT STEPS")
    print(f"="*60)
    print(f"\n1. Restart your AI Client (Claude Desktop, Cursor, etc.)")
    print(f"2. Try these prompts:")
    print(f"   • \"What is my current focus?\"")
    print(f"   • \"Show me all tasks\"")
    print(f"   • \"Add a task: Build landing page\"")
    print(f"\n📚 Docs: https://github.com/LKGargProjects/mcp-server-nucleus")
    
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='nucleus',
        description='Nucleus Brain CLI - Manage your AI coordination system'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ============================================================
    # INIT COMMAND
    # ============================================================
    init_parser = subparsers.add_parser('init', help='Initialize a new .brain directory')
    init_parser.add_argument(
        'path',
        nargs='?',
        default='.brain',
        help='Path to create .brain directory (default: .brain)'
    )
    init_parser.add_argument(
        '-t', '--template',
        choices=['default', 'solo'],
        default='default',
        help='Template to use: default (full) or solo (minimal)'
    )
    
    # ============================================================
    # DEPTH COMMANDS (ADHD Accommodation)
    # ============================================================
    depth_parser = subparsers.add_parser('depth', help='Track conversation depth (ADHD guardrail)')
    depth_subparsers = depth_parser.add_subparsers(dest='depth_action', help='Depth actions')
    
    # nucleus depth show
    depth_show = depth_subparsers.add_parser('show', help='Show current depth indicator')
    
    # nucleus depth up [--to=N]
    depth_up = depth_subparsers.add_parser('up', help='Come back up one level')
    depth_up.add_argument('--to', type=int, help='Go up to specific level (optional)')
    
    # nucleus depth reset
    depth_reset = depth_subparsers.add_parser('reset', help='Reset to root level')
    
    # nucleus depth max N
    depth_max = depth_subparsers.add_parser('max', help='Set max safe depth')
    depth_max.add_argument('level', type=int, help='Max safe depth (1-10)')
    
    # nucleus depth push TOPIC
    depth_push = depth_subparsers.add_parser('push', help='Go deeper into a topic')
    depth_push.add_argument('topic', help='Topic you are diving into')
    
    # nucleus depth map
    depth_map = depth_subparsers.add_parser('map', help='Show visual exploration map')
    
    # ============================================================
    # FEATURES COMMANDS (Feature Map)
    # ============================================================
    features_parser = subparsers.add_parser('features', help='Manage product feature map')
    features_subparsers = features_parser.add_subparsers(dest='features_action', help='Feature actions')
    
    # nucleus features list [--product=X] [--status=X]
    features_list = features_subparsers.add_parser('list', help='List all features')
    features_list.add_argument('--product', help='Filter by product (gentlequest/nucleus)')
    features_list.add_argument('--status', help='Filter by status')
    
    # nucleus features test <id>
    features_test = features_subparsers.add_parser('test', help='Show test instructions for a feature')
    features_test.add_argument('id', help='Feature ID to get test instructions for')
    
    # nucleus features search <query>
    features_search = features_subparsers.add_parser('search', help='Search features')
    features_search.add_argument('query', help='Search query')
    
    # nucleus features proof <id>
    features_proof = features_subparsers.add_parser('proof', help='Show proof document for a feature')
    features_proof.add_argument('id', help='Feature ID to show proof for')
    
    # nucleus sessions - Session management commands
    sessions_parser = subparsers.add_parser('sessions', help='Session management commands')
    sessions_subparsers = sessions_parser.add_subparsers(dest='sessions_action')
    
    # nucleus sessions list
    sessions_list = sessions_subparsers.add_parser('list', help='List all saved sessions')
    
    # nucleus sessions save <context>
    sessions_save = sessions_subparsers.add_parser('save', help='Save current session')
    sessions_save.add_argument('context', help='Context name (e.g., "Nucleus v0.5.0")')
    sessions_save.add_argument('--task', help='Current active task')
    
    # nucleus sessions resume [id]
    sessions_resume = sessions_subparsers.add_parser('resume', help='Resume a saved session')
    sessions_resume.add_argument('id', nargs='?', help='Session ID to resume (defaults to most recent)')
    
    # --- STATUS SUBCOMMAND (SATELLITE VIEW) ---
    status_parser = subparsers.add_parser('status', help='Show unified satellite view of the brain')
    status_parser.add_argument('--minimal', action='store_true', help='Show minimal view (depth only)')
    status_parser.add_argument('--sprint', action='store_true', help='Show sprint view (includes tasks)')
    status_parser.add_argument('--full', action='store_true', help='Show full view (includes session)')
    
    # --- CONSOLIDATE SUBCOMMAND ---
    consolidate_parser = subparsers.add_parser('consolidate', help='Brain consolidation and cleanup operations')
    consolidate_subparsers = consolidate_parser.add_subparsers(dest='consolidate_action', help='Consolidation commands')
    
    # nucleus consolidate archive
    consolidate_subparsers.add_parser('archive', help='Archive .resolved.* backup files to clean up brain folder')
    
    # nucleus consolidate propose
    consolidate_subparsers.add_parser('propose', help='Detect redundant artifacts and generate merge proposals')
    
    # nucleus consolidate status
    consolidate_subparsers.add_parser('status', help='Show consolidation status and archive info')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_brain(args.path, args.template)
    elif args.command == 'status':
        handle_status_command(args)
    elif args.command == 'depth':
        handle_depth_command(args)
    elif args.command == 'features':
        handle_features_command(args)
    elif args.command == 'sessions':
        handle_sessions_command(args)
    elif args.command == 'consolidate':
        handle_consolidate_command(args)
    elif args.command is None:
        # No command given, show help
        parser.print_help()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


def handle_depth_command(args):
    """Handle depth subcommands."""
    # Import the core functions from __init__
    try:
        from . import _depth_show, _depth_pop, _depth_reset, _depth_set_max, _depth_push, _generate_depth_map
    except ImportError:
        # Direct import for testing
        try:
            from mcp_server_nucleus import _depth_show, _depth_pop, _depth_reset, _depth_set_max, _depth_push, _generate_depth_map
        except ImportError:
            print("Error: Could not import depth functions. Make sure NUCLEAR_BRAIN_PATH is set.")
            return
    
    if args.depth_action == 'show' or args.depth_action is None:
        result = _depth_show()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print()
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ {result['indicator']:^59} ║")
        print(f"╟───────────────────────────────────────────────────────────╢")
        print(f"║ Status: {result['status']:<51} ║")
        print(f"╟───────────────────────────────────────────────────────────╢")
        if result['breadcrumbs']:
            print(f"║ Path: {result['breadcrumbs'][:53]:<53} ║")
        else:
            print(f"║ Path: (root level)                                       ║")
        print(f"╟───────────────────────────────────────────────────────────╢")
        print(f"║ Tree:                                                     ║")
        for line in result['tree'].split('\n')[:5]:  # Max 5 lines
            print(f"║   {line:<56} ║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        print()
        print(f"Commands: nucleus depth up | nucleus depth reset | nucleus depth push <topic>")
        
    elif args.depth_action == 'up':
        to_level = getattr(args, 'to', None)
        if to_level is not None:
            # Pop multiple times to reach target level
            result = _depth_show()
            current = result.get('current_depth', 0)
            pops_needed = current - to_level
            if pops_needed <= 0:
                print(f"Already at or below level {to_level}")
                return
            for _ in range(pops_needed):
                result = _depth_pop()
        else:
            result = _depth_pop()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(result.get('message', '✅ Popped up one level'))
        print(f"  {result['indicator']}")
        if result.get('breadcrumbs'):
            print(f"  Path: {result['breadcrumbs']}")
        
    elif args.depth_action == 'reset':
        result = _depth_reset()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        print(result['message'])
        print(f"  New session: {result['session_id']}")
        
    elif args.depth_action == 'max':
        result = _depth_set_max(args.level)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        print(f"✅ {result['message']}")
        print(f"  {result['indicator']}")
        
    elif args.depth_action == 'push':
        result = _depth_push(args.topic)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        print(f"📍 Diving into: {args.topic}")
        print(f"  {result['indicator']}")
        if result.get('warning'):
            print(f"  {result['warning']}")
        print(f"  Path: {result['breadcrumbs']}")
        
    elif args.depth_action == 'map':
        result = _generate_depth_map()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        print(f"🗺️  {result['message']}")
        print(f"  Path: {result.get('path', '(root)')}")
        print()
        print("─" * 50)
        print(result['mermaid'])
        print("─" * 50)
        print()
        print("💡 Copy the mermaid code block to visualize in any markdown viewer!")
        
    else:
        # Show depth help
        print("Usage: nucleus depth <action>")
        print()
        print("Actions:")
        print("  show    Show current depth indicator")
        print("  up      Come back up one level")
        print("  reset   Reset to root level")
        print("  max N   Set max safe depth")
        print("  push X  Go deeper into topic X")
        print("  map     Show visual exploration map")


def handle_features_command(args):
    """Handle features subcommands."""
    # Import feature functions from main module
    from . import _list_features, _get_feature, _search_features, _get_proof
    
    if args.features_action == 'list':
        result = _list_features(args.product, args.status, None)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        features = result.get("features", [])
        if not features:
            print("📋 No features found.")
            if args.product or args.status:
                print("   Try removing filters to see all features.")
            return
        
        # Group by product
        by_product = {}
        for f in features:
            prod = f.get("product", "unknown")
            by_product.setdefault(prod, []).append(f)
        
        print(f"\n📋 Features ({len(features)} total)")
        print("=" * 60)
        
        for product, prod_features in by_product.items():
            print(f"\n{product.upper()} ({len(prod_features)} features):")
            print("-" * 40)
            for f in prod_features:
                status_icon = {
                    "production": "✅",
                    "released": "✅",
                    "development": "🚧",
                    "staged": "🔄",
                    "broken": "❌",
                    "deprecated": "⚠️"
                }.get(f.get("status"), "❓")
                
                validated = f.get("validation_result")
                val_icon = "✅" if validated == "passed" else "❌" if validated == "failed" else "⏳"
                
                print(f"  {status_icon} {f.get('name'):<30} v{f.get('version'):<8} {val_icon}")
        
        print()
        
    elif args.features_action == 'test':
        result = _get_feature(args.id)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        f = result.get("feature", {})
        print(f"\n🧪 How to Test: {f.get('name')}")
        print("=" * 60)
        print(f"\n📝 Description: {f.get('description')}")
        print(f"📦 Product: {f.get('product')}")
        print(f"🏷️  Version: {f.get('version')}")
        print(f"📊 Status: {f.get('status')}")
        
        print(f"\n📋 Test Steps:")
        for i, step in enumerate(f.get("how_to_test", []), 1):
            print(f"   {i}. {step}")
        
        print(f"\n✅ Expected Result:")
        print(f"   {f.get('expected_result')}")
        
        if f.get("deployed_url"):
            print(f"\n🌐 URL: {f.get('deployed_url')}")
        
        validated = f.get("validation_result")
        last_val = f.get("last_validated")
        if validated:
            val_icon = "✅" if validated == "passed" else "❌"
            print(f"\n📅 Last Validated: {last_val} - {val_icon} {validated.upper()}")
        else:
            print(f"\n⏳ Not yet validated")
        
        print()
        
    elif args.features_action == 'search':
        result = _search_features(args.query)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        features = result.get("features", [])
        if not features:
            print(f"🔍 No features found matching '{args.query}'")
            return
        
        print(f"\n🔍 Search results for '{args.query}' ({len(features)} matches)")
        print("-" * 50)
        for f in features:
            print(f"  • {f.get('name')} ({f.get('product')}) - {f.get('description')[:50]}...")
        print()
        
    elif args.features_action == 'proof':
        result = _get_proof(args.id)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        if not result.get("exists"):
            print(f"📋 {result.get('message')}")
            print()
            print("💡 Generate a proof with:")
            print(f"   In Claude: brain_generate_proof(feature_id='{args.id}', thinking='...')")
            return
        
        print(result.get("content", ""))
        
    else:
        # Show features help
        print("Usage: nucleus features <action>")
        print()
        print("Actions:")
        print("  list              List all features")
        print("  list --product=X  Filter by product")
        print("  list --status=X   Filter by status")
        print("  test <id>         Show test instructions")
        print("  search <query>    Search features")
        print("  proof <id>        Show proof document")


def handle_sessions_command(args):
    """Handle sessions subcommands."""
    # Import session functions from main module
    from . import _list_sessions, _save_session, _resume_session
    
    if args.sessions_action == 'list':
        result = _list_sessions()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        sessions = result.get("sessions", [])
        active_id = result.get("active_session_id")
        
        if not sessions:
            print("📋 No saved sessions")
            print()
            print("💡 Save a session with:")
            print("   nucleus sessions save \"My Project Work\"")
            return
        
        print(f"\n📋 Saved Sessions ({len(sessions)} total)")
        print("=" * 60)
        
        for s in sessions:
            is_active = "→ " if s.get("id") == active_id else "  "
            print(f"{is_active}{s.get('context')}")
            print(f"    Task: {s.get('active_task')}")
            print(f"    Saved: {s.get('created_at')[:16] if s.get('created_at') else 'Unknown'}")
            print()
        
    elif args.sessions_action == 'save':
        task = getattr(args, 'task', None)
        result = _save_session(args.context, active_task=task)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"✅ Session saved!")
        print(f"   Context: {result.get('context')}")
        print(f"   ID: {result.get('session_id')}")
        print()
        print("💡 Resume later with:")
        print("   nucleus sessions resume")
        
    elif args.sessions_action == 'resume':
        session_id = getattr(args, 'id', None)
        result = _resume_session(session_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "hint" in result:
                print(f"💡 {result['hint']}")
            return
        
        print(result.get("summary", "Session resumed"))
        print()
        
    else:
        # Show sessions help
        print("Usage: nucleus sessions <action>")
        print()
        print("Actions:")
        print("  list              List all saved sessions")
        print("  save <context>    Save current session")
        print("  resume [id]       Resume a saved session")


def handle_consolidate_command(args):
    """Handle consolidate subcommands."""
    # Import the core functions from __init__
    try:
        from . import _archive_resolved_files, _get_archive_path
    except ImportError:
        try:
            from mcp_server_nucleus import _archive_resolved_files, _get_archive_path
        except ImportError:
            print("Error: Could not import consolidation functions. Make sure NUCLEAR_BRAIN_PATH is set.")
            return
    
    if args.consolidate_action == 'archive':
        print("🧹 Archiving resolved backup files...")
        print()
        
        result = _archive_resolved_files()
        
        if not result.get("success"):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        files_moved = result.get("files_moved", 0)
        archive_path = result.get("archive_path", "")
        
        if files_moved == 0:
            print("✅ No backup files to archive. Brain folder is already clean!")
            return
        
        print(f"✅ Archived {files_moved} files!")
        print(f"   Location: {archive_path}")
        print()
        print("📁 Moved files (sample):")
        for f in result.get("moved_files", [])[:5]:
            print(f"   • {f}")
        if files_moved > 5:
            print(f"   ... and {files_moved - 5} more")
        print()
        print("💡 To recover files, move them back from the archive folder.")
        
    elif args.consolidate_action == 'propose':
        try:
            from . import _generate_merge_proposals
        except ImportError:
            try:
                from mcp_server_nucleus import _generate_merge_proposals
            except ImportError:
                print("Error: Could not import proposal functions.")
                return
        
        print("🔍 Scanning brain for redundant artifacts...")
        print()
        
        result = _generate_merge_proposals()
        
        if not result.get("success"):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        total = result.get("total_proposals", 0)
        summary = result.get("summary", {})
        
        if total == 0:
            print("✅ Brain is clean! No consolidation proposals found.")
            return
        
        # Print summary table
        print(f"📋 Found {total} consolidation proposals:")
        print()
        print(f"   Versioned Duplicates: {summary.get('versioned_duplicates', 0)}")
        print(f"   Related Series:       {summary.get('related_series', 0)}")
        print(f"   Stale Files (30d):    {summary.get('stale_files', 0)}")
        print(f"   Archive Candidates:   {summary.get('archive_candidates', 0)}")
        print()
        
        # Print full proposal document
        print("─" * 60)
        print(result.get("proposal_text", ""))
        
    elif args.consolidate_action == 'status':
        try:
            archive_path = _get_archive_path()
            resolved_archive = archive_path / "resolved"
            
            if not resolved_archive.exists():
                print("📊 Consolidation Status")
                print()
                print("   Archive: Not yet created")
                print("   Run: nucleus consolidate archive")
                return
            
            # Count files in archive
            archived_count = len(list(resolved_archive.glob("*")))
            
            print("📊 Consolidation Status")
            print()
            print(f"   Archive path: {resolved_archive}")
            print(f"   Archived files: {archived_count}")
            print()
            print("💡 Run 'nucleus consolidate archive' to archive new backup files.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
    else:
        # Show consolidate help
        print("Usage: nucleus consolidate <action>")
        print()
        print("Actions:")
        print("  archive    Archive .resolved.* backup files (safe, reversible)")
        print("  status     Show consolidation status and archive info")


def handle_status_command(args):
    """Handle nucleus status command (Satellite View)."""
    from mcp_server_nucleus import (
        _get_satellite_view,
        _format_satellite_cli
    )
    
    # Determine detail level from flags
    if args.minimal:
        detail_level = "minimal"
    elif args.sprint:
        detail_level = "sprint"
    elif args.full:
        detail_level = "full"
    else:
        detail_level = "standard"
    
    try:
        view = _get_satellite_view(detail_level)
        output = _format_satellite_cli(view)
        print(output)
    except Exception as e:
        print(f"❌ Error getting satellite view: {e}")
        print()
        print("Make sure NUCLEAR_BRAIN_PATH is set correctly.")


if __name__ == "__main__":
    main()

