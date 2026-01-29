"""
Configuration management for the recruitment system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import os


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"  # openai, anthropic, local
    model: str = "gpt-4"
    temperature: float = 0.1  # Low for consistency
    max_tokens: int = 2000
    api_key: Optional[str] = None  # Set via environment variable
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")


@dataclass
class ScoringWeights:
    """Weights for candidate scoring."""
    skills: float = 0.4
    experience: float = 0.35
    education: float = 0.25
    
    def __post_init__(self):
        total = self.skills + self.experience + self.education
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total}")


@dataclass
class ThresholdConfig:
    """Threshold configuration for decision gates."""
    shortlist_threshold: float = 0.7
    test_pass_threshold: float = 0.6
    confidence_threshold: float = 0.7
    bias_audit_threshold: float = 0.8


@dataclass 
class Settings:
    """
    Central configuration for the recruitment system.
    
    All configurable parameters are defined here for transparency.
    """
    # LLM settings
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    # Scoring weights
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)
    
    # Thresholds
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    
    # Pipeline settings
    max_candidates_per_job: int = 500
    top_k_candidates: int = 10
    test_questions_count: int = 20
    
    # Audit settings
    audit_log_enabled: bool = True
    audit_log_path: str = "logs/audit.jsonl"
    
    # Human review settings
    require_human_review_for_borderline: bool = True
    borderline_margin: float = 0.1  # Score within this margin of threshold
    
    # Privacy settings
    anonymize_candidates: bool = True
    retain_pii_days: int = 90  # GDPR compliance
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
            },
            "scoring_weights": {
                "skills": self.scoring_weights.skills,
                "experience": self.scoring_weights.experience,
                "education": self.scoring_weights.education,
            },
            "thresholds": {
                "shortlist": self.thresholds.shortlist_threshold,
                "test_pass": self.thresholds.test_pass_threshold,
                "confidence": self.thresholds.confidence_threshold,
                "bias_audit": self.thresholds.bias_audit_threshold,
            },
            "pipeline": {
                "max_candidates": self.max_candidates_per_job,
                "top_k": self.top_k_candidates,
                "test_questions": self.test_questions_count,
            },
            "audit": {
                "enabled": self.audit_log_enabled,
                "log_path": self.audit_log_path,
            },
            "human_review": {
                "borderline_enabled": self.require_human_review_for_borderline,
                "borderline_margin": self.borderline_margin,
            },
            "privacy": {
                "anonymize": self.anonymize_candidates,
                "retention_days": self.retain_pii_days,
            },
        }
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        return cls(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "openai"),
                model=os.getenv("LLM_MODEL", "gpt-4"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            ),
            thresholds=ThresholdConfig(
                shortlist_threshold=float(os.getenv("SHORTLIST_THRESHOLD", "0.7")),
            ),
        )
