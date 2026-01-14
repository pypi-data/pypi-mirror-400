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
- Prefer short noun phrases (3–4 words)
- Extract concepts central to understanding the text

Format: Return as a list, one per line, without numbering.

Examples:

Text:
"Neural networks learn by adjusting weights using gradient descent to minimize a loss function. Backpropagation efficiently computes gradients through layered architectures."

High-Level Concepts:
Neural network training
Gradient descent 
Loss function 
Backpropagation algorithm

Text:
"Photosynthesis converts light energy into chemical energy using chlorophyll. This process produces glucose and releases oxygen as a byproduct."

High-Level Concepts:
Photosynthesis 
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


class ConceptExtractor(BaseExtractor):
    """
    Concept extractor. Node-level extractor. Extracts
    `extracted_concepts` metadata field.

    Args:
        llm (Optional[LLM]): LLM for concept extraction
        max_concepts (int): maximum number of concepts to extract per node
        prompt_template (str): template for concept extraction
        num_workers (int): number of workers for parallel processing
    """

    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    max_concepts: int = Field(
        default=10,
        description="The maximum number of concepts to extract.",
        gt=0,
    )
    prompt_template: str = Field(
        default=DEFAULT_CONCEPT_EXTRACT_TEMPLATE,
        description="Prompt template to use when extracting concepts.",
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        max_concepts: int = 10,
        prompt_template: str = DEFAULT_CONCEPT_EXTRACT_TEMPLATE,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:
        """Initialise parameters."""
        if max_concepts < 1:
            raise ValueError("max_concepts must be >= 1")

        super().__init__(
            llm=llm or Settings.llm,
            max_concepts=max_concepts,
            prompt_template=prompt_template,
            num_workers=num_workers,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "ConceptExtractor"

    async def _aextract_concepts_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """Extract concepts from a node and return its metadata dict."""
        if self.is_text_node_only and not isinstance(node, TextNode):
            return {}

        context_str = node.get_content(metadata_mode=self.metadata_mode)
        concepts_response = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template),
            max_concepts=self.max_concepts,
            context_str=context_str,
        )

        # parse response into list of concepts
        concepts = [
            c.strip() 
            for c in concepts_response.strip().split("\n") 
            if c.strip()
        ]

        # return as list
        return {"extracted_concepts": concepts}

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """Extract concepts from all nodes using parallel processing."""
        concept_jobs = []
        for node in nodes:
            concept_jobs.append(self._aextract_concepts_from_node(node))

        metadata_list: List[Dict] = await run_jobs(
            concept_jobs, show_progress=False, workers=self.num_workers
        )

        return metadata_list


