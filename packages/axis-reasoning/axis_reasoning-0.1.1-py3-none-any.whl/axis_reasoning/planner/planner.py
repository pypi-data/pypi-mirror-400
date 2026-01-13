"""
Sovereign Agent Planner
The cognitive core that reasons, plans, and proposes SovereignActions.
"""
import json
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from axis_reasoning._internal.config import paths
from axis_reasoning.runtime.contracts import SovereignAction

@dataclass
class PlannerConfig:
    """Configuration for the Planner (Contractual Governance)."""
    max_reasoning_tokens: int = 2048  # Updated per REASONING_GOVERNANCE.md
    max_tool_iterations: int = 10
    max_denials_before_abort: int = 2
    reasoning_required: bool = True
    
    # Phase B: Reasoning Governance
    max_thought_steps: int = 6
    max_replans: int = 2
    reasoning_timeout_ms: int = 30000


class SovereignPlanner:
    """
    The Sovereign Agent Planner.
    Generates System Prompts and parses LLM outputs into SovereignActions.
    """
    
    def __init__(self, config: PlannerConfig = None):
        self.logger = logging.getLogger("antigravity.planner")
        self.config = config or PlannerConfig()
        self.capabilities = self._load_capabilities()
        self.system_prompt = self._generate_system_prompt()
        
    def _load_capabilities(self) -> Dict:
        """Load capabilities from capabilities.yml."""
        cap_path = paths.config / "capabilities.yml"
        if not cap_path.exists():
            self.logger.warning("capabilities.yml not found. Using empty capabilities.")
            return {}
        with open(cap_path) as f:
            return yaml.safe_load(f) or {}
    
    def _generate_system_prompt(self) -> str:
        """
        Auto-generate the System Prompt from capabilities and constraints.
        This is the Planner's instruction set.
        """
        tools_section = self._format_tools_for_prompt()
        
        prompt = f"""# SOVEREIGN AGENT PLANNER — SYSTEM PROMPT v1.0

You are a Sovereign Agent operating within a governed runtime.
Your role is to analyze tasks, decompose them into steps, and propose tool actions.

## CRITICAL RULES
1. You MUST ONLY use tools listed in the AVAILABLE TOOLS section.
2. You MUST output a SINGLE JSON action per turn in the exact format specified.
3. You MUST include a 'reasoning' field explaining your decision (max 200 chars).
4. If the Gateway denies your action, you MUST choose an alternative. NEVER retry the same action.
5. If no alternative exists, respond with a natural language error message.

## OUTPUT FORMAT (STRICT JSON)
```json
{{
  "tool": "<tool_name>",
  "action": "<method_name>",
  "args": {{...}},
  "reasoning": "<why you chose this action>"
}}
```

## AVAILABLE TOOLS
{tools_section}

## CONSTRAINTS
- Max reasoning tokens: {self.config.max_reasoning_tokens}
- Max tool iterations: {self.config.max_tool_iterations}
- Max consecutive denials before abort: {self.config.max_denials_before_abort}

## TERMINATION
When the task is complete, respond with a natural language summary (no JSON).
If you cannot complete the task, explain why in natural language.

## FORBIDDEN
- Do NOT invent tools.
- Do NOT include credentials or secrets.
- Do NOT attempt to bypass the Gateway.
"""
        return prompt
    
    def _format_tools_for_prompt(self) -> str:
        """Format capabilities.yml tools into a readable prompt section."""
        if not self.capabilities.get("tools"):
            return "No tools available."
        
        lines = []
        for tool_name, tool_info in self.capabilities.get("tools", {}).items():
            desc = tool_info.get("description", "No description")
            methods = ", ".join(tool_info.get("methods", []))
            lines.append(f"- **{tool_name}**: {desc}")
            lines.append(f"  Methods: [{methods}]")
        
        return "\n".join(lines)
    
    def get_system_prompt(self) -> str:
        """Return the generated system prompt."""
        return self.system_prompt
    
    def parse_action(self, llm_output: str) -> Optional[SovereignAction]:
        """
        Parse LLM output into a SovereignAction.
        Phase D: Contract Enforcement - validates against schema.
        Returns None if the output is not a valid action (e.g., natural language response).
        """
        import re
        
        # Try to extract JSON from output (handle markdown code blocks)
        try:
            # First, try to find JSON in code block
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', llm_output, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
            else:
                # Fallback: look for raw JSON object
                json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', llm_output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    self.logger.info("No JSON found in output. Assuming natural language response.")
                    return None
            
            data = json.loads(json_str)
            
            # Phase D: Contract Enforcement - Validate required fields
            if not all(k in data for k in ["tool", "action", "args"]):
                self.logger.warning("CONTRACT_VIOLATION: Incomplete action JSON. Missing required fields.")
                return None
            
            # Validate tool is in capabilities
            if data["tool"] not in self.capabilities.get("tools", {}):
                self.logger.warning(f"CONTRACT_VIOLATION: Unknown tool '{data['tool']}' not in capabilities.yml")
                return None
            
            # Validate action is allowed for this tool
            tool_info = self.capabilities["tools"][data["tool"]]
            allowed_methods = tool_info.get("methods", [])
            if data["action"] not in allowed_methods:
                self.logger.warning(f"CONTRACT_VIOLATION: Method '{data['action']}' not allowed for tool '{data['tool']}'")
                return None
            
            # Check reasoning requirement
            if self.config.reasoning_required and not data.get("reasoning"):
                self.logger.warning("CONTRACT_VIOLATION: Reasoning is required but missing.")
                return None
            
            # Validate reasoning length
            if len(data.get("reasoning", "")) > 200:
                self.logger.warning("CONTRACT_VIOLATION: Reasoning exceeds 200 character limit.")
                # Truncate instead of rejecting
                data["reasoning"] = data["reasoning"][:200]
            
            return SovereignAction(
                tool_name=data["tool"],
                action_name=data["action"],
                arguments=data.get("args", {}),
                reasoning=data.get("reasoning", "No reasoning provided")
            )
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON from LLM output: {e}")
            return None
    
    def format_gateway_feedback(self, decision) -> str:
        """Format Gateway decision into context feedback for replanning."""
        if decision.allowed:
            return ""
        
        return f"System: TOOL_DENIED ({decision.verdict_code}): {decision.reason}. You MUST choose an alternative tool or explain why the task cannot be completed."

# Global instance
planner = SovereignPlanner()
