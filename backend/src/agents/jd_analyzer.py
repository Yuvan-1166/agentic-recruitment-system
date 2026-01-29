"""
JD Analyzer Agent

Responsibility: Parse and structure job descriptions.
Single purpose: Extract requirements, skills, and evaluation criteria from JDs.

This agent does NOT match candidates - only analyzes job descriptions.
"""

from typing import Any, Dict

from .base import BaseAgent
from ..schemas.job import (
    JobDescription,
    ParsedJD,
    SkillRequirement,
    ExperienceRequirement,
    EducationRequirement,
)


class JDAnalyzerAgent(BaseAgent[JobDescription, ParsedJD]):
    """
    Analyzes job descriptions and extracts structured requirements.
    
    Input: Raw job description
    Output: ParsedJD with skills, requirements, and evaluation criteria
    
    Key responsibilities:
    - Extract required and preferred skills
    - Identify experience requirements
    - Determine education requirements
    - Identify topics for test generation
    - Flag potential bias in JD language
    
    Does NOT:
    - Match candidates to the JD
    - Score candidates
    - Generate tests
    """
    
    @property
    def description(self) -> str:
        return (
            "Analyzes job descriptions to extract structured requirements "
            "including skills, experience, education, and topics for assessment."
        )
    
    def _process(
        self, 
        input_data: JobDescription
    ) -> tuple[ParsedJD, float, str]:
        """
        Parse a job description into structured format.
        
        Args:
            input_data: JobDescription object
        
        Returns:
            ParsedJD, confidence_score, explanation
        """
        self.log_reasoning("Starting JD analysis")
        self.log_reasoning(f"Analyzing job: {input_data.title}")
        
        # Check for potential bias in JD
        bias_flags = self._check_for_bias(input_data.raw_description)
        if bias_flags:
            self.log_reasoning(f"Potential bias detected: {bias_flags}")
        
        # TODO: Implement actual JD parsing with LLM
        # For now, return a mock parsed JD
        parsed = ParsedJD(
            job_id=input_data.job_id,
            parsing_confidence=0.9,
            job_title_normalized=input_data.title,
            seniority_level="mid",  # To be extracted
            job_function="engineering",  # To be extracted
            skills=[],  # To be populated by LLM
            experience_requirements=ExperienceRequirement(
                minimum_years=3,
                preferred_years=5,
            ),
            education_requirements=EducationRequirement(
                minimum_degree="bachelors",
            ),
            key_responsibilities=[],
            technical_topics=[],  # For test generation
            difficulty_level="intermediate",
            jd_quality_score=0.8,
            potential_bias_flags=bias_flags,
            parsing_warnings=["Mock implementation - actual parsing not yet implemented"],
        )
        
        confidence = 0.9
        explanation = (
            f"Analyzed job description for '{input_data.title}'. "
            f"Extracted {len(parsed.skills)} skill requirements, "
            f"experience requirements ({parsed.experience_requirements.minimum_years}+ years), "
            f"and education requirements ({parsed.education_requirements.minimum_degree}). "
            f"Identified {len(bias_flags)} potential bias concerns."
        )
        
        self.log_reasoning("JD analysis completed")
        
        return parsed, confidence, explanation
    
    def _check_for_bias(self, text: str) -> list[str]:
        """
        Check for potentially biased language in job descriptions.
        
        This is a simple heuristic check. A production system would
        use a more sophisticated bias detection model.
        """
        flags = []
        text_lower = text.lower()
        
        # Check for gendered language
        gendered_terms = ["rockstar", "ninja", "guru", "manpower", "manning"]
        for term in gendered_terms:
            if term in text_lower:
                flags.append(f"Potentially gendered term: '{term}'")
        
        # Check for age-related bias
        age_terms = ["young", "energetic", "digital native", "recent graduate only"]
        for term in age_terms:
            if term in text_lower:
                flags.append(f"Potentially age-biased term: '{term}'")
        
        return flags
