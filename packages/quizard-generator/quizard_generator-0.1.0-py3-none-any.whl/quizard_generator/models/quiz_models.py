"""
Data models for quiz and MCQ questions.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from quizard_generator.models.enums import Difficulty


class MCQQuestion(BaseModel):
    """
    A single multiple-choice question with integrated generation.

    The options list contains 4 shuffled options. The correct_answer_index
    tracks which option is correct after shuffling.
    """

    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="4 shuffled options")
    correct_answer_index: int = Field(
        ..., description="Index of correct answer in options list (0-3)"
    )
    concept: str = Field(..., description="The concept being tested")
    seed: Optional[str] = Field(None, description="The seed hint used for generation")
    difficulty: str = Field("medium", description="Difficulty level (easy, medium, hard)")
    type: str = Field(default="single_choice", description="Question type")
    explanation: str = Field(..., description="Explanation of why the answer is correct")

    def validate_options(self) -> None:
        """Validate that exactly 4 options are provided."""
        if len(self.options) != 4:
            raise ValueError(f"MCQQuestion must have exactly 4 options, got {len(self.options)}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialisation."""
        return {
            "question": self.question,
            "type": self.type,
            "options": self.options,
            "answer": self.correct_answer_index,
            "explanation": self.explanation,
        }


class QuestionBatch(BaseModel):
    """
    Batch of questions generated together for a single concept.
    """

    questions: List[MCQQuestion] = Field(..., description="List of generated questions")


class Quiz(BaseModel):
    """Complete quiz with metadata."""

    questions: List[MCQQuestion]
    topics: List[str]
    difficulty: Difficulty
    instruction: Optional[str] = None
    generated_at: str
    quiz_id: int = Field(..., description="Unique quiz identifier (timestamp-based)")
    title: str = Field(..., description="Quiz title")
    description: str = Field(..., description="Quiz description")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialisation."""
        # convert generated_at (ISO format) to DD/MM/YYYY
        from datetime import datetime

        dt = datetime.fromisoformat(self.generated_at)
        date_created = dt.strftime("%d/%m/%Y")

        return {
            "metadata": {
                "quiz_id": self.quiz_id,
                "title": self.title,
                "description": self.description,
                "tags": self.topics,
                "difficulty": self.difficulty.value,
                "date_created": date_created,
            },
            "questions": [q.to_dict() for q in self.questions],
        }
