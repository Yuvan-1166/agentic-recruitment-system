"""
Base Agent Protocol and Abstract Class

All agents in the recruitment system inherit from BaseAgent.
This ensures consistent interfaces, logging, and auditability.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import uuid4

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class AgentStatus(str, Enum):
    """Status of an agent's task execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"  # Waiting for human review


@dataclass
class AgentResponse(Generic[OutputT]):
    """
    Standardized response from any agent.
    
    Attributes:
        agent_id: Unique identifier of the agent instance
        agent_type: Type/name of the agent (e.g., "ResumeParserAgent")
        status: Execution status
        data: The actual output data (type-safe via generics)
        confidence: Confidence score [0.0, 1.0] for the output
        explanation: Human-readable explanation of the decision
        audit_trail: List of reasoning steps for auditability
        timestamp: When the response was generated
        duration_ms: How long the agent took to process
        errors: List of error messages if any
        warnings: Non-fatal issues or bias warnings
        requires_human_review: Flag for human-in-the-loop decisions
    """
    agent_id: str
    agent_type: str
    status: AgentStatus
    data: Optional[OutputT] = None
    confidence: float = 0.0
    explanation: str = ""
    audit_trail: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    requires_human_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "data": self.data,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "audit_trail": self.audit_trail,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "errors": self.errors,
            "warnings": self.warnings,
            "requires_human_review": self.requires_human_review,
        }


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all agents in the recruitment system.
    
    Design principles:
    - Single responsibility: Each agent does ONE thing well
    - Explainability: Every decision must be explainable
    - Auditability: All actions are logged with reasoning
    - Determinism: Same input should produce consistent output
    - Fail-safe: Errors are caught and reported, never silent
    
    Usage:
        class MyAgent(BaseAgent[InputSchema, OutputSchema]):
            def _process(self, input_data: InputSchema) -> OutputSchema:
                # Implementation here
                pass
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid4().hex[:8]}"
        self.agent_type = self.__class__.__name__
        self._audit_log: list[str] = []
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this agent does."""
        pass
    
    @property
    def required_confidence_threshold(self) -> float:
        """
        Minimum confidence required for auto-proceed.
        Below this, requires_human_review is set to True.
        Override in subclasses for different thresholds.
        """
        return 0.7
    
    def log_reasoning(self, step: str) -> None:
        """Add a reasoning step to the audit trail."""
        timestamp = datetime.utcnow().isoformat()
        self._audit_log.append(f"[{timestamp}] {step}")
    
    def run(self, input_data: InputT) -> AgentResponse[OutputT]:
        """
        Execute the agent's task with full auditing.
        
        This is the main entry point. It wraps _process() with:
        - Timing measurement
        - Error handling
        - Confidence checking
        - Audit trail management
        """
        start_time = datetime.utcnow()
        self._audit_log = []
        self.log_reasoning(f"Starting {self.agent_type} with input")
        
        try:
            # Run the actual processing
            output_data, confidence, explanation = self._process(input_data)
            
            # Check if human review is needed
            needs_review = confidence < self.required_confidence_threshold
            if needs_review:
                self.log_reasoning(
                    f"Confidence {confidence:.2f} below threshold "
                    f"{self.required_confidence_threshold:.2f} - flagging for human review"
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.log_reasoning(f"Completed successfully in {duration:.2f}ms")
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.SUCCESS,
                data=output_data,
                confidence=confidence,
                explanation=explanation,
                audit_trail=self._audit_log.copy(),
                duration_ms=duration,
                requires_human_review=needs_review,
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.log_reasoning(f"Failed with error: {str(e)}")
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                data=None,
                confidence=0.0,
                explanation=f"Agent failed: {str(e)}",
                audit_trail=self._audit_log.copy(),
                duration_ms=duration,
                errors=[str(e)],
                requires_human_review=True,
            )
    
    @abstractmethod
    def _process(self, input_data: InputT) -> tuple[OutputT, float, str]:
        """
        Core processing logic. Must be implemented by subclasses.
        
        Args:
            input_data: Typed input matching InputT
            
        Returns:
            Tuple of (output_data, confidence_score, explanation)
            - output_data: The result matching OutputT
            - confidence_score: Float between 0.0 and 1.0
            - explanation: Human-readable explanation of the result
        """
        pass
    
    def validate_input(self, input_data: InputT) -> list[str]:
        """
        Optional input validation. Override to add custom validation.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        return []
    
    def __repr__(self) -> str:
        return f"<{self.agent_type} id={self.agent_id}>"
