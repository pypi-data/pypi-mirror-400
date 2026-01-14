
import os
import json
import time
import uuid
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys
import asyncio

# Configure FastMCP to disable banner and use stderr for logging to avoid breaking MCP protocol
os.environ["FASTMCP_SHOW_CLI_BANNER"] = "False"
os.environ["FASTMCP_LOG_LEVEL"] = "WARNING"

# from fastmcp import FastMCP (Moved to try/except block below)

# Import commitment ledger module
from . import commitment_ledger

# Setup logging
# logging.basicConfig(level=logging.INFO) # Removing to prevent overriding FastMCP settings
logger = logging.getLogger("nucleus")
logger.setLevel(logging.WARNING)

# Initialize FastMCP Server
# Initialize FastMCP Server with fallback
try:
    from fastmcp import FastMCP
    mcp = FastMCP("Nucleus Brain")
except ImportError:
    import sys
    print("Warning: FastMCP not installed. Running in standalone/verification mode.", file=sys.stderr)
    class MockMCP:
        def tool(self, *args, **kwargs):
            def decorator(f): return f
            return decorator
        def resource(self, *args, **kwargs):
            def decorator(f): return f
            return decorator
        def prompt(self, *args, **kwargs):
            def decorator(f): return f
            return decorator
        def run(self): pass
    mcp = MockMCP()

def get_brain_path() -> Path:
    """Get the brain path from environment variable (read dynamically for testing)."""
    brain_path = os.environ.get("NUCLEAR_BRAIN_PATH")
    if not brain_path:
        raise ValueError("NUCLEAR_BRAIN_PATH environment variable not set")
    path = Path(brain_path)
    if not path.exists():
         raise ValueError(f"Brain path does not exist: {brain_path}")
    return path

# ============================================================
# CORE LOGIC (Testable, plain functions)
# ============================================================

def _emit_event(event_type: str, emitter: str, data: Dict[str, Any], description: str = "") -> str:
    """Core logic for emitting an event."""
    try:
        brain = get_brain_path()
        events_path = brain / "ledger" / "events.jsonl"
        
        event_id = f"evt-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        today = time.strftime("%Y-%m-%d")
        
        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "type": event_type,
            "emitter": emitter,
            "data": data,
            "description": description
        }
        
        with open(events_path, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # Update activity summary for fast satellite view (Tier 2 precomputation)
        try:
            summary_path = brain / "ledger" / "activity_summary.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary = json.load(f)
            else:
                summary = {"days": {}, "updated_at": ""}
            
            summary["days"][today] = summary["days"].get(today, 0) + 1
            summary["updated_at"] = timestamp
            
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2)
        except:
            pass  # Don't fail event emit if summary update fails
            
        return event_id
    except Exception as e:
        return f"Error emitting event: {str(e)}"

def _read_events(limit: int = 10) -> List[Dict]:
    """Core logic for reading events."""
    try:
        brain = get_brain_path()
        events_path = brain / "ledger" / "events.jsonl"
        
        if not events_path.exists():
            return []
            
        events = []
        with open(events_path, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events[-limit:]
    except Exception as e:
        logger.error(f"Error reading events: {e}")
        return []

def _get_state(path: Optional[str] = None) -> Dict:
    """Core logic for getting state."""
    try:
        brain = get_brain_path()
        state_path = brain / "ledger" / "state.json"
        
        if not state_path.exists():
            return {}
            
        with open(state_path, "r") as f:
            state = json.load(f)
            
        if path:
            keys = path.split('.')
            val = state
            for k in keys:
                val = val.get(k, {})
            return val
            
        return state
    except Exception as e:
        logger.error(f"Error reading state: {e}")
        return {}

def _update_state(updates: Dict[str, Any]) -> str:
    """Core logic for updating state."""
    try:
        brain = get_brain_path()
        state_path = brain / "ledger" / "state.json"
        
        current_state = {}
        if state_path.exists():
            with open(state_path, "r") as f:
                current_state = json.load(f)
        
        current_state.update(updates)
        
        with open(state_path, "w") as f:
            json.dump(current_state, f, indent=2)
            
        return "State updated successfully"
    except Exception as e:
        return f"Error updating state: {str(e)}"

def _read_artifact(path: str) -> str:
    """Core logic for reading an artifact."""
    try:
        brain = get_brain_path()
        target = brain / "artifacts" / path
        
        if not str(target.resolve()).startswith(str((brain / "artifacts").resolve())):
             return "Error: Access denied (path traversal)"

        if not target.exists():
            return f"Error: File not found: {path}"
            
        return target.read_text()
    except Exception as e:
        return f"Error reading artifact: {str(e)}"

def _write_artifact(path: str, content: str) -> str:
    """Core logic for writing an artifact."""
    try:
        brain = get_brain_path()
        target = brain / "artifacts" / path
        
        if not str(target.resolve()).startswith(str((brain / "artifacts").resolve())):
             return "Error: Access denied (path traversal)"
             
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing artifact: {str(e)}"

def _list_artifacts(folder: Optional[str] = None) -> List[str]:
    """Core logic for listing artifacts."""
    try:
        brain = get_brain_path()
        root = brain / "artifacts"
        if folder:
            root = root / folder
            
        if not root.exists():
            return []
            
        files = []
        for p in root.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(brain / "artifacts")))
        return files[:50]
    except Exception as e:
        return []

def _trigger_agent(agent: str, task_description: str, context_files: List[str] = None) -> str:
    """Core logic for triggering an agent."""
    data = {
        "task_id": f"task-{int(time.time())}",
        "target_agent": agent,
        "description": task_description,
        "context_files": context_files or [],
        "status": "pending"
    }
    
    event_id = _emit_event(
        event_type="task_assigned",
        emitter="nucleus_mcp",
        data=data,
        description=f"Manual trigger for {agent}"
    )
    
    return f"Triggered {agent} with event {event_id}"

def _get_triggers() -> List[Dict]:
    """Core logic for getting all triggers."""
    try:
        brain = get_brain_path()
        triggers_path = brain / "ledger" / "triggers.json"
        
        if not triggers_path.exists():
            return []
            
        with open(triggers_path, "r") as f:
            triggers_data = json.load(f)
        
        # Return list of trigger definitions
        return triggers_data.get("triggers", [])
    except Exception as e:
        logger.error(f"Error reading triggers: {e}")
        return []

def _evaluate_triggers(event_type: str, emitter: str) -> List[str]:
    """Core logic for evaluating which agents should activate."""
    try:
        triggers = _get_triggers()
        matching_agents = []
        
        for trigger in triggers:
            # Check if this trigger matches the event
            if trigger.get("event_type") == event_type:
                # Check emitter filter if specified
                emitter_filter = trigger.get("emitter_filter")
                if emitter_filter is None or emitter in emitter_filter:
                    matching_agents.append(trigger.get("target_agent"))
        
        return list(set(matching_agents))  # Dedupe
    except Exception as e:
        logger.error(f"Error evaluating triggers: {e}")
        return []

# ============================================================
# V2 TASK MANAGEMENT CORE LOGIC
# ============================================================

def _get_tasks_list() -> List[Dict]:
    """Get the tasks array from tasks.json (V2) or fallback to state.json (V1)."""
    try:
        brain = get_brain_path()
        tasks_path = brain / "ledger" / "tasks.json"

        # Priority 1: Read V2 tasks.json
        if tasks_path.exists():
            with open(tasks_path, "r") as f:
                return json.load(f)
                
        # Priority 2: Fallback to V1 state.json
        state = _get_state()
        current_sprint = state.get("current_sprint", {})
        return current_sprint.get("tasks", [])
    except Exception as e:
        logger.error(f"Error getting tasks list: {e}")
        return []

def _save_tasks_list(tasks: List[Dict]) -> str:
    """Save the tasks array (prefers V2 tasks.json if it exists)."""
    try:
        brain = get_brain_path()
        tasks_path = brain / "ledger" / "tasks.json"
        
        # Priority 1: Write to V2 tasks.json if it exists
        if tasks_path.exists():
            with open(tasks_path, "w") as f:
                json.dump(tasks, f, indent=2)
            return "Tasks saved (V2)"

        # Priority 2: Fallback to V1 state.json
        state = _get_state()
        if "current_sprint" not in state:
            state["current_sprint"] = {}
        state["current_sprint"]["tasks"] = tasks
        
        state_path = brain / "ledger" / "state.json"
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
        return "Tasks saved (V1)"
    except Exception as e:
        logger.error(f"Error saving tasks list: {e}")
        return f"Error saving tasks: {str(e)}"

