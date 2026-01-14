"""
Knowledge summarisation for quiz generation.

This module provides functionality to summarise retrieved knowledge for
question generation.
"""

import logging
from typing import List

from llama_index.core.llms import LLM
from llama_index.core.schema import NodeWithScore

from quizard_generator.exceptions import KnowledgeSummarisationError

logger = logging.getLogger(__name__)


class KnowledgeSummariser:
    """
    Summarises retrieved knowledge for question generation.

    Uses LLM to condense retrieved content into concise summaries.
    """

    def __init__(self, llm: LLM):
        """
        Initialise the knowledge summariser.

        Args:
            llm: Language model for summarisation
        """
        self.llm = llm

    def summarise(self, nodes: List[NodeWithScore], concepts: List[str]) -> str:
        """
        Summarise retrieved nodes into concise knowledge summary.

        Args:
            nodes: Retrieved nodes with scores
            concepts: Concepts to focus the summary on

        Returns:
            Summarised knowledge text

        Raises:
            KnowledgeSummarisationError: If summarisation fails
            ValueError: If nodes list is empty
        """
        if not nodes:
            raise ValueError("nodes list cannot be empty")

        try:
            # extract text from nodes
            node_texts = [node.node.get_content() for node in nodes]
            combined_text = "\n\n".join(node_texts)

            # create summarisation prompt
            concepts_str = ", ".join(concepts)
            prompt = f"""Summarise the following text focusing on these concepts: {concepts_str}

Provide a concise summary that captures the key information relevant to these concepts. The summary will be used to generate quiz questions.

Text:
{combined_text}

Summary:"""

            # generate summary using llm
            response = self.llm.complete(prompt)
            summary = response.text.strip()

            if not summary:
                raise KnowledgeSummarisationError(
                    "LLM returned empty summary",
                    concepts=concepts,
                    num_nodes=len(nodes),
                )

            # context window monitoring
            summary_length = len(summary)
            estimated_tokens = summary_length // 4

            model_limits = {"gemma3:4b": 8192, "qwen2-math:7b-instruct-q4_K_M": 32768}

            # get model name from self.llm
            model_name = getattr(self.llm, "model", "unknown")
            limit = model_limits.get(model_name, 8192)
            usage_pct = (estimated_tokens / limit) * 100

            if usage_pct > 90:
                logger.error(
                    f"Context window critical: {usage_pct:.0f}% "
                    f"({estimated_tokens}/{limit} tokens for {model_name})"
                )
            elif usage_pct > 70:
                logger.warning(
                    f"Context window high: {usage_pct:.0f}% "
                    f"({estimated_tokens}/{limit} tokens for {model_name})"
                )
            else:
                logger.info(
                    f"Summary generated: {summary_length} chars "
                    f"(~{estimated_tokens} tokens, {usage_pct:.0f}% of {limit})"
                )

            return summary

        except Exception as e:
            logger.error(f"Failed to summarise knowledge: {e}")
            raise KnowledgeSummarisationError(
                f"Unable to summarise knowledge: {str(e)}",
                concepts=concepts,
                num_nodes=len(nodes),
            ) from e
