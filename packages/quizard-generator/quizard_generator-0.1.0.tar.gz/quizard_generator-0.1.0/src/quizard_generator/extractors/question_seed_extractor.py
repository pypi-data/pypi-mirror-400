"""
Custom metadata extractors for LlamaIndex nodes.

Extractors:
    - ConceptExtractor: Extract high-level topics and concepts from nodes
    - QuestionSeedExtractor: Generate question seeds (topics/angles) per concept
"""

import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from llama_index.core.async_utils import DEFAULT_NUM_WORKERS, run_jobs
from llama_index.core.bridge.pydantic import Field, SerializeAsAny
from llama_index.core.extractors.interface import BaseExtractor
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.settings import Settings

logger = logging.getLogger(__name__)


# DEFAULT_CONCEPT_EXTRACT_TEMPLATE = """\
# {context_str}
#
# Extract up to {max_concepts} high-level key topics and concepts from this text.
#
# Requirements:
# - Focus on main topics and overarching themes
# - Be specific and descriptive
# - Avoid generic terms
# - Extract concepts that are central to understanding this text
#
# Format: Return as a list, one per line, without numbering.
#
# High-Level Concepts:"""

DEFAULT_CONCEPT_EXTRACT_TEMPLATE = """\
{context_str}

Extract up to {max_concepts} high-level key topics and concepts from this text.

Requirements:
- Focus on main topics and overarching themes
- Be specific but concise
- Avoid generic terms
- Prefer short noun phrases (3–6 words)
- Extract concepts central to understanding the text

Format: Return as a list, one per line, without numbering.

Examples:

Text:
"Neural networks learn by adjusting weights using gradient descent to minimize a loss function. Backpropagation efficiently computes gradients through layered architectures."

High-Level Concepts:
Neural network training
Gradient descent optimisation
Loss function minimization
Backpropagation algorithm

Text:
"Photosynthesis converts light energy into chemical energy using chlorophyll. This process produces glucose and releases oxygen as a byproduct."

High-Level Concepts:
Photosynthesis process
Light-to-chemical energy conversion
Chlorophyll function
Glucose production

Text:
"Newton’s second law states that force equals mass times acceleration. This relationship governs the motion of objects under applied forces."

High-Level Concepts:
Newton’s second law
Force–mass–acceleration relationship
Classical mechanics

---

High-Level Concepts:"""


DEFAULT_QUESTION_SEED_TEMPLATE = """\
Context:
{context_str}

You are a quiz question designer. For each concept below, generate {seeds_per_concept} question seeds (short topics/angles for quiz questions, NOT full questions).

Concepts to generate seeds for:
{concepts_list}

IMPORTANT INSTRUCTIONS:
1. Return ONLY valid JSON in the exact format shown below
2. Use the exact concept names provided above as keys
3. Each concept should have a list of {seeds_per_concept} short seed phrases
4. Seeds should be concise (2-6 words) and focus on different aspects
5. Do NOT include any text before or after the JSON

EXAMPLES OF GOOD SEEDS:
- "definition and key properties"
- "calculation method"
- "comparison with related concepts"
- "real-world applications"
- "common misconceptions"

FEW-SHOT EXAMPLES:

Example 1:
Input Concepts: ["Photosynthesis", "Cell Division"]
Output:
{{
  "Photosynthesis": [
    "definition and process steps",
    "required inputs and outputs",
    "light-dependent reactions"
  ],
  "Cell Division": [
    "mitosis vs meiosis",
    "phases and checkpoints",
    "role in growth and repair"
  ]
}}

Example 2:
Input Concepts: ["Quadratic Equations", "Factoring"]
Output:
{{
  "Quadratic Equations": [
    "standard form components",
    "solving methods comparison",
    "graphing parabolas"
  ],
  "Factoring": [
    "common factor extraction",
    "difference of squares",
    "trinomial patterns"
  ]
}}

Now generate seeds for the concepts above. Return ONLY the JSON object:
"""


