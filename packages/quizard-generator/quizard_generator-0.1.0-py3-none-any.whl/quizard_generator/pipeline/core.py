"""
Main quiz generation pipeline orchestrator with simplified architecture.

This module coordinates quiz generation from user instructions using a simplified
approach that removes unnecessary middleware layers.
"""

import logging
from datetime import datetime
from typing import Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM

from quizard_generator.exceptions import QuizGenerationError
from quizard_generator.models import Quiz, Difficulty
from quizard_generator.knowledge import KnowledgeRetriever, KnowledgeSummariser
from quizard_generator.generators import QuestionGenerator
from quizard_generator.providers.factory import LLMProviderFactory

logger = logging.getLogger(__name__)


class QuizGenerationPipeline:
    """
    Orchestrates the complete quiz generation process with simplified architecture.

    Pipeline steps:
    1. Retrieve nodes using instruction (or default prompt if none provided)
    2. Generate questions using batch-per-concept strategy
    3. Return complete quiz

    Removed components (from old architecture):
    - InstructionParser (use instruction directly for retrieval)
    - ConceptResolver (use metadata from retrieved nodes)
    - DistractorGenerator (integrated into question generation)
    """

    def __init__(
        self,
        index: VectorStoreIndex,
        general_llm: Optional[LLM] = None,
        specialist_llm: Optional[LLM] = None,
        num_query_variations: int = 4,
        min_nodes_per_topic: int = 1,
        llm_provider: str = "ollama",
        llm_api_key: Optional[str] = None,
    ):
        """
        Initialise the quiz generation pipeline.

        Args:
            index: Vector store index with indexed documents
            general_llm: LLM for general tasks (summarisation and query generation).
                        Uses gemma3:4b by default.
            specialist_llm: LLM for specialist tasks (question generation).
                           Uses qwen2-math by default for better reasoning.
            num_query_variations: Number of query variations for fusion retrieval
            min_nodes_per_topic: Minimum nodes required per extracted topic
            llm_provider: LLM provider to use for default LLMs (ollama, openai, etc.)
            llm_api_key: API key for cloud providers (optional, uses env var if not set)
        """
        self.index = index

        # initialise llms with defaults if not provided
        self.general_llm = general_llm or LLMProviderFactory.create_llm(
            provider=llm_provider,
            model="gemma3:4b" if llm_provider == "ollama" else "gpt-4o-mini",
            request_timeout=300.0,
            api_key=llm_api_key,
        )
        self.specialist_llm = specialist_llm or LLMProviderFactory.create_llm(
            provider=llm_provider,
            model="qwen2-math:7b-instruct-q4_K_M" if llm_provider == "ollama" else "gpt-4o",
            request_timeout=300.0,
            api_key=llm_api_key,
        )

        # initialise components with appropriate llms
        self.knowledge_retriever = KnowledgeRetriever(
            index,
            llm=self.general_llm,
            num_query_variations=num_query_variations,
            min_nodes_per_topic=min_nodes_per_topic,
        )
        self.knowledge_summariser = KnowledgeSummariser(self.general_llm)
        self.question_generator = QuestionGenerator(self.specialist_llm, self.knowledge_summariser)

    def _generate_quiz_metadata(
        self,
        topics: list[str],
        num_questions: int,
        difficulty: Difficulty,
        instruction: Optional[str] = None,
    ) -> dict:
        """
        Generate quiz title and description using LLM.

        Args:
            topics: List of topics covered in the quiz
            num_questions: Number of questions in the quiz
            difficulty: Difficulty level
            instruction: Optional user instruction

        Returns:
            Dictionary with 'title' and 'description'
        """
        topics_str = ", ".join(topics[:5])  # limit to first 5 topics for brevity

        prompt = f"""Generate a concise title and description for a quiz with the following details:

Topics covered: {topics_str}
Number of questions: {num_questions}
Difficulty: {difficulty.value}
{f"User instruction: {instruction}" if instruction else ""}

Requirements:
- Title should be concise (5-10 words) and descriptive
- Description should be 1-2 sentences summarising the quiz scope
- Use British English spelling

Format your response as:
TITLE: <your title here>
DESCRIPTION: <your description here>"""

        try:
            response = self.general_llm.complete(prompt)
            text = str(response).strip()

            # parse response
            title = "Quiz"
            description = "A collection of questions"

            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("TITLE:"):
                    title = line.replace("TITLE:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()

            logger.info(f"Generated quiz metadata - Title: {title}")
            return {"title": title, "description": description}

        except Exception as e:
            logger.warning(f"Failed to generate quiz metadata: {e}, using defaults")
            return {
                "title": f"{difficulty.value.capitalize()} Quiz",
                "description": f"A {difficulty.value} difficulty quiz covering {topics_str}.",
            }

    def generate_quiz(
        self,
        instruction: Optional[str] = None,
        num_questions: int = 5,
        difficulty: Difficulty = Difficulty.MEDIUM,
    ) -> Quiz:
        """
        Generate a complete quiz from natural language instruction.

        Args:
            instruction: Natural language instruction (None for default)
            num_questions: Number of questions to generate
            difficulty: Difficulty level for questions

        Returns:
            Complete quiz with MCQ questions

        Raises:
            QuizGenerationError: If any step of the pipeline fails
            ValueError: If invalid parameters provided
        """
        if num_questions <= 0:
            raise ValueError("num_questions must be a positive integer")

        try:
            logger.info(
                f"Starting quiz generation: instruction='{instruction}', "
                f"num_questions={num_questions}, difficulty={difficulty.value}"
            )

            # step 1: retrieve nodes using instruction
            # retrieve more nodes than questions to ensure coverage
            top_k = num_questions * 2
            extracted_topics = []

            if instruction:
                # use metadata filtering for explicit instructions
                logger.info("Using metadata-filtered retrieval with topic extraction")
                (
                    nodes,
                    extracted_topics,
                ) = self.knowledge_retriever.retrieve_with_metadata_filtering(
                    instruction=instruction, top_k=top_k
                )
            else:
                # fall back to fusion retrieval for random sampling
                logger.info(
                    "No instruction provided, using QueryFusionRetriever for random sampling"
                )
                nodes = self.knowledge_retriever.retrieve(
                    ["Generate quiz questions on various topics"], top_k=top_k
                )

            if not nodes:
                raise QuizGenerationError(
                    "No relevant knowledge nodes could be retrieved",
                    stage="retrieval",
                    instruction=instruction,
                    num_questions=num_questions,
                    nodes_retrieved=0,
                )

            logger.info(f"Retrieved {len(nodes)} nodes for quiz generation (top_k={top_k})")
            if extracted_topics:
                logger.info(f"Extracted topics to prioritise: {extracted_topics}")

            # step 2: generate questions using batch-per-concept strategy
            questions = self.question_generator.generate(
                nodes=nodes,
                num_questions=num_questions,
                difficulty=difficulty,
                priority_topics=extracted_topics,
            )

            if not questions:
                raise QuizGenerationError(
                    "No questions could be generated from retrieved knowledge",
                    stage="generation",
                    instruction=instruction,
                    num_questions=num_questions,
                    nodes_retrieved=len(nodes),
                )

            logger.info(f"Generated {len(questions)} questions")

            # extract topics from generated questions
            topics = list(set(q.concept for q in questions))

            # generate quiz metadata (title and description)
            logger.info("Generating quiz metadata (title and description)")
            metadata = self._generate_quiz_metadata(
                topics=topics,
                num_questions=len(questions),
                difficulty=difficulty,
                instruction=instruction,
            )

            # generate timestamp-based quiz_id
            quiz_id = int(datetime.now().timestamp())

            # create final quiz
            quiz = Quiz(
                questions=questions,
                topics=topics,
                difficulty=difficulty,
                instruction=instruction,
                generated_at=datetime.now().isoformat(),
                quiz_id=quiz_id,
                title=metadata["title"],
                description=metadata["description"],
            )

            logger.info(
                f"Quiz generation complete: {len(quiz.questions)} questions, "
                f"{len(topics)} unique topics"
            )

            return quiz

        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            raise QuizGenerationError(
                f"Failed to generate quiz: {str(e)}",
                instruction=instruction,
                num_questions=num_questions,
            ) from e
