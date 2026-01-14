"""
Custom exceptions for Quizard Generator.

Provides a comprehensive exception hierarchy for clean error handling
throughout the library and CLI.
"""

from typing import List, Optional


class QuizardError(Exception):
    """Base exception for all Quizard Generator errors."""

    pass


class ConfigurationError(QuizardError):
    """Raised when configuration validation fails."""

    pass


class DomainNotFoundError(QuizardError):
    """Raised when a specified domain does not exist."""

    def __init__(self, domain: str, available_domains: Optional[List[str]] = None):
        """
        Initialise domain not found error.

        Args:
            domain: The domain that was not found
            available_domains: List of available domains (optional)
        """
        self.domain = domain
        self.available_domains = available_domains or []

        message = f"Domain '{domain}' not found"
        if self.available_domains:
            message += f". Available domains: {', '.join(self.available_domains)}"

        super().__init__(message)


class ValidationError(QuizardError):
    """Raised when validation fails."""

    pass


class QuizGenerationError(QuizardError):
    """Raised when quiz generation pipeline fails."""

    def __init__(
        self,
        message: str,
        stage: Optional[str] = None,
        instruction: Optional[str] = None,
        num_questions: Optional[int] = None,
        nodes_retrieved: Optional[int] = None,
    ):
        """
        Initialise quiz generation error.

        Args:
            message: Primary error message
            stage: Pipeline stage where error occurred ("retrieval", "generation", "metadata")
            instruction: User instruction being processed
            num_questions: Number of questions requested
            nodes_retrieved: Number of knowledge nodes retrieved (if applicable)
        """
        self.message = message
        self.stage = stage
        self.instruction = instruction
        self.num_questions = num_questions
        self.nodes_retrieved = nodes_retrieved

        # build multi-line error message with indentation
        error_lines = [message]

        if stage:
            error_lines.append(f"  Stage: {stage}")

        details = []
        if instruction:
            # truncate long instructions
            instr_display = instruction[:100] + "..." if len(instruction) > 100 else instruction
            details.append(f"    Instruction: '{instr_display}'")
        if num_questions is not None:
            details.append(f"    Requested: {num_questions} questions")
        if nodes_retrieved is not None:
            details.append(f"    Nodes retrieved: {nodes_retrieved}")

        if details:
            error_lines.append("  Details:")
            error_lines.extend(details)

        super().__init__("\n".join(error_lines))


class QuestionGenerationError(QuizardError):
    """Raised when question generation fails."""

    def __init__(
        self,
        message: str,
        requested: Optional[int] = None,
        generated: Optional[int] = None,
        concept: Optional[str] = None,
        num_concepts: Optional[int] = None,
    ):
        """
        Initialise question generation error.

        Args:
            message: Primary error message
            requested: Number of questions requested
            generated: Number of questions successfully generated
            concept: Specific concept being processed when error occurred
            num_concepts: Total number of concepts being processed
        """
        self.message = message
        self.requested = requested
        self.generated = generated
        self.concept = concept
        self.num_concepts = num_concepts

        # build multi-line error message with indentation
        error_lines = [message]

        details = []
        if requested is not None and generated is not None:
            details.append(f"    Generated: {generated}/{requested} questions")
        elif requested is not None:
            details.append(f"    Requested: {requested} questions")

        if concept:
            # truncate long concept names
            concept_display = concept[:50] + "..." if len(concept) > 50 else concept
            details.append(f"    Concept: '{concept_display}'")

        if num_concepts is not None:
            details.append(f"    Total concepts: {num_concepts}")

        if details:
            error_lines.append("  Details:")
            error_lines.extend(details)

        super().__init__("\n".join(error_lines))


class KnowledgeSummarisationError(QuizardError):
    """Raised when knowledge summarisation fails."""

    def __init__(
        self,
        message: str,
        concepts: Optional[List[str]] = None,
        num_nodes: Optional[int] = None,
    ):
        """
        Initialise knowledge summarisation error.

        Args:
            message: Primary error message
            concepts: Concepts being summarised
            num_nodes: Number of knowledge nodes being summarised
        """
        self.message = message
        self.concepts = concepts or []
        self.num_nodes = num_nodes

        # build multi-line error message with indentation
        error_lines = [message]

        details = []
        if self.concepts:
            # show first 3 concepts
            concepts_display = ", ".join(self.concepts[:3])
            if len(self.concepts) > 3:
                concepts_display += f" (and {len(self.concepts) - 3} more)"
            details.append(f"    Concepts: {concepts_display}")

        if num_nodes is not None:
            details.append(f"    Nodes: {num_nodes}")

        if details:
            error_lines.append("  Details:")
            error_lines.extend(details)

        super().__init__("\n".join(error_lines))


class KnowledgeRetrievalError(QuizardError):
    """Raised when knowledge retrieval fails."""

    def __init__(
        self,
        message: str,
        concepts: Optional[List[str]] = None,
        instruction: Optional[str] = None,
    ):
        """
        Initialise knowledge retrieval error.

        Args:
            message: Primary error message
            concepts: Concepts that were being retrieved
            instruction: User instruction being processed
        """
        self.message = message
        self.concepts = concepts or []
        self.instruction = instruction

        # build multi-line error message with indentation
        error_lines = [message]

        details = []
        if self.concepts:
            # show first 3 concepts
            concepts_display = ", ".join(self.concepts[:3])
            if len(self.concepts) > 3:
                concepts_display += f" (and {len(self.concepts) - 3} more)"
            details.append(f"    Concepts: {concepts_display}")

        if instruction:
            # truncate long instructions
            instr_display = instruction[:100] + "..." if len(instruction) > 100 else instruction
            details.append(f"    Instruction: '{instr_display}'")

        if details:
            error_lines.append("  Details:")
            error_lines.extend(details)

        super().__init__("\n".join(error_lines))
