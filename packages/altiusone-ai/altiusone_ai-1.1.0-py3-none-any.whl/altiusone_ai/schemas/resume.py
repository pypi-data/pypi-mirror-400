"""
AltiusOne AI SDK - Resume/CV Schema
===================================
Predefined schema for resume/CV extraction.
"""

from typing import Any, Dict


# Raw schema dictionary
RESUME_SCHEMA: Dict[str, Any] = {
    "personal_info": {
        "full_name": "string",
        "email": "string?",
        "phone": "string?",
        "address": "string?",
        "city": "string?",
        "country": "string?",
        "date_of_birth": "string?",
        "nationality": "string?",
        "linkedin": "string?",
        "website": "string?",
    },
    "summary": "string?",
    "work_experience": [{
        "company": "string",
        "job_title": "string",
        "location": "string?",
        "start_date": "string",
        "end_date": "string?",
        "is_current": "boolean?",
        "responsibilities": "string[]",
        "achievements": "string[]?",
    }],
    "education": [{
        "institution": "string",
        "degree": "string",
        "field_of_study": "string?",
        "location": "string?",
        "start_date": "string?",
        "end_date": "string?",
        "grade": "string?",
    }],
    "skills": {
        "technical": "string[]?",
        "languages": [{
            "language": "string",
            "level": "string?",
        }],
        "soft_skills": "string[]?",
    },
    "certifications": [{
        "name": "string",
        "issuer": "string?",
        "date": "string?",
        "expiry_date": "string?",
    }],
    "projects": [{
        "name": "string",
        "description": "string?",
        "technologies": "string[]?",
        "url": "string?",
    }],
    "references": [{
        "name": "string",
        "title": "string?",
        "company": "string?",
        "contact": "string?",
    }],
}


class ResumeSchema:
    """
    Resume/CV extraction schema.

    Extracts:
    - Personal information
    - Professional summary
    - Work experience
    - Education
    - Skills (technical, languages, soft skills)
    - Certifications
    - Projects
    - References

    Example:
        ```python
        from altiusone_ai import AltiusOneAI
        from altiusone_ai.schemas import ResumeSchema

        client = AltiusOneAI(api_url="https://ai.altiusone.ch", api_key="...")

        data = client.extract(
            text=cv_text,
            schema=ResumeSchema.schema()
        )
        ```
    """

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Get the full resume schema dictionary."""
        return RESUME_SCHEMA.copy()

    @staticmethod
    def minimal() -> Dict[str, Any]:
        """Get a minimal resume schema (essential fields only)."""
        return {
            "full_name": "string",
            "email": "string?",
            "phone": "string?",
            "current_job_title": "string?",
            "years_of_experience": "number?",
            "skills": "string[]",
            "education_summary": "string?",
        }

    @staticmethod
    def for_recruitment() -> Dict[str, Any]:
        """Get schema optimized for recruitment screening."""
        return {
            "full_name": "string",
            "email": "string?",
            "phone": "string?",
            "location": "string?",
            "current_position": {
                "title": "string?",
                "company": "string?",
            },
            "total_years_experience": "number?",
            "key_skills": "string[]",
            "highest_education": {
                "degree": "string?",
                "field": "string?",
                "institution": "string?",
            },
            "languages": [{
                "language": "string",
                "level": "string",
            }],
            "availability": "string?",
            "salary_expectation": "string?",
        }

    @staticmethod
    def with_custom_fields(**fields: str) -> Dict[str, Any]:
        """Get resume schema with additional custom fields."""
        schema = RESUME_SCHEMA.copy()
        schema.update(fields)
        return schema
