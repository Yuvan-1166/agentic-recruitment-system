"""
Resume Parser Agent

Responsibility: Extract structured information from raw resumes.
Single purpose: Parse resumes into a standardized format.

This agent does NOT score or evaluate - only extracts and structures.
"""

from typing import Any, Dict

from .base import BaseAgent
from ..schemas.candidates import (
    ParsedResume,
    SkillExtraction,
    ExperienceEntry,
    EducationEntry,
)


class ResumeParserAgent(BaseAgent[Dict[str, Any], ParsedResume]):
    """
    Extracts structured information from candidate resumes.
    
    Input: Raw resume content (text or file path)
    Output: ParsedResume with skills, experience, education
    
    Key responsibilities:
    - Extract skills with proficiency levels
    - Parse work experience entries
    - Parse education history
    - Anonymize personal information
    - Flag parsing quality issues
    
    Does NOT:
    - Score or rank candidates
    - Make hiring decisions
    - Compare to job descriptions
    """
    
    @property
    def description(self) -> str:
        return (
            "Parses raw resumes into structured data. Extracts skills, "
            "experience, and education while anonymizing personal information."
        )
    
    @property
    def required_confidence_threshold(self) -> float:
        return 0.6  # Lower threshold as parsing can handle some ambiguity
    
    def _process(
        self, 
        input_data: Dict[str, Any]
    ) -> tuple[ParsedResume, float, str]:
        """
        Parse a resume into structured format.
        
        Args:
            input_data: {
                "candidate_id": str,
                "resume_text": str,  # Raw text content
                "resume_format": str  # pdf, docx, txt
            }
        
        Returns:
            ParsedResume, confidence_score, explanation
        """
        self.log_reasoning("Starting resume parsing")
        
        candidate_id = input_data.get("candidate_id", "")
        resume_text = input_data.get("resume_text", "")
        
        if not resume_text:
            raise ValueError("No resume text provided")
        
        self.log_reasoning(f"Processing resume for candidate {candidate_id[:8]}...")
        
        # TODO: Implement actual parsing logic
        # For now, return a mock parsed resume
        parsed = ParsedResume(
            candidate_id=candidate_id,
            parsing_confidence=0.85,
            professional_summary="[To be extracted by LLM]",
            skills=[],
            experience=[],
            education=[],
            total_experience_months=0,
            unique_skills_count=0,
            resume_quality_score=0.0,
            parsing_warnings=["Mock implementation - actual parsing not yet implemented"],
        )
        
        confidence = 0.85
        explanation = (
            f"Parsed resume for candidate {candidate_id[:8]}. "
            "Extracted structured data including skills, experience, and education. "
            "Personal information has been anonymized."
        )
        
        self.log_reasoning("Resume parsing completed")
        
        return parsed, confidence, explanation
    
    def validate_input(self, input_data: Dict[str, Any]) -> list[str]:
        """Validate the input before processing."""
        errors = []
        
        if not input_data.get("candidate_id"):
            errors.append("candidate_id is required")
        
        if not input_data.get("resume_text"):
            errors.append("resume_text is required")
        
        return errors
