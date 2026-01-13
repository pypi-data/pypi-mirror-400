from __future__ import annotations

import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

from dotenv import load_dotenv

# Load environment variables BEFORE any clients are initialized
load_dotenv()

import json

import anthropic  # Anthropic SDK [Phase 13.1]
import yaml
from google import genai  # Google Gemini SDK
from google.genai import types as genai_types  # Gemini type definitions

from axis_reasoning._internal.config import paths
from axis_reasoning._internal.kill_switch import KillSwitch
from axis_reasoning._internal.observability import cost_tracker, observe
from axis_reasoning.orchestrator.context import SovereignContext
from axis_reasoning.orchestrator.context_cache import context_cache_manager
from axis_reasoning.model_selector import model_selector
from axis_reasoning._internal.telemetry import (
    telemetry_engine as telemetry,  # Keep for decorators only
)
from axis_reasoning._internal.schemas import ActorType, EventType, TelemetrySource
from axis_reasoning._internal.logging import log_error, log_info, log_warning

if TYPE_CHECKING:
    from axis_reasoning.planner.planner import SovereignPlanner
    from axis_reasoning.orchestrator.context import SovereignContext


class AgentExecutor:
    """
    Executes agent commands using the appropriate CLI tool.
    """

    def __init__(self):
        self.log_dir = paths.logs / "agents"
        self.logger = logging.getLogger("antigravity.orchestrator.executor")

        # Load optimization config
        self.optimization_config = self._load_optimization_config()
        self.shadow_mode = self.optimization_config.get("optimization", {}).get(
            "shadow_mode", True
        )
        self.shadow_log_file = "antigravity/logs/autonomy_performance.jsonl"

        # Initialize Google Gemini Client
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.logger.warning("⚠️  GOOGLE_API_KEY not set. SDK execution will fail.")
            self.gemini_client = None
        else:
            try:
                self.gemini_client = genai.Client(api_key=api_key)
                self.logger.info("✅ Google Gemini client initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Gemini client: {e}")
                self.gemini_client = None

        # Initialize Anthropic Client [Phase 13.1]
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            self.logger.warning(
                "⚠️  ANTHROPIC_API_KEY not set. Anthropic execution will fail."
            )
            self.anthropic_client = None
        else:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                self.logger.info("✅ Anthropic client initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Anthropic client: {e}")
                self.anthropic_client = None

        # Phase 10: Autonomy Gates
        self.data_volume_threshold = 50
        self.kill_switch = KillSwitch()

        # FASE 4: Epistemology via DI (telemetry + budget + memory unified)
        self.epistemology = self._get_epistemology()

        # Telemetry (via epistemology store)
        self.meter = self.epistemology.get_meter("antigravity.executor")
        self.execution_counter = self.meter.create_counter(
            "mnemos.agent.execution", description="Agent executions"
        )
        self.token_counter = self.meter.create_counter(
            "mnemos.agent.tokens", description="Estimated token usage"
        )

    def _get_epistemology(self):
        """
        Resolves EpistemologyStore via DI if enabled, else uses direct imports (backward compat).

        Feature flag: epistemology_via_di (from di-bindings.yml)
        """
        from axis_reasoning._internal.di import get_container

        container = get_container()
        config = container.config

        if config.epistemology_via_di:
            # DI path: resolve via container
            from axis_sdk.protocols import EpistemologyStore
            from axis_reasoning._internal.epistemology import EpistemologyStoreStub

            return container.resolve(EpistemologyStore) or EpistemologyStoreStub()
        else:
            from axis_reasoning._internal.epistemology import EpistemologyStoreStub

            return EpistemologyStoreStub()

    def set_shadow_log_path(self, path: str):
        """Set a custom path for the shadow mode log."""
        self.shadow_log_file = path
        os.makedirs(os.path.dirname(self.shadow_log_file), exist_ok=True)
        self.logger.info(f"📝 Shadow log path set to: {self.shadow_log_file}")

    def reset_shadow_log(self):
        """Clear the current shadow log file if it exists."""
        if os.path.exists(self.shadow_log_file):
            os.remove(self.shadow_log_file)
            self.logger.info("🧹 Shadow log reset.")

    def _load_optimization_config(self) -> dict:
        """Load optimization configuration."""
        try:
            config_path = paths.config / "optimization_config.yml"
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load optimization config: {e}")
            return {}

    def _log_shadow_decision(self, shadow_data: dict):
        """Log shadow mode decision to JSONL file."""
        if not self.shadow_mode:
            return

        try:
            os.makedirs(os.path.dirname(self.shadow_log_file), exist_ok=True)
            with open(self.shadow_log_file, "a") as f:
                f.write(json.dumps(shadow_data) + "\n")
            self.logger.debug(f"📝 Shadow decision logged: {shadow_data.get('task_id')}")
        except Exception as e:
            self.logger.error(f"Failed to log shadow decision: {e}")

    def _get_tool_for_agent(self, agent_id: str) -> str:
        """Determine which CLI tool to use for the agent."""
        if "claude" in agent_id:
            return "claude"
        elif "gemini" in agent_id:
            return "gemini"
        elif "gpt" in agent_id:
            return "gpt"
        elif "codex" in agent_id:
            return "dev"
        else:
            return "claude"

    @telemetry.trace_span("Executor._execute_sdk")
    def _execute_sdk(
        self,
        agent_id: str,
        prompt: str,
        session_id: str,
        cache_id: Optional[str] = None,
        thinking_config: Optional[Dict[str, Any]] = None,
        model_name: str = "models/gemini-2.0-flash-001",
    ) -> Tuple[bool, str, int, int, Optional[str]]:
        """
        Real SDK execution with Context Caching support via Google Gemini API.
        Returns: (success, output, tokens_used, cached_tokens, new_cache_id)

        Note: Gemini 2.0 Flash requires minimum 4096 tokens for caching.
        """
        if not self.gemini_client:
            return False, "❌ GOOGLE_API_KEY not configured", 0, 0, None

        try:
            # model_name passed from selector

            # CACHE LOGIC: Try to reuse existing cache
            cache = None
            if cache_id:
                try:
                    cache = self.gemini_client.caches.get(name=cache_id)
                    self.logger.info(f"🎯 CACHE HIT: Reusing {cache_id}")
                except Exception as e:
                    self.logger.warning(
                        f"⏱️  Cache {cache_id} not found or expired: {e}"
                    )

            # Estimate content size (rough: 1 token ≈ 4 chars)
            # Minimum 4096 tokens required for Gemini 2.0 Flash caching
            system_instruction = f"Session: {session_id}\nYou are {agent_id}."
            estimated_tokens = len(system_instruction) // 4 + len(prompt) // 4

            # Only create cache if we have enough content (4096+ tokens)
            # AND no existing cache was found
            if not cache and estimated_tokens >= 4096:
                try:
                    cache = self.gemini_client.caches.create(
                        model=model_name,
                        config=genai_types.CreateCachedContentConfig(
                            display_name=f"{agent_id}_{session_id}",
                            system_instruction=system_instruction,
                            contents=[prompt],  # Cache the initial prompt as context
                            ttl="3600s",  # 1 hour default
                        ),
                    )
                    self.logger.info(
                        f"💾 NEW CACHE: {cache.name} ({estimated_tokens} est. tokens)"
                    )
                except Exception as e:
                    # If cache creation fails (e.g., quota, size), proceed without cache
                    self.logger.warning(
                        f"⚠️  Cache creation failed: {e}. Using direct generation."
                    )
                    cache = None
            elif not cache:
                self.logger.debug(
                    f"ℹ️  Content too small for caching ({estimated_tokens} tokens, "
                    f"min 4096 required). Using direct generation."
                )

            # GENERATE CONTENT
            generation_config = genai_types.GenerateContentConfig()
            if cache:
                generation_config.cached_content = cache.name

            # Phase 10: Support thinking_config
            if thinking_config:
                generation_config.thinking_config = genai_types.ThinkingConfig(
                    **thinking_config
                )
                self.logger.debug(f"🧠 Applied thinking_config: {thinking_config}")

            response = self.gemini_client.models.generate_content(
                model=model_name, contents=prompt, config=generation_config
            )

            # Extract usage metadata
            usage = response.usage_metadata
            tokens_used = usage.total_token_count
            cached_tokens = getattr(usage, "cached_content_token_count", 0)

            self.logger.info(
                f"✅ SDK Response: {tokens_used} total tokens "
                f"({cached_tokens} from cache)"
            )

            output_text = response.text
            return (
                True,
                output_text,
                tokens_used,
                cached_tokens,
                cache.name if cache else None,
            )

        except Exception as e:
            self.logger.error(f"❌ SDK execution failed: {e}")
            return False, f"SDK Error: {str(e)}", 0, 0, None

    @telemetry.trace_span("Executor._execute_anthropic_sdk")
    def _execute_anthropic_sdk(
        self,
        agent_id: str,
        prompt: str,
        session_id: str,
        model_name: str = "claude-3-5-sonnet-20240620",
        system_prompt: Optional[str] = None,
    ) -> Tuple[bool, str, int, int, Optional[str]]:
        """
        Real Anthropic SDK execution for Claude models with Prompt Caching support.

        Implements Anthropic Prompt Caching (https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching):
        - Caches system prompts with "cache_control" breakpoints
        - Minimum 1024 tokens required for caching
        - 5-minute TTL, up to 90% cost savings on cache hits

        Returns: (success, output, tokens_used, cached_tokens, None)
        """
        if not self.anthropic_client:
            return False, "❌ ANTHROPIC_API_KEY not configured", 0, 0, None

        try:
            # System instruction with cache control marker
            # If custom system_prompt provided (e.g., planner system prompt), use it
            # Otherwise fallback to minimal agent identification
            if system_prompt:
                system_instruction = system_prompt
            else:
                system_instruction = f"Session: {session_id}\nYou are {agent_id}."

            # Estimate tokens (rough: 1 token ≈ 4 chars)
            estimated_tokens = len(system_instruction) // 4

            # Only apply cache_control if system instruction >= 1024 tokens
            # (Anthropic minimum for caching)
            system_blocks = []
            if estimated_tokens >= 256:  # 256 chars * 4 = 1024 tokens (approx)
                system_blocks.append(
                    {
                        "type": "text",
                        "text": system_instruction,
                        "cache_control": {
                            "type": "ephemeral"
                        },  # Enable caching for this block
                    }
                )
                self.logger.debug(
                    f"💾 Applying prompt caching to system instruction "
                    f"(~{estimated_tokens} tokens, min 1024 required)"
                )
            else:
                # Too small to cache - use simple string format
                system_blocks = system_instruction
                self.logger.debug(
                    f"ℹ️  System instruction too small for caching "
                    f"(~{estimated_tokens} tokens, min 1024 required)"
                )

            response = self.anthropic_client.messages.create(
                model=model_name,
                max_tokens=4096,
                system=system_blocks,  # Can be string or list of blocks with cache_control
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract usage metadata
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            tokens_used = input_tokens + output_tokens

            # Extract cache metrics (Anthropic returns these in usage object)
            cache_creation_tokens = getattr(
                response.usage, "cache_creation_input_tokens", 0
            )
            cache_read_tokens = getattr(response.usage, "cache_read_input_tokens", 0)
            cached_tokens = cache_creation_tokens + cache_read_tokens

            # Log cache performance
            if cache_read_tokens > 0:
                cache_hit_pct = (
                    (cache_read_tokens / input_tokens * 100) if input_tokens > 0 else 0
                )
                self.logger.info(
                    f"✅ Anthropic SDK Response: {tokens_used} total tokens "
                    f"({input_tokens} in, {output_tokens} out) | "
                    f"🎯 CACHE HIT: {cache_read_tokens} tokens ({cache_hit_pct:.1f}%)"
                )
            elif cache_creation_tokens > 0:
                self.logger.info(
                    f"✅ Anthropic SDK Response: {tokens_used} total tokens "
                    f"({input_tokens} in, {output_tokens} out) | "
                    f"💾 CACHE CREATED: {cache_creation_tokens} tokens"
                )
            else:
                self.logger.info(
                    f"✅ Anthropic SDK Response: {tokens_used} total tokens "
                    f"({input_tokens} in, {output_tokens} out)"
                )

            # Join content items if multiple (usually one text item)
            output_text = "".join(
                [block.text for block in response.content if hasattr(block, "text")]
            )
            return True, output_text, tokens_used, cached_tokens, None

        except Exception as e:
            self.logger.error(f"❌ Anthropic SDK execution failed: {e}")
            return False, f"Anthropic SDK Error: {str(e)}", 0, 0, None

    @telemetry.trace_span("Executor.execute_batch")
    @observe(as_type="span", name="agent_batch_execution")
    def execute_batch(
        self, agent_requests: Dict[str, str], session_id: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Executes a batch of independent agent prompts.
        Useful for parallel audits (Clarity Sentinel + Code Review).
        """
        log_info(f"📦 [BATCH EXECUTION] processing {len(agent_requests)} requests.")
        results = {}

        # For Phase 6, we execute them sequentially or via threads, but the 'Intelligent' part
        # is the unified record retrieval.
        for agent_id, prompt in agent_requests.items():
            success, output, tokens = self.execute(agent_id, prompt, session_id)
            results[agent_id] = {
                "success": success,
                "output": output,
                "tokens_used": tokens,
            }

        return results

    @telemetry.trace_span("Executor.execute")
    @observe(as_type="span", name="agent_execution")
    def execute(
        self, agent_id: str, task_description: str, session_id: str
    ) -> Tuple[bool, str, int]:
        """
        Execute a task with the specified agent.
        Returns: (success, output, tokens_used)
        """
        tool = self._get_tool_for_agent(agent_id)

        # Construct the prompt
        # In a real scenario, we might load a template here
        prompt = f"Task for {agent_id} (Session: {session_id}):\n{task_description}"

        cmd = [tool]
        if tool == "claude":
            cmd.extend(["--output-format", "json", "-p", prompt])
        elif tool == "dev":
            import sys

            cmd = [sys.executable, "-m", "antigravity.cli", "dev"]
            if "lint" in task_description:
                cmd.extend(["lint", ".", "--json"])  # Enforce structured output
            else:
                cmd.extend(["scan", ".", "--json"])
        elif tool == "gpt":
            import sys

            cmd = [
                sys.executable,
                "-m",
                "antigravity.cli",
                "gpt",
                "chat",
                prompt,
                "--format",
                "json",
            ]
        else:
            cmd.append(prompt)

        self.logger.info(
            f"Executing agent {agent_id} using {tool} (Observability Source)"
        )
        self.execution_counter.add(1, {"agent_id": agent_id, "tool": tool})

        try:
            # Capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise immediately, check return code
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # Estimate tokens (very rough approximation: 1 token ~= 4 chars)
                tokens_used = len(output) // 4 + len(prompt) // 4
                self.token_counter.add(tokens_used, {"agent_id": agent_id})
                return True, output, tokens_used
            else:
                error_msg = result.stderr.strip()
                self.logger.error(f"Agent execution failed: {error_msg}")
                return False, error_msg, 0

        except FileNotFoundError:
            msg = f"CLI tool '{tool}' not found in PATH."
            self.logger.error(msg)
            return False, msg, 0
        finally:
            # Phase 8.2: Emit Observability Event for CLI executions
            from axis_reasoning._internal.ingestor import ingestor

            ingestor.emit(
                event_type=EventType.EXECUTION,
                actor_id=agent_id,
                actor_type=ActorType.AGENT,
                session_id=session_id,
                metadata={"tool": tool, "mode": "cli"},
                usage={"total_tokens": 0},  # CLI doesn't always return tokens easily
                accounting_source=TelemetrySource.CLI,
                verdict="COMPLETED",
            )

    @telemetry.trace_span("Executor.execute_with_cache")
    def execute_with_cache(
        self, ctx: SovereignContext, prompt: str, use_cache: bool = True
    ) -> Tuple[bool, str, int, TelemetrySource]:
        """
        Execute with Context Caching and Phase 8 Optimization using SovereignContext.
        Returns: (success, output, tokens, accounting_source)
        """
        agent_id = ctx.agent_id
        session_id = ctx.session_id
        recent_lucidity = ctx.recent_lucidity
        budget_remaining = ctx.budget_remaining
        cache_id = None

        # 1. Model Selection (would-be decision in shadow mode)
        if ctx.forced_model:
            would_be_model = ctx.forced_model
            selection_reasoning = (
                f"FORCED_OVERRIDE (Phase 14 Benchmark): {would_be_model}"
            )
            self.logger.info(f"🚀 {selection_reasoning}")
        else:
            would_be_model, selection_reasoning = model_selector.select_model(
                task_description=prompt,
                agent_id=agent_id,
                recent_lucidity=recent_lucidity,
                budget_remaining=budget_remaining,
            )

        # 2. Determine actual model (shadow mode or dry run uses default/intended)
        autonomous_mode = self.kill_switch.get_autonomous_mode()

        # 2. CANONICAL EXECUTION POLICY
        # ---------------------------------------------------------------------
        # PRINCIPLE: API is for the system. CLI/UI is for the human.
        # MANDATORY: Gemini API for Benchmarks/Shadow. Claude API PROHIBITED.

        # PROVIDER ROUTING logic
        is_anthropic = "claude" in would_be_model.lower()

        # RULE 1: Global Prohibition of Claude API
        if is_anthropic:
            self.logger.info(
                f"🔒 CANONICAL: Claude API is PROHIBITED. Routing {agent_id} to CLI."
            )
            success, output, tokens = self.execute(agent_id, prompt, session_id)
            return success, output, tokens, TelemetrySource.CLI

        # RULE 2: Systemic Requirements (Mandatory Gemini API)
        is_systemic = (
            bool(ctx.forced_model) or self.shadow_mode or autonomous_mode == "dry_run"
        )

        if is_systemic:
            # Mandate Gemini API for Benchmarks (forced_model) and Shadow Mode
            if ctx.forced_model:
                actual_model = ctx.forced_model
                self.logger.info(
                    f"💎 SYSTEMIC (Benchmark): Using Gemini API -> {actual_model}"
                )
            else:
                actual_model = "models/gemini-2.0-flash-001"
                self.logger.info(f"🌑 SYSTEMIC (Shadow/Dry): Using Gemini API Flash")
        else:
            # DEFAULT: Use CLI for local Pro/Plus accounts
            self.logger.info(
                f"🕹️ CANONICAL: Engineering/Decision -> Routing {agent_id} to CLI."
            )
            success, output, tokens = self.execute(agent_id, prompt, session_id)
            return success, output, tokens, TelemetrySource.CLI

        # Log Decision to Unified Ingestor (v0.1 Schema)
        from axis_reasoning._internal.ingestor import ingestor

        ingestor.emit(
            event_type=EventType.DECISION,
            actor_id=agent_id,
            actor_type=ActorType.SYSTEM,
            session_id=session_id,
            decision_kind="model_selection",
            metadata={
                "would_be_model": would_be_model,
                "actual_model": actual_model,
                "reasoning": selection_reasoning,
                "recent_lucidity": recent_lucidity,
            },
            accounting_source=TelemetrySource.SDK,
            verdict="SELECTED",
        )

        # Update context
        ctx.update_with_selection(actual_model, selection_reasoning)

        # 3. ROUTE TO PROVIDER SDK
        if "claude" in actual_model.lower():
            # Hybrid Strategy: Use SDK if key exists, otherwise fallback to CLI (Claude Pro)
            if self.anthropic_client:
                (
                    success,
                    output,
                    tokens,
                    cached_tokens,
                    new_cache_id,
                ) = self._execute_anthropic_sdk(
                    agent_id,
                    prompt,
                    session_id,
                    model_name=actual_model,
                    system_prompt=ctx.system_prompt,  # Pass planner system prompt for caching
                )
            else:
                success, output, tokens = self.execute(agent_id, prompt, session_id)
                return success, output, tokens, TelemetrySource.CLI
        else:
            # 3. Try to find existing cache (Gemini only for now)
            cache_id = context_cache_manager.get_cache_id(agent_id, prompt)

            # 4. Execute via SDK
            thinking_config = None
            if "gemini" in actual_model.lower():
                # TODO: Migrate reasoning_controller in Phase 2
                reasoning_controller = None
                if reasoning_controller:
                    complexity = model_selector.score_complexity(prompt, agent_id)
                    thinking_config = reasoning_controller.get_thinking_config(
                        lucidity=recent_lucidity,
                        complexity=complexity,
                        model_name=actual_model,
                    )

            success, output, tokens, cached_tokens, new_cache_id = self._execute_sdk(
                agent_id,
                prompt,
                session_id,
                cache_id=cache_id,
                thinking_config=thinking_config,
                model_name=actual_model,
            )

            # 5. Save new cache if created
            if success and new_cache_id and not cache_id:
                context_cache_manager.set_cache_id(agent_id, prompt, new_cache_id)

        # 6. Track cost
        if success and tokens > 0:
            # Estimate input/output split (rough: 70% input, 30% output)
            input_tokens = int(tokens * 0.7)
            output_tokens = int(tokens * 0.3)
            # cached_tokens now extracted from SDK usage metadata

            cost = cost_tracker.track_generation_cost(
                agent_id=agent_id,
                model=actual_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
            )

        # 7. Record feedback
        from axis_reasoning.orchestrator.feedback_collector import feedback_collector

        feedback_collector.record_execution(
            agent_id=agent_id,
            task_type="gemini_execution",
            success=success,
            tokens_used=tokens,
            model=actual_model,
            lucidity_score=recent_lucidity,
            cached_tokens=cached_tokens,
            execution_time_ms=None,
        )

        # 8. Shadow mode logging
        if self.shadow_mode:
            shadow_data = {
                "task_id": f"{session_id}_{agent_id}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "would_be_model": would_be_model,
                "would_be_budget": budget_remaining,
                "actual_model": actual_model,
                "actual_budget": budget_remaining,  # Same in shadow mode
                "selection_reasoning": selection_reasoning,
                "lucidity": recent_lucidity,
                "tokens_used": tokens,
                "success": success,
                "cached": cache_id is not None,
                "intended_action": autonomous_mode == "dry_run",
                "authority_level": "SHARED"
                if autonomous_mode == "dry_run"
                else "ADVISORY",
            }
            self._log_shadow_decision(shadow_data)

            # Phase 9: Governance Mapping v1.0 - Always-On Decision Logging
            # Generate evidence reference (shadow log entry ID for traceability)
            evidence_ref = f"shadow_{session_id}_{agent_id}_{int(time.time())}"

            # DECISION 1: Shadow Recommendation (ALWAYS)
            # Documents what the optimizer recommended based on lucidity + budget
            from axis_reasoning._internal.ingestor import ingestor

            ingestor.emit(
                event_type=EventType.DECISION,
                actor_id="shadow_optimizer",
                actor_type=ActorType.SYSTEM,
                session_id=session_id,
                decision_kind="shadow_recommendation",
                metadata={
                    "recommended_model": would_be_model,
                    "lucidity_estimate": recent_lucidity,  # From context
                    "budget_remaining": budget_remaining,
                    "selection_reasoning": selection_reasoning,
                    "intended_action": autonomous_mode == "dry_run",
                    "authority_level": "SHARED"
                    if autonomous_mode == "dry_run"
                    else "ADVISORY",
                },
                accounting_source=TelemetrySource.SDK,
                usage={"total_tokens": 0},  # No tokens consumed by decision
                evidence_ref=evidence_ref,
                verdict="RECOMMENDED",
            )

            # DECISION 2: Shadow Deployment (ALWAYS)
            # Documents what model was actually deployed + actual costs
            ingestor.emit(
                event_type=EventType.DECISION,
                actor_id="shadow_optimizer",
                actor_type=ActorType.SYSTEM,
                session_id=session_id,
                decision_kind="shadow_deployment",
                metadata={
                    "deployed_model": actual_model,
                    "actual_tokens": tokens,
                    "cached_tokens": cached_tokens,
                    "success": success,
                },
                accounting_source=TelemetrySource.SDK,
                usage={"total_tokens": tokens, "cached_tokens": cached_tokens},
                evidence_ref=evidence_ref,
                verdict="DEPLOYED",
            )

            # DECISION 3: Shadow Divergence (CONDITIONAL - only when differs)
            # Identifies optimization opportunities (when recommendation != deployment)
            if would_be_model != actual_model:
                ingestor.emit(
                    event_type=EventType.DECISION,
                    actor_id="shadow_optimizer",
                    actor_type=ActorType.SYSTEM,
                    session_id=session_id,
                    decision_kind="shadow_divergence",
                    metadata={
                        "recommended_model": would_be_model,
                        "deployed_model": actual_model,
                        "divergence_reason": "shadow_mode_active",
                        "lucidity_estimate": recent_lucidity,
                        "budget_remaining": budget_remaining,
                        "potential_savings": "TBD",  # Phase 10 calculation
                    },
                    accounting_source=TelemetrySource.SDK,
                    usage={"total_tokens": 0},
                    evidence_ref=evidence_ref,
                    verdict="DIVERGED",
                )

        self.token_counter.add(
            tokens, {"agent_id": agent_id, "cached": str(cache_id is not None)}
        )
        return success, output, tokens, TelemetrySource.SDK

    def _get_shadow_mode_count(self) -> int:
        """Helper to get current shadow mode decision count."""
        try:
            if os.path.exists(self.shadow_log_file):
                with open(self.shadow_log_file, "r") as f:
                    return sum(1 for line in f)
            # Record performance feedback
            from axis_reasoning._internal.di import get_container
            from axis_reasoning._internal.state_paths import StatePathResolver

            try:
                container = get_container()
                resolver = StatePathResolver(
                    enable_isolation=container.config.context_isolation
                )
            except:
                resolver = StatePathResolver(enable_isolation=True)

            fb_path = str(resolver.get_performance_feedback_path())
            if os.path.exists(fb_path):
                with open(fb_path, "r") as f:
                    data = json.load(f)
                    return len(data)
        except Exception:
            return 0
        return 0

    def should_activate_autonomy(self, session_id: str) -> bool:
        """
        Phase 10: Smart Activation Gate.
        Evaluates Kill Switch and Data Volume threshold.
        """
        # 1. Kill Switch Authority (Absolute)
        autonomous_mode = self.kill_switch.get_autonomous_mode()
        if autonomous_mode == "false":
            self.kill_switch.log_kill_switch_block(session_id)
            return False

        # 2. Data Volume Gate
        count = self._get_shadow_mode_count()
        if count < self.data_volume_threshold:
            # Phase 10.5 Override: If in DRY_RUN or TRUE, we might want to bypass for testing
            # but usually, we honor the threshold unless explicitly forced.
            from axis_reasoning._internal.decision_logger import log_decision

            log_decision(
                actor_id="orchestrator",
                session_id=session_id,
                decision_kind="autonomy_data_gate",
                metadata={
                    "status": "blocked",
                    "count": count,
                    "threshold": self.data_volume_threshold,
                    "mode": autonomous_mode,
                },
                verdict="WARN_SHADOW",
            )
            # For Phase 10.5 dry run specifically, we allow it if mode is dry_run or true
            # but keep the log.
            if autonomous_mode not in ["dry_run", "true"]:
                return False

        return True


# Global instance
executor = AgentExecutor()
