"""
Orchestrator Engine v6.1 — Full Governance Integration (Phase 5)
Coordinates the Sovereign Loop with Intent Lock, Reasoning Limits, and Contract Enforcement.
"""
from __future__ import annotations

import logging
import time
import os
import re
from typing import Dict, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass

from axis_reasoning._internal.config import paths
from axis_reasoning._internal.logging import log_info, log_warning, log_error, log_success
from axis_reasoning._internal.telemetry import telemetry_engine as telemetry  # Keep for decorators only
from axis_reasoning.session.ledger import ledger
from axis_reasoning.orchestrator.routing_context import get_latest_decision_id
from axis_reasoning.orchestrator.context import SovereignContext
from axis_reasoning._internal.schemas import EventType, ActorType, TelemetrySource
from axis_reasoning._internal.observability import log_event

# Runtime Components (contracts only - implementations via DI)
from axis_reasoning.runtime.contracts import (
    SovereignAction, GatewayDecision, IntentAnchor,
    create_intent_anchor, check_intent_drift
)

# Planner Components
from axis_reasoning.planner.planner import SovereignPlanner, PlannerConfig
from axis_reasoning.planner.diagnostics import diagnostics
from axis_reasoning._internal.context7_schemas import ShadowModeEvent, sanitize_query

# Runtime Errors
from axis_reasoning.runtime.orchestrator_errors import (
    OrchestratorBudgetExceeded,
    OrchestratorTimeout,
    OrchestratorGovernanceBlocked
)

# Legacy Inference (Brain) — used for LLM calls
from axis_reasoning.executor import executor as brain_executor

# Governance Gates (Phase 10.5) - TODO: Migrate in Phase 2

if TYPE_CHECKING:
    from axis_reasoning.planner.planner import SovereignPlanner
    from axis_reasoning.orchestrator.context import SovereignContext

# TODO: Migrate knowledge/compliance/autonomy components in Phase 2.
class TaskContractResolver:
    def resolve_contract(self, _task: str):
        return None


class KnowledgeInjector:
    def gather_knowledge_stack(self, _task_contract):
        return []


class SemanticBinder:
    def create_binding(self, _content, _authority, _source_id, _task_contract, _metadata):
        return None

    def render_semantic_envelope(self, _bindings, _task_contract):
        return ""


class UseCaseDetector:
    def detect(self, _query: str, shadow_mode: bool = False):
        return None

    def _extract_libraries(self, _query: str):
        return []


class ShadowLoggerStub:
    def log_event(self, _event) -> None:
        return None


shadow_logger = ShadowLoggerStub()


class _ToolServerStub:
    def execute(self, _invocation):
        raise RuntimeError("Tool server is not available in stubbed runtime.")


class _AuthorityAdapterStub:
    def __init__(self):
        self._gateway = None

    def evaluate(self, _action, _agent_id: Optional[str] = None) -> GatewayDecision:
        return GatewayDecision(
            allowed=True,
            verdict_code="APPROVED",
            risk_score=0.0,
            reason="Stub authority adapter",
        )

    def resolve_invocation(self, action):
        return action

    def get_routing_decision(self, _task: str, _context: Optional[Dict[str, Any]] = None) -> str:
        return "claude_coder"


class _RuntimeAdapterStub:
    def __init__(self):
        self._gateway = None
        self._tool_server = _ToolServerStub()
        self._planner = None

    def get_planner(self):
        return self._planner


class ImpactLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AuthorityStatus(str):
    ADVISORY_ONLY = "ADVISORY_ONLY"
    BLOCKED = "BLOCKED"
    ALLOWED = "ALLOWED"


class GovernanceEngine:
    def __init__(self):
        self.state_anchor_path = "governance_anchor_stub"

    def determine_impact(self, _task_description: str) -> str:
        return ImpactLevel.LOW

    def get_authority_status(self, _impact: str) -> str:
        return AuthorityStatus.ALLOWED

@dataclass
class OrchestrationResult:
    session_id: str
    primary_agent: str
    status: str
    task_type: str
    output: Optional[str] = None
    diagnostics: Optional[Dict] = None
    tokens_used: int = 0
    fatigue_applied: bool = False

