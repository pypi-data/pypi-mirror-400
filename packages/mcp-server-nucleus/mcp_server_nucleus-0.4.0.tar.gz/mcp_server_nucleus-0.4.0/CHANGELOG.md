# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-01-08

### Added
- **Nucleus Agent Runtime (NAR)**: Ephemeral execution environment for autonomous agents
  - Spawns disposable agents based on intent
  - `ContextFactory` dynamically constructs relevant context
  - `brain_spawn_agent` tool for on-demand delegation

- **Dual-Engine Intelligence**: Robust AGENTIC capabilities
  - Integrated `google-genai` v0.2.2 as primary cognitive engine
  - Automatic fallback to secondary models for resilience
  - Smart routing based on task complexity

- **New Tools**:
  - `brain_list_services`: List Render.com services (delegated via Lazy Loading)

### Fixed
- **Circular Imports**: Implemented Lazy Loading pattern for `RenderOps` to prevent import cycles
- **Context Hygiene**: Enforced "Tool-First Execution" protocol - agents must act, not suggest



### Added
- **Depth Tracker**: ADHD accommodation - warns (but allows) when going deep into rabbit holes
  - `brain_depth_push/pop/show/reset/set_max` MCP tools
  - `brain://depth` resource
  - `nucleus depth show/up/reset/max/push/map` CLI commands
  - Visual indicator: `🟢 DEPTH: ●●○○○ (2/5)`
  
- **Render Poller**: Monitor deployments without leaving chat
  - `brain_start_deploy_poll`, `brain_check_deploy`, `brain_complete_deploy` tools
  - `brain_smoke_test` for health checks
  - Logs events to ledger for traceability

- **Feature Map**: Living inventory of product features
  - `brain_add_feature`, `brain_list_features`, `brain_get_feature` tools
  - `brain_update_feature`, `brain_mark_validated`, `brain_search_features` tools
  - `nucleus features list/test/search/proof` CLI commands
  - Multi-product support (`gentlequest.json`, `nucleus.json`)

- **Proof System**: Build trust with tangible evidence
  - `brain_generate_proof`, `brain_get_proof`, `brain_list_proofs` tools
  - Captures AI thinking, deployed URL, files changed, rollback plan
  - Stored as markdown in `.brain/features/proofs/`

## [0.3.2] - 2026-01-04
### Fixed
- **Hotfix:** The v0.3.1 release missed the core logic update to read `tasks.json`. This release properly enables V2 tasks, checking `tasks.json` first and falling back to `state.json`.

## [0.3.1] - 2026-01-04

### Added
- **Onboarding Flow**: `nucleus-init` now creates instructional seed tasks
  - 3 guided tasks teach users how to use Nucleus
  - Tasks form a dependency chain (blocked_by) demonstrating V2 features
- **In-Brain README**: `.brain/README.md` explains folder structure and quick commands
- **Improved CLI Output**: Clearer "Next Steps" section after init

## [0.3.0] - 2026-01-03

### Added
- **V2 Task Management System**: Complete agent-native task orchestration
  - `brain_list_tasks`: Query tasks with optional filters (status, priority, skill, claimed_by)
  - `brain_get_next_task`: Get highest-priority unblocked task matching agent skills
  - `brain_claim_task`: Atomically claim a task to prevent race conditions
  - `brain_update_task`: Update task fields (status, priority, description, etc.)
  - `brain_add_task`: Create new tasks with full V2 schema
  - `brain_escalate`: Request human help when agent is stuck

### Schema
- **11-Field Task Schema**: id, description, status, priority, blocked_by, required_skills, claimed_by, source, escalation_reason, created_at, updated_at
- **Status States**: PENDING, READY, IN_PROGRESS, BLOCKED, DONE, FAILED, ESCALATED
- **Backward Compatible**: Automatically migrates legacy tasks (TODO→PENDING, COMPLETE→DONE)

### Documentation
- Added `docs/SPECIFICATION.md`: Complete V2 specification (403 lines, 14 thinking passes)
- Defines 5 core principles: Legibility, Reversibility, Degradation, Trust, Simplicity

## [0.2.6] - 2026-01-03

### Added
- **Auto-Backup on Overwrite**: `nucleus-init` now automatically backs up existing `.brain/` before overwriting
  - Creates timestamped backup: `.brain.backup.YYYYMMDD_HHMMSS/`
  - Stricter confirmation for active brains (>10 files): requires typing `BACKUP-AND-OVERWRITE`
  - Your brain is never deleted without a backup existing first

## [0.2.5] - 2026-01-03

### Added
- **Template System**: `nucleus-init` now supports `--template` argument
  - `--template=solo`: Minimal structure for solo founders
    - Creates `ledger/`, `meta/`, `memory/` (no `agents/` folder)
    - Includes `thread_registry.md` for agent identity management
    - Simplified `state.json` with `mode: "solo"`
  - `--template=default`: Full structure (existing behavior)
- **Thread Registry**: New `meta/thread_registry.md` file for stable agent identity
  - Agents self-identify via thread ID lookup
  - Works across IDE thread renames

## [0.2.4] - 2025-12-30

### Added
- **`cold_start` prompt**: Get instant context when starting a new session
  - Shows current sprint, focus, and status
  - Lists recent events and artifacts
  - Detects workflow files (e.g., `lead_agent_model.md`)
  - Works across all MCP clients
- **`brain://context` resource**: Auto-visible in Claude Desktop sidebar
  - One-click access to full brain context
  - No need to type commands

### Improved
- Enhanced context loading with workflow detection
- Better error handling for missing brain paths

## [0.2.2] - 2025-12-27

### Added
- **Snippet Generator**: `nucleus init` now outputs a copyable JSON config snippet
- Shows config file paths for Claude Desktop, Cursor, and Windsurf
- Pre-fills absolute brain path for zero-friction setup

## [0.2.1] - 2025-12-27

### Added
- `nucleus-init` CLI command to bootstrap a new `.brain/` directory
- Sample state.json, triggers.json, and agent template
- Interactive init with next steps guidance

## [0.2.0] - 2025-12-27

### Added
- `brain_get_triggers` - Get all defined neural triggers
- `brain_evaluate_triggers` - Evaluate which agents should activate
- MCP Resources:
  - `brain://state` - Live state.json content
  - `brain://events` - Recent events stream
  - `brain://triggers` - Trigger definitions
- MCP Prompts:
  - `activate_synthesizer` - Orchestrate current sprint
  - `start_sprint` - Initialize a new sprint

### Changed
- Cleaned repo structure (internal files moved out)
- Improved code organization

## [0.1.0] - 2025-12-27
  - `brain_emit_event` - Emit events to the ledger
  - `brain_read_events` - Read recent events
  - `brain_get_state` - Query brain state
  - `brain_update_state` - Update brain state
  - `brain_read_artifact` - Read artifact files
  - `brain_write_artifact` - Write artifact files
  - `brain_list_artifacts` - List all artifacts
  - `brain_trigger_agent` - Trigger agent with task
- FastMCP integration for MCP protocol compliance
- Claude Desktop configuration support
- MIT License
