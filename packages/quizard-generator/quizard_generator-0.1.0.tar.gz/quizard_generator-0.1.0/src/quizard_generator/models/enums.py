"""
Enumerations for quiz models.
"""

from enum import Enum


class Difficulty(Enum):
    """Quiz difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
