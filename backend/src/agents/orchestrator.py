"""
Orchestrator Agent

Responsibility: Coordinate the entire recruitment pipeline.
Single purpose: Manage agent execution order, state, and decision flow.

This is the CENTRAL COORDINATOR that manages the agentic workflow.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from .base import BaseAgent, AgentResponse, AgentStatus
from .jd_analyzer import JDAnalyzerAgent
from .resume_parser import ResumeParserAgent
from .matcher import MatcherAgent, MatcherInput
from .shortlister import ShortlisterAgent, ShortlistInput
from .test_generator import TestGeneratorAgent, TestGeneratorInput
from .test_evaluator import TestEvaluatorAgent, TestEvaluatorInput
from .ranker import RankerAgent, RankerInput
from .bias_auditor import BiasAuditorAgent, BiasAuditInput

from ..schemas.messages import (
    PipelineState,
    PipelineStage,
    AgentMessage,
    MessageType,
    DecisionGate,
)
from ..schemas.job import JobDescription
from ..schemas.candidates import CandidateProfile


class OrchestratorAction(str, Enum):
    """Actions the orchestrator can take."""
    CONTINUE = "continue"  # Proceed to next stage
    PAUSE = "pause"  # Wait for human input
    RETRY = "retry"  # Retry current stage
    ABORT = "abort"  # Stop the pipeline
    COMPLETE = "complete"  # Pipeline finished


@dataclass
class OrchestratorDecision:
    """Decision made by the orchestrator after each stage."""
    action: OrchestratorAction
    next_stage: Optional[PipelineStage] = None
    reason: str = ""
    requires_human_approval: bool = False
    blocked_by: List[str] = None  # Issues blocking progress


class OrchestratorAgent:
    """
    Central coordinator for the recruitment pipeline.
    
    The Orchestrator:
    - Manages pipeline state
    - Coordinates agent execution order
    - Handles decision gates
    - Ensures auditability
    - Manages human-in-the-loop checkpoints
    
    Design:
    - Framework-agnostic (can be wrapped by LangGraph, CrewAI, etc.)
    - Stateful (maintains pipeline state)
    - Event-driven (agents communicate via messages)
    - Fail-safe (handles errors gracefully)
    
    NOT responsible for:
    - Actual resume parsing (ResumeParser does that)
    - Scoring logic (Matcher, Ranker do that)
    - Bias detection (BiasAuditor does that)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize agents
        self.jd_analyzer = JDAnalyzerAgent()
        self.resume_parser = ResumeParserAgent()
        self.matcher = MatcherAgent()
        self.shortlister = ShortlisterAgent()
        self.test_generator = TestGeneratorAgent()
        self.test_evaluator = TestEvaluatorAgent()
        self.ranker = RankerAgent()
        self.bias_auditor = BiasAuditorAgent()
        
        # Pipeline state
        self.state: Optional[PipelineState] = None
        
        # Event handlers (for framework integration)
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Audit log
        self._audit_log: List[Dict[str, Any]] = []
    
    def create_pipeline(self, job: JobDescription, candidates: List[CandidateProfile]) -> PipelineState:
        """
        Initialize a new recruitment pipeline.
        
        Args:
            job: The job description
            candidates: List of candidates to evaluate
        
        Returns:
            Initialized PipelineState
        """
        self.state = PipelineState(
            job_id=job.job_id,
            current_stage=PipelineStage.INITIALIZED,
            job_description=job.to_dict(),
            candidates=[c.to_dict() for c in candidates],
        )
        
        self._log_event("pipeline_created", {
            "job_id": job.job_id,
            "candidate_count": len(candidates),
        })
        
        return self.state
    
    def run_pipeline(self) -> PipelineState:
        """
        Execute the complete recruitment pipeline.
        
        Returns:
            Final pipeline state
        """
        if not self.state:
            raise ValueError("Pipeline not initialized. Call create_pipeline first.")
        
        self._log_event("pipeline_started", {"job_id": self.state.job_id})
        
        # Pipeline execution loop
        while self.state.current_stage not in [
            PipelineStage.COMPLETED,
            PipelineStage.FAILED,
            PipelineStage.AWAITING_HUMAN_REVIEW,
        ]:
            try:
                decision = self._execute_current_stage()
                
                if decision.action == OrchestratorAction.CONTINUE:
                    self.state.current_stage = decision.next_stage
                elif decision.action == OrchestratorAction.PAUSE:
                    self.state.current_stage = PipelineStage.AWAITING_HUMAN_REVIEW
                    break
                elif decision.action == OrchestratorAction.ABORT:
                    self.state.current_stage = PipelineStage.FAILED
                    self.state.errors.append(decision.reason)
                    break
                elif decision.action == OrchestratorAction.COMPLETE:
                    self.state.current_stage = PipelineStage.COMPLETED
                    break
                    
            except Exception as e:
                self._log_event("stage_error", {
                    "stage": self.state.current_stage.value,
                    "error": str(e),
                })
                self.state.errors.append(f"Error in {self.state.current_stage.value}: {str(e)}")
                self.state.current_stage = PipelineStage.FAILED
                break
        
        self._log_event("pipeline_finished", {
            "job_id": self.state.job_id,
            "final_stage": self.state.current_stage.value,
            "error_count": len(self.state.errors),
        })
        
        return self.state
    
    def _execute_current_stage(self) -> OrchestratorDecision:
        """Execute the current pipeline stage and decide next action."""
        stage = self.state.current_stage
        
        self._log_event("stage_started", {"stage": stage.value})
        
        if stage == PipelineStage.INITIALIZED:
            return self._run_jd_analysis()
        elif stage == PipelineStage.JD_ANALYSIS:
            return self._run_resume_parsing()
        elif stage == PipelineStage.RESUME_PARSING:
            return self._run_matching()
        elif stage == PipelineStage.MATCHING:
            return self._run_shortlisting()
        elif stage == PipelineStage.SHORTLISTING:
            return self._run_test_generation()
        elif stage == PipelineStage.TEST_GENERATION:
            # In real implementation, would wait for test completion
            return self._run_test_evaluation()
        elif stage == PipelineStage.TEST_EVALUATION:
            return self._run_ranking()
        elif stage == PipelineStage.RANKING:
            return self._run_bias_audit()
        elif stage == PipelineStage.BIAS_AUDIT:
            return OrchestratorDecision(
                action=OrchestratorAction.COMPLETE,
                reason="Pipeline completed successfully",
            )
        else:
            return OrchestratorDecision(
                action=OrchestratorAction.ABORT,
                reason=f"Unknown stage: {stage}",
            )
    
    def _run_jd_analysis(self) -> OrchestratorDecision:
        """Run JD analysis stage."""
        job_dict = self.state.job_description
        job = JobDescription(**{k: v for k, v in job_dict.items() 
                               if k in JobDescription.__dataclass_fields__})
        
        response = self.jd_analyzer.run(job)
        self._record_agent_response(response)
        
        if response.status == AgentStatus.SUCCESS:
            self.state.parsed_jd = response.data.to_dict() if response.data else {}
            return OrchestratorDecision(
                action=OrchestratorAction.CONTINUE,
                next_stage=PipelineStage.JD_ANALYSIS,
                reason="JD analysis completed",
            )
        else:
            return OrchestratorDecision(
                action=OrchestratorAction.ABORT,
                reason=f"JD analysis failed: {response.errors}",
            )
    
    def _run_resume_parsing(self) -> OrchestratorDecision:
        """Run resume parsing for all candidates."""
        parsed_resumes = []
        
        for candidate_dict in self.state.candidates:
            input_data = {
                "candidate_id": candidate_dict.get("candidate_id", ""),
                "resume_text": "[Mock resume text]",  # Would load actual text
                "resume_format": "txt",
            }
            
            response = self.resume_parser.run(input_data)
            self._record_agent_response(response)
            
            if response.status == AgentStatus.SUCCESS and response.data:
                parsed_resumes.append(response.data.to_dict())
        
        # Store parsed resumes in state (would update candidate entries)
        self.state.candidates = [
            {**c, "parsed_resume": pr}
            for c, pr in zip(self.state.candidates, parsed_resumes)
        ]
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.RESUME_PARSING,
            reason=f"Parsed {len(parsed_resumes)} resumes",
        )
    
    def _run_matching(self) -> OrchestratorDecision:
        """Run resume-JD matching."""
        # Mock implementation - would use actual parsed data
        self.state.match_results = []
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.MATCHING,
            reason="Matching completed",
        )
    
    def _run_shortlisting(self) -> OrchestratorDecision:
        """Run shortlisting decision gate."""
        # Mock implementation
        threshold = self.state.job_description.get("shortlist_threshold", 0.7)
        
        # Create decision gate
        gate = DecisionGate(
            gate_name="shortlist_gate",
            condition=f"Match score >= {threshold}",
            threshold=threshold,
            passed=True,
            explanation="Shortlisting decision gate passed",
        )
        self.state.add_decision_gate(gate)
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.SHORTLISTING,
            reason="Shortlisting completed",
        )
    
    def _run_test_generation(self) -> OrchestratorDecision:
        """Generate assessment test."""
        # Mock implementation
        self.state.test_questions = []
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.TEST_GENERATION,
            reason="Test generation completed",
        )
    
    def _run_test_evaluation(self) -> OrchestratorDecision:
        """Evaluate test responses."""
        # Mock implementation
        self.state.test_results = []
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.TEST_EVALUATION,
            reason="Test evaluation completed",
        )
    
    def _run_ranking(self) -> OrchestratorDecision:
        """Produce final rankings."""
        # Mock implementation
        self.state.final_rankings = []
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.RANKING,
            reason="Ranking completed",
        )
    
    def _run_bias_audit(self) -> OrchestratorDecision:
        """Run final bias audit."""
        # Mock implementation
        self.state.bias_audit_results = {
            "audit_passed": True,
            "fairness_score": 0.9,
            "findings": [],
        }
        
        return OrchestratorDecision(
            action=OrchestratorAction.CONTINUE,
            next_stage=PipelineStage.BIAS_AUDIT,
            reason="Bias audit completed",
        )
    
    def _record_agent_response(self, response: AgentResponse) -> None:
        """Record an agent's response in the pipeline state."""
        self.state.add_agent_response(response.to_dict())
        
        if response.warnings:
            self.state.warnings.extend(response.warnings)
        
        self._log_event("agent_response", {
            "agent_type": response.agent_type,
            "status": response.status.value,
            "confidence": response.confidence,
            "requires_review": response.requires_human_review,
        })
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an orchestrator event for auditing."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "pipeline_id": self.state.pipeline_id if self.state else None,
            "data": data,
        }
        self._audit_log.append(event)
        
        # Emit to registered handlers
        for handler in self._event_handlers.get(event_type, []):
            handler(event)
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register an event handler for framework integration."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the complete audit log."""
        return self._audit_log.copy()
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get a summary of the current pipeline state."""
        if not self.state:
            return {"status": "not_initialized"}
        
        return {
            "pipeline_id": self.state.pipeline_id,
            "job_id": self.state.job_id,
            "current_stage": self.state.current_stage.value,
            "candidate_count": len(self.state.candidates),
            "shortlisted_count": len(self.state.shortlisted_candidates),
            "final_rankings_count": len(self.state.final_rankings),
            "error_count": len(self.state.errors),
            "warning_count": len(self.state.warnings),
            "decision_gates_passed": sum(
                1 for g in self.state.decision_gates if g.get("passed", False)
            ),
            "requires_human_review": any(
                r.get("requires_human_review", False) 
                for r in self.state.agent_responses
            ),
        }
