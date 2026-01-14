"""
Knowledge retrieval for quiz generation.

This module provides functionality to retrieve relevant knowledge from the
vector index for question generation.
"""

import logging
from typing import Dict, List, Optional, Tuple

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores.types import (
    MetadataFilters,
    MetadataFilter,
    FilterOperator,
    FilterCondition,
)

from quizard_generator.exceptions import KnowledgeRetrievalError

logger = logging.getLogger(__name__)


TOPIC_EXTRACTION_PROMPT = """\
Extract distinct topics or concepts from this quiz instruction.

Instruction: "{instruction}"

Requirements:
- Return ONLY topic names/keywords that can be searched in metadata
- Be specific and concise
- If multiple topics mentioned (e.g., "A as well as B"), list them separately
- Return one topic per line
- Maximum 5 topics
- Do not include generic terms like "quiz", "test", "questions"

Examples:

Instruction: "quiz me on photosynthesis and cellular respiration"
Topics:
photosynthesis
cellular respiration

Instruction: "test me on variables, loops, and functions"
Topics:
variables
loops
functions

Instruction: "questions about World War I and the Treaty of Versailles"
Topics:
World War I
Treaty of Versailles

Topics:
"""


class KnowledgeRetriever:
    """
    Retrieves relevant knowledge from vector index based on concepts.

    Uses QueryFusionRetriever to generate multiple query variations and
    ensure broad coverage across multiple documents and topics.
    """

    def __init__(
        self,
        index: VectorStoreIndex,
        llm: Optional[LLM] = None,
        num_query_variations: int = 4,
        min_nodes_per_topic: int = 1,
    ):
        """
        Initialise the knowledge retriever.

        Args:
            index: Vector store index containing indexed documents
            llm: LLM for query generation and topic extraction
            num_query_variations: Number of query variations to generate
            min_nodes_per_topic: Minimum nodes required per extracted topic
        """
        self.index = index
        self.llm = llm
        self.num_query_variations = num_query_variations
        self.min_nodes_per_topic = min_nodes_per_topic

    def retrieve(self, concepts: List[str], top_k: int = 5) -> List[NodeWithScore]:
        """
        Retrieve relevant nodes from the index based on concepts.

        Uses QueryFusionRetriever to generate multiple query variations,
        ensuring broad coverage across documents and topics.

        Args:
            concepts: List of concept names to search for
            top_k: Number of top results to return per concept

        Returns:
            List of nodes with scores

        Raises:
            KnowledgeRetrievalError: If retrieval fails
            ValueError: If concepts list is empty or top_k is not positive
        """
        if not concepts:
            raise ValueError("concepts list cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        try:
            logger.info(f"Starting retrieval for {len(concepts)} concept(s)")

            # increase similarity_top_k to account for fusion deduplication
            # fusion retriever will deduplicate results, so we need more initially
            adjusted_top_k = top_k * self.num_query_variations

            logger.info(
                f"Adjusted similarity_top_k to {adjusted_top_k} "
                f"({top_k} * {self.num_query_variations} query variations)"
            )

            # create base retriever from index with adjusted top_k
            base_retriever = self.index.as_retriever(similarity_top_k=adjusted_top_k)

            # create query fusion retriever for enhanced coverage
            # similarity_top_k controls final number of results after fusion
            fusion_retriever = QueryFusionRetriever(
                retrievers=[base_retriever],
                llm=self.llm,
                similarity_top_k=top_k,  # final number of results to return
                num_queries=self.num_query_variations,
                use_async=False,
                verbose=True,  # enable verbose logging for query generation
            )

            # retrieve nodes for each concept using fusion retrieval
            all_nodes = []
            for i, concept in enumerate(concepts, 1):
                query = f"Information about {concept}"

                logger.info(f"Concept {i}/{len(concepts)}: '{concept}'")
                logger.info(f"Generating {self.num_query_variations} query variations...")

                # fusion retriever will generate variations and retrieve
                nodes = fusion_retriever.retrieve(query)

                logger.info(
                    f"Retrieved {len(nodes)} nodes for concept '{concept}' (before deduplication)"
                )

                # log retrieved nodes with scores and source documents
                for j, node in enumerate(nodes, 1):
                    file_name = node.node.metadata.get("file_name", "unknown")
                    extracted_concepts = node.node.metadata.get("extracted_concepts", [])

                    logger.debug(
                        f"  [{j}] Node: {node.node.node_id[:8]}... | "
                        f"Score: {node.score:.4f} | "
                        f"Source: {file_name} | "
                        f"Concepts: {extracted_concepts}"
                    )

                all_nodes.extend(nodes)

            # deduplicate nodes by node_id
            seen_ids = set()
            unique_nodes = []
            for node in all_nodes:
                if node.node.node_id not in seen_ids:
                    seen_ids.add(node.node.node_id)
                    unique_nodes.append(node)

            # collect source documents for summary
            source_documents = set()
            for node in unique_nodes:
                file_name = node.node.metadata.get("file_name", "unknown")
                source_documents.add(file_name)

            logger.info(
                f"Retrieved {len(unique_nodes)} unique nodes from "
                f"{len(source_documents)} source document(s): {sorted(source_documents)}"
            )

            # detailed logging of deduplicated nodes in verbose mode
            logger.info("Deduplicated nodes with scores:")
            for i, node in enumerate(unique_nodes, 1):
                file_name = node.node.metadata.get("file_name", "unknown")
                extracted_concepts = node.node.metadata.get("extracted_concepts", [])

                logger.info(
                    f"  [{i}] Node: {node.node.node_id[:8]}... | "
                    f"Score: {node.score:.4f} | "
                    f"Source: {file_name} | "
                    f"Concepts: {extracted_concepts}"
                )

            return unique_nodes

        except Exception as e:
            logger.error(f"Failed to retrieve knowledge for concepts {concepts}: {e}")
            raise KnowledgeRetrievalError(
                f"Unable to retrieve knowledge: {str(e)}",
                concepts=concepts,
            ) from e

    def extract_topics_from_instruction(self, instruction: str) -> List[str]:
        """
        Extract distinct topics/concepts from natural language instruction.

        Works across any domain: mathematics, biology, programming, history, etc.

        Args:
            instruction: Natural language quiz instruction

        Returns:
            List of topic keywords

        Examples:
            >>> retriever.extract_topics_from_instruction(
            ...     "quiz me on photosynthesis and respiration"
            ... )
            ["photosynthesis", "respiration"]

            >>> retriever.extract_topics_from_instruction(
            ...     "test me on variables and functions in programming"
            ... )
            ["variables", "functions", "programming"]
        """
        if not instruction:
            return []

        if not self.llm:
            logger.warning("No LLM available for topic extraction")
            return []

        try:
            prompt = TOPIC_EXTRACTION_PROMPT.format(instruction=instruction)
            response = self.llm.complete(prompt)

            # parse response - one topic per line
            topics = [
                line.strip()
                for line in response.text.strip().split("\n")
                if line.strip() and len(line.strip()) > 1
            ]

            # deduplicate whilst preserving order
            seen = set()
            unique_topics = []
            for topic in topics:
                topic_lower = topic.lower()
                if topic_lower not in seen:
                    seen.add(topic_lower)
                    unique_topics.append(topic)

            logger.info(f"Extracted {len(unique_topics)} topics: {unique_topics}")
            return unique_topics

        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
            return []

    def create_metadata_filters_for_topics(self, topics: List[str]) -> MetadataFilters:
        """
        Create OR-combined metadata filters for extracted_concepts field.

        Uses CONTAINS operator for flexible substring matching across any domain.

        Args:
            topics: List of topic keywords from any domain

        Returns:
            MetadataFilters with OR condition

        Examples:
            Biology: "photosynthesis" matches "Photosynthesis process"
            Programming: "variables" matches "Variable declaration and scope"
            History: "World War I" matches "Causes of World War I"
        """
        if not topics:
            raise ValueError("topics cannot be empty")

        filters = [
            MetadataFilter(key="extracted_concepts", value=topic, operator=FilterOperator.CONTAINS)
            for topic in topics
        ]

        return MetadataFilters(
            filters=filters,
            condition=FilterCondition.OR,  # match ANY topic
        )

    def _map_nodes_to_topics(
        self, nodes: List[NodeWithScore], topics: List[str]
    ) -> Dict[str, List[NodeWithScore]]:
        """
        Map retrieved nodes to topics they match.

        A node can match multiple topics if its extracted_concepts contain them.
        """
        topic_map = {topic: [] for topic in topics}

        for node in nodes:
            node_concepts = node.node.metadata.get("extracted_concepts", [])
            node_concepts_str = " ".join(node_concepts).lower()

            for topic in topics:
                if topic.lower() in node_concepts_str:
                    topic_map[topic].append(node)

        return topic_map

    def _log_retrieval_coverage(
        self,
        nodes: List[NodeWithScore],
        topics: List[str],
        topic_node_map: Dict[str, List[NodeWithScore]],
    ):
        """
        Log detailed retrieval coverage information.

        All log messages use dynamic topic names - no hardcoded domain-specific terms.
        """
        # per-topic node count
        logger.info("Nodes per topic:")
        for topic in topics:
            count = len(topic_node_map[topic])
            logger.info(f"  {topic}: {count} node(s)")

        # per-source document count
        source_docs = {}
        for node in nodes:
            file_name = node.node.metadata.get("file_name", "unknown")
            source_docs[file_name] = source_docs.get(file_name, 0) + 1

        logger.info("Nodes by source document:")
        for doc, count in sorted(source_docs.items()):
            logger.info(f"  {doc}: {count} node(s)")

        # which nodes matched which topics
        logger.info("Topic to node mapping:")
        for topic, topic_nodes in topic_node_map.items():
            if topic_nodes:
                node_ids = [n.node.node_id[:8] + "..." for n in topic_nodes[:3]]
                suffix = f" (and {len(topic_nodes) - 3} more)" if len(topic_nodes) > 3 else ""
                logger.info(f"  {topic}: {', '.join(node_ids)}{suffix}")

    def _deduplicate_nodes(self, nodes: List[NodeWithScore]) -> List[NodeWithScore]:
        """
        Deduplicate nodes by node_id whilst preserving order.
        """
        seen_ids = set()
        unique = []
        for node in nodes:
            if node.node.node_id not in seen_ids:
                seen_ids.add(node.node.node_id)
                unique.append(node)
        return unique

    def _filter_nodes_by_topics(
        self, nodes: List[NodeWithScore], topics: List[str]
    ) -> List[NodeWithScore]:
        """
        Client-side filtering of nodes by topics (CONTAINS matching).

        Since SimpleVectorStore doesn't support metadata filters,
        we filter retrieved nodes in Python.
        """
        filtered = []
        topics_lower = [t.lower() for t in topics]

        for node in nodes:
            node_concepts = node.node.metadata.get("extracted_concepts", [])
            node_concepts_str = " ".join(node_concepts).lower()

            # check if ANY topic matches ANY concept
            if any(topic in node_concepts_str for topic in topics_lower):
                filtered.append(node)

        return filtered

    def _retrieve_with_fusion(self, query: str, top_k: int) -> List[NodeWithScore]:
        """
        Fall back to QueryFusionRetriever (existing implementation).
        """
        # call existing retrieve method with QueryFusionRetriever
        return self.retrieve([query], top_k)

    def retrieve_with_metadata_filtering(
        self, instruction: str, top_k: int = 5
    ) -> Tuple[List[NodeWithScore], List[str]]:
        """
        Retrieve nodes using metadata filtering based on instruction topics.

        Strategy:
        1. Extract topics from instruction using LLM
        2. Create OR-combined metadata filters
        3. Retrieve nodes matching ANY topic
        4. Validate minimum nodes per topic
        5. Fall back to QueryFusionRetriever if needed

        Args:
            instruction: Natural language instruction
            top_k: Target number of nodes to retrieve

        Returns:
            Tuple of (nodes with scores, extracted topics list)
        """
        logger.info(f"Starting metadata-filtered retrieval for instruction")

        # step 1: extract topics
        topics = self.extract_topics_from_instruction(instruction)

        if not topics:
            logger.info("No topics extracted, falling back to QueryFusionRetriever")
            nodes = self._retrieve_with_fusion(instruction, top_k)
            return nodes, []

        logger.info(f"Extracted {len(topics)} topics: {topics}")

        try:
            # step 2: create metadata filters (note: SimpleVectorStore doesn't support filters)
            # we'll retrieve more nodes and filter client-side instead
            logger.info(f"Retrieving nodes for client-side filtering by {len(topics)} topics")

            # step 3: retrieve MORE nodes since we'll filter client-side
            retriever = self.index.as_retriever(
                similarity_top_k=top_k * 6  # retrieve many more for filtering
            )

            all_nodes = retriever.retrieve(instruction)
            logger.info(f"Retrieved {len(all_nodes)} nodes before filtering")

            # step 4: client-side filtering by topics
            nodes = self._filter_nodes_by_topics(all_nodes, topics)
            logger.info(f"Filtered to {len(nodes)} nodes matching topics")

            logger.info(f"Retrieved {len(nodes)} nodes with metadata filtering")

            # step 4: analyse coverage by topic and source
            topic_node_map = self._map_nodes_to_topics(nodes, topics)
            self._log_retrieval_coverage(nodes, topics, topic_node_map)

            # step 5: validate minimum nodes per topic
            topics_below_min = [
                topic
                for topic, topic_nodes in topic_node_map.items()
                if len(topic_nodes) < self.min_nodes_per_topic
            ]

            if topics_below_min:
                logger.warning(
                    f"{len(topics_below_min)} topic(s) have fewer than "
                    f"{self.min_nodes_per_topic} nodes: {topics_below_min}"
                )

            # step 6: fallback check (proportional to num_questions)
            # only fall back if we have very few nodes (less than 3 or less than 1/3 of target)
            min_threshold = max(3, top_k // 3)  # at least 3, or one-third of top_k
            if len(nodes) < min_threshold:
                logger.warning(
                    f"Only {len(nodes)} nodes retrieved (threshold: {min_threshold}), "
                    f"falling back to QueryFusionRetriever"
                )
                fallback_nodes = self._retrieve_with_fusion(instruction, top_k)
                return fallback_nodes, []

            # deduplicate by node_id
            unique_nodes = self._deduplicate_nodes(nodes)

            logger.info(
                f"Metadata filtering successful: {len(unique_nodes)} unique nodes "
                f"covering {len(topics)} topics"
            )

            return unique_nodes[:top_k], topics

        except Exception as e:
            logger.error(f"Metadata filtering failed: {e}, falling back")
            fallback_nodes = self._retrieve_with_fusion(instruction, top_k)
            return fallback_nodes, []
