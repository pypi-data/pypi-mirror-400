"""Generate command implementation."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from llama_index.core import load_index_from_storage, StorageContext

from quizard_generator import (
    Difficulty,
    DomainManager,
    QuizGenerationPipeline,
    QuizardConfig,
    QuizardContext,
)
from quizard_generator.exceptions import DomainNotFoundError
from quizard_generator.providers.factory import LLMProviderFactory

logger = logging.getLogger(__name__)


def generate_command(
    domain: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    instruction: Optional[str] = None,
    config_path: Optional[str] = None,
):
    """
    Generate quiz for a specific domain.

    Args:
        domain: Domain name
        num_questions: Number of questions to generate
        difficulty: Difficulty level (easy, medium, hard)
        instruction: Optional natural language instruction
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print(f"GENERATE: Creating Quiz for Domain '{domain}'")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info(
        f"Configuration loaded: data_dir={config.data_dir}, storage_dir={config.storage_dir}"
    )

    logger.info("Initialising DomainManager")
    domain_manager = DomainManager(config.data_dir, config.storage_dir)

    # validate domain exists
    logger.info(f"Validating domain '{domain}'")
    try:
        domain_manager.validate_or_raise(domain)
        logger.info(f"Domain '{domain}' validated successfully")
    except DomainNotFoundError as e:
        logger.error(f"Domain validation failed: {e}")
        print(f"\n{e}\n")
        return

    # get storage path
    storage_path = domain_manager.get_storage_path(domain)
    logger.info(f"Storage path: {storage_path}")

    # check if index exists
    if not os.path.exists(storage_path):
        logger.error(f"No index found at {storage_path}")
        print(f"Error: No index found for domain '{domain}'")
        print(f"Please run: quizard index --domain {domain}")
        return

    logger.info("Index directory exists")

    # convert difficulty string to enum
    try:
        difficulty_enum = Difficulty[difficulty.upper()]
        logger.info(f"Difficulty level set to: {difficulty_enum.value}")
    except KeyError:
        logger.error(f"Invalid difficulty value: {difficulty}")
        print(f"Error: Invalid difficulty '{difficulty}'. Must be easy/medium/hard")
        return

    # use QuizardContext for Settings management
    with QuizardContext(config):
        # load index
        print("Loading index...")
        logger.info(f"Loading index from storage: {storage_path}")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=storage_path)
            index = load_index_from_storage(storage_context)
            logger.info("Index loaded successfully from storage")
            print("Index loaded successfully\n")
        except Exception as e:
            logger.exception(f"Failed to load index from {storage_path}")
            print(f"Error loading index: {e}")
            return

        # create llms from config
        logger.info(f"Creating LLMs from configuration:")
        logger.info(f"  Provider: {config.llm_provider}")
        logger.info(f"  General LLM: {config.generation_general_llm_model}")
        logger.info(f"  Specialist LLM: {config.generation_specialist_llm_model}")
        logger.info(f"  Request timeout: {config.llm_request_timeout}s")

        # determine which API key to use
        api_key = None
        if config.llm_provider == "openai":
            api_key = config.openai_api_key
        elif config.llm_provider == "anthropic":
            api_key = config.anthropic_api_key
        elif config.llm_provider == "google":
            api_key = config.google_api_key

        general_llm = LLMProviderFactory.create_llm(
            provider=config.llm_provider,
            model=config.generation_general_llm_model,
            request_timeout=config.llm_request_timeout,
            api_key=api_key,
        )
        specialist_llm = LLMProviderFactory.create_llm(
            provider=config.llm_provider,
            model=config.generation_specialist_llm_model,
            request_timeout=config.llm_request_timeout,
            api_key=api_key,
        )

        # create pipeline
        print("Initialising quiz generation pipeline...")
        logger.info("Creating QuizGenerationPipeline with configured LLMs")
        logger.info(f"  Query variations for retrieval: {config.retrieval_num_query_variations}")
        logger.info(f"  Minimum nodes per topic: {config.retrieval_min_nodes_per_topic}")
        pipeline = QuizGenerationPipeline(
            index=index,
            general_llm=general_llm,
            specialist_llm=specialist_llm,
            num_query_variations=config.retrieval_num_query_variations,
            min_nodes_per_topic=config.retrieval_min_nodes_per_topic,
        )
        print("Pipeline initialised\n")

        # generate quiz
        print("Generating quiz...")
        print(f"  Domain: {domain}")
        print(f"  Instruction: {instruction if instruction else 'None (random sampling)'}")
        print(f"  Questions: {num_questions}")
        print(f"  Difficulty: {difficulty_enum.value}\n")

        logger.info("Starting quiz generation")
        logger.info(f"  Domain: {domain}")
        logger.info(f"  Instruction: {instruction if instruction else 'None (random sampling)'}")
        logger.info(f"  Num questions: {num_questions}")
        logger.info(f"  Difficulty: {difficulty_enum.value}")

        try:
            quiz = pipeline.generate_quiz(
                instruction=instruction,
                num_questions=num_questions,
                difficulty=difficulty_enum,
            )

            logger.info(f"Quiz generation completed successfully")
            logger.info(f"  Generated {len(quiz.questions)} questions")
            logger.info(f"  Topics covered: {', '.join(quiz.topics)}")

            print("=" * 80)
            print("QUIZ GENERATED SUCCESSFULLY")
            print("=" * 80 + "\n")

            # display quiz
            print(f"Quiz ID: {quiz.quiz_id}")
            print(f"Title: {quiz.title}")
            print(f"Description: {quiz.description}")
            print(f"Domain: {domain}")
            print(f"Tags: {', '.join(quiz.topics)}")
            print(f"Difficulty: {quiz.difficulty.value}")
            print(f"Number of Questions: {len(quiz.questions)}")
            print(f"Generated at: {quiz.generated_at}\n")

            print("=" * 80)
            print("QUESTIONS")
            print("=" * 80 + "\n")

            for idx, question in enumerate(quiz.questions, 1):
                print(f"Question {idx} [{question.concept}]")
                print(f"{question.question}\n")

                # display options
                for opt_idx, option in enumerate(question.options):
                    print(f"  {chr(65 + opt_idx)}. {option}")

                # display correct answer and explanation
                correct_letter = chr(65 + question.correct_answer_index)
                print(f"\n  Correct Answer: {correct_letter}")
                print(f"  Explanation: {question.explanation}")

                # display metadata for logging/debugging
                if question.seed:
                    print(f"  Seed: {question.seed}")
                print(f"  Difficulty: {question.difficulty}")
                print()

            # save to file with timestamp
            # create generated_quizzes directory if it doesn't exist
            output_dir = Path("generated_quizzes")
            output_dir.mkdir(exist_ok=True)

            # generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"generated_quiz_{domain}_{timestamp}.json"

            logger.info(f"Saving quiz to {output_file}")
            with open(output_file, "w") as f:
                json.dump(quiz.to_dict(), f, indent=2)
            logger.info(f"Quiz successfully saved to {output_file}")

            print("=" * 80)
            print(f"Quiz saved to {output_file}")
            print("=" * 80 + "\n")

        except Exception as e:
            logger.exception("Quiz generation failed with exception")
            print(f"\nError generating quiz: {e}\n")
