"""
Audit logging for the recruitment system.

All decisions and actions are logged for compliance and explainability.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class AuditEntry:
    """A single audit log entry."""
    entry_id: str
    timestamp: str
    event_type: str
    pipeline_id: Optional[str]
    job_id: Optional[str]
    candidate_id: Optional[str]
    agent_type: Optional[str]
    action: str
    details: Dict[str, Any]
    outcome: Optional[str]
    confidence: Optional[float]
    requires_review: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Structured audit logging for compliance and explainability.
    
    All significant events in the recruitment pipeline are logged:
    - Agent decisions with confidence scores
    - Decision gate outcomes
    - Human review requests
    - Configuration changes
    - Error conditions
    
    Logs are stored in JSONL format for easy processing.
    """
    
    def __init__(self, log_path: str = "logs/audit.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: List[AuditEntry] = []
    
    def log(
        self,
        event_type: str,
        action: str,
        details: Dict[str, Any],
        pipeline_id: Optional[str] = None,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        outcome: Optional[str] = None,
        confidence: Optional[float] = None,
        requires_review: bool = False,
    ) -> AuditEntry:
        """
        Log an audit event.
        
        Args:
            event_type: Category of event (decision, error, review_request, etc.)
            action: What happened
            details: Detailed information about the event
            pipeline_id: Associated pipeline
            job_id: Associated job
            candidate_id: Associated candidate (if any)
            agent_type: Agent that generated the event
            outcome: Result of the action
            confidence: Confidence score if applicable
            requires_review: Whether human review is needed
        
        Returns:
            The created AuditEntry
        """
        entry = AuditEntry(
            entry_id=uuid4().hex,
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            pipeline_id=pipeline_id,
            job_id=job_id,
            candidate_id=candidate_id,
            agent_type=agent_type,
            action=action,
            details=details,
            outcome=outcome,
            confidence=confidence,
            requires_review=requires_review,
        )
        
        self._entries.append(entry)
        self._write_entry(entry)
        
        return entry
    
    def log_decision(
        self,
        agent_type: str,
        decision: str,
        confidence: float,
        explanation: str,
        pipeline_id: Optional[str] = None,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log an agent decision."""
        return self.log(
            event_type="decision",
            action=decision,
            details={"explanation": explanation},
            pipeline_id=pipeline_id,
            job_id=job_id,
            candidate_id=candidate_id,
            agent_type=agent_type,
            outcome="recorded",
            confidence=confidence,
            requires_review=confidence < 0.7,
        )
    
    def log_decision_gate(
        self,
        gate_name: str,
        passed: bool,
        threshold: float,
        actual_value: float,
        pipeline_id: Optional[str] = None,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log a decision gate evaluation."""
        return self.log(
            event_type="decision_gate",
            action=f"gate_{gate_name}",
            details={
                "threshold": threshold,
                "actual_value": actual_value,
                "margin": abs(actual_value - threshold),
            },
            pipeline_id=pipeline_id,
            job_id=job_id,
            candidate_id=candidate_id,
            outcome="passed" if passed else "failed",
            requires_review=abs(actual_value - threshold) < 0.1,
        )
    
    def log_human_review_request(
        self,
        reason: str,
        context: Dict[str, Any],
        pipeline_id: Optional[str] = None,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log a human review request."""
        return self.log(
            event_type="review_request",
            action="human_review_requested",
            details={"reason": reason, "context": context},
            pipeline_id=pipeline_id,
            job_id=job_id,
            candidate_id=candidate_id,
            outcome="pending",
            requires_review=True,
        )
    
    def log_bias_finding(
        self,
        finding_type: str,
        severity: str,
        description: str,
        affected_candidates: List[str],
        pipeline_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log a bias audit finding."""
        return self.log(
            event_type="bias_finding",
            action=f"bias_{finding_type}",
            details={
                "severity": severity,
                "description": description,
                "affected_count": len(affected_candidates),
            },
            pipeline_id=pipeline_id,
            job_id=job_id,
            outcome="flagged",
            requires_review=severity in ["high", "critical"],
        )
    
    def _write_entry(self, entry: AuditEntry) -> None:
        """Write an entry to the log file."""
        with open(self.log_path, "a") as f:
            f.write(entry.to_json() + "\n")
    
    def get_entries(
        self,
        pipeline_id: Optional[str] = None,
        event_type: Optional[str] = None,
        requires_review: Optional[bool] = None,
    ) -> List[AuditEntry]:
        """Query audit entries with filters."""
        results = self._entries
        
        if pipeline_id:
            results = [e for e in results if e.pipeline_id == pipeline_id]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if requires_review is not None:
            results = [e for e in results if e.requires_review == requires_review]
        
        return results
    
    def get_review_queue(self) -> List[AuditEntry]:
        """Get all entries requiring human review."""
        return [e for e in self._entries if e.requires_review]
    
    def export_for_compliance(self, pipeline_id: str) -> Dict[str, Any]:
        """Export all audit data for a pipeline for compliance review."""
        entries = self.get_entries(pipeline_id=pipeline_id)
        
        return {
            "pipeline_id": pipeline_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_entries": len(entries),
            "entries": [e.to_dict() for e in entries],
            "summary": {
                "decisions": len([e for e in entries if e.event_type == "decision"]),
                "gates_passed": len([e for e in entries if e.event_type == "decision_gate" and e.outcome == "passed"]),
                "gates_failed": len([e for e in entries if e.event_type == "decision_gate" and e.outcome == "failed"]),
                "review_requests": len([e for e in entries if e.event_type == "review_request"]),
                "bias_findings": len([e for e in entries if e.event_type == "bias_finding"]),
            },
        }
