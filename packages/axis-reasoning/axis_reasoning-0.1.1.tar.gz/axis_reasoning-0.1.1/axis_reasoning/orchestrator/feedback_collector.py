"""
Performance Feedback Collector — Tracks agent execution metrics for optimization.

Collects and analyzes performance data to improve future budget and model selection decisions.
Part of Phase 8: Autonomous Optimization.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path

logger = logging.getLogger(__name__)

# FASE 6: Context-aware state paths
from axis_reasoning._internal.state_paths import StatePathResolver
from axis_reasoning._internal.di import get_container

if TYPE_CHECKING:
    from axis_reasoning.engine import Engine
    from axis_reasoning.planner.planner import SovereignPlanner

# Get context-aware feedback path
try:
    container = get_container()
    _resolver = StatePathResolver(enable_isolation=container.config.context_isolation)
except:
    # Fallback if DI not initialized
    _resolver = StatePathResolver(enable_isolation=True)

FEEDBACK_DATA_DIR = "data/feedback"
FEEDBACK_DATA_FILE = str(_resolver.get_performance_feedback_path())


class PerformanceFeedbackCollector:
    """
    Collects performance metrics for autonomous optimization.
    
    Tracked Metrics:
    - Task success/failure rates per agent
    - Lucidity scores post-execution
    - Token usage efficiency
    - Model performance comparison
    - Cache hit rates
    """
    
    def __init__(self):
        self.data_file = FEEDBACK_DATA_FILE
        self._ensure_data_dir()
        self.state = self._load_state()
    
    def _ensure_data_dir(self):
        """Ensure feedback data directory exists."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        # Only create FEEDBACK_DATA_DIR if it's the default or within a sandbox
        if FEEDBACK_DATA_DIR in self.data_file or "tmp" in self.data_file:
             os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def set_storage_path(self, path: str):
        """Set a custom storage path for the feedback data."""
        self.data_file = path
        self._ensure_data_dir()
        self.state = self._load_state()
        logger.info(f"💾 Feedback storage path set to: {self.data_file}")

    def reset(self):
        """Reset the collector's state in memory and on disk."""
        self.state = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "agents": {}
        }
        self._save_state()
        logger.info("🧹 Feedback state reset.")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load existing feedback state."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load feedback state: {e}")
        
        return {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "agents": {}
        }
    
    def _save_state(self):
        """Persist feedback state to disk."""
        try:
            self.state["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(self.data_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback state: {e}")
    
    def reset(self):
        """Reset collector state (primarily for testing)."""
        self.state = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "agents": {}
        }
        self._save_state()
        logger.info("📊 Feedback collector state reset.")
    
    def record_execution(
        self,
        agent_id: str,
        task_type: str,
        success: bool,
        tokens_used: int,
        model: str,
        lucidity_score: Optional[float] = None,
        cached_tokens: int = 0,
        execution_time_ms: Optional[int] = None
    ):
        """
        Record a single agent execution for feedback analysis.
        
        Args:
            agent_id: Agent identifier
            task_type: Type of task executed
            success: Whether task completed successfully
            tokens_used: Total tokens consumed
            model: Model used (e.g., gemini-2.0-flash-001)
            lucidity_score: Post-execution lucidity (optional)
            cached_tokens: Tokens served from cache
            execution_time_ms: Execution duration in milliseconds
        """
        # Initialize agent data structure if needed
        if agent_id not in self.state["agents"]:
            self.state["agents"][agent_id] = {}
        
        if task_type not in self.state["agents"][agent_id]:
            self.state["agents"][agent_id][task_type] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_tokens": 0,
                "total_cached_tokens": 0,
                "avg_lucidity": 0.0,
                "lucidity_samples": [],
                "model_stats": {}
            }
        
        task_stats = self.state["agents"][agent_id][task_type]
        
        # Update execution counts
        task_stats["total_executions"] += 1
        if success:
            task_stats["successful_executions"] += 1
        else:
            task_stats["failed_executions"] += 1
        
        # Update token usage
        task_stats["total_tokens"] += tokens_used
        task_stats["total_cached_tokens"] += cached_tokens
        
        # Update lucidity tracking
        if lucidity_score is not None:
            task_stats["lucidity_samples"].append(lucidity_score)
            # Keep only last 10 samples for moving average
            if len(task_stats["lucidity_samples"]) > 10:
                task_stats["lucidity_samples"] = task_stats["lucidity_samples"][-10:]
            # Recalculate average with temporal decay (Weighted Moving Average)
            # Weights: [1, 2, ..., N] where N is recency
            samples = task_stats["lucidity_samples"]
            weights = list(range(1, len(samples) + 1))
            weighted_sum = sum(s * w for s, w in zip(samples, weights))
            task_stats["avg_lucidity"] = weighted_sum / sum(weights)
        
        # Update model-specific stats
        if model not in task_stats["model_stats"]:
            task_stats["model_stats"][model] = {
                "executions": 0,
                "successes": 0,
                "total_tokens": 0,
                "avg_tokens": 0
            }
        
        model_stat = task_stats["model_stats"][model]
        model_stat["executions"] += 1
        if success:
            model_stat["successes"] += 1
        model_stat["total_tokens"] += tokens_used
        model_stat["avg_tokens"] = model_stat["total_tokens"] / model_stat["executions"]
        
        self._save_state()
        
        logger.info(
            f"📊 Feedback recorded: {agent_id}/{task_type} - "
            f"Success: {success}, Tokens: {tokens_used}, Model: {model}"
        )
    
    def get_agent_stats(self, agent_id: str, task_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve performance statistics for an agent.
        
        Args:
            agent_id: Agent identifier
            task_type: Optional task type filter
        
        Returns:
            Performance statistics dictionary
        """
        if agent_id not in self.state["agents"]:
            return {}
        
        if task_type:
            return self.state["agents"][agent_id].get(task_type, {})
        
        return self.state["agents"][agent_id]
    
    def get_success_rate(self, agent_id: str, task_type: str) -> float:
        """
        Calculate success rate for agent/task combination.
        
        Returns:
            Success rate as float 0.0-1.0, or 0.0 if no data
        """
        stats = self.get_agent_stats(agent_id, task_type)
        if not stats or stats["total_executions"] == 0:
            return 0.0
        
        return stats["successful_executions"] / stats["total_executions"]
    
    def calculate_lucidity_estimate(self, agent_id: str, task_type: str, window: int = 5) -> float:
        """
        Signal Contract v0.1: lucidity_estimate (EMA/WMA without governance clamp).
        
        This is the RAW SIGNAL - no governance guards applied.
        Exponential Moving Average (α=0.3) gives recent executions more weight.
        
        Returns:
            Unguarded estimate for telemetry transparency (0.0-1.0)
        """
        stats = self.get_agent_stats(agent_id, task_type)
        if not stats:
            return None  # Semantic Correction: None = No History
        
        samples = stats.get("lucidity_samples", [])
        if not samples:
            return None
        
        # Take last N samples (window)
        recent_samples = samples[-window:]
        
        # Exponential Moving Average with α=0.3
        # weight_i = (1 - α)^(N - i - 1) where i is position in recent_samples
        alpha = 0.3
        weighted_sum = 0.0
        total_weight = 0.0
        
        for i, score in enumerate(reversed(recent_samples)):
            weight = (1 - alpha) ** i
            weighted_sum += score * weight
            total_weight += weight
        
        # NO CLAMP - return raw signal
        return weighted_sum / total_weight if total_weight > 0 else None
    
    def get_lucidity_estimate(self, agent_id: str, task_type: str) -> float:
        """
        Canonical getter for lucidity estimate (unguarded signal).
        Signal Contract v0.1.
        """
        return self.calculate_lucidity_estimate(agent_id, task_type)
    
    def get_avg_lucidity(self, agent_id: str, task_type: str) -> float:
        """
        Get average lucidity score for agent/task combination.
        
        Legacy method - delegates to get_lucidity_estimate for backward compatibility.
        
        Returns:
            Average lucidity score, or 0.0 if no data
        """
        return self.get_lucidity_estimate(agent_id, task_type)
    
    def get_model_performance(self, agent_id: str, task_type: str, model: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific model.
        
        Returns:
            Model performance stats or empty dict
        """
        stats = self.get_agent_stats(agent_id, task_type)
        if not stats:
            return {}
        
        return stats.get("model_stats", {}).get(model, {})


# Global Instance
feedback_collector = PerformanceFeedbackCollector()
