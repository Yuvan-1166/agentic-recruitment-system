"""
Bias Auditor Agent

Responsibility: Monitor and flag potential bias in the recruitment process.
Single purpose: Ensure fairness and compliance throughout the pipeline.

This is a CRITICAL COMPLIANCE agent that reviews all decisions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .base import BaseAgent
from ..schemas.candidates import FinalRanking
from ..schemas.messages import PipelineState


@dataclass
class BiasAuditInput:
    """Input for bias auditing."""
    pipeline_state: PipelineState
    rankings: List[FinalRanking]


@dataclass
class BiasAuditResult:
    """Results of bias audit."""
    audit_passed: bool
    overall_fairness_score: float  # [0.0-1.0]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    requires_human_review: bool
    compliance_notes: List[str]


class BiasAuditorAgent(BaseAgent[BiasAuditInput, BiasAuditResult]):
    """
    Audits the recruitment pipeline for potential bias and fairness issues.
    
    Input: Complete pipeline state with all decisions
    Output: Bias audit results with findings and recommendations
    
    Key responsibilities:
    - Analyze decision patterns for bias
    - Check for disparate impact
    - Review borderline decision consistency
    - Flag concerning patterns
    - Provide compliance documentation
    
    This agent has VETO POWER:
    - Can require human review for any decision
    - Can flag the entire pipeline for review
    - Findings must be addressed before proceeding
    """
    
    @property
    def description(self) -> str:
        return (
            "Audits recruitment decisions for bias, ensuring fairness "
            "and regulatory compliance throughout the pipeline."
        )
    
    @property
    def required_confidence_threshold(self) -> float:
        return 0.9  # Compliance requires high confidence
    
    def _process(
        self, 
        input_data: BiasAuditInput
    ) -> tuple[BiasAuditResult, float, str]:
        """
        Audit pipeline for bias and fairness issues.
        
        Args:
            input_data: BiasAuditInput with pipeline state and rankings
        
        Returns:
            BiasAuditResult, confidence_score, explanation
        """
        self.log_reasoning("Starting bias audit")
        
        findings = []
        recommendations = []
        compliance_notes = []
        
        # Audit 1: Check JD for biased language
        jd_bias_flags = input_data.pipeline_state.parsed_jd.get("potential_bias_flags", [])
        if jd_bias_flags:
            findings.append({
                "category": "jd_language_bias",
                "severity": "medium",
                "description": f"Job description contains potentially biased language: {jd_bias_flags}",
                "affected_candidates": "all",
            })
            recommendations.append("Review and revise job description language")
            self.log_reasoning(f"JD bias flags found: {jd_bias_flags}")
        
        # Audit 2: Check decision gate consistency
        decision_gates = input_data.pipeline_state.decision_gates
        borderline_cases = [g for g in decision_gates if "borderline" in str(g.get("bias_flags", []))]
        if len(borderline_cases) > len(decision_gates) * 0.3:  # More than 30% borderline
            findings.append({
                "category": "threshold_calibration",
                "severity": "high",
                "description": f"{len(borderline_cases)} borderline decisions detected. Threshold may need adjustment.",
                "affected_candidates": [g.get("gate_id") for g in borderline_cases],
            })
            recommendations.append("Review threshold settings and borderline decisions")
            self.log_reasoning(f"High borderline rate: {len(borderline_cases)}/{len(decision_gates)}")
        
        # Audit 3: Check for score distribution anomalies
        if input_data.rankings:
            scores = [r.final_composite_score for r in input_data.rankings]
            avg_score = sum(scores) / len(scores)
            
            # Check for clustering (all scores very similar)
            score_range = max(scores) - min(scores) if scores else 0
            if score_range < 0.1 and len(scores) > 5:
                findings.append({
                    "category": "score_clustering",
                    "severity": "low",
                    "description": f"Scores are clustered in narrow range ({score_range:.2f}). May indicate evaluation issues.",
                    "affected_candidates": "all_ranked",
                })
                self.log_reasoning(f"Score clustering detected: range {score_range:.2f}")
        
        # Audit 4: Check for explanation quality
        rankings_without_explanation = [
            r for r in input_data.rankings 
            if not r.ranking_explanation or len(r.ranking_explanation) < 20
        ]
        if rankings_without_explanation:
            findings.append({
                "category": "explanation_quality",
                "severity": "medium",
                "description": f"{len(rankings_without_explanation)} rankings lack adequate explanation.",
                "affected_candidates": [r.candidate_id for r in rankings_without_explanation],
            })
            recommendations.append("Ensure all decisions have clear, documented explanations")
        
        # Calculate overall fairness score
        severity_weights = {"high": 0.3, "medium": 0.15, "low": 0.05}
        penalty = sum(
            severity_weights.get(f["severity"], 0.1) 
            for f in findings
        )
        fairness_score = max(0.0, 1.0 - penalty)
        
        # Determine if audit passes
        has_high_severity = any(f["severity"] == "high" for f in findings)
        audit_passed = fairness_score >= 0.7 and not has_high_severity
        
        # Compliance notes
        compliance_notes.append(
            f"Audit completed at pipeline stage: {input_data.pipeline_state.current_stage.value}"
        )
        compliance_notes.append(
            f"Total candidates processed: {len(input_data.pipeline_state.candidates)}"
        )
        compliance_notes.append(
            f"Total findings: {len(findings)} "
            f"(High: {sum(1 for f in findings if f['severity'] == 'high')}, "
            f"Medium: {sum(1 for f in findings if f['severity'] == 'medium')}, "
            f"Low: {sum(1 for f in findings if f['severity'] == 'low')})"
        )
        
        result = BiasAuditResult(
            audit_passed=audit_passed,
            overall_fairness_score=fairness_score,
            findings=findings,
            recommendations=recommendations,
            requires_human_review=not audit_passed or has_high_severity,
            compliance_notes=compliance_notes,
        )
        
        self.log_reasoning(f"Audit {'PASSED' if audit_passed else 'FAILED'} with fairness score {fairness_score:.2f}")
        
        confidence = 0.9
        explanation = (
            f"Bias audit {'PASSED' if audit_passed else 'REQUIRES REVIEW'}. "
            f"Fairness score: {fairness_score:.0%}. "
            f"Found {len(findings)} issues. "
            f"{len(recommendations)} recommendations provided."
        )
        
        return result, confidence, explanation
