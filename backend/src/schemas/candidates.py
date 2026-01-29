"""
Candidate-related schemas for the recruitment pipeline.

These schemas define the data structures for candidate information
as it flows through the various stages of evaluation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class CandidateProfile:
    """
    Basic candidate information.
    
    Note: Deliberately excludes demographic information to prevent bias.
    Fields like age, gender, ethnicity are NOT collected.
    """
    candidate_id: str = field(default_factory=lambda: uuid4().hex)
    anonymized_id: str = ""  # Used for blind review
    email_hash: str = ""  # Hashed for privacy
    resume_file_path: str = ""
    application_date: datetime = field(default_factory=datetime.utcnow)
    
    # Consent tracking (GDPR compliance)
    data_consent_given: bool = False
    consent_timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "anonymized_id": self.anonymized_id,
            "email_hash": self.email_hash,
            "resume_file_path": self.resume_file_path,
            "application_date": self.application_date.isoformat(),
            "data_consent_given": self.data_consent_given,
            "consent_timestamp": self.consent_timestamp.isoformat() if self.consent_timestamp else None,
        }


@dataclass
class SkillExtraction:
    """A skill extracted from a resume with confidence."""
    skill_name: str = ""
    category: str = ""  # technical, soft, domain
    proficiency_level: str = ""  # beginner, intermediate, advanced, expert
    evidence: str = ""  # Quote from resume supporting this
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "category": self.category,
            "proficiency_level": self.proficiency_level,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }


@dataclass
class ExperienceEntry:
    """A work experience entry from a resume."""
    company_anonymized: str = ""  # Company name removed for blind review
    role: str = ""
    duration_months: int = 0
    responsibilities: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_anonymized": self.company_anonymized,
            "role": self.role,
            "duration_months": self.duration_months,
            "responsibilities": self.responsibilities,
            "achievements": self.achievements,
            "skills_used": self.skills_used,
        }


@dataclass
class EducationEntry:
    """An education entry from a resume."""
    degree: str = ""
    field_of_study: str = ""
    institution_anonymized: str = ""  # Institution name removed for blind review
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    relevant_coursework: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "field_of_study": self.field_of_study,
            "institution_anonymized": self.institution_anonymized,
            "graduation_year": self.graduation_year,
            "gpa": self.gpa,
            "relevant_coursework": self.relevant_coursework,
        }


@dataclass
class ParsedResume:
    """
    Structured representation of a parsed resume.
    
    All personally identifiable information is either removed
    or anonymized to support blind evaluation.
    """
    candidate_id: str = ""
    parsing_timestamp: datetime = field(default_factory=datetime.utcnow)
    parsing_confidence: float = 0.0
    
    # Extracted content
    professional_summary: str = ""
    skills: List[SkillExtraction] = field(default_factory=list)
    experience: List[ExperienceEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Computed metrics
    total_experience_months: int = 0
    unique_skills_count: int = 0
    
    # Quality indicators
    resume_quality_score: float = 0.0  # How well-structured the resume is
    parsing_warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "parsing_timestamp": self.parsing_timestamp.isoformat(),
            "parsing_confidence": self.parsing_confidence,
            "professional_summary": self.professional_summary,
            "skills": [s.to_dict() for s in self.skills],
            "experience": [e.to_dict() for e in self.experience],
            "education": [e.to_dict() for e in self.education],
            "certifications": self.certifications,
            "projects": self.projects,
            "total_experience_months": self.total_experience_months,
            "unique_skills_count": self.unique_skills_count,
            "resume_quality_score": self.resume_quality_score,
            "parsing_warnings": self.parsing_warnings,
        }


@dataclass
class SkillMatch:
    """How well a candidate's skill matches a JD requirement."""
    required_skill: str = ""
    candidate_skill: str = ""
    match_type: str = ""  # exact, semantic, partial, missing
    match_score: float = 0.0
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required_skill": self.required_skill,
            "candidate_skill": self.candidate_skill,
            "match_type": self.match_type,
            "match_score": self.match_score,
            "explanation": self.explanation,
        }


