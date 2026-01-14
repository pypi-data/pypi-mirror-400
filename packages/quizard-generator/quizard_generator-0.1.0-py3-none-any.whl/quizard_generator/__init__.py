"""
Quizard Generator - Domain-based quiz generation using LLMs.

A library and CLI tool for generating quiz questions from domain-specific documents
using Large Language Models (LLMs) and vector indexing.

Example library usage:
    >>> from quizard_generator import QuizardConfig, QuizardContext
    >>> from quizard_generator.pipeline import QuizGenerationPipeline
    >>> from quizard_generator.indexing import DomainManager
    >>>
    >>> config = QuizardConfig(data_dir="./data", indexing_llm_model="gemma3:4b")
    >>> with QuizardContext(config):
    ...     domain_manager = DomainManager(config.data_dir, config.storage_dir)
    ...     # index and generate quizzes
"""

from quizard_generator._version import __version__
from quizard_generator.config import (
    QuizardConfig,
    QuizardContext,
    configure_settings,
)
from quizard_generator.exceptions import (
    ConfigurationError,
    DomainNotFoundError,
    KnowledgeRetrievalError,
    KnowledgeSummarisationError,
    QuestionGenerationError,
    QuizardError,
    QuizGenerationError,
    ValidationError,
)
from quizard_generator.indexing import DomainManager, IndexManifest
from quizard_generator.models import (
    Difficulty,
    MCQQuestion,
    Quiz,
)
from quizard_generator.pipeline import QuizGenerationPipeline

# main pipeline and components are accessible via direct imports
__all__ = [
    # version
    "__version__",
    # configuration
    "QuizardConfig",
    "QuizardContext",
    "configure_settings",
    # exceptions
    "QuizardError",
    "ConfigurationError",
    "DomainNotFoundError",
    "QuizGenerationError",
    "QuestionGenerationError",
    "KnowledgeSummarisationError",
    "KnowledgeRetrievalError",
    "ValidationError",
    # domain management
    "DomainManager",
    "IndexManifest",
    # models
    "Difficulty",
    "MCQQuestion",
    "Quiz",
    # pipeline
    "QuizGenerationPipeline",
]