def _list_tasks(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    skill: Optional[str] = None,
    claimed_by: Optional[str] = None
) -> List[Dict]:
    """List tasks with optional filters."""
    try:
        tasks = _get_tasks_list()
        
        # Ensure all tasks have V2 fields (backward compat)
        for task in tasks:
            if "id" not in task:
                task["id"] = f"task-{str(uuid.uuid4())[:8]}"
            if "priority" not in task:
                task["priority"] = 3  # Default medium
            if "blocked_by" not in task:
                task["blocked_by"] = []
            if "required_skills" not in task:
                # Migrate from preferred_role
                if "preferred_role" in task:
                    task["required_skills"] = [task["preferred_role"].lower()]
                else:
                    task["required_skills"] = []
            if "source" not in task:
                task["source"] = "synthesizer"
            if "created_at" not in task:
                task["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            if "updated_at" not in task:
                task["updated_at"] = task["created_at"]
        
        # Apply filters
        filtered = tasks
        
        if status:
            # Map old status names to new
            status_map = {"TODO": "PENDING", "COMPLETE": "DONE"}
            target_status = status_map.get(status, status)
            filtered = [t for t in filtered if t.get("status", "").upper() == target_status.upper() 
                       or t.get("status", "").upper() == status.upper()]
        
        if priority is not None:
            filtered = [t for t in filtered if t.get("priority") == priority]
        
        if skill:
            filtered = [t for t in filtered if skill.lower() in 
                       [s.lower() for s in t.get("required_skills", [])]]
        
        if claimed_by:
            filtered = [t for t in filtered if claimed_by in str(t.get("claimed_by", ""))]
        
        # Sort by priority (1=Highest, so ascending order)
        filtered.sort(key=lambda x: x.get("priority", 3))
        
        return filtered
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return []

def _get_next_task(skills: List[str]) -> Optional[Dict]:
    """Get highest priority unblocked task matching skills."""
    try:
        tasks = _list_tasks()
        
        # Filter for actionable tasks
        actionable = []
        for task in tasks:
            status = task.get("status", "").upper()
            # Include TODO (legacy) and PENDING/READY (V2)
            if status not in ["TODO", "PENDING", "READY"]:
                continue
            
            # Skip if already claimed
            if task.get("claimed_by"):
                continue
            
            # Skip if blocked
            blocked_by = task.get("blocked_by", [])
            if blocked_by:
                # Check if blocking tasks are done
                all_tasks = _get_tasks_list()
                blocking_done = True
                for blocker_id in blocked_by:
                    for t in all_tasks:
                        if t.get("id") == blocker_id:
                            if t.get("status", "").upper() not in ["DONE", "COMPLETE"]:
                                blocking_done = False
                                break
                if not blocking_done:
                    continue
            
            # Check skill match
            required = [s.lower() for s in task.get("required_skills", [])]
            available = [s.lower() for s in skills]
            
            if not required or any(r in available for r in required):
                actionable.append(task)
        
        # Sort by priority (1 = highest)
        actionable.sort(key=lambda t: t.get("priority", 3))
        
        return actionable[0] if actionable else None
    except Exception as e:
        logger.error(f"Error getting next task: {e}")
        return None

def _claim_task(task_id: str, agent_id: str) -> Dict:
    """Atomically claim a task."""
    try:
        tasks = _get_tasks_list()
        
        for task in tasks:
            # Match by id or by description (backward compat)
            if task.get("id") == task_id or task.get("description") == task_id:
                # Check if already claimed
                if task.get("claimed_by"):
                    return {"success": False, "error": f"Task already claimed by {task['claimed_by']}"}
                
                # Check status
                status = task.get("status", "").upper()
                if status not in ["TODO", "PENDING", "READY"]:
                    return {"success": False, "error": f"Task status is {status}, cannot claim"}
                
                # Claim it
                task["claimed_by"] = agent_id
                task["status"] = "IN_PROGRESS"
                task["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                
                _save_tasks_list(tasks)
                
                # Emit event
                _emit_event("task_claimed", agent_id, {
                    "task_id": task.get("id", task_id),
                    "description": task.get("description")
                })
                
                return {"success": True, "task": task}
        
        return {"success": False, "error": "Task not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _update_task(task_id: str, updates: Dict[str, Any]) -> Dict:
    """Update task fields."""
    try:
        tasks = _get_tasks_list()
        
        for task in tasks:
            if task.get("id") == task_id or task.get("description") == task_id:
                # VALIDATION: Check for valid keys
                valid_keys = ["status", "priority", "description", "blocked_by", 
                              "required_skills", "claimed_by"]
                
                # VALIDATION: Referential Integrity for 'blocked_by'
                if "blocked_by" in updates:
                    all_ids = {t["id"] for t in tasks}
                    for dep_id in updates["blocked_by"]:
                        if dep_id not in all_ids:
                             raise ValueError(f"Referential integrity violation: Dependency task '{dep_id}' does not exist")

                # Capture old state for event
                old_status = task.get("status")
                
                # Apply updates
                for key, value in updates.items():
                    if key in valid_keys:
                        task[key] = value
                
                task["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                
                _save_tasks_list(tasks)
                
                # Emit event if status changed
                new_status = task.get("status")
                if old_status != new_status and "status" in updates:
                    try:
                        _emit_event(
                            "task_state_changed",
                            "brain_update_task",
                            {
                                "task_id": task.get("id"),
                                "old_status": old_status,
                                "new_status": new_status,
                                "description": task.get("description", "")[:60]
                            },
                            description=f"Task {task.get('id')} {old_status} → {new_status}"
                        )
                    except Exception:
                        pass  # Don't fail task update if event emission fails
                
                return {"success": True, "task": task}
        
        return {"success": False, "error": "Task not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _add_task(
    description: str,
    priority: int = 3,
    blocked_by: List[str] = None,
    required_skills: List[str] = None,
    source: str = "synthesizer"
) -> Dict:
    """Create a new task.
    
    Safety Properties Enforced:
    - Referential Integrity: blocked_by references must exist
    - DAG Property: No circular dependencies (simple check for self-reference)
    """
    try:
        tasks = _get_tasks_list()
        task_ids = {t.get("id") for t in tasks if t.get("id")}
        
        # Validate blocked_by references (Referential Integrity)
        if blocked_by:
            for dep_id in blocked_by:
                if dep_id not in task_ids:
                    return {
                        "success": False, 
                        "error": f"Referential integrity violation: dependency '{dep_id}' does not exist"
                    }
        
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        new_task_id = f"task-{str(uuid.uuid4())[:8]}"
        
        # Check for self-reference (basic DAG property)
        if blocked_by and new_task_id in blocked_by:
            return {
                "success": False,
                "error": "DAG violation: task cannot block itself"
            }
        
        new_task = {
            "id": new_task_id,
            "description": description,
            "status": "PENDING" if not blocked_by else "BLOCKED",
            "priority": priority,
            "blocked_by": blocked_by or [],
            "required_skills": required_skills or [],
            "claimed_by": None,
            "source": source,
            "escalation_reason": None,
            "created_at": now,
            "updated_at": now
        }
        
        tasks.append(new_task)
        _save_tasks_list(tasks)
        
        # Emit event
        _emit_event("task_created", "nucleus_mcp", {
            "task_id": new_task["id"],
            "description": description,
            "source": source
        })
        
        return {"success": True, "task": new_task}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _escalate_task(task_id: str, reason: str) -> Dict:
    """Escalate a task to request human help."""
    try:
        tasks = _get_tasks_list()
        
        for task in tasks:
            if task.get("id") == task_id or task.get("description") == task_id:
                task["status"] = "ESCALATED"
                task["escalation_reason"] = reason
                task["claimed_by"] = None  # Unclaim
                task["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                
                _save_tasks_list(tasks)
                
                # Emit event
                _emit_event("task_escalated", "nucleus_mcp", {
                    "task_id": task.get("id", task_id),
                    "reason": reason
                })
                
                return {"success": True, "task": task}
        
        return {"success": False, "error": "Task not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# DEPTH TRACKER - TIER 1 MVP (ADHD Accommodation)
# ============================================================
# Purpose: Real-time "you are here" indicator for conversation depth
# Philosophy: WARN but ALLOW - guardrail, not a wall

def _get_depth_path() -> Path:
    """Get the path to the depth tracking file."""
    brain = get_brain_path()
    session_dir = brain / "session"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / "depth.json"

def _get_depth_state() -> Dict:
    """Get current depth tracking state."""
    try:
        depth_path = _get_depth_path()
        
        if not depth_path.exists():
            # Initialize with default state
            default_state = {
                "session_id": f"session-{time.strftime('%Y%m%d')}",
                "current_depth": 0,
                "max_safe_depth": 5,
                "levels": [],
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")
            }
            with open(depth_path, "w") as f:
                json.dump(default_state, f, indent=2)
            return default_state
        
        with open(depth_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error getting depth state: {e}")
        return {"current_depth": 0, "levels": [], "max_safe_depth": 5}

def _save_depth_state(state: Dict) -> str:
    """Save depth tracking state."""
    try:
        depth_path = _get_depth_path()
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with open(depth_path, "w") as f:
            json.dump(state, f, indent=2)
        return "Depth state saved"
    except Exception as e:
        return f"Error saving depth state: {str(e)}"

def _depth_push(topic: str) -> Dict:
    """Go deeper into a subtopic. Returns current state with warnings."""
    try:
        state = _get_depth_state()
        
        new_depth = state.get("current_depth", 0) + 1
        max_safe = state.get("max_safe_depth", 5)
        
        # Create new level entry
        new_level = {
            "depth": new_depth,
            "topic": topic,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "status": "current"
        }
        
        # Update previous level status
        levels = state.get("levels", [])
        for level in levels:
            if level.get("status") == "current":
                level["status"] = "active"
        
        levels.append(new_level)
        
        state["current_depth"] = new_depth
        state["levels"] = levels
        _save_depth_state(state)
        
        # Generate warning based on depth
        warning = None
        warning_level = "safe"
        
        if new_depth >= max_safe:
            warning = f"🔴🔴 RABBIT HOLE! You're at level {new_depth}/{max_safe}. Consider resurfacing."
            warning_level = "danger"
        elif new_depth >= max_safe - 1:
            warning = f"🔴 DEEP DIVE ALERT! Level {new_depth}/{max_safe}. You're in the danger zone."
            warning_level = "danger"
        elif new_depth >= 3:
            warning = f"🟡 CAUTION: Level {new_depth}/{max_safe}. Getting deep - just so you know."
            warning_level = "caution"
        
        # Build breadcrumb path
        breadcrumbs = " → ".join([l["topic"] for l in levels])
        
        # Emit event
        _emit_event("depth_increased", "depth_tracker", {
            "new_depth": new_depth,
            "topic": topic,
            "warning_level": warning_level
        })
        
        return {
            "current_depth": new_depth,
            "max_safe_depth": max_safe,
            "topic": topic,
            "breadcrumbs": breadcrumbs,
            "warning": warning,
            "warning_level": warning_level,
            "indicator": _format_depth_indicator(new_depth, max_safe)
        }
    except Exception as e:
        return {"error": str(e)}

def _depth_pop() -> Dict:
    """Come back up one level. Returns new state."""
    try:
        state = _get_depth_state()
        levels = state.get("levels", [])
        
        if not levels:
            return {
                "current_depth": 0,
                "message": "Already at root level (depth 0). Nothing to pop.",
                "indicator": _format_depth_indicator(0, state.get("max_safe_depth", 5))
            }
        
        # Pop the current level
        popped = levels.pop()
        
        # Set new current
        if levels:
            levels[-1]["status"] = "current"
        
        new_depth = len(levels)
        state["current_depth"] = new_depth
        state["levels"] = levels
        _save_depth_state(state)
        
        # Build breadcrumb path
        breadcrumbs = " → ".join([l["topic"] for l in levels]) if levels else "(root)"
        returned_to = levels[-1]["topic"] if levels else "root"
        
        # Emit event
        _emit_event("depth_decreased", "depth_tracker", {
            "new_depth": new_depth,
            "returned_to": returned_to,
            "popped_topic": popped["topic"]
        })
        
        return {
            "current_depth": new_depth,
            "returned_to": returned_to,
            "popped_topic": popped["topic"],
            "breadcrumbs": breadcrumbs,
            "message": f"✅ Resurfaced! Now at level {new_depth}: {returned_to}",
            "indicator": _format_depth_indicator(new_depth, state.get("max_safe_depth", 5))
        }
    except Exception as e:
        return {"error": str(e)}

def _depth_show() -> Dict:
    """Show current depth state with visual indicator."""
    try:
        state = _get_depth_state()
        current_depth = state.get("current_depth", 0)
        max_safe = state.get("max_safe_depth", 5)
        levels = state.get("levels", [])
        
        # Build breadcrumb path
        breadcrumbs = " → ".join([l["topic"] for l in levels]) if levels else "(root)"
        
        # Build tree visualization
        tree_lines = []
        for i, level in enumerate(levels):
            indent = "  " * i
            prefix = "└─ " if i > 0 else ""
            marker = " ← YOU ARE HERE" if level.get("status") == "current" else ""
            tree_lines.append(f"{indent}{prefix}{i}: {level['topic']}{marker}")
        
        tree = "\n".join(tree_lines) if tree_lines else "(At root level)"
        
        # Generate status
        if current_depth >= max_safe:
            status = "🔴 RABBIT HOLE"
        elif current_depth >= max_safe - 1:
            status = "🔴 DANGER ZONE"
        elif current_depth >= 3:
            status = "🟡 CAUTION"
        else:
            status = "🟢 SAFE"
        
        return {
            "current_depth": current_depth,
            "max_safe_depth": max_safe,
            "status": status,
            "breadcrumbs": breadcrumbs,
            "tree": tree,
            "indicator": _format_depth_indicator(current_depth, max_safe),
            "levels": levels,
            "session_id": state.get("session_id"),
            "help": "Commands: brain_depth_push(topic), brain_depth_pop(), brain_depth_reset(), brain_depth_set_max(n)"
        }
    except Exception as e:
        return {"error": str(e)}

def _depth_reset() -> Dict:
    """Reset depth to 0 (root level). Clears all levels."""
    try:
        state = _get_depth_state()
        
        # Keep session ID and max_safe_depth
        new_state = {
            "session_id": f"session-{time.strftime('%Y%m%d-%H%M%S')}",
            "current_depth": 0,
            "max_safe_depth": state.get("max_safe_depth", 5),
            "levels": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }
        
        _save_depth_state(new_state)
        
        # Emit event
        _emit_event("depth_reset", "depth_tracker", {
            "previous_depth": state.get("current_depth", 0),
            "new_session_id": new_state["session_id"]
        })
        
        return {
            "message": "✅ Session reset! Back to root level (depth 0).",
            "current_depth": 0,
            "session_id": new_state["session_id"],
            "indicator": _format_depth_indicator(0, new_state["max_safe_depth"])
        }
    except Exception as e:
        return {"error": str(e)}

def _depth_set_max(max_depth: int) -> Dict:
    """Set the maximum safe depth threshold."""
    try:
        if max_depth < 1 or max_depth > 10:
            return {"error": "Max depth must be between 1 and 10"}
        
        state = _get_depth_state()
        old_max = state.get("max_safe_depth", 5)
        state["max_safe_depth"] = max_depth
        _save_depth_state(state)
        
        return {
            "message": f"Max safe depth changed from {old_max} to {max_depth}",
            "max_safe_depth": max_depth,
            "current_depth": state.get("current_depth", 0),
            "indicator": _format_depth_indicator(state.get("current_depth", 0), max_depth)
        }
    except Exception as e:
        return {"error": str(e)}

def _format_depth_indicator(current: int, max_safe: int) -> str:
    """Format a visual depth indicator with dots and colors."""
    filled = "●" * current
    empty = "○" * (max_safe - current) if current < max_safe else ""
    overflow = "●" * (current - max_safe) if current > max_safe else ""
    
    # Color indicator
    if current >= max_safe:
        color = "🔴"
    elif current >= max_safe - 1:
        color = "🔴"
    elif current >= 3:
        color = "🟡"
    else:
        color = "🟢"
    
    return f"{color} DEPTH: {filled}{empty}{overflow} ({current}/{max_safe})"

def _generate_depth_map() -> Dict:
    """Generate a Mermaid diagram of the current exploration path."""
    try:
        state = _get_depth_state()
        levels = state.get("levels", [])
        max_safe = state.get("max_safe_depth", 5)
        
        if not levels:
            return {
                "mermaid": "```mermaid\ngraph TD\n    ROOT((🏠 START))\n    style ROOT fill:#ccffcc,stroke:#0a0\n```",
                "message": "You're at the root level. No exploration path yet.",
                "node_count": 0
            }
        
        # Build Mermaid graph
        lines = ["graph TD"]
        lines.append("    ROOT((🏠 START))")
        
        prev_id = "ROOT"
        for i, level in enumerate(levels):
            node_id = f"L{i}"
            topic = level.get("topic", f"Level {i+1}")
            # Escape quotes and special chars
            topic_safe = topic.replace('"', "'").replace("[", "(").replace("]", ")")
            
            # Determine node style based on depth
            depth = i + 1
            if depth >= max_safe:
                style = "fill:#ffcccc,stroke:#f00"  # Red - rabbit hole
                node_shape = f'{node_id}[["🔴 {topic_safe}"]]'
            elif depth >= max_safe - 1:
                style = "fill:#ffddcc,stroke:#f60"  # Orange - danger
                node_shape = f'{node_id}[["🔴 {topic_safe}"]]'
            elif depth >= 3:
                style = "fill:#ffffcc,stroke:#cc0"  # Yellow - caution
                node_shape = f'{node_id}["🟡 {topic_safe}"]'
            else:
                style = "fill:#ccffcc,stroke:#0a0"  # Green - safe
                node_shape = f'{node_id}["🟢 {topic_safe}"]'
            
            lines.append(f"    {prev_id} --> {node_shape}")
            lines.append(f"    style {node_id} {style}")
            prev_id = node_id
        
        # Mark the last node as current
        if levels:
            lines.append(f"    style {prev_id} stroke-width:3px")
        
        # Wrap in code block
        mermaid_code = "```mermaid\n" + "\n".join(lines) + "\n```"
        
        # Build path summary
        path = " → ".join([l.get("topic", "?") for l in levels])
        
        return {
            "mermaid": mermaid_code,
            "path": f"🏠 → {path}",
            "current_depth": len(levels),
            "max_safe_depth": max_safe,
            "node_count": len(levels),
            "message": f"Exploration map with {len(levels)} nodes. Current depth: {len(levels)}/{max_safe}"
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# RENDER POLLER (Deploy monitoring)
# ============================================================

def _get_render_config() -> Dict:
    """Get Render service configuration from state.json."""
    try:
        state = _get_state()
        render_config = state.get("render", {})
        return render_config
    except Exception:
        return {}

def _save_render_config(config: Dict) -> None:
    """Save Render configuration to state.json."""
    state = _get_state()
    state["render"] = config
    brain = get_brain_path()
    state_path = brain / "ledger" / "state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

def _run_smoke_test(deploy_url: str, endpoint: str = "/api/health") -> Dict:
    """Run a quick health check on deployed service."""
    import urllib.request
    import urllib.error
    
    try:
        url = f"{deploy_url.rstrip('/')}{endpoint}"
        start = time.time()
        
        request = urllib.request.Request(url, headers={"User-Agent": "Nucleus-Smoke-Test/1.0"})
        with urllib.request.urlopen(request, timeout=10) as response:
            latency_ms = (time.time() - start) * 1000
            data = json.loads(response.read().decode())
            
            if response.status == 200:
                status = data.get("status", "unknown")
                if status in ["healthy", "ok", "success"]:
                    return {
                        "passed": True,
                        "latency_ms": round(latency_ms, 2),
                        "status": status,
                        "url": url
                    }
                else:
                    return {
                        "passed": False,
                        "reason": f"Health status: {status}",
                        "latency_ms": round(latency_ms, 2)
                    }
            else:
                return {
                    "passed": False,
                    "reason": f"HTTP {response.status}",
                    "latency_ms": round(latency_ms, 2)
                }
                
    except urllib.error.HTTPError as e:
        return {"passed": False, "reason": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"passed": False, "reason": f"URL Error: {str(e.reason)}"}
    except TimeoutError:
        return {"passed": False, "reason": "Timeout (10s)"}
    except Exception as e:
        return {"passed": False, "reason": str(e)}

def _poll_render_once(service_id: str) -> Dict:
    """Check current deploy status once. Returns latest deploy info."""
    # This is a placeholder - actual implementation would call Render MCP
    # For now, we document what it would return
    return {
        "status": "unknown",
        "message": "Use mcp_render_list_deploys() to check deploy status",
        "service_id": service_id,
        "action": "Call brain_check_deploy() with the service ID to poll Render"
    }

def _start_deploy_poll(service_id: str, commit_sha: str = None) -> Dict:
    """Start monitoring a deploy. Logs event and returns poll instructions."""
    try:
        # Log the poll start event
        _emit_event("deploy_poll_started", "render_poller", {
            "service_id": service_id,
            "commit_sha": commit_sha,
            "poll_interval_seconds": 30,
            "timeout_minutes": 20
        })
        
        # Get or create active polls file
        brain = get_brain_path()
        polls_path = brain / "ledger" / "active_polls.json"
        
        if polls_path.exists():
            with open(polls_path) as f:
                polls = json.load(f)
        else:
            polls = {"polls": []}
        
        # Add new poll
        poll_id = f"poll-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        new_poll = {
            "poll_id": poll_id,
            "service_id": service_id,
            "commit_sha": commit_sha,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "status": "polling"
        }
        
        # Cancel any existing poll for same service
        polls["polls"] = [p for p in polls["polls"] if p.get("service_id") != service_id]
        polls["polls"].append(new_poll)
        
        with open(polls_path, "w") as f:
            json.dump(polls, f, indent=2)
        
        return {
            "poll_id": poll_id,
            "service_id": service_id,
            "commit_sha": commit_sha,
            "status": "polling_started",
            "message": f"Deploy monitoring started. Use brain_check_deploy('{service_id}') to check status.",
            "next_check": "Call mcp_render_list_deploys() or brain_check_deploy() to see current status"
        }
    except Exception as e:
        return {"error": str(e)}

def _check_deploy_status(service_id: str) -> Dict:
    """Check deploy status and update poll state. Returns formatted status."""
    try:
        brain = get_brain_path()
        polls_path = brain / "ledger" / "active_polls.json"
        
        # Check if we have an active poll
        if not polls_path.exists():
            return {
                "status": "no_active_poll",
                "message": "No active polling for this service. Start one with brain_start_deploy_poll()."
            }
        
        with open(polls_path) as f:
            polls = json.load(f)
        
        active_poll = next((p for p in polls.get("polls", []) if p.get("service_id") == service_id), None)
        
        if not active_poll:
            return {
                "status": "no_active_poll",
                "message": f"No active polling for service {service_id}."
            }
        
        # Calculate elapsed time
        started_at = active_poll.get("started_at", "")
        elapsed_minutes = 0
        if started_at:
            try:
                start_time = time.mktime(time.strptime(started_at[:19], "%Y-%m-%dT%H:%M:%S"))
                elapsed_minutes = (time.time() - start_time) / 60
            except:
                pass
        
        return {
            "poll_id": active_poll.get("poll_id"),
            "service_id": service_id,
            "commit_sha": active_poll.get("commit_sha"),
            "status": "polling",
            "elapsed_minutes": round(elapsed_minutes, 1),
            "message": f"Polling for {elapsed_minutes:.1f} minutes. Use mcp_render_list_deploys('{service_id}') to check Render status.",
            "next_action": "Check Render MCP for actual deploy status, then call brain_complete_deploy() when done"
        }
    except Exception as e:
        return {"error": str(e)}

def _complete_deploy(service_id: str, success: bool, deploy_url: str = None, 
                     error: str = None, run_smoke_test: bool = True) -> Dict:
    """Mark deploy as complete. Optionally runs smoke test."""
    try:
        brain = get_brain_path()
        polls_path = brain / "ledger" / "active_polls.json"
        
        # Remove from active polls
        if polls_path.exists():
            with open(polls_path) as f:
                polls = json.load(f)
            
            polls["polls"] = [p for p in polls.get("polls", []) if p.get("service_id") != service_id]
            
            with open(polls_path, "w") as f:
                json.dump(polls, f, indent=2)
        
        # Run smoke test if successful
        smoke_result = None
        if success and deploy_url and run_smoke_test:
            smoke_result = _run_smoke_test(deploy_url)
        
        # Determine final status
        if success:
            if smoke_result and smoke_result.get("passed"):
                status = "deploy_success_verified"
                message = f"✅ Deploy complete and verified! URL: {deploy_url}"
            elif smoke_result and not smoke_result.get("passed"):
                status = "deploy_success_smoke_failed"
                message = f"⚠️ Deploy succeeded but smoke test failed: {smoke_result.get('reason')}"
            else:
                status = "deploy_success"
                message = f"✅ Deploy complete! URL: {deploy_url}"
        else:
            status = "deploy_failed"
            message = f"❌ Deploy failed: {error}"
        
        # Log completion event
        _emit_event("deploy_complete", "render_poller", {
            "service_id": service_id,
            "success": success,
            "url": deploy_url,
            "error": error,
            "smoke_test": smoke_result,
            "status": status
        })
        
        return {
            "status": status,
            "message": message,
            "deploy_url": deploy_url,
            "smoke_test": smoke_result,
            "service_id": service_id
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# FEATURE MAP (Product feature inventory)
# ============================================================

def _get_features_path(product: str) -> Path:
    """Get path to product's features.json file."""
    brain = get_brain_path()
    return brain / "features" / f"{product}.json"

def _load_features(product: str) -> Dict:
    """Load features for a product."""
    path = _get_features_path(product)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"product": product, "last_updated": None, "total_features": 0, "features": []}

def _save_features(product: str, data: Dict) -> None:
    """Save features for a product."""
    path = _get_features_path(product)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    data["total_features"] = len(data.get("features", []))
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _add_feature(product: str, name: str, description: str, source: str, 
                 version: str, how_to_test: List[str], expected_result: str,
                 status: str = "development", **kwargs) -> Dict:
    """Add a new feature to the product's feature map."""
    try:
        data = _load_features(product)
        
        # Generate ID from name
        feature_id = name.lower().replace(" ", "_").replace("-", "_")
        feature_id = "".join(c for c in feature_id if c.isalnum() or c == "_")
        
        # Check for duplicates
        if any(f.get("id") == feature_id for f in data.get("features", [])):
            return {"error": f"Feature '{feature_id}' already exists"}
        
        # Build feature dict
        feature = {
            "id": feature_id,
            "name": name,
            "description": description,
            "product": product,
            "source": source,
            "version": version,
            "status": status,
            "how_to_test": how_to_test,
            "expected_result": expected_result,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "last_validated": None,
            "validation_result": None
        }
        
        # Add optional fields
        for key in ["tier", "deployed_at", "deployed_url", "released_at", 
                    "pypi_url", "files_changed", "commit_sha", "tags"]:
            if key in kwargs:
                feature[key] = kwargs[key]
        
        data.setdefault("features", []).append(feature)
        _save_features(product, data)
        
        return {"success": True, "feature": feature}
    except Exception as e:
        return {"error": str(e)}

def _list_features(product: str = None, status: str = None, tag: str = None) -> Dict:
    """List features with optional filters."""
    try:
        brain = get_brain_path()
        features_dir = brain / "features"
        
        if not features_dir.exists():
            return {"features": [], "total": 0}
        
        all_features = []
        
        # Get all product files or just the specified one
        if product:
            products = [product]
        else:
            products = [f.stem for f in features_dir.glob("*.json")]
        
        for p in products:
            data = _load_features(p)
            for feature in data.get("features", []):
                # Apply filters
                if status and feature.get("status") != status:
                    continue
                if tag and tag not in feature.get("tags", []):
                    continue
                all_features.append(feature)
        
        return {"features": all_features, "total": len(all_features)}
    except Exception as e:
        return {"error": str(e)}

def _get_feature(feature_id: str) -> Dict:
    """Get a specific feature by ID."""
    try:
        brain = get_brain_path()
        features_dir = brain / "features"
        
        if not features_dir.exists():
            return {"error": f"Feature '{feature_id}' not found"}
        
        for json_file in features_dir.glob("*.json"):
            data = _load_features(json_file.stem)
            for feature in data.get("features", []):
                if feature.get("id") == feature_id:
                    return {"feature": feature}
        
        return {"error": f"Feature '{feature_id}' not found"}
    except Exception as e:
        return {"error": str(e)}

def _update_feature(feature_id: str, **updates) -> Dict:
    """Update a feature."""
    try:
        brain = get_brain_path()
        features_dir = brain / "features"
        
        for json_file in features_dir.glob("*.json"):
            product = json_file.stem
            data = _load_features(product)
            
            for i, feature in enumerate(data.get("features", [])):
                if feature.get("id") == feature_id:
                    # Apply updates
                    for key, value in updates.items():
                        data["features"][i][key] = value
                    
                    _save_features(product, data)
                    return {"success": True, "feature": data["features"][i]}
        
        return {"error": f"Feature '{feature_id}' not found"}
    except Exception as e:
        return {"error": str(e)}

def _mark_validated(feature_id: str, result: str) -> Dict:
    """Mark a feature as validated."""
    if result not in ["passed", "failed"]:
        return {"error": "Result must be 'passed' or 'failed'"}
    
    return _update_feature(
        feature_id,
        last_validated=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        validation_result=result
    )

def _search_features(query: str) -> Dict:
    """Search features by name, description, or tags."""
    try:
        result = _list_features()
        if "error" in result:
            return result
        
        query_lower = query.lower()
        matches = []
        
        for feature in result.get("features", []):
            # Search in name, description, tags
            searchable = " ".join([
                feature.get("name", ""),
                feature.get("description", ""),
                " ".join(feature.get("tags", []))
            ]).lower()
            
            if query_lower in searchable:
                matches.append(feature)
        
        return {"features": matches, "total": len(matches), "query": query}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# PROOF SYSTEM (Feature validation proof)
# ============================================================

def _get_proofs_path() -> Path:
    """Get path to proofs directory."""
    brain = get_brain_path()
    return brain / "features" / "proofs"

def _generate_proof(feature_id: str, thinking: str = None, 
                    deployed_url: str = None, files_changed: List[str] = None,
                    rollback_command: str = None, risk_level: str = "low",
                    rollback_time: str = "15 minutes") -> Dict:
    """Generate a proof document for a feature.
    
    Creates a markdown file with:
    - AI thinking (options considered, choice, reasoning, fallback)
    - Deployed URL
    - Files changed (as diff-style list)
    - Rollback plan with risk level
    """
    try:
        # Get feature to verify it exists
        feature_result = _get_feature(feature_id)
        if "error" in feature_result:
            return feature_result
        
        feature = feature_result.get("feature", {})
        proofs_dir = _get_proofs_path()
        proofs_dir.mkdir(parents=True, exist_ok=True)
        
        # Build proof markdown
        proof_lines = [
            f"# Proof: {feature.get('name', feature_id)}",
            "",
            f"> Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"> Feature ID: `{feature_id}`",
            f"> Product: {feature.get('product', 'unknown')}",
            f"> Version: {feature.get('version', 'unknown')}",
            "",
            "---",
            ""
        ]
        
        # AI Thinking section
        if thinking:
            proof_lines.extend([
                "## Thinking",
                "",
                thinking,
                "",
                "---",
                ""
            ])
        else:
            proof_lines.extend([
                "## Thinking",
                "",
                "*No thinking captured. Add with `brain_generate_proof(thinking=...)`*",
                "",
                "---",
                ""
            ])
        
        # Deployed URL
        url = deployed_url or feature.get("deployed_url", "")
        proof_lines.extend([
            "## Deployed URL",
            "",
            url if url else "*Not deployed yet*",
            "",
            "---",
            ""
        ])
        
        # Files Changed
        files = files_changed or feature.get("files_changed", [])
        proof_lines.append("## Files Changed")
        proof_lines.append("")
        if files:
            proof_lines.append("```")
            for f in files:
                proof_lines.append(f"  {f}")
            proof_lines.append("```")
        else:
            proof_lines.append("*No files tracked*")
        proof_lines.extend(["", "---", ""])
        
        # Rollback Plan
        commit_sha = feature.get("commit_sha", "HEAD")
        rollback_cmd = rollback_command or f"git revert {commit_sha}\ngit push origin main"
        
        proof_lines.extend([
            "## Rollback Plan",
            "",
            "### Command:",
            "```bash",
            rollback_cmd,
            "```",
            "",
            f"### Risk Level: {risk_level.capitalize()}",
            "",
            f"### Estimated Rollback Time: {rollback_time}",
            ""
        ])
        
        # Write proof file
        proof_path = proofs_dir / f"{feature_id}.md"
        with open(proof_path, "w") as f:
            f.write("\n".join(proof_lines))
        
        # Update feature with proof URL
        _update_feature(feature_id, proof_url=f"file://.brain/features/proofs/{feature_id}.md")
        
        return {
            "success": True,
            "feature_id": feature_id,
            "proof_path": str(proof_path),
            "message": f"Proof generated for '{feature.get('name')}'"
        }
    except Exception as e:
        return {"error": str(e)}

def _get_proof(feature_id: str) -> Dict:
    """Get the proof document for a feature."""
    try:
        proofs_dir = _get_proofs_path()
        proof_path = proofs_dir / f"{feature_id}.md"
        
        if not proof_path.exists():
            return {
                "exists": False,
                "feature_id": feature_id,
                "message": f"No proof exists for '{feature_id}'. Generate one with brain_generate_proof()."
            }
        
        with open(proof_path) as f:
            content = f.read()
        
        return {
            "exists": True,
            "feature_id": feature_id,
            "proof_path": str(proof_path),
            "content": content
        }
    except Exception as e:
        return {"error": str(e)}

def _list_proofs() -> Dict:
    """List all proof documents."""
    try:
        proofs_dir = _get_proofs_path()
        
        if not proofs_dir.exists():
            return {"proofs": [], "total": 0}
        
        proofs = []
        for proof_file in proofs_dir.glob("*.md"):
            feature_id = proof_file.stem
            stat = proof_file.stat()
            proofs.append({
                "feature_id": feature_id,
                "path": str(proof_file),
                "size_bytes": stat.st_size,
                "modified_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stat.st_mtime))
            })
        
        return {"proofs": proofs, "total": len(proofs)}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# SESSION MANAGEMENT (Pathway preservation)
# ============================================================

def _get_sessions_path() -> Path:
    """Get path to sessions directory."""
    brain = get_brain_path()
    return brain / "sessions"

def _get_active_session_path() -> Path:
    """Get path to active session file."""
    return _get_sessions_path() / "active.json"

def _save_session(context: str, active_task: str = None,
                  pending_decisions: List[str] = None,
                  breadcrumbs: List[str] = None,
                  next_steps: List[str] = None) -> Dict:
    """Save current session state for later resumption.
    
    Creates a session snapshot with:
    - Context name (e.g., "Nucleus v0.5.0", "GentleQuest marketing")
    - Active task being worked on
    - Pending decisions that need resolution
    - Breadcrumbs showing what led to current state
    - Next steps planned
    
    Sessions are per-context-switch (new session when you change projects).
    Keeps last 10 sessions (rolling).
    """
    try:
        sessions_dir = _get_sessions_path()
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate session ID based on context and timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        context_slug = context.lower().replace(" ", "_")[:30]
        session_id = f"{context_slug}_{timestamp}"
        
        # Get current depth state if available
        depth_state = {}
        try:
            depth_state = _get_depth_state()
        except:
            pass
        
        session = {
            "id": session_id,
            "context": context,
            "active_task": active_task or "Not specified",
            "pending_decisions": pending_decisions or [],
            "breadcrumbs": breadcrumbs or [],
            "next_steps": next_steps or [],
            "depth_snapshot": {
                "current_depth": depth_state.get("current_depth", 0),
                "levels": depth_state.get("levels", [])
            },
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "is_active": True
        }
        
        # Save session file
        session_path = sessions_dir / f"{session_id}.json"
        with open(session_path, "w") as f:
            json.dump(session, f, indent=2)
        
        # Update active session pointer
        with open(_get_active_session_path(), "w") as f:
            json.dump({"active_session_id": session_id}, f)
        
        # Prune old sessions (keep last 10)
        _prune_old_sessions(max_sessions=10)
        
        # Emit event for orchestration
        try:
            _emit_event(
                "session_saved",
                "brain_save_session",
                {
                    "session_id": session_id,
                    "context": context,
                    "active_task": active_task or "Not specified",
                    "depth": depth_state.get("current_depth", 0)
                },
                description=f"Session saved: {context}"
            )
        except Exception:
            pass  # Don't fail session save if event emission fails
        
        return {
            "success": True,
            "session_id": session_id,
            "context": context,
            "message": f"Session saved. Resume later with: nucleus sessions resume"
        }
    except Exception as e:
        return {"error": str(e)}

def _prune_old_sessions(max_sessions: int = 10) -> None:
    """Keep only the most recent N sessions."""
    sessions_dir = _get_sessions_path()
    session_files = sorted(
        sessions_dir.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    # Exclude active.json from pruning
    session_files = [f for f in session_files if f.name != "active.json"]
    
    # Remove old sessions beyond the limit
    for old_session in session_files[max_sessions:]:
        old_session.unlink()

def _list_sessions() -> Dict:
    """List all saved sessions."""
    try:
        sessions_dir = _get_sessions_path()
        
        if not sessions_dir.exists():
            return {"sessions": [], "total": 0, "active_session_id": None}
        
        sessions = []
        for session_file in sorted(sessions_dir.glob("*.json"), reverse=True):
            if session_file.name == "active.json":
                continue
            
            with open(session_file) as f:
                session = json.load(f)
            
            sessions.append({
                "id": session.get("id"),
                "context": session.get("context"),
                "active_task": session.get("active_task"),
                "created_at": session.get("created_at"),
                "is_active": session.get("is_active", False)
            })
        
        # Get active session ID
        active_session_id = None
        active_path = _get_active_session_path()
        if active_path.exists():
            with open(active_path) as f:
                active_data = json.load(f)
                active_session_id = active_data.get("active_session_id")
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "active_session_id": active_session_id
        }
    except Exception as e:
        return {"error": str(e)}

def _get_session(session_id: str) -> Dict:
    """Get a specific session by ID."""
    try:
        sessions_dir = _get_sessions_path()
        session_path = sessions_dir / f"{session_id}.json"
        
        if not session_path.exists():
            return {"error": f"Session '{session_id}' not found"}
        
        with open(session_path) as f:
            session = json.load(f)
        
        return {"session": session}
    except Exception as e:
        return {"error": str(e)}

def _resume_session(session_id: str = None) -> Dict:
    """Resume a saved session.
    
    If no session_id provided, resumes the most recent active session.
    Returns the session context for rebuilding mental state.
    """
    try:
        sessions_dir = _get_sessions_path()
        
        # If no session specified, get the active one
        if not session_id:
            active_path = _get_active_session_path()
            if active_path.exists():
                with open(active_path) as f:
                    active_data = json.load(f)
                    session_id = active_data.get("active_session_id")
        
        if not session_id:
            return {
                "error": "No active session found",
                "hint": "Save a session first with brain_save_session()"
            }
        
        # Load the session
        session_result = _get_session(session_id)
        if "error" in session_result:
            return session_result
        
        session = session_result.get("session", {})
        
        # Check if session is recent (<24h)
        created_str = session.get("created_at", "")
        is_recent = True  # Default to recent if can't parse
        try:
            # Simple check - if date matches today or yesterday
            today = time.strftime("%Y-%m-%d")
            session_date = created_str[:10]
            is_recent = session_date == today
        except:
            pass
        
        # Build resume context
        resume_context = {
            "session_id": session_id,
            "context": session.get("context"),
            "active_task": session.get("active_task"),
            "pending_decisions": session.get("pending_decisions", []),
            "breadcrumbs": session.get("breadcrumbs", []),
            "next_steps": session.get("next_steps", []),
            "depth_snapshot": session.get("depth_snapshot", {}),
            "is_recent": is_recent,
            "created_at": created_str
        }
        
        # Format as readable summary
        summary_lines = [
            f"📍 **Resuming: {session.get('context')}**",
            "",
            f"**Active Task:** {session.get('active_task')}",
            ""
        ]
        
        if session.get("pending_decisions"):
            summary_lines.append("**Pending Decisions:**")
            for d in session.get("pending_decisions", []):
                summary_lines.append(f"  • {d}")
            summary_lines.append("")
        
        if session.get("breadcrumbs"):
            summary_lines.append("**How you got here:**")
            summary_lines.append(f"  {' → '.join(session.get('breadcrumbs', []))}")
            summary_lines.append("")
        
        if session.get("next_steps"):
            summary_lines.append("**Planned next steps:**")
            for step in session.get("next_steps", []):
                summary_lines.append(f"  1. {step}")
        
        resume_context["summary"] = "\n".join(summary_lines)
        
        return resume_context
    except Exception as e:
        return {"error": str(e)}

def _check_for_recent_session() -> Dict:
    """Check if there's a recent session (<24h) to offer resumption."""
    try:
        result = _list_sessions()
        if "error" in result or not result.get("sessions"):
            return {"has_recent": False}
        
        # Check most recent session
        most_recent = result["sessions"][0]
        created_str = most_recent.get("created_at", "")
        
        # Check if within 24 hours
        today = time.strftime("%Y-%m-%d")
        session_date = created_str[:10] if created_str else ""
        is_recent = session_date == today
        
        if is_recent:
            return {
                "has_recent": True,
                "session_id": most_recent.get("id"),
                "context": most_recent.get("context"),
                "active_task": most_recent.get("active_task"),
                "prompt": f"Resume where you left off? Context: {most_recent.get('context')}"
            }
        
        return {"has_recent": False}
    except Exception as e:
        return {"has_recent": False, "error": str(e)}

# ============================================================
# BRAIN CONSOLIDATION - TIER 1 (Reversibility-First)
# ============================================================
# Purpose: Automated cleanup of artifact noise without data loss
# Philosophy: MOVE, never DELETE - all actions are reversible

def _get_archive_path() -> Path:
    """Get the path to the archive directory."""
    brain = get_brain_path()
    archive_path = brain / "archive"
    archive_path.mkdir(parents=True, exist_ok=True)
    return archive_path

def _archive_resolved_files() -> Dict:
    """Archive all .resolved.* backup files to archive/resolved/.
    
    These are version snapshot files created by Antigravity when editing.
    Moving them clears visual clutter while preserving file history.
    
    Returns:
        Dict with moved count, archive path, and list of moved files
    """
    try:
        brain = get_brain_path()
        archive_dir = _get_archive_path() / "resolved"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        moved_files = []
        skipped_files = []
        
        # Find all .resolved.* files (pattern: *.resolved or *.resolved.N)
        for f in brain.glob("*.resolved*"):
            if f.is_file():
                try:
                    dest = archive_dir / f.name
                    # Handle duplicate names in archive
                    if dest.exists():
                        base = f.stem
                        suffix = f.suffix
                        counter = 1
                        while dest.exists():
                            dest = archive_dir / f"{base}.dup{counter}{suffix}"
                            counter += 1
                    
                    f.rename(dest)
                    moved_files.append(f.name)
                except Exception as e:
                    skipped_files.append({"file": f.name, "error": str(e)})
        
        # Also check for metadata.json files (Antigravity auto-generated)
        for f in brain.glob("*.metadata.json"):
            if f.is_file():
                try:
                    dest = archive_dir / f.name
                    if dest.exists():
                        base = f.stem
                        suffix = f.suffix
                        counter = 1
                        while dest.exists():
                            dest = archive_dir / f"{base}.dup{counter}{suffix}"
                            counter += 1
                    
                    f.rename(dest)
                    moved_files.append(f.name)
                except Exception as e:
                    skipped_files.append({"file": f.name, "error": str(e)})
        
        # Log the consolidation event
        if moved_files:
            _emit_event(
                "brain_consolidated",
                "BRAIN_CONSOLIDATION",
                {
                    "tier": 1,
                    "action": "archive_resolved",
                    "files_moved": len(moved_files),
                    "archive_path": str(archive_dir)
                },
                f"Archived {len(moved_files)} resolved/metadata files"
            )
        
        return {
            "success": True,
            "files_moved": len(moved_files),
            "files_skipped": len(skipped_files),
            "archive_path": str(archive_dir),
            "moved_files": moved_files[:20],  # Limit output size
            "skipped_files": skipped_files,
            "message": f"Archived {len(moved_files)} files to {archive_dir}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _detect_redundant_artifacts() -> Dict:
    """Detect potentially redundant artifacts based on filename patterns.
    
    Looks for:
    1. Versioned duplicates (file.md vs FILE_V0_4_0.md)
    2. Related synthesis docs (SYNTHESIS_PART1, SYNTHESIS_PART2, etc.)
    3. Stale files (not modified in 30+ days, no references)
    
    Returns:
        Dict with categorized redundancy findings
    """
    try:
        brain = get_brain_path()
        
        findings = {
            "versioned_duplicates": [],
            "related_series": [],
            "stale_files": [],
            "archive_candidates": []
        }
        
        all_files = list(brain.glob("*.md"))
        filenames = {f.stem.lower(): f for f in all_files}
        
        # 1. Detect versioned duplicates
        # e.g., implementation_plan.md vs IMPLEMENTATION_PLAN_V0_4_0.md
        version_patterns = ["_v0", "_v1", "_v2", "_v3", "_v4", "_v5"]
        processed = set()
        
        for f in all_files:
            stem = f.stem.lower()
            
            # Skip if already processed
            if f.name in processed:
                continue
                
            # Check for versioned variant
            for vp in version_patterns:
                if vp in stem:
                    # This IS the versioned file, find the unversioned
                    base_name = stem.split(vp)[0].replace("_", "").strip()
                    
                    # Look for potential match
                    for other_f in all_files:
                        other_stem = other_f.stem.lower().replace("_", "")
                        if other_f != f and base_name in other_stem and vp not in other_f.stem.lower():
                            findings["versioned_duplicates"].append({
                                "old": other_f.name,
                                "new": f.name,
                                "reason": "Versioned file likely supersedes unversioned",
                                "suggestion": "Archive old, keep new"
                            })
                            processed.add(other_f.name)
                            processed.add(f.name)
                            break
        
        # 2. Detect related series (SYNTHESIS_PART1, SYNTHESIS_PART2, etc.)
        series_patterns = {
            "SYNTHESIS_PART": [],
            "RAW_MONOLOGUE_PART": [],
            "DESIGN_": [],
        }
        
        for f in all_files:
            for pattern in series_patterns:
                if pattern in f.stem:
                    series_patterns[pattern].append(f.name)
        
        for pattern, files in series_patterns.items():
            if len(files) > 2:
                findings["related_series"].append({
                    "pattern": pattern,
                    "files": files[:5],  # Limit to first 5
                    "count": len(files),
                    "reason": f"{len(files)} related files in series",
                    "suggestion": f"Consider consolidating into single {pattern.replace('_', '')}ALL.md"
                })
        
        # 3. Detect stale files (30+ days old)
        import time
        thirty_days_ago = time.time() - (30 * 24 * 60 * 60)
        
        for f in all_files:
            if f.stat().st_mtime < thirty_days_ago:
                # Skip key preserved files
                preserved = ["NORTH_STAR", "task", "README", "PROTOCOL"]
                if any(p in f.stem for p in preserved):
                    continue
                    
                findings["stale_files"].append({
                    "file": f.name,
                    "last_modified": time.strftime("%Y-%m-%d", time.localtime(f.stat().st_mtime)),
                    "reason": "Not modified in 30+ days",
                    "suggestion": "Review for archiving"
                })
        
        # 4. Archive candidates (temp files, completed work)
        archive_keywords = ["_exploration", "_proposal", "_draft", "_temp", "_old"]
        for f in all_files:
            stem = f.stem.lower()
            for kw in archive_keywords:
                if kw in stem:
                    findings["archive_candidates"].append({
                        "file": f.name,
                        "keyword": kw,
                        "reason": f"Contains '{kw}' suggesting temporary nature",
                        "suggestion": "Move to archive/"
                    })
                    break
        
        return {
            "success": True,
            "total_files_scanned": len(all_files),
            "findings": findings,
            "summary": {
                "versioned_duplicates": len(findings["versioned_duplicates"]),
                "related_series": len(findings["related_series"]),
                "stale_files": len(findings["stale_files"]),
                "archive_candidates": len(findings["archive_candidates"])
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _generate_merge_proposals() -> Dict:
    """Generate human-readable merge proposal document.
    
    Runs detection and formats results as actionable proposals.
    Does NOT execute any merges - proposals only.
    
    Returns:
        Dict with proposal_text and structured data
    """
    try:
        detection_result = _detect_redundant_artifacts()
        
        if not detection_result.get("success"):
            return detection_result
        
        findings = detection_result.get("findings", {})
        summary = detection_result.get("summary", {})
        
        # Generate markdown proposal
        today = time.strftime("%Y-%m-%d")
        lines = [
            f"# Brain Consolidation Proposals",
            f"",
            f"> **Generated:** {today}  ",
            f"> **Status:** Awaiting human review  ",
            f"> **Action:** None taken - proposals only",
            f"",
            f"---",
            f"",
        ]
        
        # Summary
        total_proposals = sum(summary.values())
        lines.append(f"## Summary")
        lines.append(f"")
        lines.append(f"| Category | Count |")
        lines.append(f"|:---------|:------|")
        lines.append(f"| Versioned Duplicates | {summary.get('versioned_duplicates', 0)} |")
        lines.append(f"| Related Series | {summary.get('related_series', 0)} |")
        lines.append(f"| Stale Files (30+ days) | {summary.get('stale_files', 0)} |")
        lines.append(f"| Archive Candidates | {summary.get('archive_candidates', 0)} |")
        lines.append(f"| **Total Proposals** | **{total_proposals}** |")
        lines.append(f"")
        
        if total_proposals == 0:
            lines.append(f"✅ **Brain is clean!** No consolidation needed.")
            return {
                "success": True,
                "total_proposals": 0,
                "proposal_text": "\n".join(lines),
                "findings": findings
            }
        
        lines.append(f"---")
        lines.append(f"")
        
        # Versioned duplicates section
        if findings.get("versioned_duplicates"):
            lines.append(f"## Versioned Duplicates")
            lines.append(f"")
            lines.append(f"These files appear to have old/new versions. Consider archiving the old one.")
            lines.append(f"")
            for i, dup in enumerate(findings["versioned_duplicates"], 1):
                lines.append(f"### {i}. {dup['old']}")
                lines.append(f"- **Old:** `{dup['old']}`")
                lines.append(f"- **New:** `{dup['new']}`")
                lines.append(f"- **Reason:** {dup['reason']}")
                lines.append(f"- **Suggestion:** {dup['suggestion']}")
                lines.append(f"")
        
        # Related series section
        if findings.get("related_series"):
            lines.append(f"## Related File Series")
            lines.append(f"")
            lines.append(f"These files form related series that could potentially be consolidated.")
            lines.append(f"")
            for i, series in enumerate(findings["related_series"], 1):
                lines.append(f"### {i}. {series['pattern']}* ({series['count']} files)")
                lines.append(f"- **Pattern:** `{series['pattern']}*`")
                lines.append(f"- **Files:** {', '.join(['`' + f + '`' for f in series['files']])}")
                if series['count'] > 5:
                    lines.append(f"  - ... and {series['count'] - 5} more")
                lines.append(f"- **Suggestion:** {series['suggestion']}")
                lines.append(f"")
        
        # Stale files section
        if findings.get("stale_files"):
            lines.append(f"## Stale Files (30+ Days Old)")
            lines.append(f"")
            lines.append(f"These files haven't been modified in 30+ days. Review if still relevant.")
            lines.append(f"")
            for i, stale in enumerate(findings["stale_files"][:10], 1):  # Limit to 10
                lines.append(f"{i}. `{stale['file']}` - Last modified: {stale['last_modified']}")
            if len(findings["stale_files"]) > 10:
                lines.append(f"   ... and {len(findings['stale_files']) - 10} more")
            lines.append(f"")
        
        # Archive candidates section
        if findings.get("archive_candidates"):
            lines.append(f"## Archive Candidates")
            lines.append(f"")
            lines.append(f"These files contain keywords suggesting they're temporary work.")
            lines.append(f"")
            for i, cand in enumerate(findings["archive_candidates"][:10], 1):
                lines.append(f"{i}. `{cand['file']}` - Contains '{cand['keyword']}'")
            if len(findings["archive_candidates"]) > 10:
                lines.append(f"   ... and {len(findings['archive_candidates']) - 10} more")
            lines.append(f"")
        
        # Next steps section
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## Next Steps")
        lines.append(f"")
        lines.append(f"1. Review proposals above")
        lines.append(f"2. To archive files, run: `nucleus consolidate archive`")
        lines.append(f"3. To manually move files: `mv file.md .brain/archive/`")
        lines.append(f"4. Tier 3 (Execute Merges) coming soon...")
        lines.append(f"")
        
        proposal_text = "\n".join(lines)
        
        # Log event
        _emit_event(
            "merge_proposals_generated",
            "BRAIN_CONSOLIDATION",
            {
                "tier": 2,
                "total_proposals": total_proposals,
                "categories": summary
            },
            f"Generated {total_proposals} consolidation proposals"
        )
        
        return {
            "success": True,
            "total_proposals": total_proposals,
            "proposal_text": proposal_text,
            "findings": findings,
            "summary": summary
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# FEATURE MAP TOOLS (MCP wrappers)
# ============================================================



@mcp.tool()
def brain_add_feature(product: str, name: str, description: str, source: str,
                      version: str, how_to_test: List[str], expected_result: str,
                      status: str = "development", tags: List[str] = None) -> Dict:
    """Add a new feature to the product's feature map.
    
    Args:
        product: "gentlequest" or "nucleus"
        name: Human-readable feature name
        description: What the feature does
        source: Where it lives (e.g., "gentlequest_app", "pypi_mcp")
        version: Which version it shipped in
        how_to_test: List of test steps
        expected_result: What should happen when testing
        status: development/staged/production/released
        tags: Searchable tags
    
    Returns:
        Created feature object
    """
    kwargs = {}
    if tags:
        kwargs["tags"] = tags
    return _add_feature(product, name, description, source, version, 
                        how_to_test, expected_result, status, **kwargs)

@mcp.tool()
def brain_list_features(product: str = None, status: str = None, tag: str = None) -> Dict:
    """List all features, optionally filtered.
    
    Args:
        product: Filter by product ("gentlequest" or "nucleus")
        status: Filter by status
        tag: Filter by tag
    
    Returns:
        List of matching features
    """
    return _list_features(product, status, tag)

@mcp.tool()
def brain_get_feature(feature_id: str) -> Dict:
    """Get a specific feature by ID.
    
    Args:
        feature_id: The feature ID (snake_case)
    
    Returns:
        Feature object with test instructions
    """
    return _get_feature(feature_id)

@mcp.tool()
def brain_update_feature(feature_id: str, status: str = None, 
                         description: str = None, version: str = None) -> Dict:
    """Update a feature's fields.
    
    Args:
        feature_id: Feature to update
        status: New status
        description: New description
        version: New version
    
    Returns:
        Updated feature
    """
    updates = {}
    if status:
        updates["status"] = status
    if description:
        updates["description"] = description
    if version:
        updates["version"] = version
    
    if not updates:
        return {"error": "No updates provided"}
    
    return _update_feature(feature_id, **updates)

@mcp.tool()
def brain_mark_validated(feature_id: str, result: str) -> Dict:
    """Mark a feature as validated after testing.
    
    Args:
        feature_id: Feature that was tested
        result: "passed" or "failed"
    
    Returns:
        Updated feature with validation timestamp
    """
    return _mark_validated(feature_id, result)

@mcp.tool()
def brain_search_features(query: str) -> Dict:
    """Search features by name, description, or tags.
    
    Args:
        query: Search query
    
    Returns:
        Matching features
    """
    return _search_features(query)

# ============================================================
# PROOF SYSTEM TOOLS (MCP wrappers)
# ============================================================

@mcp.tool()
def brain_generate_proof(feature_id: str, thinking: str = None,
                         deployed_url: str = None, 
                         files_changed: List[str] = None,
                         risk_level: str = "low",
                         rollback_time: str = "15 minutes") -> Dict:
    """Generate a proof document for a feature.
    
    Creates a markdown proof file with:
    - AI thinking (options, choice, reasoning, fallback)
    - Deployed URL
    - Files changed
    - Rollback plan with risk level
    
    Args:
        feature_id: Feature to generate proof for
        thinking: AI's decision-making process (markdown)
        deployed_url: Production URL
        files_changed: List of files modified
        risk_level: low/medium/high
        rollback_time: Estimated time to rollback
    
    Returns:
        Proof generation result with path
    """
    return _generate_proof(feature_id, thinking, deployed_url, 
                           files_changed, None, risk_level, rollback_time)

@mcp.tool()
def brain_get_proof(feature_id: str) -> Dict:
    """Get the proof document for a feature.
    
    Args:
        feature_id: Feature ID to get proof for
    
    Returns:
        Proof content or message if not found
    """
    return _get_proof(feature_id)

@mcp.tool()
def brain_list_proofs() -> Dict:
    """List all proof documents.
    
    Returns:
        List of proofs with metadata
    """
    return _list_proofs()

# ============================================================
# SESSION MANAGEMENT TOOLS (MCP wrappers)
# ============================================================

@mcp.tool()
def brain_save_session(context: str, active_task: str = None,
                       pending_decisions: List[str] = None,
                       breadcrumbs: List[str] = None,
                       next_steps: List[str] = None) -> Dict:
    """Save current session for later resumption.
    
    Call this when switching contexts or ending a work session.
    The session captures your mental state so you can resume later.
    
    Args:
        context: What you're working on (e.g., "Nucleus v0.5.0", "GentleQuest marketing")
        active_task: Current task being worked on
        pending_decisions: List of decisions that need resolution
        breadcrumbs: List showing what led to current state
        next_steps: Planned next steps
    
    Returns:
        Session save confirmation with session ID
    """
    return _save_session(context, active_task, pending_decisions, breadcrumbs, next_steps)

@mcp.tool()
def brain_resume_session(session_id: str = None) -> Dict:
    """Resume a saved session.
    
    Restores context from a previous session, including:
    - Active task
    - Pending decisions
    - Breadcrumbs (how you got here)
    - Next steps
    
    Args:
        session_id: Optional session ID to resume (defaults to most recent)
    
    Returns:
        Session context with formatted summary
    """
    return _resume_session(session_id)

@mcp.tool()
def brain_list_sessions() -> Dict:
    """List all saved sessions.
    
    Returns:
        List of sessions with metadata (context, task, date)
    """
    return _list_sessions()

@mcp.tool()
def brain_check_recent_session() -> Dict:
    """Check if there's a recent session to offer resumption.
    
    Call this at the start of a new conversation to see if
    the user should be offered to resume their previous work.
    
    Returns:
        Whether a recent session exists with prompt text
    """
    return _check_for_recent_session()

# ============================================================
# BRAIN CONSOLIDATION TOOLS (MCP wrappers)
# ============================================================

@mcp.tool()
def brain_archive_resolved() -> Dict:
    """Archive all .resolved.* backup files to clean up the brain folder.
    
    This moves auto-generated version backup files (created by Antigravity)
    to the archive/resolved/ folder. The files are NOT deleted - they can
    be recovered from the archive at any time.
    
    Safe to run regularly (nightly recommended). Reversible action.
    
    Returns:
        Summary of archived files including count and paths
    """
    return _archive_resolved_files()

@mcp.tool()
def brain_propose_merges() -> Dict:
    """Detect redundant artifacts and generate merge proposals.
    
    Scans the brain folder for:
    - Versioned duplicates (old.md vs NEW_V0_4_0.md)
    - Related series (SYNTHESIS_PART1, PART2, etc.)
    - Stale files (30+ days unmodified)
    - Archive candidates (temp files, drafts)
    
    Returns proposals only - no files are moved or modified.
    Human reviews proposals before any action is taken.
    
    Returns:
        Merge proposals with structured findings and readable report
    """
    return _generate_merge_proposals()

@mcp.tool()
def brain_emit_event(event_type: str, emitter: str, data: Dict[str, Any], description: str = "") -> str:
    """Emit a new event to the brain ledger."""
    return _emit_event(event_type, emitter, data, description)

@mcp.tool()
def brain_read_events(limit: int = 10) -> List[Dict]:
    """Read the most recent events from the ledger."""
    return _read_events(limit)

@mcp.tool()
def brain_get_state(path: Optional[str] = None) -> Dict:
    """Get the current state of the brain."""
    return _get_state(path)

@mcp.tool()
def brain_update_state(updates: Dict[str, Any]) -> str:
    """Update the brain state with new values (shallow merge)."""
    return _update_state(updates)

@mcp.tool()
def brain_read_artifact(path: str) -> str:
    """Read contents of an artifact file (relative to .brain/artifacts)."""
    return _read_artifact(path)

@mcp.tool()
def brain_write_artifact(path: str, content: str) -> str:
    """Write contents to an artifact file."""
    return _write_artifact(path, content)

@mcp.tool()
def brain_list_artifacts(folder: Optional[str] = None) -> List[str]:
    """List artifacts in a folder."""
    return _list_artifacts(folder)

@mcp.tool()
def brain_trigger_agent(agent: str, task_description: str, context_files: List[str] = None) -> str:
    """Trigger an agent by emitting a task_assigned event."""
    return _trigger_agent(agent, task_description, context_files)

@mcp.tool()
def brain_get_triggers() -> List[Dict]:
    """Get all defined neural triggers from triggers.json."""
    return _get_triggers()

@mcp.tool()
def brain_evaluate_triggers(event_type: str, emitter: str) -> List[str]:
    """Evaluate which agents should activate for a given event type and emitter."""
    return _evaluate_triggers(event_type, emitter)

# ============================================================
# V2 TASK MANAGEMENT TOOLS
# ============================================================

@mcp.tool()
def brain_list_tasks(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    skill: Optional[str] = None,
    claimed_by: Optional[str] = None
) -> List[Dict]:
    """List tasks with optional filters.
    
    Args:
        status: Filter by status (PENDING, READY, IN_PROGRESS, BLOCKED, DONE, FAILED, ESCALATED)
        priority: Filter by priority (1=highest, 5=lowest)
        skill: Filter by required skill
        claimed_by: Filter by agent who claimed the task
    
    Returns:
        List of matching tasks
    """
    return _list_tasks(status, priority, skill, claimed_by)

@mcp.tool()
def brain_get_next_task(skills: List[str]) -> Optional[Dict]:
    """Get the highest-priority unblocked task matching the given skills.
    
    Args:
        skills: List of skills the agent has (e.g., ["python", "marketing"])
    
    Returns:
        The next task to work on, or None if no matching tasks
    """
    return _get_next_task(skills)

@mcp.tool()
def brain_claim_task(task_id: str, agent_id: str) -> Dict:
    """Atomically claim a task to prevent race conditions.
    
    Args:
        task_id: The task ID or description to claim
        agent_id: The agent/thread ID claiming the task
    
    Returns:
        Result with success boolean and task or error
    """
    return _claim_task(task_id, agent_id)

@mcp.tool()
def brain_update_task(task_id: str, updates: Dict[str, Any]) -> Dict:
    """Update task fields (status, priority, description, etc.).
    
    Args:
        task_id: The task ID or description to update
        updates: Dictionary of fields to update
    
    Returns:
        Result with success boolean and updated task or error
    """
    return _update_task(task_id, updates)

@mcp.tool()
def brain_add_task(
    description: str,
    priority: int = 3,
    blocked_by: List[str] = None,
    required_skills: List[str] = None,
    source: str = "synthesizer"
) -> Dict:
    """Create a new task in the queue.
    
    Args:
        description: What needs to be done
        priority: 1=highest, 5=lowest (default: 3)
        blocked_by: List of task IDs that must complete first
        required_skills: List of skills needed (e.g., ["python"])
        source: "user" or "synthesizer" (user = priority override)
    
    Returns:
        Result with success boolean and created task or error
    """
    return _add_task(description, priority, blocked_by, required_skills, source)

@mcp.tool()
def brain_escalate(task_id: str, reason: str) -> Dict:
    """Escalate a task to request human help.
    
    Args:
        task_id: The task ID or description to escalate
        reason: Why the agent needs human help
    
    Returns:
        Result with success boolean and updated task or error
    """
    return _escalate_task(task_id, reason)

# ============================================================
# DEPTH TRACKER TOOLS (ADHD Accommodation)
# ============================================================

@mcp.tool()
def brain_depth_push(topic: str) -> Dict:
    """Go deeper into a subtopic. Tracks your position in the conversation tree.
    
    Use this when diving into a sub-problem or branching topic.
    The system will warn (but not block) when you're getting deep.
    
    Args:
        topic: What you're diving into (e.g., "Implementing auth system")
    
    Returns:
        Current depth, breadcrumbs, and any warnings
    """
    return _depth_push(topic)

@mcp.tool()
def brain_depth_pop() -> Dict:
    """Come back up one level in the conversation tree.
    
    Use this when you've finished a subtopic and want to return
    to the parent context.
    
    Returns:
        New depth level and what topic you returned to
    """
    return _depth_pop()

@mcp.tool()
def brain_depth_show() -> Dict:
    """Show current depth state with visual indicator and tree.
    
    Use this to see:
    - Where you are in the conversation tree
    - How deep you've gone
    - The path you took to get here
    
    Returns:
        Full depth state including visual tree and breadcrumbs
    """
    return _depth_show()

@mcp.tool()
def brain_depth_reset() -> Dict:
    """Reset depth to root level (0). Clears all levels.
    
    Use this when starting a completely new topic tree
    or when you want to clear the current session.
    
    Returns:
        Confirmation and new session ID
    """
    return _depth_reset()

@mcp.tool()
def brain_depth_set_max(max_depth: int) -> Dict:
    """Set the maximum safe depth threshold.
    
    Default is 5. Increase if you KNOW you need to go deep.
    Warnings trigger at max-1, danger at max.
    
    Args:
        max_depth: New max (1-10, default 5)
    
    Returns:
        Updated max and current depth indicator
    """
    return _depth_set_max(max_depth)

@mcp.tool()
def brain_depth_map() -> Dict:
    """Generate a visual exploration map of your current session.
    
    Returns a Mermaid diagram showing your exploration path as a tree.
    Nodes are color-coded: 🟢 safe, 🟡 caution, 🔴 danger/rabbit hole.
    
    Use this to get a "Strategy Game" view of where you've been.
    
    Returns:
        Mermaid diagram code and path summary
    """
    return _generate_depth_map()

# ============================================================
# RENDER POLLER TOOLS (Deploy monitoring)
# ============================================================

@mcp.tool()
def brain_list_services() -> str:
    """
    List all Render services to find service IDs.
    Delegates to RenderOps capability.
    """
    try:
        from .runtime.capabilities.render_ops import RenderOps
        return RenderOps().execute_tool("render_list_services", {})
    except Exception as e:
        return f"Error listing services: {e}"


@mcp.tool()
def brain_start_deploy_poll(service_id: str, commit_sha: str = None) -> Dict:
    """Start monitoring a Render deploy. 
    
    Call this after git push to start tracking deploy status.
    The system will log events and you can check status with brain_check_deploy().
    
    Args:
        service_id: Render service ID (e.g., 'srv-abc123')
        commit_sha: Optional Git commit SHA being deployed
    
    Returns:
        Poll ID and instructions for checking status
    """
    return _start_deploy_poll(service_id, commit_sha)

@mcp.tool()
def brain_check_deploy(service_id: str) -> Dict:
    """Check status of an active deploy poll.
    
    Returns elapsed time and instructions. Use mcp_render_list_deploys()
    to get actual status from Render, then call brain_complete_deploy()
    when the deploy finishes.
    
    Args:
        service_id: Render service ID to check
    
    Returns:
        Current poll status and next action hints
    """
    return _check_deploy_status(service_id)

@mcp.tool()
def brain_complete_deploy(service_id: str, success: bool, deploy_url: str = None,
                          error: str = None, run_smoke_test: bool = True) -> Dict:
    """Mark a deploy as complete and optionally run smoke test.
    
    Call this when you see the deploy is 'live' in Render.
    If success=True and deploy_url is provided, runs a health check.
    
    Args:
        service_id: Render service ID
        success: True if deploy succeeded, False if failed
        deploy_url: URL of deployed service (for smoke test)
        error: Error message if deploy failed
        run_smoke_test: Whether to run health check (default True)
    
    Returns:
        Final status with smoke test results
    """
    return _complete_deploy(service_id, success, deploy_url, error, run_smoke_test)

@mcp.tool()
def brain_smoke_test(url: str, endpoint: str = "/api/health") -> Dict:
    """Run a smoke test on any URL.
    
    Useful for quick health checks without full deploy workflow.
    
    Args:
        url: Base URL of service (e.g., 'https://myapp.onrender.com')
        endpoint: Health endpoint to hit (default: '/api/health')
    
    Returns:
        Smoke test result with pass/fail and latency
    """
    return _run_smoke_test(url, endpoint)

# ============================================================
# MCP RESOURCES (Subscribable data)
# ============================================================

@mcp.resource("brain://state")
def resource_state() -> str:
    """Live state.json content - subscribable."""
    state = _get_state()
    return json.dumps(state, indent=2)

@mcp.resource("brain://events")
def resource_events() -> str:
    """Recent events - subscribable."""
    events = _read_events(limit=20)
    return json.dumps(events, indent=2)

@mcp.resource("brain://triggers")
def resource_triggers() -> str:
    """Trigger definitions - subscribable."""
    triggers = _get_triggers()
    return json.dumps(triggers, indent=2)

@mcp.resource("brain://depth")
def resource_depth() -> str:
    """Current depth tracking state - subscribable. Shows where you are in the conversation tree."""
    depth_state = _depth_show()
    return json.dumps(depth_state, indent=2)

@mcp.resource("brain://context")
def resource_context() -> str:
    """Full context for cold start - auto-visible in sidebar. Click this first in any new session."""
    try:
        brain = get_brain_path()
        state = _get_state()
        sprint = state.get("current_sprint", {})
        agents = state.get("active_agents", [])
        actions = state.get("top_3_leverage_actions", [])
        
        # Format actions
        actions_text = ""
        if actions:
            for i, action in enumerate(actions[:3], 1):
                if isinstance(action, dict):
                    actions_text += f"  {i}. {action.get('action', 'Unknown')}\n"
                else:
                    actions_text += f"  {i}. {action}\n"
        else:
            actions_text = "  (None set)"
        
        # Recent events
        events = _read_events(limit=3)
        events_text = ""
        for evt in events:
            events_text += f"  - {evt.get('type', 'unknown')}: {evt.get('description', '')[:50]}\n"
        if not events_text:
            events_text = "  (No recent events)"
        
        # Check for workflow
        workflow_hint = ""
        workflow_path = brain / "workflows" / "lead_agent_model.md"
        if workflow_path.exists():
            workflow_hint = "📋 Workflow: Read .brain/workflows/lead_agent_model.md for coordination rules"
        
        return f"""# Nucleus Brain Context

## Current Sprint
- Name: {sprint.get('name', 'No active sprint')}
- Focus: {sprint.get('focus', 'Not set')}
- Status: {sprint.get('status', 'Unknown')}

## Active Agents
{', '.join(agents) if agents else 'None'}

## Top Priorities
{actions_text}
## Recent Activity
{events_text}
{workflow_hint}

---
You are the Lead Agent. Use brain_* tools to explore and act."""
    except Exception as e:
        return f"Error loading context: {str(e)}"

# ============================================================
# MCP PROMPTS (Pre-built orchestration)
# ============================================================

@mcp.prompt()
def activate_synthesizer() -> str:
    """Activate Synthesizer agent to orchestrate the current sprint."""
    state = _get_state()
    sprint = state.get("current_sprint", {})
    return f"""You are the Synthesizer, the orchestrating intelligence of this Nuclear Brain.

Current Sprint: {sprint.get('name', 'Unknown')}
Focus: {sprint.get('focus', 'Unknown')}

Your job is to:
1. Review the current state and recent events
2. Determine which agents need to be activated
3. Emit appropriate task_assigned events

Use the available brain_* tools to coordinate the agents."""

@mcp.prompt()
def start_sprint(goal: str = "MVP Launch") -> str:
    """Initialize a new sprint with the given goal."""
    return f"""Initialize a new sprint with goal: {goal}

Steps:
1. Use brain_update_state to set current_sprint with name, focus, and start date
2. Use brain_emit_event to emit a sprint_started event
3. Identify top 3 leverage actions and emit task_assigned events for each

Goal: {goal}"""

@mcp.prompt()
def cold_start() -> str:
    """Get instant context when starting a new session. Call this first in any new conversation."""
    try:
        brain = get_brain_path()
        state = _get_state()
        sprint = state.get("current_sprint", {})
        agents = state.get("active_agents", [])
        actions = state.get("top_3_leverage_actions", [])
        
        # Format top actions
        actions_text = ""
        if actions:
            for i, action in enumerate(actions[:3], 1):
                if isinstance(action, dict):
                    actions_text += f"{i}. {action.get('action', 'Unknown')}\n"
                else:
                    actions_text += f"{i}. {action}\n"
        else:
            actions_text = "None set - check state.json"
        
        # Recent events
        events = _read_events(limit=5)
        events_text = ""
        for evt in events[-3:]:  # Show last 3
            evt_type = evt.get('type', 'unknown')
            evt_desc = evt.get('description', '')[:40]
            events_text += f"- {evt_type}: {evt_desc}\n"
        if not events_text:
            events_text = "(No recent events)"
        
        # Check for workflow
        workflow_hint = ""
        workflow_path = brain / "workflows" / "lead_agent_model.md"
        if workflow_path.exists():
            workflow_hint = "\n📋 **Coordination:** Read `.brain/workflows/lead_agent_model.md` for multi-tool rules."
        
        # Recent artifacts
        artifacts = _list_artifacts()[:5]
        artifacts_text = ", ".join([a.split("/")[-1] for a in artifacts]) if artifacts else "None"
        
        return f"""# Nucleus Cold Start

You are now connected to a Nucleus Brain.

## Current State
- **Sprint:** {sprint.get('name', 'No active sprint')}
- **Focus:** {sprint.get('focus', 'Not set')}
- **Status:** {sprint.get('status', 'Unknown')}
- **Active Agents:** {', '.join(agents) if agents else 'None'}

## Top Priorities
{actions_text}
## Recent Activity
{events_text}
## Recent Artifacts
{artifacts_text}
{workflow_hint}

---

## Your Role
You are now the **Lead Agent** for this session.
- No strict role restrictions - you can do code, strategy, research
- Use brain_* tools to read/write state and artifacts
- Emit events to coordinate with other agents

What would you like to work on?"""
    except Exception as e:
        return f"""# Nucleus Cold Start

⚠️ Could not load brain state: {str(e)}

Make sure NUCLEAR_BRAIN_PATH is set correctly.

You can still use brain_* tools to explore the brain manually."""

# ============================================================
# SATELLITE VIEW (Unified Status Dashboard)
# ============================================================

def _generate_sparkline(counts: List[int], chars: str = "▁▂▃▄▅▆▇█") -> str:
    """Generate a sparkline string from a list of counts."""
    if not counts or max(counts) == 0:
        return "▁" * len(counts) if counts else "▁▁▁▁▁▁▁"
    
    max_val = max(counts)
    scale = (len(chars) - 1) / max_val
    return "".join(chars[int(c * scale)] for c in counts)


def _get_activity_sparkline(days: int = 7) -> Dict:
    """Get activity sparkline for the last N days from events.jsonl."""
    try:
        brain = get_brain_path()
        
        # Fast path: use precomputed summary if available (Tier 2)
        summary_path = brain / "ledger" / "activity_summary.json"
        if summary_path.exists():
            try:
                from datetime import datetime, timedelta
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                
                # Build counts from summary
                today = datetime.now().date()
                counts = []
                day_labels = []
                for i in range(days - 1, -1, -1):
                    day = (today - timedelta(days=i)).isoformat()
                    counts.append(summary.get("days", {}).get(day, 0))
                    day_labels.append(day)
                
                if sum(counts) > 0:  # Only use if we have data
                    peak_idx = counts.index(max(counts)) if counts else 0
                    peak_day = day_labels[peak_idx] if day_labels else None
                    return {
                        "sparkline": _generate_sparkline(counts),
                        "total_events": sum(counts),
                        "peak_day": peak_day,
                        "days_covered": days,
                        "source": "precomputed"
                    }
            except:
                pass  # Fall through to slow path
        
        # Slow path: read events.jsonl
        events_path = brain / "ledger" / "events.jsonl"
        
        if not events_path.exists():
            return {
                "sparkline": "▁▁▁▁▁▁▁",
                "total_events": 0,
                "peak_day": None,
                "days_covered": days
            }

        
        # Read last 500 events (performance optimization)
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        day_counts = defaultdict(int)
        today = datetime.now().date()
        
        # Read events efficiently (tail approach)
        events = []
        with open(events_path, "r") as f:
            for line in f:
                if line.strip():
                    events.append(line)
        
        # Only process last 500 events
        for line in events[-500:]:
            try:
                evt = json.loads(line)
                timestamp = evt.get("timestamp", "")
                if timestamp:
                    # Parse timestamp (format: 2026-01-06T14:00:00+0530)
                    evt_date = timestamp[:10]  # Get YYYY-MM-DD
                    day_counts[evt_date] += 1
            except:
                pass
        
        # Build counts for last N days
        counts = []
        day_labels = []
        for i in range(days - 1, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            counts.append(day_counts.get(day, 0))
            day_labels.append(day)
        
        # Find peak day
        peak_idx = counts.index(max(counts)) if counts else 0
        peak_day = day_labels[peak_idx] if day_labels else None
        
        return {
            "sparkline": _generate_sparkline(counts),
            "total_events": sum(counts),
            "peak_day": peak_day,
            "days_covered": days
        }
    except Exception as e:
        return {
            "sparkline": "▁▁▁▁▁▁▁",
            "total_events": 0,
            "peak_day": None,
            "error": str(e)
        }


def _get_health_stats() -> Dict:
    """Get brain health statistics."""
    try:
        brain = get_brain_path()
        artifacts_path = brain / "artifacts"
        archive_path = brain / "archive"
        
        # Count artifacts
        artifacts_count = 0
        if artifacts_path.exists():
            artifacts_count = len(list(artifacts_path.rglob("*.md")))
        
        # Count archived files
        archive_count = 0
        if archive_path.exists():
            archive_count = len(list(archive_path.rglob("*")))
        
        # Count stale files (older than 30 days)
        stale_count = 0
        import time
        now = time.time()
        thirty_days_ago = now - (30 * 24 * 60 * 60)
        
        if artifacts_path.exists():
            for f in artifacts_path.rglob("*.md"):
                if f.stat().st_mtime < thirty_days_ago:
                    stale_count += 1
        
        return {
            "artifacts_count": artifacts_count,
            "archive_count": archive_count,
            "stale_count": stale_count
        }
    except Exception as e:
        return {
            "artifacts_count": 0,
            "archive_count": 0,
            "stale_count": 0,
            "error": str(e)
        }


def _get_satellite_view(detail_level: str = "standard") -> Dict:
    """
    Get unified satellite view of the brain.
    
    Detail levels:
    - "minimal": depth only (1 file read)
    - "standard": depth + activity + health (3 reads)
    - "full": depth + activity + health + session (4 reads)
    """
    result = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "detail_level": detail_level
    }
    
    # Always include depth
    try:
        depth = _depth_show()
        result["depth"] = {
            "current": depth.get("current_depth", 0),
            "max": depth.get("max_safe_depth", 5),
            "breadcrumbs": depth.get("breadcrumbs", ""),
            "indicator": depth.get("indicator", "🟢 ○○○○○")
        }
    except:
        result["depth"] = {
            "current": 0,
            "max": 5,
            "breadcrumbs": "(not tracked)",
            "indicator": "⚪ ○○○○○"
        }
    
    if detail_level == "minimal":
        return result
    
    # Standard: add activity and health
    result["activity"] = _get_activity_sparkline(days=7)
    result["health"] = _get_health_stats()
    
    # Add commitment health (PEFS Phase 2)
    try:
        ledger = commitment_ledger.load_ledger(brain)
        stats = ledger.get("stats", {})
        result["commitments"] = {
            "total_open": stats.get("total_open", 0),
            "green": stats.get("green_tier", 0),
            "yellow": stats.get("yellow_tier", 0),
            "red": stats.get("red_tier", 0),
            "last_scan": ledger.get("last_scan")
        }
    except:
        result["commitments"] = None
    
    if detail_level == "standard":
        return result
    
    # Sprint: add current sprint and active tasks
    if detail_level in ("sprint", "full"):
        try:
            state = _get_state()
            sprint = state.get("sprint", {})
            result["sprint"] = {
                "name": sprint.get("name", "(no sprint)"),
                "focus": sprint.get("focus", ""),
                "status": sprint.get("status", "")
            }
            
            # Get active tasks (top 3 priority)
            try:
                tasks = _list_tasks()
                active_tasks = [t for t in tasks if t.get("status") in ("READY", "IN_PROGRESS")][:3]
                result["active_tasks"] = [
                    {"id": t.get("id", ""), "description": t.get("description", "")[:40]}
                    for t in active_tasks
                ]
            except:
                result["active_tasks"] = []
        except:
            result["sprint"] = None
            result["active_tasks"] = []
    
    if detail_level == "sprint":
        return result
    
    # Full: add session info
    try:
        sessions = _list_sessions()
        if sessions:
            latest = sessions[0]
            result["session"] = {
                "id": latest.get("session_id", ""),
                "context": latest.get("context", ""),
                "active_task": latest.get("active_task", ""),
                "saved_at": latest.get("saved_at", "")
            }
        else:
            result["session"] = None
    except:
        result["session"] = None
    
    return result



def _format_satellite_cli(view: Dict) -> str:
    """Format satellite view for CLI output."""
    lines = []
    
    # Header
    lines.append("╭─────────────────────────────────────────────────────────╮")
    lines.append("│  🧠 NUCLEUS SATELLITE VIEW                              │")
    lines.append("├─────────────────────────────────────────────────────────┤")
    lines.append("│                                                         │")
    
    # Depth
    depth = view.get("depth", {})
    indicator = depth.get("indicator", "⚪ ○○○○○")
    breadcrumbs = depth.get("breadcrumbs", "(not tracked)")
    # Truncate breadcrumbs if too long
    if len(breadcrumbs) > 45:
        breadcrumbs = breadcrumbs[:42] + "..."
    lines.append(f"│  📍 DEPTH: {indicator:<45} │")
    lines.append(f"│     {breadcrumbs:<52} │")
    lines.append("│                                                         │")
    
    # Activity (if present)
    activity = view.get("activity")
    if activity:
        sparkline = activity.get("sparkline", "▁▁▁▁▁▁▁")
        total = activity.get("total_events", 0)
        peak = activity.get("peak_day", "")
        if peak:
            peak_short = peak[5:]  # Remove year, show MM-DD
        else:
            peak_short = "N/A"
        lines.append(f"│  📈 ACTIVITY (7d): {sparkline}  ({total} events, peak: {peak_short:<5}) │")
        lines.append("│                                                         │")
    
    # Sprint (if present)
    sprint = view.get("sprint")
    if sprint:
        sprint_name = sprint.get("name", "(no sprint)")[:40]
        sprint_focus = sprint.get("focus", "")[:40]
        lines.append(f"│  🎯 SPRINT: {sprint_name:<45} │")
        if sprint_focus:
            lines.append(f"│     Focus: {sprint_focus:<46} │")
        
        # Active tasks (if present)
        active_tasks = view.get("active_tasks", [])
        if active_tasks:
            lines.append("│     Tasks:                                              │")
            for task in active_tasks[:3]:
                task_desc = task.get("description", "")[:42]
                lines.append(f"│       • {task_desc:<49} │")
        lines.append("│                                                         │")
    
    # Session (if present)
    session = view.get("session")
    if session:
        context = session.get("context", "(none)")[:40]
        task = session.get("active_task", "(none)")[:40]
        lines.append(f"│  🔥 SESSION: {context:<44} │")
        lines.append(f"│     Task: {task:<47} │")
        lines.append("│                                                         │")
    
    # Health (if present)
    health = view.get("health")
    if health:
        artifacts = health.get("artifacts_count", 0)
        archived = health.get("archive_count", 0)
        stale = health.get("stale_count", 0)
        lines.append("│  🏥 HEALTH                                              │")
        lines.append(f"│     Artifacts: {artifacts} active | {archived} archived{' ' * (28 - len(str(artifacts)) - len(str(archived)))} │")
        if stale > 0:
            lines.append(f"│     ⚠️  {stale} stale files (30+ days){' ' * (36 - len(str(stale)))} │")
        lines.append("│                                                         │")
    
    # Commitments (PEFS - if present)
    commitments = view.get("commitments")
    if commitments:
        total = commitments.get("total_open", 0)
        green = commitments.get("green", 0)
        yellow = commitments.get("yellow", 0)
        red = commitments.get("red", 0)
        
        # Mental load indicator
        if red > 0:
            load = "🔴"
        elif yellow > 2:
            load = "🟡"
        elif total == 0:
            load = "✨"
        else:
            load = "🟢"
        
        lines.append(f"│  🎯 COMMITMENTS {load}                                       │")
        lines.append(f"│     Open loops: {total} (🟢{green} 🟡{yellow} 🔴{red}){' ' * (27 - len(str(total)) - len(str(green)) - len(str(yellow)) - len(str(red)))} │")
        lines.append("│                                                         │")
    
    # Footer
    lines.append("╰─────────────────────────────────────────────────────────╯")
    
    return "\n".join(lines)


@mcp.tool()
def brain_satellite_view(detail_level: str = "standard") -> str:
    """
    Get unified satellite view of the brain.
    
    Shows depth, activity, health, and session in one view.
    
    Args:
        detail_level: "minimal", "standard", or "full"
    
    Returns:
        Formatted satellite view
    """
    view = _get_satellite_view(detail_level)
    return _format_satellite_cli(view)

# ============================================================
# COMMITMENT LEDGER MCP TOOLS (PEFS Phase 2)
# ============================================================

@mcp.tool()
def brain_scan_commitments() -> str:
    """
    Scan artifacts for new commitments (checklists, TODOs).
    Updates the ledger with any new items found.
    (MDR_005 Compliant: Logic moved to shared library)
    
    Returns:
        Scan results
    """
    try:
        brain = get_brain_path()
        result = commitment_ledger.scan_for_commitments(brain)
        return f"✅ Scan complete. Found {result.get('new_found', 0)} new items."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_archive_stale() -> str:
    """
    Auto-archive commitments older than 30 days.
    
    Returns:
        Count of archived items
    """
    try:
        brain = get_brain_path()
        count = commitment_ledger.auto_archive_stale(brain)
        return f"✅ Archive complete. Archived {count} stale items."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_export() -> str:
    """
    Export the brain content to a zip file in .brain/exports/.
    Respects .brain/.brainignore patterns to protect IP.
    (MDR_008 Compliance)
    
    Returns:
        Path to the exported zip file
    """
    try:
        brain = get_brain_path()
        if hasattr(commitment_ledger, 'export_brain'):
            result = commitment_ledger.export_brain(brain)
            return f"✅ {result}"
        return "Error: export_brain validation failed (function missing)."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_list_commitments(tier: str = None) -> str:
    """
    List all open commitments.
    
    Args:
        tier: Optional filter by tier ("green", "yellow", "red")
    
    Returns:
        List of open commitments with details
    """
    try:
        brain = get_brain_path()
        ledger = commitment_ledger.load_ledger(brain)
        
        # Filter open commitments by tier if specified
        all_commitments = ledger.get('commitments', [])
        commitments = [c for c in all_commitments if c.get('status') == 'open']
        if tier:
            commitments = [c for c in commitments if c.get('tier') == tier]
        
        if not commitments:
            return "✅ No open commitments!"
        
        output = f"**Open Commitments ({len(commitments)} total)**\n\n"
        
        for comm in commitments:
            tier_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(comm["tier"], "⚪")
            output += f"{tier_emoji} **{comm['description'][:60]}**\n"
            output += f"   Age: {comm['age_days']} days | Suggested: {comm['suggested_action']}\n"
            output += f"   Reason: {comm['suggested_reason']}\n"
            output += f"   ID: `{comm['id']}`\n\n"
        
        return output
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_close_commitment(commitment_id: str, method: str) -> str:
    """
    Close a commitment with specified method.
    
    Args:
        commitment_id: The commitment ID (e.g., comm_20260106_163000_0)
        method: Closure method (do_now, scheduled, archived, killed, delegated)
    
    Returns:
        Confirmation with updated commitment
    """
    try:
        brain = get_brain_path()
        commitment = commitment_ledger.close_commitment(brain, commitment_id, method)
        
        # Emit event
        _emit_event(
            "commitment_closed",
            "user",
            {"commitment_id": commitment_id, "method": method},
            description=f"Closed: {commitment['description'][:50]}"
        )
        
        return f"""✅ Commitment closed!

**Description:** {commitment['description']}
**Method:** {method}
**Was open:** {commitment['age_days']} days
**Closed at:** {commitment['closed_at']}"""
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_commitment_health() -> str:
    """
    Get commitment health summary.
    
    Shows open loop count, tier breakdown, and mental load estimate.
    Useful for quick status check.
    
    Returns:
        Health summary with actionable insights
    """
    try:
        brain = get_brain_path()
        ledger = commitment_ledger.load_ledger(brain)
        stats = ledger.get("stats", {})
        
        total = stats.get("total_open", 0)
        green = stats.get("green_tier", 0)
        yellow = stats.get("yellow_tier", 0)
        red = stats.get("red_tier", 0)
        by_type = stats.get("by_type", {})
        
        # Mental load calculation
        if red > 0:
            mental_load = "🔴 HIGH"
            advice = "Focus on red-tier items first"
        elif yellow > 2:
            mental_load = "🟡 MEDIUM"
            advice = "Clear yellow items before they go red"
        elif total == 0:
            mental_load = "✨ ZERO"
            advice = "No open loops - guilt-free operation!"
        else:
            mental_load = "🟢 LOW"
            advice = "Looking good, maintain momentum"
        
        # Format by_type
        type_str = ", ".join([f"{t}: {c}" for t, c in by_type.items()]) if by_type else "(none)"
        
        return f"""## 🎯 Commitment Health

**Open loops:** {total}
- 🟢 Green: {green}
- 🟡 Yellow: {yellow}
- 🔴 Red: {red}

**By type:** {type_str}

**Mental load:** {mental_load}
**Advice:** {advice}

**Last scan:** {ledger.get('last_scan', 'Never')[:16] if ledger.get('last_scan') else 'Never'}"""
    except Exception as e:
        return f"Error: {e}"

# ============================================================
# CLOUD INTEGRATION TOOLS
# ============================================================

@mcp.tool()
def brain_list_services() -> str:
    """
    List all Render services to find service IDs.
    Delegates to RenderOps capability.
    
    Returns:
        List of services with IDs
    """
    try:
        from .runtime.capabilities.render_ops import RenderOps
        cap = RenderOps()
        return cap.execute_tool("render_list_services", {})
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_open_loops(
    type_filter: str = None,
    tier_filter: str = None
) -> str:
    """
    Unified view of ALL open loops (tasks, todos, drafts, decisions).
    
    This is the single source of truth for what needs attention.
    Replaces the need to check separate task/commitment systems.
    
    Args:
        type_filter: Filter by type ("task", "todo", "draft", "decision")
        tier_filter: Filter by tier ("green", "yellow", "red")
    
    Returns:
        All open loops grouped by type and priority
    """
    try:
        brain = get_brain_path()
        ledger = commitment_ledger.load_ledger(brain)
        
        open_comms = [c for c in ledger["commitments"] if c["status"] == "open"]
        
        # Apply filters
        if type_filter:
            open_comms = [c for c in open_comms if c.get("type") == type_filter]
        if tier_filter:
            open_comms = [c for c in open_comms if c.get("tier") == tier_filter]
        
        if not open_comms:
            return "✅ No open loops! Guilt-free operation."
        
        # Group by type
        by_type = {}
        for c in open_comms:
            t = c.get("type", "unknown")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(c)
        
        # Build output
        output = f"## 📋 Open Loops ({len(open_comms)} total)\n\n"
        
        type_emoji = {"task": "🔧", "todo": "☑️", "draft": "📝", "decision": "🤔"}
        
        for t, items in by_type.items():
            emoji = type_emoji.get(t, "📌")
            output += f"### {emoji} {t.upper()} ({len(items)})\n\n"
            
            # Sort by tier (red first) then age
            items.sort(key=lambda x: ({"red": 0, "yellow": 1, "green": 2}.get(x.get("tier"), 3), -x.get("age_days", 0)))
            
            for c in items[:5]:  # Max 5 per type
                tier_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(c.get("tier"), "⚪")
                output += f"{tier_emoji} **{c['description'][:50]}**\n"
                output += f"   {c.get('age_days', 0)}d old | Suggested: {c.get('suggested_action')}\n"
                output += f"   ID: `{c['id']}`\n\n"
            
            if len(items) > 5:
                output += f"   ...and {len(items) - 5} more\n\n"
        
        return output
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_add_loop(
    description: str,
    loop_type: str = "task",
    priority: int = 3
) -> str:
    """
    Manually add a new open loop (task, todo, draft, or decision).
    
    Use this when you want to track something that isn't in a document.
    
    Args:
        description: What needs to be done
        loop_type: Type of loop ("task", "todo", "draft", "decision")
        priority: 1-5, lower is higher priority
    
    Returns:
        Created loop details
    """
    try:
        brain = get_brain_path()
        commitment = commitment_ledger.add_commitment(
            brain,
            source_file="manual",
            source_line=0,
            description=description,
            comm_type=loop_type,
            source="manual",
            priority=priority
        )
        
        # Emit event for orchestration
        try:
            _emit_event(
                "commitment_created",
                "brain_add_loop",
                {
                    "commitment_id": commitment['id'],
                    "type": loop_type,
                    "description": description[:60],
                    "priority": priority,
                    "tier": commitment.get('tier', 'green')
                },
                description=f"New {loop_type}: {description[:40]}"
            )
        except Exception:
            pass  # Don't fail loop creation if event emission fails
        
        return f"""✅ Loop created!

**ID:** `{commitment['id']}`
**Type:** {loop_type}
**Description:** {description}
**Priority:** {priority}
**Suggested:** {commitment['suggested_action']} - {commitment['suggested_reason']}"""
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_weekly_challenge(
    action: str = "get",  # get, set, list
    challenge_id: str = None
) -> str:
    """
    Manage the weekly growth challenge.
    
    Args:
        action: "get" (current status), "set" (start new), "list" (show options)
        challenge_id: ID of challenge to set (if action="set")
    
    Returns:
        Challenge status or list of options
    """
    try:
        brain = get_brain_path()
        
        if action == "list":
            challenges = commitment_ledger.get_starter_challenges()
            output = "## 🏆 Weekly Challenges\n\n"
            for c in challenges:
                output += f"**{c['title']}** (`{c['id']}`)\n"
                output += f"{c['description']}\n"
                output += f"🏆 Reward: {c['reward']}\n\n"
            return output
            
        if action == "set":
            if not challenge_id:
                return "⚠️ Please provide `challenge_id` to set a challenge."
            
            challenges = commitment_ledger.get_starter_challenges()
            selected = next((c for c in challenges if c["id"] == challenge_id), None)
            
            if not selected:
                return f"❌ Challenge `{challenge_id}` not found."
            
            # Start fresh
            selected["started_at"] = datetime.now().isoformat()
            selected["status"] = "active"
            commitment_ledger.set_challenge(brain, selected)
            
            return f"✅ **Challenge Accepted: {selected['title']}**\n\nGoal: {selected['description']}\nGo get it!"
            
        # Default: get
        challenge = commitment_ledger.load_challenge(brain)
        if not challenge:
            return "No active challenge. Run `brain_weekly_challenge(action='list')` to pick one!"
            
        return f"""## 🏆 Current Challenge: {challenge['title']}

📝 **Goal:** {challenge['description']}
📅 **Started:** {challenge['started_at'][:10]}
🎁 **Reward:** {challenge['reward']}

Keep pushing!"""

    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_patterns(
    action: str = "list",  # list, learn
) -> str:
    """
    Manage learned patterns for commitment closure.
    
    Args:
        action: "list" (show learned patterns), "learn" (scan ledger for new patterns)
    
    Returns:
        List of patterns or learning result
    """
    try:
        brain = get_brain_path()
        
        if action == "learn":
            patterns = commitment_ledger.learn_patterns(brain)
            return f"✅ Learning complete. Total patterns: {len(patterns)}"
            
        # List
        patterns = commitment_ledger.load_patterns(brain)
        if not patterns:
            return "No patterns learned yet. Run `brain_patterns(action='learn')` after closing some items!"
            
        output = "## 🧠 Learned Patterns\n\n"
        for p in patterns:
            output += f"**{p['name']}**\n"
            output += f"• Keywords: {', '.join(p['keywords'])}\n"
            output += f"• Action: {p['action']}\n\n"
            
        return output

    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_metrics() -> str:
    """
    Get coordination metrics (velocity, closure rates, mental load).
    
    Returns:
        Formatted metrics report
    """
    try:
        brain = get_brain_path()
        metrics = commitment_ledger.calculate_metrics(brain)
        
        output = "## 📊 Coordination Metrics (Last 7 Days)\n\n"
        output += f"**🚀 Velocity:** {metrics['velocity_7d']} items closed\n"
        output += f"**⏱️ Speed:** {metrics['avg_days_to_close']} days avg to close\n\n"
        
        output += "**📈 Closure Rates by Type:**\n"
        if metrics['closure_rates']:
            for t, rate in metrics['closure_rates'].items():
                output += f"- {t}: {rate}\n"
        else:
            output += "(No closed items yet)\n"
            
        output += "\n**🧠 Current Load:**\n"
        output += f"- Total Open: {metrics['current_load']['total']}\n"
        output += f"- Red Tier: {metrics['current_load']['red']}\n"
        
        return output

    except Exception as e:
        return f"Error: {e}"

    except Exception as e:
        return f"Error: {e}"

def _generate_proof(feature_id: str, thinking: str = "", deployed_url: str = "", files_changed: List[str] = [], risk_level: str = "low", rollback_time: str = "15m") -> Dict[str, Any]:
    """Core logic wrapper for generating a proof."""
    try:
        from .runtime.capabilities.proof_system import ProofSystem
        proof_sys = ProofSystem()
        return proof_sys._generate_proof({
            "feature_id": feature_id,
            "thinking": thinking,
            "deployed_url": deployed_url,
            "files_changed": files_changed,
            "risk_level": risk_level,
            "rollback_time": rollback_time
        })
    except Exception as e:
        return {"error": str(e)}

def _get_proof(feature_id: str) -> Dict[str, Any]:
    """Core logic wrapper for getting a proof."""
    try:
        from .runtime.capabilities.proof_system import ProofSystem
        proof_sys = ProofSystem()
        content = proof_sys._get_proof(feature_id)
        if content.startswith("Proof for"): # Not found message
             return {"exists": False, "message": content}
        return {"exists": True, "content": content}
    except Exception as e:
        return {"error": str(e)}

from mcp_server_nucleus.runtime.factory import ContextFactory
from mcp_server_nucleus.runtime.agent import EphemeralAgent

@mcp.tool()
async def brain_spawn_agent(
    intent: str,
    execute_now: bool = True
) -> str:
    """
    Spawn an Ephemeral Agent via the Nucleus Agent Runtime (NAR).
    The factory constructs a context based on intent and launches a disposable agent.
    MDR_044: Now uses Dual-Engine LLM (google.genai + fallback).
    
    Args:
        intent: The high-level goal (e.g., "Deploy production service")
        execute_now: Whether to run immediately or just return the plan.
        
    Returns:
        Execution log or plan details.
    """
    try:
        from uuid import uuid4
        from .runtime.llm_client import DualEngineLLM
        
        session_id = f"spawn-{str(uuid4())[:8]}"
        factory = ContextFactory()
        context = factory.create_context(session_id, intent)
        
        output = f"## 🏭 NAR Factory Receipt\n"
        output += f"**Intent:** {intent}\n"
        output += f"**Capabilities:** {', '.join(context['capabilities'])}\n"
        output += f"**Tools Mapped:** {len(context['tools'])}\n"
        
        if not context['tools']:
            return output + "\n❌ No tools mapped. Agent would be powerless."
            
        if execute_now:
            output += "\n--- Executive Trace (Dual-Engine) ---\n"
            
            # Initialize with Dual-Engine (New + Legacy fallback)
            llm = DualEngineLLM()
            output += f">> 🧠 Active Engine: {llm.active_engine}\n"
            
            agent = EphemeralAgent(context, model=llm)
            log = await agent.run()
            output += log + "\n"
            output += "✅ Ephemeral Agent executed and terminated.\n"
            
        return output

    except Exception as e:
        return f"Error spawning agent: {e}"

# ============================================================
# MDR_010: USAGE TELEMETRY & FEEDBACK MCP TOOLS
# ============================================================

@mcp.tool()
def brain_record_interaction() -> str:
    """
    Record a user interaction timestamp (MDR_010).
    Call this when the user engages with any brain functionality.
    """
    try:
        brain = get_brain_path()
        commitment_ledger.record_interaction(brain)
        return "✅ Interaction recorded"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_value_ratio() -> str:
    """
    Get the Value Ratio metric (MDR_010).
    Value Ratio = High Impact Closures / Notifications Sent.
    """
    try:
        brain = get_brain_path()
        ratio = commitment_ledger.calculate_value_ratio(brain)
        output = "## 📊 Value Ratio (MDR_010)\n\n"
        output += f"**Notifications Sent:** {ratio['notifications_sent']}\n"
        output += f"**High Impact Closures:** {ratio['high_impact_closed']}\n"
        output += f"**Ratio:** {ratio['ratio']}\n"
        output += f"**Verdict:** {ratio['verdict']}\n"
        return output
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_check_kill_switch() -> str:
    """
    Check Kill Switch status (MDR_010).
    Detects inactivity and suggests pausing notifications.
    """
    try:
        brain = get_brain_path()
        status = commitment_ledger.check_kill_switch(brain)
        output = "## 🛑 Kill Switch Status (MDR_010)\n\n"
        output += f"**Action:** {status['action']}\n"
        output += f"**Message:** {status.get('message', 'N/A')}\n"
        if 'days_inactive' in status:
            output += f"**Days Inactive:** {status['days_inactive']}\n"
        return output
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_pause_notifications() -> str:
    """
    Pause all PEFS notifications (Kill Switch activation).
    Call this when the user requests to stop notifications.
    """
    try:
        brain = get_brain_path()
        commitment_ledger.pause_notifications(brain)
        return "🛑 Notifications paused. Use brain_resume_notifications() to restart."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_resume_notifications() -> str:
    """
    Resume PEFS notifications after pause.
    """
    try:
        brain = get_brain_path()
        commitment_ledger.resume_notifications(brain)
        commitment_ledger.record_interaction(brain)
        return "✅ Notifications resumed. Interaction recorded."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_record_feedback(notification_type: str, score: int) -> str:
    """
    Record user feedback on a notification (MDR_010).
    
    Args:
        notification_type: Type of notification (e.g., 'daily', 'red_tier', 'challenge')
        score: Feedback score (1-5, where 5=helpful, 1=noise)
    """
    try:
        brain = get_brain_path()
        entry = commitment_ledger.record_feedback(brain, notification_type, score)
        if score >= 4:
            msg = "✅ Positive feedback recorded. Marked as high-impact."
        elif score >= 2:
            msg = "📝 Neutral feedback recorded."
        else:
            msg = "😔 Negative feedback recorded. Will try to improve."
        return msg
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_mark_high_impact() -> str:
    """
    Manually mark a loop closure as high-impact (MDR_010).
    Use when a notification led to a meaningful outcome.
    """
    try:
        brain = get_brain_path()
        commitment_ledger.mark_high_impact_closure(brain)
        return "✅ Marked as high-impact closure. Value ratio updated."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def brain_session_start() -> str:
    """
    START HERE - Mandatory session start protocol.
    
    Returns current Brain state to drive your work:
    - Satellite view (depth, activity, health)
    - Top 5 pending tasks by priority
    - Active sprint (if any)
    - Recommendations
    
    CRITICAL: Call this BEFORE starting significant work.
    Read AGENT_PROTOCOL.md for full workflow.
    
    Returns:
        Formatted report with priorities and recommendations
    """
    try:
        # Direct File I/O for robustness (avoid internal function call issues)
        brain_path = os.environ.get("NUCLEAR_BRAIN_PATH")
        if not brain_path:
            return "Error: NUCLEAR_BRAIN_PATH env var not set"
        
        brain = Path(brain_path)
        
        # 1. Get Depth
        depth_path = brain / "depth_state.json"
        depth_data = {}
        if depth_path.exists():
            try:
                with open(depth_path, "r") as f:
                    depth_data = json.load(f)
            except: pass
            
        depth_current = depth_data.get("current_depth", 0)
        depth_max = depth_data.get("max_safe_depth", 5)
        depth_indicator = depth_data.get("indicator", "🟢 ○○○○○")
        
        # 2. Get Tasks
        tasks_path = brain / "ledger" / "tasks.json"
        pending_tasks = []
        if tasks_path.exists():
            try:
                with open(tasks_path, "r") as f:
                    all_tasks = json.load(f)
                    pending_tasks = [t for t in all_tasks if t.get("status") == "PENDING"]
            except: pass
            
        # Sort by priority
        sorted_tasks = sorted(pending_tasks, key=lambda t: t.get("priority", 999))[:5]
        
        # 3. Get Session
        state_path = brain / "ledger" / "state.json"
        has_session = False
        active_context = "None"
        active_task = "None"
        
        if state_path.exists():
            try:
                with open(state_path, "r") as f:
                    state = json.load(f)
                    session = state.get("current_session", {})
                    if session:
                        has_session = True
                        active_context = session.get("context", "Unknown")
                        active_task = session.get("active_task", "None")
            except: pass

        # Build Report
        output = []
        output.append("=" * 60)
        output.append("🧠 BRAIN SESSION START - Workflow Enforcement Active")
        output.append("=" * 60)
        output.append("")
        
        # Satellite View Simulation
        output.append("📊 CURRENT STATE:")
        output.append(f"   📍 DEPTH: {depth_indicator} ({depth_current}/{depth_max})")
        output.append("")
        
        # Priority Tasks
        output.append("🎯 TOP PRIORITY TASKS:")
        if not sorted_tasks:
            output.append("   ✅ No pending tasks! All clear.")
        else:
            for i, task in enumerate(sorted_tasks, 1):
                priority = task.get("priority", "?")
                desc = task.get("description", "")[:70]
                task_id = task.get("id", "")
                
                priority_icon = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "⚪"}.get(priority, "⚫")
                
                output.append(f"   {i}. {priority_icon} P{priority} | {desc}")
                output.append(f"      ID: {task_id}")
                
                if priority <= 2:
                    output.append(f"      ⚠️  HIGH PRIORITY - Should work on this first")
                output.append("")
        
        # Active Sprint
        output.append("🏃 ACTIVE SPRINT:")
        if has_session:
            output.append(f"   Context: {active_context}")
            output.append(f"   Task: {active_task}")
        else:
            output.append("   No active sprint - consider setting one with brain_save_session()")
        output.append("")
        
        # Recommendations
        output.append("💡 RECOMMENDATIONS:")
        if sorted_tasks and sorted_tasks[0].get("priority", 99) <= 2:
            top = sorted_tasks[0]
            output.append(f"   ⚠️  Work on Priority {top['priority']} task first:")
            output.append(f"   '{top['description'][:60]}...'")
        elif not has_session and sorted_tasks:
            output.append("   1. Pick a task from above")
            output.append("   2. Create sprint: brain_save_session(context='...')")
            output.append("   3. Stay focused on that sprint")
        else:
            output.append("   Continue current sprint or work on top priority task")
        output.append("")
        
        output.append("📖 Read AGENT_PROTOCOL.md for full workflow requirements")
        output.append("=" * 60)
        
        # Emit event (safe)
        try:
             _emit_event("session_started", "brain", {"task_count": len(sorted_tasks)})
        except: pass
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error in session start: {e}"


def main():
    # Helper to log to debug file
    def log_debug(msg):
        with open("/tmp/mcp_debug.log", "a") as f:
            f.write(f"{msg}\n")
    
    try:
        log_debug("Entering mcp.run()")
        mcp.run()
        log_debug("Exited mcp.run() normally")
    except Exception as e:
        log_debug(f"Exception in mcp.run(): {e}")
        import traceback
        with open("/tmp/mcp_debug.log", "a") as f:
            traceback.print_exc(file=f)
        raise

if __name__ == "__main__":
    main()