class QuestionSeedExtractor(BaseExtractor):
    """
    Question seed extractor. Node-level extractor. Extracts
    `concept_question_seeds` metadata field.

    This extractor reads concepts from `extracted_concepts` metadata and generates
    question seeds (topics/angles) for each concept that can guide quiz generation.

    Args:
        llm (Optional[LLM]): LLM for seed generation
        seeds_per_concept (int): maximum number of seeds per concept
        prompt_template (str): template for seed extraction
        num_workers (int): number of workers for parallel processing

    Output:
        concept_question_seeds: Dict[str, List[str]] - mapping of concepts to seeds
    """

    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    seeds_per_concept: int = Field(
        default=5,
        description="The maximum number of question seeds per concept.",
        gt=0,
    )
    prompt_template: str = Field(
        default=DEFAULT_QUESTION_SEED_TEMPLATE,
        description="Prompt template for seed generation.",
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        seeds_per_concept: int = 5,
        prompt_template: str = DEFAULT_QUESTION_SEED_TEMPLATE,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:
        """Initialise parameters."""
        if seeds_per_concept < 1:
            raise ValueError("seeds_per_concept must be >= 1")

        super().__init__(
            llm=llm or Settings.llm,
            seeds_per_concept=seeds_per_concept,
            prompt_template=prompt_template,
            num_workers=num_workers,
            **kwargs,
        )

        # initialise extraction statistics
        self._extraction_stats = {
            "total_nodes": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_concepts_attempted": 0,
            "total_concepts_extracted": 0,
        }

    @classmethod
    def class_name(cls) -> str:
        return "QuestionSeedExtractor"

    async def _aextract_seeds_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """Extract question seeds from a node and return its metadata dict."""
        self._extraction_stats["total_nodes"] += 1

        if self.is_text_node_only and not isinstance(node, TextNode):
            return {}

        # check if concepts were extracted
        if "extracted_concepts" not in node.metadata:
            return {"concept_question_seeds": {}}

        concepts = node.metadata.get("extracted_concepts", [])

        # skip if no concepts
        if not concepts or len(concepts) == 0:
            return {"concept_question_seeds": {}}

        self._extraction_stats["total_concepts_attempted"] += len(concepts)

        # generate seeds for all concepts in one batched LLM call
        concept_seed_map = await self._generate_seeds_for_concepts(
            concepts=concepts, node_content=node.get_content(metadata_mode=self.metadata_mode)
        )

        # track statistics
        if concept_seed_map:
            self._extraction_stats["successful_extractions"] += 1
            self._extraction_stats["total_concepts_extracted"] += len(concept_seed_map)
        else:
            self._extraction_stats["failed_extractions"] += 1
            logger.warning(
                f"Failed to extract seeds for node. "
                f"Concepts attempted: {', '.join(concepts[:3])}"
                + ("..." if len(concepts) > 3 else "")
            )

        return {"concept_question_seeds": concept_seed_map}

    async def _generate_seeds_for_concepts(
        self, concepts: List[str], node_content: str
    ) -> Dict[str, List[str]]:
        """Generate question seeds for all concepts in a single batched LLM call."""

        # format concepts list for prompt
        concepts_list = "\n".join([f"- {concept}" for concept in concepts])

        # use LLM to generate seeds for all concepts at once
        response = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template),
            concepts_list=concepts_list,
            seeds_per_concept=self.seeds_per_concept,
            context_str=node_content,
        )

        # parse JSON response
        response_text = response.strip()

        try:
            # try to extract JSON from response

            # handle case where response might have extra text before/after JSON
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                concept_seed_map = json.loads(json_text)

                # validate and clean up the response
                cleaned_map = {}
                for concept in concepts:
                    # check if concept exists in response
                    seeds = concept_seed_map.get(concept, [])

                    # filter out empty seeds
                    seeds = [s.strip() for s in seeds if s and s.strip()]

                    if seeds:
                        cleaned_map[concept] = seeds

                # log success
                logger.info(
                    f"Successfully extracted seeds for {len(cleaned_map)}/{len(concepts)} concepts"
                )

                # warn about missing concepts
                missing_concepts = set(concepts) - set(cleaned_map.keys())
                if missing_concepts:
                    logger.warning(
                        f"Failed to extract seeds for concepts: {', '.join(list(missing_concepts)[:3])}"
                        + ("..." if len(missing_concepts) > 3 else "")
                    )

                return cleaned_map
            else:
                # log failure - no JSON found
                logger.error(
                    f"No valid JSON found in LLM response. "
                    f"Response preview: {response_text[:200]}"
                    + ("..." if len(response_text) > 200 else "")
                )
                return {}

        except json.JSONDecodeError as e:
            # log JSON parsing failure with details
            logger.error(
                f"JSON decode error: {e}. "
                f"Failed to parse seeds for concepts: {', '.join(concepts[:3])}"
                + ("..." if len(concepts) > 3 else "")
            )
            logger.debug(f"Raw LLM response: {response_text[:500]}")
            return {}
        except Exception as e:
            # catch any other unexpected errors
            logger.error(f"Unexpected error during seed extraction: {e}")
            logger.debug(f"Concepts: {concepts}")
            return {}

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """Extract question seeds from all nodes using parallel processing."""
        # reset statistics
        self._extraction_stats = {
            "total_nodes": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_concepts_attempted": 0,
            "total_concepts_extracted": 0,
        }

        seed_jobs = []
        for node in nodes:
            seed_jobs.append(self._aextract_seeds_from_node(node))

        metadata_list: List[Dict] = await run_jobs(
            seed_jobs, show_progress=False, workers=self.num_workers
        )

        # display extraction summary
        self._print_extraction_summary()

        return metadata_list

    def _print_extraction_summary(self):
        """Print summary of seed extraction results."""
        stats = self._extraction_stats

        success_rate = (
            (stats["successful_extractions"] / stats["total_nodes"] * 100)
            if stats["total_nodes"] > 0
            else 0
        )

        concept_success_rate = (
            (stats["total_concepts_extracted"] / stats["total_concepts_attempted"] * 100)
            if stats["total_concepts_attempted"] > 0
            else 0
        )

        print("\n" + "=" * 80)
        print("SEED EXTRACTION SUMMARY")
        print("=" * 80)
        print(f"Total nodes processed: {stats['total_nodes']}")
        print(f"Successful extractions: {stats['successful_extractions']} ({success_rate:.1f}%)")
        print(f"Failed extractions: {stats['failed_extractions']}")
        print(
            f"Concepts extracted: {stats['total_concepts_extracted']}/{stats['total_concepts_attempted']} ({concept_success_rate:.1f}%)"
        )

        if stats["failed_extractions"] > 0 or concept_success_rate < 80:
            print("\n⚠️  WARNING: Some seed extractions failed or had low success rate!")
            print("   This may be due to LLM model compatibility issues.")
            print("   Consider using models with better instruction-following capabilities.")
            # try to get model name, fallback to class name if not available
            try:
                model_info = getattr(Settings.llm, "model", str(type(Settings.llm).__name__))
                print(f"   Current model: {model_info}")
            except:
                print(f"   Current model: {type(Settings.llm).__name__}")
            print("   Check logs for details.")

        print("=" * 80 + "\n")
