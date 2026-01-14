"""
Question generation with integrated Q+A+D using batch-per-concept strategy.

This module generates questions with correct answers and distractors in a single
LLM call, using a simplified architecture that removes unnecessary middleware.
"""

import logging
import random
from typing import Dict, List, Optional

from llama_index.core.llms import LLM
from llama_index.core.schema import NodeWithScore

from quizard_generator.exceptions import QuestionGenerationError
from quizard_generator.knowledge import KnowledgeSummariser
from quizard_generator.models import Difficulty, MCQQuestion, QuestionBatch

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Generates MCQ questions using batch-per-concept strategy.

    Simplified architecture:
    1. Group nodes by concept (from metadata)
    2. Distribute questions equally across concepts
    3. For each concept: summarise once, generate batch of Q+A+D
    4. Random seed selection with replacement (never depletes)
    """

    MAX_RETRIES = 2  # max retry attempts per batch

    def __init__(self, llm: LLM, knowledge_summariser: KnowledgeSummariser):
        """
        Initialise the question generator.

        Args:
            llm: Language model for question generation
            knowledge_summariser: Summariser for creating concept summaries
        """
        self.llm = llm.as_structured_llm(output_cls=QuestionBatch)
        self.knowledge_summariser = knowledge_summariser

    def generate(
        self,
        nodes: List[NodeWithScore],
        num_questions: int,
        difficulty: Difficulty,
        priority_topics: Optional[List[str]] = None,
    ) -> List[MCQQuestion]:
        """
        Generate MCQ questions using batch-per-concept strategy.

        Args:
            nodes: Retrieved nodes from vector store
            num_questions: Number of questions to generate
            difficulty: Difficulty level for questions
            priority_topics: Topics extracted from instruction to prioritise in distribution

        Returns:
            List of MCQ questions with integrated Q+A+D

        Raises:
            QuestionGenerationError: If question generation fails
            ValueError: If invalid parameters provided
        """
        if num_questions <= 0:
            raise ValueError("num_questions must be a positive integer")

        if not nodes:
            raise ValueError("nodes cannot be empty")

        try:
            # step 1: group nodes by concept
            concept_groups = self._group_by_concept(nodes)

            if not concept_groups:
                raise QuestionGenerationError(
                    "No concepts found in node metadata",
                    requested=num_questions,
                )

            logger.info(f"Grouped {len(nodes)} nodes into {len(concept_groups)} concepts")

            # step 2: distribute questions across concepts with guaranteed minimums
            question_distribution = self._distribute_questions(
                num_questions, concept_groups, priority_topics
            )

            # log complete distribution (not truncated)
            logger.info(f"Question distribution across {len(question_distribution)} concepts:")
            for concept, count in question_distribution.items():
                if count > 0:
                    logger.info(f"  {concept}: {count} question(s)")

            # also log concepts with 0 questions
            zero_concepts = [c for c, count in question_distribution.items() if count == 0]
            if zero_concepts:
                logger.info(f"Concepts with 0 questions allocated: {len(zero_concepts)} total")
                for concept in zero_concepts[:10]:
                    logger.debug(f"  {concept}: 0 questions")
                if len(zero_concepts) > 10:
                    logger.debug(f"  ... and {len(zero_concepts) - 10} more")

            # step 3: generate questions batch-by-batch per concept
            all_questions = []

            for concept, batch_size in question_distribution.items():
                if batch_size == 0:
                    continue

                concept_nodes = concept_groups[concept]

                # summarise nodes for this concept (1 LLM call)
                summary = self.knowledge_summariser.summarise(concept_nodes, [concept])

                # extract seeds for this concept
                seeds = self._extract_seeds(concept_nodes, concept)

                # generate batch of questions (1 LLM call with retries)
                batch_questions = self._generate_batch_with_retry(
                    concept=concept,
                    summary=summary,
                    seeds=seeds,
                    batch_size=batch_size,
                    difficulty=difficulty,
                )

                all_questions.extend(batch_questions)

                logger.info(
                    f"Generated {len(batch_questions)}/{batch_size} questions for concept '{concept[:50]}'"
                )

            # validate we have enough questions
            if len(all_questions) < num_questions:
                raise QuestionGenerationError(
                    "Insufficient questions generated",
                    requested=num_questions,
                    generated=len(all_questions),
                    num_concepts=len(concept_groups),
                )

            # shuffle options before returning (correct answer is always at index 0 from LLM)
            for question in all_questions:
                self._shuffle_options(question)

            logger.info(f"Question generation complete: {len(all_questions)} questions")

            return all_questions[:num_questions]

        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            raise QuestionGenerationError(
                f"Unable to generate questions: {str(e)}",
                requested=num_questions,
            ) from e

    def _group_by_concept(self, nodes: List[NodeWithScore]) -> Dict[str, List[NodeWithScore]]:
        """
        Group nodes by their extracted concepts.

        Args:
            nodes: Retrieved nodes with metadata

        Returns:
            Dictionary mapping concept -> list of nodes
        """
        concept_groups = {}

        for node in nodes:
            if not hasattr(node.node, "metadata"):
                continue

            metadata = node.node.metadata

            if "extracted_concepts" not in metadata:
                continue

            concepts = metadata["extracted_concepts"]

            if not isinstance(concepts, list):
                continue

            # add node to each concept group
            for concept in concepts:
                if concept not in concept_groups:
                    concept_groups[concept] = []
                concept_groups[concept].append(node)

        return concept_groups

    def _distribute_questions(
        self,
        num_questions: int,
        concept_groups: Dict[str, List[NodeWithScore]],
        priority_topics: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Distribute questions across concepts with guaranteed minimums.

        Strategy:
        1. Guarantee at least 1 question for concepts matching priority topics
        2. Calculate weight for each concept (node_count * avg_score)
        3. Guarantee 1 question for remaining top concepts (up to num_questions)
        4. Distribute remaining questions proportionally by weight

        Args:
            num_questions: Total questions to generate
            concept_groups: Map of concept -> nodes
            priority_topics: Topics from instruction to prioritise (e.g., ["GCD", "LCM"])

        Returns:
            Map of concept -> question count
        """
        if not concept_groups:
            return {}

        # calculate weights for each concept
        concept_weights = {}
        for concept, nodes in concept_groups.items():
            node_count = len(nodes)
            avg_score = sum(n.score for n in nodes) / node_count if node_count > 0 else 0
            # weight = node count * (1 + average relevance score)
            concept_weights[concept] = node_count * (1 + avg_score)

        # identify priority concepts (concepts that match any priority topic)
        priority_concepts = set()
        if priority_topics:
            priority_topics_lower = [t.lower() for t in priority_topics]
            for concept in concept_groups.keys():
                concept_lower = concept.lower()
                if any(topic in concept_lower for topic in priority_topics_lower):
                    priority_concepts.add(concept)

            if priority_concepts:
                logger.info(f"Priority concepts matching extracted topics: {priority_concepts}")

        # sort concepts by priority first, then weight
        def concept_sort_key(item):
            concept, weight = item
            # priority concepts get boosted weight
            is_priority = concept in priority_concepts
            return (is_priority, weight)

        sorted_concepts = sorted(concept_weights.items(), key=concept_sort_key, reverse=True)

        distribution = {}

        # Phase 1: Guarantee 1 question for top concepts (priority first)
        guaranteed_count = min(num_questions, len(sorted_concepts))
        for i in range(guaranteed_count):
            concept = sorted_concepts[i][0]
            distribution[concept] = 1

        remaining = num_questions - guaranteed_count

        # Phase 2: Distribute remaining questions proportionally
        if remaining > 0:
            # only consider concepts that already have allocation
            allocated_concepts = [(c, w) for c, w in sorted_concepts[:guaranteed_count]]
            total_weight = sum(w for _, w in allocated_concepts)

            for concept, weight in allocated_concepts:
                proportion = weight / total_weight if total_weight > 0 else 0
                additional = int(remaining * proportion)
                distribution[concept] += additional

        # Phase 3: Distribute any leftover questions to top concepts
        allocated_total = sum(distribution.values())
        if allocated_total < num_questions:
            deficit = num_questions - allocated_total
            for i in range(deficit):
                concept = sorted_concepts[i % guaranteed_count][0]
                distribution[concept] += 1

        # set 0 for concepts not in distribution
        for concept in concept_groups.keys():
            if concept not in distribution:
                distribution[concept] = 0

        return distribution

    def _extract_seeds(self, nodes: List[NodeWithScore], concept: str) -> List[str]:
        """
        Extract question seeds for a specific concept from node metadata.

        Args:
            nodes: Nodes for this concept
            concept: Concept name

        Returns:
            List of seed hints for question generation
        """
        seeds = []

        for node in nodes:
            if not hasattr(node.node, "metadata"):
                continue

            metadata = node.node.metadata

            if "concept_question_seeds" not in metadata:
                continue

            seed_dict = metadata["concept_question_seeds"]

            if not isinstance(seed_dict, dict):
                continue

            # extract seeds for this specific concept
            if concept in seed_dict:
                concept_seeds = seed_dict[concept]

                if isinstance(concept_seeds, list):
                    seeds.extend(concept_seeds)
                elif isinstance(concept_seeds, str):
                    seeds.append(concept_seeds)

        # remove duplicates while preserving order
        unique_seeds = []
        seen = set()

        for seed in seeds:
            if seed not in seen:
                unique_seeds.append(seed)
                seen.add(seed)

        return unique_seeds

    def _generate_batch_with_retry(
        self,
        concept: str,
        summary: str,
        seeds: List[str],
        batch_size: int,
        difficulty: Difficulty,
    ) -> List[MCQQuestion]:
        """
        Generate a batch of questions with retry logic.

        Args:
            concept: Concept name
            summary: Knowledge summary for context
            seeds: List of seed hints
            batch_size: Number of questions to generate
            difficulty: Difficulty level

        Returns:
            List of MCQ questions
        """
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                questions = self._generate_batch(
                    concept=concept,
                    summary=summary,
                    seeds=seeds,
                    batch_size=batch_size,
                    difficulty=difficulty,
                )

                if questions:
                    if attempt > 0:
                        logger.info(
                            f"Retry succeeded on attempt {attempt + 1} for concept '{concept[:30]}'"
                        )
                    return questions

            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    logger.debug(
                        f"Retrying batch generation for '{concept[:30]}' "
                        f"(attempt {attempt + 2}/{self.MAX_RETRIES + 1}): {e}"
                    )
                else:
                    logger.warning(
                        f"Batch generation failed after {self.MAX_RETRIES + 1} attempts "
                        f"for concept '{concept[:50]}': {e}"
                    )

        return []

    def _generate_batch(
        self,
        concept: str,
        summary: str,
        seeds: List[str],
        batch_size: int,
        difficulty: Difficulty,
    ) -> List[MCQQuestion]:
        """
        Generate a batch of questions for a single concept.

        Uses random seed selection with replacement to ensure we never run out
        of seeds.

        Args:
            concept: Concept name
            summary: Knowledge summary for context
            seeds: List of seed hints
            batch_size: Number of questions to generate
            difficulty: Difficulty level

        Returns:
            List of MCQ questions with integrated Q+A+D
        """
        # select seeds randomly with replacement
        if seeds:
            batch_seeds = random.choices(seeds, k=batch_size)
            seed_section = f"""Question Focus Areas (use these as inspiration for generating diverse questions):
{chr(10).join(f"- {seed}" for seed in batch_seeds)}"""
        else:
            # no seeds available, generate without them
            seed_section = "Generate diverse questions covering different aspects of the concept."
            batch_seeds = [""] * batch_size

        # create prompt for batch generation
        prompt = f"""Generate {batch_size} multiple-choice quiz questions.

Concept: {concept}
Difficulty: {difficulty.value}

Knowledge Summary:
{summary}

{seed_section}

For each question:
- Create a clear, specific question about the concept
- Provide exactly 4 options where the FIRST option is the correct answer
- The other 3 options should be plausible but incorrect distractors
- Provide a detailed explanation (1-3 sentences) that justifies why the correct answer is correct
- Explanations should help students understand the underlying concept
- Ensure questions test understanding, not just memorisation

Generate exactly {batch_size} questions in the specified format with explanations."""

        try:
            # call LLM with structured output
            response = self.llm.complete(prompt)

            # extract questions from structured response
            if not hasattr(response, "raw") or response.raw is None:
                logger.error(f"Response missing 'raw' attribute for concept '{concept[:50]}'")
                return []

            question_batch = response.raw

            if not hasattr(question_batch, "questions") or not question_batch.questions:
                logger.error(
                    f"Structured response missing 'questions' attribute for concept '{concept[:50]}'"
                )
                return []

            questions = question_batch.questions

            # validate each question
            validated_questions = []

            for i, question in enumerate(questions):
                try:
                    # validate options count
                    if len(question.options) != 4:
                        logger.warning(
                            f"Question {i + 1} has {len(question.options)} options (expected 4), skipping"
                        )
                        continue

                    # validate explanation exists and is non-empty
                    if (
                        not hasattr(question, "explanation")
                        or not question.explanation
                        or not question.explanation.strip()
                    ):
                        logger.warning(f"Question {i + 1} missing explanation, skipping")
                        continue

                    # set metadata
                    question.concept = concept
                    question.difficulty = difficulty.value
                    question.seed = batch_seeds[i] if i < len(batch_seeds) else None
                    # correct answer is at index 0 before shuffling
                    question.correct_answer_index = 0

                    validated_questions.append(question)

                except Exception as e:
                    logger.warning(
                        f"Failed to validate question {i + 1} for concept '{concept[:30]}': {e}"
                    )
                    continue

            if len(validated_questions) < batch_size:
                logger.warning(
                    f"Only validated {len(validated_questions)}/{batch_size} questions "
                    f"for concept '{concept[:50]}'"
                )

            return validated_questions

        except AttributeError as e:
            logger.error(f"Failed to extract questions from structured response: {e}")
            return []

        except Exception as e:
            logger.warning(f"Batch generation failed for concept '{concept[:50]}': {e}")
            return []

    def _shuffle_options(self, question: MCQQuestion) -> None:
        """
        Shuffle options so correct answer is not always at index 0.

        Tracks the new position of the correct answer after shuffling.
        Modifies the question in-place.

        Args:
            question: Question to shuffle options for
        """
        if len(question.options) != 4:
            return

        # store correct answer (currently at index 0)
        correct_answer = question.options[0]

        # shuffle options
        random.shuffle(question.options)

        # find new position of correct answer
        question.correct_answer_index = question.options.index(correct_answer)
