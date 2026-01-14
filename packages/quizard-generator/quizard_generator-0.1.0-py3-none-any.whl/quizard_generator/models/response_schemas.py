"""
Pydantic schemas for structured LLM responses.

These schemas define the expected output format for various LLM operations
using structured output capabilities.
"""

from typing import Dict
from pydantic import BaseModel, Field


class QuestionAnswerResponse(BaseModel):
    """Structured response for question and answer generation."""
    
    question: str = Field(description="The generated question")
    answer: str = Field(description="The correct answer to the question")


class ConceptMapping(BaseModel):
    """Mapping from resolved concept names to stored concept names."""
    
    mappings: Dict[str, str] = Field(
        description=(
            "Dictionary where keys are resolved concepts and values are "
            "the best matching stored concepts. Use empty string if no "
            "good match exists."
        )
    )
