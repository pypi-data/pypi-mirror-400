"""
Model Selector — Intelligent model selection based on task complexity.

Chooses between Gemini Flash (fast/cheap) and Pro (complex/expensive) based on:
- Task complexity scoring
- Performance history
- Budget constraints
- Lucidity feedback

Part of Phase 8: Autonomous Optimization.
"""

import logging
import re
from typing import Tuple, Dict, Any, Optional
import yaml
from pathlib import Path

from axis_reasoning._internal.config import paths
from axis_reasoning.orchestrator.feedback_collector import feedback_collector

logger = logging.getLogger(__name__)


class ModelSelector:
    """
    Selects optimal model based on task complexity and performance history.
    
    Models:
    - gemini-2.0-flash-001: Fast, cheap, good for simple-medium tasks
    - gemini-1.5-pro: Slower, expensive, best for complex tasks
    """
    
    def __init__(self):
        self.config_path = paths.config / "optimization_config.yml"
        self.config = self._load_config()
        self.models = self.config.get("optimization", {}).get("model_selection", {}).get("models", {})
        self.downgrade_policy = self.config.get("optimization", {}).get("model_selection", {}).get("downgrade_policy", {})
    
    def _load_config(self) -> Dict:
        """Load optimization configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Optimization config not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return {}
    
    def score_complexity(self, task_description: str, agent_id: str) -> float:
        """
        Score task complexity on 0.0-1.0 scale.
        
        Heuristics:
        - Code refactoring/architecture → High (0.7-1.0)
        - Simple queries/lookups → Low (0.0-0.3)
        - Agent execution/analysis → Medium (0.4-0.6)
        
        Args:
            task_description: Task description text
            agent_id: Agent performing the task
        
        Returns:
            Complexity score 0.0-1.0
        """
        score = 0.5  # Default: medium complexity
        
        # High complexity indicators
        high_complexity_keywords = [
            "refactor", "architecture", "design", "optimize", "migrate",
            "complex", "integrate", "performance", "scale"
        ]
        
        # Low complexity indicators
        low_complexity_keywords = [
            "simple", "quick", "lookup", "fetch", "get", "list",
            "query", "read", "view"
        ]
        
        task_lower = task_description.lower()
        
        # Check for high complexity
        high_count = sum(1 for keyword in high_complexity_keywords if keyword in task_lower)
        if high_count >= 2:
            score = 0.8
        elif high_count == 1:
            score = 0.6
        
        # Check for low complexity
        low_count = sum(1 for keyword in low_complexity_keywords if keyword in task_lower)
        if low_count >= 2:
            score = 0.2
        elif low_count == 1:
            score = 0.3
        
        # Adjust based on agent type
        if "code" in agent_id.lower() or "review" in agent_id.lower():
            score += 0.1  # Code tasks tend to be more complex
        elif "clarity" in agent_id.lower():
            score += 0.05  # Brand tasks are moderately complex
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, score))
    
    def select_model(
        self,
        task_description: str,
        agent_id: str,
        recent_lucidity: Optional[float] = None,
        budget_remaining: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Select optimal model for the task following the hierarchy:
        1. Routing Config Rules (quick queries, etc.)  
        2. Specialist Mapping (model_mapping.yml)
        3. Lucidity / Complexity Heuristics
        4. Default Model (Flash)
        
        Args:
            task_description: Task description
            agent_id: Agent ID
            recent_lucidity: Recent lucidity score (0.0-1.0)
            budget_remaining: Remaining token budget
        
        Returns:
            (model_name, reasoning)
        """
        # 1. Load Specialist Mapping & Routing Config
        specialist_mapping_path = paths.config / "model_mapping.yml"
        specialist_config = {}
        if specialist_mapping_path.exists():
            try:
                with open(specialist_mapping_path, 'r') as f:
                    specialist_config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Failed to load specialist mapping: {e}")

        specialists = specialist_config.get("specialists", {})
        routing_config = specialist_config.get("routing_config", {})
        
        # Default models from config
        flash_model = self.models.get("flash", {}).get("name", "models/gemini-2.0-flash-001")
        pro_model = self.models.get("pro", {}).get("name", "models/gemini-1.5-pro")
        
        # Extract routing config values
        default_model = routing_config.get("default_model", flash_model)
        specialist_threshold = routing_config.get("specialist_threshold", 0.65)
        quick_query_override = routing_config.get("quick_query_override", True)
        quick_query_token_limit = routing_config.get("quick_query_token_limit", 100)
        
        # Estimate token count (rough: 1 token ≈ 4 chars)
        estimated_tokens = len(task_description) // 4
        
        # ROUTING RULE 1: Quick Query Override
        # Short queries always use default (Flash) regardless of specialist
        if quick_query_override and estimated_tokens < quick_query_token_limit:
            logger.info(f"⚡ Quick Query Override: {estimated_tokens} tokens < {quick_query_token_limit} limit")
            return default_model, f"Quick query override (estimated {estimated_tokens} tokens)"
        
        # Score complexity for later threshold checks
        complexity = self.score_complexity(task_description, agent_id)
        
        # 2. Check Specialist Mapping (Level 2)
        if agent_id in specialists:
            specialist_model = specialists[agent_id].get("model")
            if specialist_model:
                # ROUTING RULE 2: Specialist Threshold
                # Only use specialist if complexity meets threshold
                if complexity >= specialist_threshold:
                    # Still respect budget floor if it's a "pro" class model
                    budget_floor = self.config.get("optimization", {}).get("model_selection", {}).get("budget_floor_for_pro", 30000)
                    is_pro = "pro" in specialist_model.lower() or "sonnet" in specialist_model.lower()
                    
                    if not is_pro or (budget_remaining is None or budget_remaining >= budget_floor):
                        logger.info(f"🎯 Specialist Routing: Agent {agent_id} -> {specialist_model} (complexity {complexity:.2f} >= {specialist_threshold})")
                        return specialist_model, f"Specialist mapping for {agent_id} (complexity {complexity:.2f} >= threshold)"
                    else:
                        logger.warning(f"⚠️ Specialist Routing Blocked: Low budget for {agent_id}")
                        # Fallthrough to heuristics or default
                else:
                    logger.info(f"⚠️ Specialist Threshold Not Met: {complexity:.2f} < {specialist_threshold}, using default")
                    return default_model, f"Complexity {complexity:.2f} below specialist threshold {specialist_threshold}"

        # 3. Lucidity / Complexity Heuristics (Level 3)        
        # Get model selection config
        config = self.config.get("optimization", {}).get("model_selection", {})
        complexity_threshold = config.get("complexity_threshold_pro", 0.7)
        budget_floor = config.get("budget_floor_for_pro", 30000)
        
        # Decision logic for Heuristics
        selected_model = flash_model
        reasoning = f"Flash model (complexity: {complexity:.2f} < threshold {complexity_threshold})"
        
        # Upgrade to Pro if:
        # - Complexity is high enough
        # - Budget allows it
        if complexity >= complexity_threshold:
            if budget_remaining is None or budget_remaining >= budget_floor:
                selected_model = pro_model
                reasoning = f"Pro model (complexity: {complexity:.2f} >= threshold {complexity_threshold})"
            else:
                reasoning = f"Flash model (budget constraint: {budget_remaining} < floor {budget_floor})"
        
        # Downgrade from Pro if low lucidity (Internal Heuristic)
        if selected_model == pro_model and recent_lucidity is not None and recent_lucidity < 0.6:
            selected_model = flash_model
            reasoning = f"Flash model (low recent lucidity: {recent_lucidity:.2f}, downgrading from Pro)"
        
        # 4. Final Fallback (Level 4) is implicit in selected_model defaulting to flash_model
        
        logger.info(f"🤖 Model selection: {selected_model.split('/')[-1]} — {reasoning}")
        return selected_model, reasoning
    
    def get_downgrade_action(self, failure_reason: str) -> str:
        """
        Get downgrade action based on failure reason.
        
        Args:
            failure_reason: Type of failure (budget_pressure, timeout, error)
        
        Returns:
            Action to take (retry_with_flash, partial_response, escalate_once_then_block)
        """
        if "budget" in failure_reason.lower():
            return self.downgrade_policy.get("on_budget_pressure", "retry_with_flash")
        elif "timeout" in failure_reason.lower():
            return self.downgrade_policy.get("on_timeout", "partial_response")
        else:
            return self.downgrade_policy.get("on_failure", "escalate_once_then_block")


# Global Instance
model_selector = ModelSelector()
