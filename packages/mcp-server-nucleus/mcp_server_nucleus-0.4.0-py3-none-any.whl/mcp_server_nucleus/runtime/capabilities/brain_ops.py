from typing import List, Dict, Any
from pathlib import Path
from .base import Capability
from ... import commitment_ledger

class BrainOps(Capability):
    @property
    def name(self) -> str:
        return "brain_ops"

    @property
    def description(self) -> str:
        return "Tools for managing the centralized commitment ledger (The Brain)."

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "brain_add_commitment",
                "description": "Add a new commitment (task, todo, loop) to the ledger.",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "description": {"type": "string"},
                        "loop_type": {"type": "string", "enum": ["task", "todo", "draft", "decision"]},
                        "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                        "source": {"type": "string"}
                    },
                    "required": ["description"]
                }
            },
            {
                "name": "brain_get_open_loops",
                "description": "Get all active open loops.",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "type_filter": {"type": "string"}
                    }
                }
            },
            {
                "name": "brain_scan_commitments",
                "description": "Trigger the Librarian to scan artifacts for checklist items.",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "brain_archive_stale",
                "description": "Trigger the Librarian to archive stale commitments.",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "brain_export",
                "description": "Export the brain content to a zip file (respecting .brainignore).",
                "parameters": {"type": "object", "properties": {}}
            }
        ]

    def execute_tool(self, tool_name: str, args: Dict) -> str:
        """Execute the tool locally using commitment_ledger."""
        # Helper to get brain path - assuming default location for NAR
        # In prod, this should be injected
        brain_path = Path("/Users/lokeshgarg/ai-mvp-backend/.brain")
        
        if tool_name == "brain_add_commitment":
            result = commitment_ledger.add_commitment(
                brain_path=brain_path,
                source_file="NAR_AGENT",
                source_line=0,
                description=args['description'],
                comm_type=args.get('loop_type', 'task'),
                priority=args.get('priority', 3),
                source=args.get('source', 'nar_agent')
            )
            return f"Commitment Added: {result['id']}"
            
        elif tool_name == "brain_get_open_loops":
            loops = commitment_ledger.load_ledger(brain_path)["commitments"]
            # Filter logic could go here
            return f"Found {len([c for c in loops if c['status']=='open'])} open loops."
            
        elif tool_name == "brain_scan_commitments":
            result = commitment_ledger.scan_for_commitments(brain_path)
            return f"Scan Complete: {result}"
            
        elif tool_name == "brain_archive_stale":
            count = commitment_ledger.auto_archive_stale(brain_path)
            return f"Archived {count} stale items."
            
        elif tool_name == "brain_export":
            # Call export logic (implemented in commitment_ledger for centralization)
            if hasattr(commitment_ledger, 'export_brain'):
                result = commitment_ledger.export_brain(brain_path)
                return f"Export Complete: {result}"
            return "Error: export_brain not implemented in ledger."

        return f"Tool {tool_name} not found in BrainOps."
