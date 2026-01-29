"""
Matcher Agent

Responsibility: Compare parsed resumes against parsed job descriptions.
Single purpose: Calculate similarity scores with explainable metrics.

This agent does NOT make shortlisting decisions - only calculates scores.
"""

from typing import Any, Dict, List

from .base import BaseAgent
from ..schemas.candidates import ParsedResume, MatchResult, SkillMatch
from ..schemas.job import ParsedJD


class MatcherInput:
    """Input structure for the Matcher agent."""
    def __init__(self, parsed_resume: ParsedResume, parsed_jd: ParsedJD):
        self.parsed_resume = parsed_resume
        self.parsed_jd = parsed_jd


class MatcherAgent(BaseAgent[MatcherInput, MatchResult]):
    """
    Matches candidate resumes against job descriptions.
    
    Input: ParsedResume + ParsedJD
    Output: MatchResult with detailed scoring breakdown
    
    Key responsibilities:
    - Calculate skill match scores
    - Calculate experience match scores
    - Calculate education match scores
    - Provide detailed match explanations
    - Identify strengths and gaps
    
    Does NOT:
    - Make shortlisting decisions
    - Rank candidates against each other
    - Generate tests
    """
    
    @property
    def description(self) -> str:
        return (
            "Calculates similarity scores between resumes and job descriptions "
            "with detailed, explainable metrics for each component."
        )
    
    def _process(
        self, 
        input_data: MatcherInput
    ) -> tuple[MatchResult, float, str]:
        """
        Match a resume against a job description.
        
        Args:
            input_data: MatcherInput containing ParsedResume and ParsedJD
        
        Returns:
            MatchResult, confidence_score, explanation
        """
        resume = input_data.parsed_resume
        jd = input_data.parsed_jd
        
        self.log_reasoning(f"Matching candidate {resume.candidate_id[:8]} to job {jd.job_id[:8]}")
        
        # Calculate component scores
        skills_score = self._calculate_skills_match(resume, jd)
        self.log_reasoning(f"Skills match score: {skills_score:.2f}")
        
        experience_score = self._calculate_experience_match(resume, jd)
        self.log_reasoning(f"Experience match score: {experience_score:.2f}")
        
        education_score = self._calculate_education_match(resume, jd)
        self.log_reasoning(f"Education match score: {education_score:.2f}")
        
        # Calculate weighted overall score
        weights = jd.scoring_weights
        overall_score = (
            skills_score * weights.get("skills", 0.4) +
            experience_score * weights.get("experience", 0.35) +
            education_score * weights.get("education", 0.25)
        )
        self.log_reasoning(f"Overall weighted score: {overall_score:.2f}")
        
        # Build match result
        result = MatchResult(
            candidate_id=resume.candidate_id,
            job_id=jd.job_id,
            overall_match_score=overall_score,
            confidence=0.85,  # TODO: Calculate based on data quality
            skills_match_score=skills_score,
            experience_match_score=experience_score,
            education_match_score=education_score,
            skill_matches=[],  # TODO: Populate with detailed skill matches
            required_skills_met=0,  # TODO: Calculate
            required_skills_total=len(jd.get_required_skills()),
            meets_experience_requirement=experience_score >= 0.7,
            match_explanation=f"Candidate has {overall_score:.0%} match to the job requirements.",
            strengths=self._identify_strengths(resume, jd),
            gaps=self._identify_gaps(resume, jd),
        )
        
        confidence = 0.85
        explanation = (
            f"Matched candidate to job with {overall_score:.0%} overall score. "
            f"Skills: {skills_score:.0%}, Experience: {experience_score:.0%}, "
            f"Education: {education_score:.0%}. "
            f"Found {len(result.strengths)} strengths and {len(result.gaps)} gaps."
        )
        
        return result, confidence, explanation
    
    def _calculate_skills_match(self, resume: ParsedResume, jd: ParsedJD) -> float:
        """Calculate how well candidate skills match JD requirements."""
        # TODO: Implement actual skill matching with semantic similarity
        # Mock implementation
        return 0.75
    
    def _calculate_experience_match(self, resume: ParsedResume, jd: ParsedJD) -> float:
        """Calculate experience match based on years and relevance."""
        # TODO: Implement actual experience matching
        # Mock implementation
        required_months = jd.experience_requirements.minimum_years * 12
        candidate_months = resume.total_experience_months
        
        if candidate_months >= required_months:
            return 1.0
        return candidate_months / required_months if required_months > 0 else 0.5
    
    def _calculate_education_match(self, resume: ParsedResume, jd: ParsedJD) -> float:
        """Calculate education match."""
        # TODO: Implement actual education matching
        # Mock implementation
        return 0.8
    
    def _identify_strengths(self, resume: ParsedResume, jd: ParsedJD) -> List[str]:
        """Identify candidate's strengths relative to the job."""
        # TODO: Implement strength identification
        return ["Mock strength - actual analysis not yet implemented"]
    
    def _identify_gaps(self, resume: ParsedResume, jd: ParsedJD) -> List[str]:
        """Identify gaps between candidate profile and job requirements."""
        # TODO: Implement gap identification
        return ["Mock gap - actual analysis not yet implemented"]
