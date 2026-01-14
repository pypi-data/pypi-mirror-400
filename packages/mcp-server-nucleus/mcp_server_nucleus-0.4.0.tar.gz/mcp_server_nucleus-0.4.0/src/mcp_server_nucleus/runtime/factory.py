"""
Nucleus Agent Runtime (NAR) - Context Factory
==============================================
MDR_004 Compliant: Full Agent-Tool Fit routing with persona-based tool loading
MDR Third-Pass: Now loads rich agent definitions from .brain/agents/*.md

Supports both:
- Ephemeral agents (fast, minimal prompts) - DevOps, Librarian
- Nuanced agents (rich, 400-line prompts) - Critic, Researcher, Synthesizer
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .capabilities.base import Capability
from .capabilities.render_ops import RenderOps
from .capabilities.brain_ops import BrainOps
from .capabilities.depth_tracker import DepthTracker
from .capabilities.feature_map import FeatureMap
from .capabilities.proof_system import ProofSystem
from .capabilities.render_poller_cap import RenderPolling


# ============================================================
# CONFIGURATION
# ============================================================

# Path to brain (can be overridden via env var)
BRAIN_PATH = Path(os.environ.get("NUCLEUS_BRAIN_PATH", ".brain"))


# ============================================================
# PERSONA REGISTRY: 8 Personas (4 Fast + 4 Rich)
# ============================================================

PERSONAS = {
    # --- FAST PERSONAS (Ephemeral, Directive Prompts) ---
    "librarian": {
        "name": "Librarian",
        "mode": "fast",
        "description": "Background scanner. Converts files to structured data.",
        "capabilities": ["brain_ops", "feature_map", "proof_system"],
        "system_prompt_fragment": """You are a Librarian (Database Operator).
    
        CRITICAL RULES (MDR_002 DIRECTIVE):
        1. Your ONLY output should be tool calls.
        2. Do NOT chat, explain, or write prose.
        3. Translate the user's request into tool calls.
        4. Output format: JSON tool call blocks.
        
        If you output text instead of tool calls, you have FAILED.
        """,
        "agent_file": None  # Uses inline prompt
    },
    
    "devops": {
        "name": "DevOps",
        "mode": "fast",
        "description": "Operator. Deployment and infrastructure actions.",
        "capabilities": ["render_ops", "render_poller"],
        "system_prompt_fragment": """You are a DevOps Specialist (Infrastructure Operator).
        
        CRITICAL RULES (MDR_002 DIRECTIVE):
        1. Your ONLY output should be tool calls.
        2. Do NOT chat, explain, or give status updates as text.
        3. Execute infrastructure tasks using ONLY the provided tools.
        4. Output format: JSON tool call blocks.
        
        If you output text instead of tool calls, you have FAILED.
        """,
        "agent_file": None  # Uses inline prompt
    },
    
    # --- RICH PERSONAS (Nuanced, Load from .brain/agents/*.md) ---
    "synthesizer": {
        "name": "Synthesizer",
        "mode": "rich",
        "description": "Meta-orchestrator. Sees across all domains. Founder's force multiplier.",
        "capabilities": ["brain_ops", "depth_tracker"],  # Orchestration tools
        "system_prompt_fragment": None,  # Loaded from file
        "agent_file": "synthesizer.md"
    },
    
    "critic": {
        "name": "Critic",
        "mode": "rich",
        "description": "Quality gate. Code review, security audit, strategy validation.",
        "capabilities": ["brain_ops", "proof_system"],
        "system_prompt_fragment": None,
        "agent_file": "critic.md"
    },
    
    "developer": {
        "name": "Developer",
        "mode": "rich",
        "description": "Implementation specialist. Code execution, testing.",
        "capabilities": ["brain_ops", "proof_system"],
        "system_prompt_fragment": None,
        "agent_file": "developer.md"
    },
    
    "researcher": {
        "name": "Researcher",
        "mode": "rich",
        "description": "Information gatherer. Search, analysis, documentation.",
        "capabilities": ["brain_ops"],
        "system_prompt_fragment": None,
        "agent_file": "researcher.md"
    },
    
    "architect": {
        "name": "Architect",
        "mode": "rich",
        "description": "System designer. Specs, architecture, depth tracking.",
        "capabilities": ["brain_ops", "depth_tracker"],
        "system_prompt_fragment": None,
        "agent_file": "architect.md"
    },
    
    "strategist": {
        "name": "Strategist",
        "mode": "rich",
        "description": "Business strategy. Decisions, roadmap, positioning.",
        "capabilities": ["brain_ops"],
        "system_prompt_fragment": None,
        "agent_file": "strategist.md"
    },
}


# ============================================================
# INTENT CLASSIFICATION (MDR_004)
# ============================================================

INTENT_KEYWORDS = {
    "orchestrate": ["start sprint", "digest", "optimize", "meta", "daily", "weekly"],
    "review": ["review", "audit", "check", "validate", "security", "quality"],
    "implement": ["implement", "code", "build", "fix", "develop", "create component"],
    "research": ["research", "analyze", "search", "find", "investigate", "learn"],
    "design": ["design", "architect", "spec", "plan", "structure", "depth"],
    "strategy": ["strategy", "decide", "pivot", "position", "roadmap", "business"],
    "deploy": ["deploy", "render", "service", "smoke", "poll", "infra"],
    "admin": ["task", "loop", "commitment", "feature", "proof", "add", "close", "scan"],
}


def classify_intent(message: str) -> str:
    """
    Classify user intent into a category.
    Extended for 8 personas.
    """
    message_lower = message.lower()
    
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in message_lower:
                scores[intent] += 1
    
    # Default to 'admin' if no matches
    if all(s == 0 for s in scores.values()):
        return "admin"
    
    return max(scores, key=scores.get)


def get_persona_for_intent(intent: str) -> Dict:
    """
    Map classified intent to persona (MDR_004 Extended).
    """
    mapping = {
        "orchestrate": PERSONAS["synthesizer"],
        "review": PERSONAS["critic"],
        "implement": PERSONAS["developer"],
        "research": PERSONAS["researcher"],
        "design": PERSONAS["architect"],
        "strategy": PERSONAS["strategist"],
        "deploy": PERSONAS["devops"],
        "admin": PERSONAS["librarian"],
    }
    return mapping.get(intent, PERSONAS["librarian"])


# ============================================================
# CONTEXT FACTORY (MDR_004 + Third-Pass Enhanced)
# ============================================================

class ContextFactory:
    """
    The Compiler.
    Maps Intent -> Persona -> Toolset.
    
    Supports:
    - Fast personas: Inline directive prompts (5-10 lines)
    - Rich personas: Load full protocols from .brain/agents/*.md (400+ lines)
    - External agent definitions: Load from any path (marketplace-ready)
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        self._registry: Dict[str, Capability] = {}
        self._brain_path = brain_path or BRAIN_PATH
        self._agent_cache: Dict[str, str] = {}  # Cache loaded agent prompts
        self._register_defaults()

    def _register_defaults(self):
        """Register all available capabilities"""
        self.register(RenderOps())
        self.register(BrainOps())
        self.register(DepthTracker())
        self.register(FeatureMap())
        self.register(ProofSystem())
        self.register(RenderPolling())

    def register(self, capability: Capability):
        """Register a capability for use by agents"""
        self._registry[capability.name] = capability

    def load_agent_prompt(self, agent_file: str) -> Optional[str]:
        """
        Load an agent prompt from .brain/agents/{agent_file}.
        Extracts key sections: IDENTITY, CORE FUNCTIONS, CONSTRAINTS.
        Caches for performance.
        """
        if agent_file in self._agent_cache:
            return self._agent_cache[agent_file]
        
        agent_path = self._brain_path / "agents" / agent_file
        
        if not agent_path.exists():
            return None
        
        try:
            full_content = agent_path.read_text()
            
            # Extract key sections using regex
            sections = []
            
            # Get IDENTITY section
            identity_match = re.search(
                r'## IDENTITY\s*(.*?)(?=## |\Z)', 
                full_content, 
                re.DOTALL
            )
            if identity_match:
                sections.append(identity_match.group(1).strip())
            
            # Get CORE FUNCTIONS or PERMISSIONS section
            core_match = re.search(
                r'## (?:CORE FUNCTIONS|PERMISSIONS)\s*(.*?)(?=## |\Z)', 
                full_content, 
                re.DOTALL
            )
            if core_match:
                sections.append(core_match.group(1).strip())
            
            # Get CONSTRAINTS section
            constraints_match = re.search(
                r'## CONSTRAINTS\s*(.*?)(?=## |\Z)', 
                full_content, 
                re.DOTALL
            )
            if constraints_match:
                sections.append(constraints_match.group(1).strip())
            
            # Combine extracted sections
            prompt = "\n\n".join(sections) if sections else full_content[:2000]
            
            # Cache it
            self._agent_cache[agent_file] = prompt
            return prompt
            
        except Exception as e:
            print(f"Warning: Could not load agent prompt {agent_file}: {e}")
            return None

    def load_external_agent(self, path: str) -> Optional[str]:
        """
        Load an agent definition from any external path.
        Supports marketplace-style agent loading.
        """
        try:
            ext_path = Path(path)
            if ext_path.exists():
                return ext_path.read_text()
        except Exception:
            pass
        return None

    def get_persona(self, persona_name: str) -> Optional[Dict]:
        """Get a persona by name (case-insensitive)"""
        return PERSONAS.get(persona_name.lower())

    def create_context(self, session_id: str, intent: str) -> Dict[str, Any]:
        """
        Create an execution context for an agent.
        MDR_004 Enhanced + Third-Pass: Supports rich agent prompts.
        """
        # Step 1: Classify intent
        intent_category = classify_intent(intent)
        
        # Step 2: Get persona
        persona = get_persona_for_intent(intent_category)
        
        # Step 3: Load capabilities
        tools = []
        active_caps_names = []
        active_caps_instances = []
        
        for cap_name in persona.get("capabilities", []):
            cap = self._registry.get(cap_name)
            if cap:
                tools.extend(cap.get_tools())
                active_caps_names.append(cap.name)
                active_caps_instances.append(cap)
        
        # Step 4: Generate system prompt (fast or rich)
        system_prompt = self._generate_system_prompt(intent, persona, active_caps_names)
        
        return {
            "session_id": session_id,
            "intent": intent,
            "intent_category": intent_category,
            "persona": persona["name"],
            "persona_mode": persona.get("mode", "fast"),
            "capabilities": active_caps_names,
            "capability_instances": active_caps_instances,
            "tools": tools,
            "tool_count": len(tools),
            "system_prompt": system_prompt
        }

    def create_context_for_persona(
        self, 
        session_id: str, 
        persona_name: str, 
        intent: str,
        external_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create context for a specific persona (skip intent classification).
        Useful for event-driven orchestration and direct delegation.
        
        Args:
            external_prompt: Optional external agent definition (marketplace)
        """
        persona = self.get_persona(persona_name)
        if not persona:
            # Fallback to librarian
            persona = PERSONAS["librarian"]
        
        # Load capabilities
        tools = []
        active_caps_names = []
        active_caps_instances = []
        
        for cap_name in persona.get("capabilities", []):
            cap = self._registry.get(cap_name)
            if cap:
                tools.extend(cap.get_tools())
                active_caps_names.append(cap.name)
                active_caps_instances.append(cap)
        
        # Generate prompt (external overrides everything)
        if external_prompt:
            system_prompt = f"{external_prompt}\n\nIntent: {intent}"
        else:
            system_prompt = self._generate_system_prompt(intent, persona, active_caps_names)
        
        return {
            "session_id": session_id,
            "intent": intent,
            "intent_category": "direct",
            "persona": persona["name"],
            "persona_mode": persona.get("mode", "fast"),
            "capabilities": active_caps_names,
            "capability_instances": active_caps_instances,
            "tools": tools,
            "tool_count": len(tools),
            "system_prompt": system_prompt
        }

    def _generate_system_prompt(
        self, 
        intent: str, 
        persona: Dict, 
        caps: List[str]
    ) -> str:
        """
        Generate persona-specific system prompt.
        - Fast mode: Use inline fragment
        - Rich mode: Load from .brain/agents/*.md
        """
        mode = persona.get("mode", "fast")
        agent_file = persona.get("agent_file")
        
        # Try to load rich prompt
        if mode == "rich" and agent_file:
            loaded_prompt = self.load_agent_prompt(agent_file)
            if loaded_prompt:
                return f"""
# {persona['name']} Agent

{loaded_prompt}

---
## Current Task

Intent: {intent}
Active Capabilities: {', '.join(caps) if caps else 'None (Files Only)'}
Tool Count: {len(caps)}

Execute the intent. Once complete, output 'TERMINATE'.
"""
        
        # Fallback to inline fragment (fast mode)
        fragment = persona.get("system_prompt_fragment", "Execute the user's request.")
        
        return f"""
You are an Ephemeral Agent: {persona['name']}.

{fragment}

Intent: {intent}
Active Capabilities: {', '.join(caps) if caps else 'None (Files Only)'}
Tool Count: {len(caps)}

Your Goal: Execute the intent using the provided tools. 
Once the task is done, output 'TERMINATE'.
"""

    def list_personas(self) -> List[Dict]:
        """List all available personas"""
        return [
            {
                "name": p["name"],
                "mode": p.get("mode", "fast"),
                "description": p["description"],
                "capabilities": p.get("capabilities", []),
                "has_rich_prompt": p.get("agent_file") is not None
            }
            for p in PERSONAS.values()
        ]

    def list_capabilities(self) -> List[str]:
        """List all registered capabilities"""
        return list(self._registry.keys())

    def clear_cache(self):
        """Clear the agent prompt cache"""
        self._agent_cache.clear()
