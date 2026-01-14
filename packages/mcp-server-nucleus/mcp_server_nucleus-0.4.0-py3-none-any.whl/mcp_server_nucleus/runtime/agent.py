from typing import Dict, Any, List, Optional
from .. import commitment_ledger
from pathlib import Path
import os
import asyncio
import json

# Gemini types imported dynamically or duck-typed via DualEngineLLM

def get_brain_path_internal() -> Path:
    """Helper to get brain path inside runtime"""
    return Path(os.getenv("NUCLEAR_BRAIN_PATH", "/Users/lokeshgarg/ai-mvp-backend/.brain"))

class EphemeralAgent:
    """
    The Runtime.
    A disposable agent that runs until completion.
    MDR_005: Supports both LLM-driven (Smart) and Heuristic (Fast) modes.
    MDR_002: Implements Active Correction (Critic) in LLM mode.
    """
    def __init__(self, context: Dict[str, Any], model: Any = None):
        self.context = context
        self.model = model
        self.history: List[str] = []
        self.active = True

    async def run(self) -> str:
        """
        Execute the agent loop.
        Returns execution log.
        """
        # MDR_010: Auto-record telemetry
        try:
             brain_path = get_brain_path_internal()
             commitment_ledger.record_interaction(brain_path)
        except Exception:
             pass 

        log = []
        log.append(f"--- Spawning Ephemeral Agent ({self.context['persona']}) ---")
        log.append(f"Intent: {self.context['intent']}")
        
        if self.model:
            return await self._run_llm(log)
        else:
            return self._run_heuristic(log)

    async def _run_llm(self, log: List[str]) -> str:
        """
        MDR_005 / MDR_002: Real LLM Execution Loop with Critic
        """
        log.append(">> Mode: LLM (Smart)")
        
        # 1. Build Prompt
        system_prompt = self.context.get('system_prompt', "You are an agent.")
        tools_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in self.context['tools']])
        
        full_prompt = f"""{system_prompt}

AVAILABLE TOOLS:
{tools_desc}

CRITICAL RULES (MDR_002):
1. You MUST call a tool to perform actions.
2. Do not just say you did it.
3. Output a JSON block with "tool" and "args" to call a tool.
   Format: 
   ```json
   {{
     "tool": "tool_name",
     "args": {{ ... }}
   }}
   ```
"""
        # 2. Call LLM
        try:
            response = self.model.generate_content(full_prompt)
            text = response.text
            log.append(f"[LLM Output]: {text[:200]}...")
            
            # 3. Parse and Execute
            import re
            match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            
            if match:
                tool_call = json.loads(match.group(1))
                tool_name = tool_call.get("tool")
                args = tool_call.get("args", {})
                
                log.append(f">> Tool detected: {tool_name}")
                result = self._execute_tool(tool_name, args)
                log.append(f"[Tool Result]: {result}")
                
            else:
                # =======================================================
                # MDR_002: THE ACTIVE CRITIC
                # =======================================================
                # If no tool call detected, and persona is NOT Synthesizer (writer),
                # assume failure and CRITIQUE.
                
                if self.context['persona'] != 'Synthesizer':
                    log.append("⚠️ [CRITIC INTERVENTION] No tool call detected.")
                    
                    # Retry once with critique
                    critique_prompt = f"""{full_prompt}
                    
                    PREVIOUS RESPONSE:
                    {text}
                    
                    SYSTEM CRITIC:
                    You did not call a tool! You just talked. 
                    You MUST output a JSON tool call block to execute the action.
                    """
                    
                    response_retry = self.model.generate_content(critique_prompt)
                    text_retry = response_retry.text
                    log.append(f"[LLM Retry Output]: {text_retry[:200]}...")
                    
                    match_retry = re.search(r'```json\s*(\{.*?\})\s*```', text_retry, re.DOTALL)
                    if match_retry:
                        tool_call = json.loads(match_retry.group(1))
                        tool_name = tool_call.get("tool")
                        args = tool_call.get("args", {})
                        
                        log.append(f">> Tool detected (after critique): {tool_name}")
                        result = self._execute_tool(tool_name, args)
                        log.append(f"[Tool Result]: {result}")
                    else:
                         log.append("❌ Agent failed to call tool after critique.")

        except Exception as e:
            log.append(f"LLM Error: {e}")
            
        return "\n".join(log)

    def _run_heuristic(self, log: List[str]) -> str:
        """Legacy Heuristic Mode"""
        log.append(">> Mode: Heuristic (Fast)")
        
        full_intent = self.context['intent'].lower()
        executed = False
        
        # 1. BRAIN OPS
        if "brain" in full_intent or "task" in full_intent or "scan" in full_intent:
             # Heuristic mapping for heuristic mode
             pass 

        # 2. RENDER OPS
        if "deploy" in full_intent or "check" in full_intent or "list" in full_intent:
             if "render_list_services" in [t['name'] for t in self.context['tools']] and ("list" in full_intent or "check" in full_intent):
                 result = self._execute_tool("render_list_services", {})
                 log.append(f">> [Heuristic] Calling render_list_services...")
                 log.append(result)
                 executed = True
             elif "render_deploy_service" in [t['name'] for t in self.context['tools']] and "deploy" in full_intent:
                 # Extract Service ID (Mock logic for now, or assume args provided in context?)
                 # For now, just list to be safe if no ID found
                 result = self._execute_tool("render_list_services", {}) 
                 log.append(f">> [Heuristic] Intent detected deploy, listing services first...")
                 log.append(result)
                 executed = True

        if not executed:
             log.append("No heuristic action map found.")
             
        log.append("--- Agent Terminated ---")
        return "\n".join(log)

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        # Find the capability that owns this tool
        caps = self.context.get('capability_instances', [])
        for cap in caps:
            tools = [t['name'] for t in cap.get_tools()]
            if tool_name in tools:
                return cap.execute_tool(tool_name, args)
        
        return f"Error: Tool {tool_name} implementation not found."