@dataclass
class MatchResult:
    """
    Result of matching a candidate's resume against a job description.
    
    Includes detailed scoring breakdown for explainability.
    """
    candidate_id: str = ""
    job_id: str = ""
    match_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Overall scores
    overall_match_score: float = 0.0  # Weighted combination [0.0-1.0]
    confidence: float = 0.0
    
    # Component scores (all [0.0-1.0])
    skills_match_score: float = 0.0
    experience_match_score: float = 0.0
    education_match_score: float = 0.0
    
    # Detailed breakdowns
    skill_matches: List[SkillMatch] = field(default_factory=list)
    
    # Requirements coverage
    required_skills_met: int = 0
    required_skills_total: int = 0
    preferred_skills_met: int = 0
    preferred_skills_total: int = 0
    
    # Experience analysis
    meets_experience_requirement: bool = False
    experience_gap_months: int = 0  # Positive = exceeds, negative = falls short
    
    # Explanation
    match_explanation: str = ""
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    
    # Bias check flags
    bias_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "match_timestamp": self.match_timestamp.isoformat(),
            "overall_match_score": self.overall_match_score,
            "confidence": self.confidence,
            "skills_match_score": self.skills_match_score,
            "experience_match_score": self.experience_match_score,
            "education_match_score": self.education_match_score,
            "skill_matches": [s.to_dict() for s in self.skill_matches],
            "required_skills_met": self.required_skills_met,
            "required_skills_total": self.required_skills_total,
            "preferred_skills_met": self.preferred_skills_met,
            "preferred_skills_total": self.preferred_skills_total,
            "meets_experience_requirement": self.meets_experience_requirement,
            "experience_gap_months": self.experience_gap_months,
            "match_explanation": self.match_explanation,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "bias_flags": self.bias_flags,
        }


@dataclass
class TestResponse:
    """A candidate's response to a single test question."""
    question_id: str = ""
    selected_option: str = ""
    response_time_seconds: float = 0.0
    is_correct: bool = False
    partial_credit: float = 0.0  # For partial scoring [0.0-1.0]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "selected_option": self.selected_option,
            "response_time_seconds": self.response_time_seconds,
            "is_correct": self.is_correct,
            "partial_credit": self.partial_credit,
        }


@dataclass
class TestResult:
    """
    Complete test results for a candidate.
    """
    candidate_id: str = ""
    job_id: str = ""
    test_id: str = ""
    test_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Scores
    total_score: float = 0.0  # [0.0-1.0]
    questions_attempted: int = 0
    questions_correct: int = 0
    questions_total: int = 0
    
    # Per-category scores
    category_scores: Dict[str, float] = field(default_factory=dict)
    
    # Individual responses
    responses: List[TestResponse] = field(default_factory=list)
    
    # Time analysis
    total_time_seconds: float = 0.0
    average_time_per_question: float = 0.0
    
    # Integrity flags
    integrity_flags: List[str] = field(default_factory=list)  # e.g., "unusual_timing_pattern"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "test_id": self.test_id,
            "test_timestamp": self.test_timestamp.isoformat(),
            "total_score": self.total_score,
            "questions_attempted": self.questions_attempted,
            "questions_correct": self.questions_correct,
            "questions_total": self.questions_total,
            "category_scores": self.category_scores,
            "responses": [r.to_dict() for r in self.responses],
            "total_time_seconds": self.total_time_seconds,
            "average_time_per_question": self.average_time_per_question,
            "integrity_flags": self.integrity_flags,
        }


@dataclass
class FinalRanking:
    """
    Final ranking for a candidate after all evaluation stages.
    """
    candidate_id: str = ""
    job_id: str = ""
    rank: int = 0
    
    # Component scores
    resume_match_score: float = 0.0
    test_score: float = 0.0
    final_composite_score: float = 0.0
    
    # Weights used (for transparency)
    weights_used: Dict[str, float] = field(default_factory=dict)
    
    # Decision
    recommendation: str = ""  # "strongly_recommend", "recommend", "consider", "not_recommended"
    confidence: float = 0.0
    
    # Explanation
    ranking_explanation: str = ""
    key_strengths: List[str] = field(default_factory=list)
    key_concerns: List[str] = field(default_factory=list)
    
    # Compliance
    bias_audit_passed: bool = False
    human_review_required: bool = False
    human_review_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "rank": self.rank,
            "resume_match_score": self.resume_match_score,
            "test_score": self.test_score,
            "final_composite_score": self.final_composite_score,
            "weights_used": self.weights_used,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "ranking_explanation": self.ranking_explanation,
            "key_strengths": self.key_strengths,
            "key_concerns": self.key_concerns,
            "bias_audit_passed": self.bias_audit_passed,
            "human_review_required": self.human_review_required,
            "human_review_reason": self.human_review_reason,
        }