class OrchestratorEngine:
    """
    Sovereign Agent Orchestrator (v6.1 - Full Governance).
    Implements Intent Lock, Reasoning Limits, and Contract Enforcement.
    Now supports specialized sub-agents with context isolation.
    """

    def __init__(self):
        self.logger = logging.getLogger("antigravity.orchestrator")

        # Risk 5.1: Recursive Spawning Check
        if os.environ.get("ANTIGRAVITY_LEVEL") == "Max":
            msg = "CRITICAL: Recursive Spawning Detected! Orchestrator cannot run inside itself."
            self.logger.critical(msg)
            raise RuntimeError(msg)

        # FASE 5: Runtime Initialization via DI (feature-flagged)
        from axis_reasoning._internal.di import get_container
        
        container = get_container()
        config = container.config
        
        # Authority Provider (governance + routing)
        if config.authority_via_di:
            from axis_sdk.protocols import AuthorityProvider
            self.authority = container.resolve(AuthorityProvider) or _AuthorityAdapterStub()
        else:
            # Legacy path: adapter wrapping GovernanceGateway (stubbed)
            self.authority = _AuthorityAdapterStub()
        
        # Runtime Executor (tool execution + planning)
        if config.runtime_via_di:
            from axis_sdk.protocols import RuntimeExecutor
            self.runtime = container.resolve(RuntimeExecutor) or _RuntimeAdapterStub()
        else:
            # Legacy path: adapter wrapping ToolServer + Planner (stubbed)
            self.runtime = _RuntimeAdapterStub()
        
        # Legacy compatibility: expose gateway/tool_server/planner for existing code
        # These delegate to authority/runtime internally
        if config.authority_via_di or config.runtime_via_di:
            # Create compatibility shims
            self.gateway = self.authority if hasattr(self.authority, "evaluate") else None
            self.planner = self.runtime.get_planner() if hasattr(self.runtime, 'get_planner') else None
            # tool_server not directly exposed in new model
        else:
            # Direct access for legacy path (via adapters)
            self.gateway = (
                self.authority._gateway if hasattr(self.authority, "_gateway") else self.authority
            )
            self.planner = self.runtime._planner if hasattr(self.runtime, "_planner") else None
            self.tool_server = (
                self.runtime._tool_server if hasattr(self.runtime, "_tool_server") else None
            )

        # SKIB Governance Engine
        self.contract_resolver = TaskContractResolver()
        self.injector = KnowledgeInjector()
        self.binder = SemanticBinder()
        self.use_case_detector = UseCaseDetector()

        # FASE 4: Epistemology via DI (telemetry + budget + memory unified)
        self.epistemology = self._get_epistemology()

        # Telemetry (via epistemology store)
        self.meter = self.epistemology.get_meter("antigravity.orchestrator")
        self.task_counter = self.meter.create_counter("mnemos.task.count")

        # Governance Config (from planner)
        planner_config = self.planner.config if self.planner else PlannerConfig()
        self.MAX_ITERATIONS = planner_config.max_tool_iterations
        self.MAX_DENIALS = planner_config.max_denials_before_abort
        self.MAX_THOUGHT_STEPS = planner_config.max_thought_steps
        self.MAX_REPLANS = planner_config.max_replans

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

    @telemetry.trace_span("Orchestrator.run_sovereign_loop")
    def orchestrate_task(self, task_description: str, agent_id: str = "claude_coder", session_id: str = None, dry_run: bool = False) -> OrchestrationResult:
        """
        Executes the Sovereign Agent Loop with Full Governance.
        Args:
            dry_run: If True, blocks actual execution and mimics success.
        """
        start_time = time.time()
        self.task_counter.add(1)
        
        # Session Setup
        if not session_id:
            mode = "sovereign_dry_run" if dry_run else "sovereign"
            session_id = ledger.create_session(
                task_type="sovereign_task",
                agents=[agent_id],
                metadata={"mode": mode, "planner": "v6.0_governance"}
            )
        
        # Phase 8 + Signal Contract v0.1: Initialize Sovereign Context with dual lucidity
        from axis_reasoning.orchestrator.feedback_collector import feedback_collector
        
        # 1. Get RAW SIGNAL (unguarded EMA)
        lucidity_estimate = feedback_collector.get_lucidity_estimate(agent_id, "sovereign_task")
        
        # 2. Apply GOVERNANCE GUARD (max 10% drop per turn)
        # Retrieve previous guarded value from session metadata (explicit state governance)
        previous_guarded = None
        if session_id:
            session_data = ledger.get_session(session_id)
            if session_data and session_data.metadata:
                previous_guarded = session_data.metadata.get("last_lucidity_guarded")
        
        # If no previous session or first turn, use estimate as baseline
        if previous_guarded is None:
            lucidity_guarded = lucidity_estimate
        else:
            # Apply governance: max 10% drop from previous guarded value
            max_drop = previous_guarded * 0.10
            lucidity_guarded = max(lucidity_estimate, previous_guarded - max_drop)
        
        # 3. Create Sovereign Context with BOTH signal values (explicit state)
        # Include planner system prompt for Anthropic prompt caching
        planner_system_prompt = self.planner.get_system_prompt() if self.planner else None

        ctx = SovereignContext(
            session_id=session_id,
            agent_id=agent_id,
            task_description=task_description,
            recent_lucidity=lucidity_guarded,  # Backward compat (used for decisions)
            lucidity_estimate=lucidity_estimate,  # Raw signal (Signal Contract v0.1)
            lucidity_guarded=lucidity_guarded,    # Governance-protected
            budget_remaining=self.epistemology.get_remaining_budget(agent_id),
            is_dry_run=dry_run,
            system_prompt=planner_system_prompt  # For prompt caching
        )
        
        # GE-P2 Authority Gate (Phase 10.5)
        gov_engine = GovernanceEngine()
        impact = gov_engine.determine_impact(task_description)
        auth_status = gov_engine.get_authority_status(impact)
        
        if auth_status == AuthorityStatus.ADVISORY_ONLY:
            log_warning(f"GE-P2 AUTHORITY INTERVENTION: Downgrading to ADVISORY mode.")
            log_warning(f"  Task: {task_description[:100]}...")
            log_warning(f"  Impact: {impact}")
            log_warning(f"  Reason: Institutional Phase 2 not active.")
            log_warning(f"  Source: {gov_engine.state_anchor_path}")
            ctx.is_dry_run = True
            ctx.metadata["governance_mode"] = "ADVISORY"
            ctx.metadata["authority_source"] = str(gov_engine.state_anchor_path)
            
        elif auth_status == AuthorityStatus.BLOCKED:
            log_error(f"GE-P2 AUTHORITY BLOCK: Task impact {impact} is BLOCKED.")
            log_error(f"  Reason: High-risk actions require direct Human-in-Command.")
            raise OrchestratorGovernanceBlocked(f"Task impact {impact} requires manual authorization.")
        
        # 4. Emit DUAL TELEMETRY (Signal Contract v0.1)
        # Note: Using record_event wrapper - full ingestor.emit signature via adapter
        from axis_reasoning._internal.ingestor import ingestor
        ingestor.emit(
            event_type=EventType.TRACE,
            actor_id=agent_id,
            actor_type=ActorType.AGENT,
            session_id=session_id,
            metadata={
                "lucidity_estimate": lucidity_estimate,  # Raw signal
                "lucidity_guarded": lucidity_guarded,    # Governance-protected
                "guard_applied": abs((lucidity_estimate or 0.0) - (lucidity_guarded or 0.0)) > 0.001,
                "guard_delta": (lucidity_guarded or 0.0) - (lucidity_estimate or 0.0) if previous_guarded else 0.0
            },
            accounting_source=TelemetrySource.SDK,
            usage={"total_tokens": 0},  # No tokens yet
            verdict="SIGNAL_LOGGED"
        )

        # ADR-0108: Context7 Shadow Mode Telemetry (Logging only)
        if os.getenv("CONTEXT7_SHADOW_MODE", "false").lower() == "true":
            self._log_context7_shadow_event(task_description, session_id)

        # Phase A: Intent Lock - Create Anchor
        intent_anchor = create_intent_anchor(task_description, session_id)
        log_info(f"🔒 Intent Lock created: {len(intent_anchor.intent_keywords)} keywords")
        
        # --- Phase 4: Expansion & Calibration (Budget & Fatigue) ---
        metadata = {} # Placeholder for actual metadata retrieval
        priority = metadata.get("priority", "P1") if session_id else "P1" # Fallback
        try:
            self.epistemology.check_budget(agent_id, estimated_tokens=0, priority=priority)
        except OrchestratorBudgetExceeded as e:
            log_error(f"💰 Budget/Fatigue Block: {str(e)}")
            return OrchestrationResult(
                session_id=session_id or "failed",
                primary_agent=agent_id,
                status="blocked",
                task_type="sovereign_task",
                output=f"Budget or Fatigue limit reached: {str(e)}"
            )

        # Restore Fatigue Penalty (v1.1)
        penalty_ratio = self.epistemology.get_fatigue_penalty(agent_id)
        current_max_thought_steps = self.MAX_THOUGHT_STEPS
        fatigue_applied = False
        if penalty_ratio > 0:
            current_max_thought_steps = int(self.MAX_THOUGHT_STEPS * (1.0 - penalty_ratio))
            log_warning(f"🔋 FATIGUE PENALTY applied: Thought steps reduced to {current_max_thought_steps}")
            fatigue_applied = True
        # -----------------------------------------------------------

        if dry_run:
            log_info("🧪 DRY RUN ACTIVE: All actions will be simulated. Gateway validation remains active.")

        # Diagnostics
        diag_session = diagnostics.start_session(session_id, task_description)
        
        # SKIB: Knowledge Injection
        task_contract = self.contract_resolver.resolve_contract(task_description)
        knowledge_chunks = self.injector.gather_knowledge_stack(task_contract)
        bindings = [
            self.binder.create_binding(c.content, c.authority, c.source_id, task_contract, c.metadata) 
            for c in knowledge_chunks
        ]
        binding_envelope = self.binder.render_semantic_envelope(bindings, task_contract)
        
        # MEMORY ENRICHMENT: Query past similar tasks (Phase 10.6)
        memory_context = ""
        if self.epistemology.is_memory_available():
            memories = self.epistemology.search_memory(
                query=task_description,
                limit=3,
                success_only=True
            )
            if memories:
                memory_lines = ["\n[SYSTEM: Historical Context]"]
                for i, mem in enumerate(memories, 1):
                    memory_lines.append(f"{i}. Similar task ({mem['timestamp'][:10]}): {mem['document'][:200]}...")
                memory_context = "\n".join(memory_lines)
                log_info(f"💾 Memory enrichment: {len(memories)} relevant past tasks injected")
        
        # Build Initial Context with System Prompt
        system_prompt = self.planner.get_system_prompt()
        context_memory = [
            f"[SYSTEM]\n{system_prompt}\n\n{binding_envelope}{memory_context}",
            f"[USER TASK]\n{task_description}"
        ]
        
        # Initialize loop variables
        denial_count = 0
        replan_count = 0
        thought_steps = 0
        final_output = ""
        status = "failed"
        
        for turn in range(1, self.MAX_ITERATIONS + 1):
            log_info(f"🔄 Turn {turn}/{self.MAX_ITERATIONS}")
            thought_steps += 1
            diag_session.log_event("turn_start", {"turn": turn, "thought_steps": thought_steps})
            
            # Phase B: Reasoning Limit Check
            if thought_steps > current_max_thought_steps:
                log_warning(f"⚠️ Thought steps limit reached ({current_max_thought_steps})")
                final_output = {
                    "status": "COGNITIVE_LIMIT",
                    "code": "THOUGHT_STEPS_EXCEEDED",
                    "message": f"Reasoning depth limit reached after {thought_steps} steps. Unable to proceed.",
                    "partial_result": context_memory[-1] if context_memory else "No progress"
                }
                status = "limit_exceeded"
                diag_session.log_event("limit_exceeded", {"type": "thought_steps", "value": thought_steps})
                break
            
            
            # 1. BRAIN: Call LLM with context (Context Caching enabled)
            current_prompt = "\n\n".join(context_memory[-6:])
            
            # Execute with unified context
            success, raw_output, tokens, source = brain_executor.execute_with_cache(
                ctx,
                current_prompt
            )

            # Log to Unified Ingestor (v0.1 Schema)
            ingestor.emit(
                event_type=EventType.EXECUTION,
                actor_id=agent_id,
                actor_type=ActorType.AGENT,
                session_id=session_id,
                metadata={"model": ctx.selected_model},
                usage={"total_tokens": tokens},
                accounting_source=TelemetrySource.SDK,
                verdict="SUCCESS" if success else "FAILURE"
            )

            
            diag_session.reasoning_tokens_total += tokens
            
            if not success:
                log_error("Brain freeze (LLM execution failed).")
                diag_session.log_event("llm_error", {"output": raw_output[:200]})
                break
                
            # 2. PARSE: Extract SovereignAction
            action = self.planner.parse_action(raw_output)
            
            if not action:
                # No tool call = final response or conversation
                log_info("🗣️ Planner returned natural language response.")
                final_output = raw_output
                status = "completed"
                diag_session.log_event("task_complete", {"output": raw_output[:200]})
                break
                
            log_info(f"🤔 Planner proposes: {action.tool_name}.{action.action_name}")
            diag_session.log_event("action_proposed", {
                "tool": action.tool_name,
                "action": action.action_name,
                "reasoning": action.reasoning
            })
            
            # Phase A: Intent Drift Check
            is_drift, overlap = check_intent_drift(action, intent_anchor)
            diag_session.log_event("intent_check", {"drift": is_drift, "overlap": overlap})
            
            if is_drift:
                log_warning(f"⚠️ INTENT DRIFT detected (overlap: {overlap})")
                diag_session.log_event("intent_drift", {"overlap": overlap, "action": action.tool_name})
                feedback = f"System: INTENT_DRIFT detected. Your action '{action.tool_name}' does not align with the original task."
                context_memory.append(feedback)
                replan_count += 1
                if replan_count >= self.MAX_REPLANS:
                    status = "blocked"
                    break
                continue
            
            # 4. GATEWAY: Validate Action
            decision = self.gateway.evaluate(action, agent_id)
            diag_session.log_event("gateway_decision", {
                "allowed": decision.allowed,
                "verdict": decision.verdict_code,
                "reason": decision.reason
            })
            
            if not decision.allowed:
                log_warning(f"🛑 Gateway blocked: {decision.reason}")
                denial_count += 1
                replan_count += 1
                feedback = self.planner.format_gateway_feedback(decision)
                context_memory.append(feedback)
                if replan_count >= self.MAX_REPLANS or denial_count >= self.MAX_DENIALS:
                    status = "blocked"
                    break
                continue
                
            # 4. EXECUTE: Run the approved action
            try:
                if dry_run:
                    log_success(f"🧪 [DRY RUN] Action Validated & Simulated: {action.tool_name}")
                    result = f"[SIMULATED OUTPUT] {action.tool_name} executed."
                else:
                    invocation = self.gateway.resolve_invocation(action)
                    if decision.modifications:
                        invocation.safe_payload.update(decision.modifications)
                    result = self.tool_server.execute(invocation)
                    log_success(f"✅ Tool Executed: {action.tool_name}")
                
                # 5. REFLECT: Feed result back
                truncated_result = str(result)[:2000]
                context_memory.append(f"<tool_output tool=\"{action.tool_name}\">\n{truncated_result}\n</tool_output>")
                
            except Exception as e:
                log_error(f"Execution Error: {e}")
                context_memory.append(f"System Error: Tool execution failed: {e}")

        # Finalization
        # Persist lucidity_guarded to session metadata (governance state)
        session_data = ledger.get_session(session_id)
        if session_data:
            if not session_data.metadata:
                session_data.metadata = {}
            session_data.metadata["last_lucidity_guarded"] = lucidity_guarded
            ledger._save_session(session_data)  # Persist updated metadata
        
        ledger.update_status(session_id, status)
        duration = time.time() - start_time
        del intent_anchor
        diag_summary = diagnostics.end_session(session_id)
        
        tokens_total = diag_session.reasoning_tokens_total if hasattr(diag_session, 'reasoning_tokens_total') else 0
        
        # Determine source (default to SDK if not tracked per turn, but here we track best-effort)
        # Note: In a multi-turn loop, source might change, but the policy usually keeps it stable.
        source = locals().get('source', TelemetrySource.SDK)
        self.epistemology.record_usage(agent_id, tokens_total, session_id=session_id, source=source)

        # MEMORY STORAGE: Persist execution outcome (Phase 10.6)
        if self.epistemology.is_memory_available():
            self.epistemology.store_memory(
                agent_id=agent_id,
                task_type="sovereign_task",
                context=task_description[:500],
                outcome=str(final_output)[:500] if final_output else "No output",
                success=(status == "completed"),
                tokens_used=tokens_total,
                metadata={
                    "session_id": session_id,
                    "duration_seconds": duration,
                    "fatigue_applied": fatigue_applied
                }
            )
            log_info(f"💾 Memory stored for session {session_id}")

        return OrchestrationResult(
            session_id=session_id,
            primary_agent=agent_id,
            status=status,
            task_type="sovereign_task",
            output=str(final_output),
            diagnostics=diag_summary,
            tokens_used=tokens_total,
            fatigue_applied=fatigue_applied
        )

    @telemetry.trace_span("Orchestrator.execute_sub_agent")
    def execute_sub_agent(self, sub_agent_id: str, prompt: str, session_id: str, parent_agent: str = "claude_coder") -> Dict[str, Any]:
        """
        Executes a specialized Sub-agent with strict Context Isolation (Hard Gate 1).
        """
        log_info(f"🕵️ Invoking sub-agent: {sub_agent_id} (Isolated Context)")
        
        # 1. Budget & Fatigue Correlation (Hard Gate 4)
        try:
            self.epistemology.check_budget(sub_agent_id, estimated_tokens=0, priority="P1")
        except OrchestratorBudgetExceeded as e:
            return {"status": "blocked", "verdict": "BLOCK", "reason": f"Sub-agent budget exceeded: {str(e)}"}

        penalty_ratio = self.epistemology.get_fatigue_penalty(parent_agent)
        
        # 2. Preparation (Isolation: New system prompt, no memory leak)
        from axis_registry import load_registry
        registry = load_registry()
        agent_data = registry["agents"].get(sub_agent_id)
        
        if not agent_data:
            return {"status": "error", "reason": f"Sub-agent {sub_agent_id} not found in registry"}
            
        system_prompt = agent_data.get("system_prompt", "You are a specialized assistant.")
        
        # Execution (Direct Brain call, no loop to ensure isolation)
        # Apply Fatigue Correlation (Hard Gate 4): -15% reasoning depth
        penalty_msg = ""
        if penalty_ratio > 0:
            sub_penalty = penalty_ratio * 0.15
            log_warning(f"🔋 Sub-agent fatigue correlation applied: {sub_penalty:.2f}")
            penalty_msg = f"\n[SYSTEM NOTICE] You are operating under a cognitive fatigue penalty of {sub_penalty*100:.1f}%. Be extra concise."

        isolated_prompt = f"[SYSTEM]\n{system_prompt}{penalty_msg}\n\n[TASK]\n{prompt}"
        success, raw_output, tokens = brain_executor.execute(sub_agent_id, isolated_prompt, session_id)
        
        if not success:
            return {"status": "error", "reason": "Brain execution failed for sub-agent"}
            
        # 3. Post-Process & Audit
        self.epistemology.record_usage(sub_agent_id, tokens, session_id=session_id, source=TelemetrySource.SDK)
        
        # Parse Verdict
        verdict_match = re.search(r"\[VERDICT\]:\s*(APPROVE|BLOCK|WARN)", raw_output)
        reason_match = re.search(r"\[REASON\]:\s*(.*)", raw_output)
        
        verdict = verdict_match.group(1) if verdict_match else "WARN"
        reason = reason_match.group(1) if reason_match else "No reason provided."
        
        return {
            "status": "success",
            "agent_id": sub_agent_id,
            "verdict": verdict,
            "reason": reason,
            "output": raw_output,
            "tokens_used": tokens
        }

    def _log_context7_shadow_event(self, query: str, session_id: Optional[str]):
        """Logs shadow detection event for Context7 validation (ADR-0108)."""
        try:
            # Detect use case (shadow_mode=True ensures no side effects)
            use_case_id = self.use_case_detector.detect(query, shadow_mode=True)
            query_hash = sanitize_query(query)
            libraries = self.use_case_detector._extract_libraries(query)
            
            event = ShadowModeEvent(
                detected_use_case=use_case_id,
                query_hash=query_hash,
                libraries=libraries,
                session_id=session_id
            )
            shadow_logger.log_event(event)
        except Exception as e:
            # Safety gate: logging should never break the main loop
            self.logger.error(f"Context7 shadow logging failed: {e}")

# Public alias
Engine = OrchestratorEngine

# Global Instance
engine = OrchestratorEngine()
