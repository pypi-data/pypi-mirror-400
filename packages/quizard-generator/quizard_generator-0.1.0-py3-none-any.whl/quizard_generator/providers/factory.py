"""
LLM provider factory for multi-provider support.

This module provides factory functions to instantiate LLM and embedding models
from different providers based on configuration.
"""

import logging
import os
from typing import Optional

from llama_index.core.llms import LLM
from llama_index.core.embeddings import BaseEmbedding

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM and embedding instances based on provider configuration."""

    @staticmethod
    def create_llm(
        provider: str,
        model: str,
        request_timeout: float = 300.0,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> LLM:
        """
        Create LLM instance based on provider.

        Args:
            provider: Provider name (ollama, openai, anthropic, google)
            model: Model identifier
            request_timeout: Request timeout in seconds
            api_key: API key (optional, uses environment variable if not provided)
            **kwargs: Provider-specific parameters

        Returns:
            LLM instance for the specified provider

        Raises:
            ValueError: If provider is not supported
            ImportError: If provider package is not installed
        """
        provider = provider.lower()

        if provider == "ollama":
            try:
                from llama_index.llms.ollama import Ollama
            except ImportError as e:
                raise ImportError(
                    "Ollama provider requires llama-index-llms-ollama. "
                    "Install with: pip install llama-index-llms-ollama"
                ) from e

            logger.info(f"Creating Ollama LLM with model: {model}")
            return Ollama(model=model, request_timeout=request_timeout, **kwargs)

        elif provider == "openai":
            try:
                from llama_index.llms.openai import OpenAI
            except ImportError as e:
                raise ImportError(
                    "OpenAI provider requires llama-index-llms-openai. "
                    "Install with: pip install llama-index-llms-openai"
                ) from e

            # get API key from parameter or environment
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning(
                    "No OpenAI API key provided. Set OPENAI_API_KEY environment variable "
                    "or provide api_key in configuration."
                )

            logger.info(f"Creating OpenAI LLM with model: {model}")
            return OpenAI(model=model, api_key=api_key, timeout=request_timeout, **kwargs)

        elif provider == "anthropic":
            try:
                from llama_index.llms.anthropic import Anthropic
            except ImportError as e:
                raise ImportError(
                    "Anthropic provider requires llama-index-llms-anthropic. "
                    "Install with: pip install llama-index-llms-anthropic"
                ) from e

            # get API key from parameter or environment
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning(
                    "No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable "
                    "or provide api_key in configuration."
                )

            logger.info(f"Creating Anthropic LLM with model: {model}")
            return Anthropic(model=model, api_key=api_key, timeout=request_timeout, **kwargs)

        elif provider == "google":
            try:
                from llama_index.llms.gemini import Gemini
            except ImportError as e:
                raise ImportError(
                    "Google provider requires llama-index-llms-gemini. "
                    "Install with: pip install llama-index-llms-gemini"
                ) from e

            # get API key from parameter or environment
            api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning(
                    "No Google API key provided. Set GOOGLE_API_KEY environment variable "
                    "or provide api_key in configuration."
                )

            logger.info(f"Creating Google Gemini LLM with model: {model}")
            return Gemini(model=model, api_key=api_key, timeout=request_timeout, **kwargs)

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: ollama, openai, anthropic, google"
            )

    @staticmethod
    def create_embedding(
        provider: str, model: str, api_key: Optional[str] = None, **kwargs
    ) -> BaseEmbedding:
        """
        Create embedding model instance based on provider.

        Args:
            provider: Provider name (ollama, openai, huggingface, google)
            model: Model identifier
            api_key: API key (optional, uses environment variable if not provided)
            **kwargs: Provider-specific parameters

        Returns:
            Embedding instance for the specified provider

        Raises:
            ValueError: If provider is not supported
            ImportError: If provider package is not installed
        """
        provider = provider.lower()

        if provider == "ollama":
            try:
                from llama_index.embeddings.ollama import OllamaEmbedding
            except ImportError as e:
                raise ImportError(
                    "Ollama embedding requires llama-index-embeddings-ollama. "
                    "Install with: pip install llama-index-embeddings-ollama"
                ) from e

            logger.info(f"Creating Ollama embedding with model: {model}")
            return OllamaEmbedding(model_name=model, **kwargs)

        elif provider == "openai":
            try:
                from llama_index.embeddings.openai import OpenAIEmbedding
            except ImportError as e:
                raise ImportError(
                    "OpenAI embedding requires llama-index-embeddings-openai. "
                    "Install with: pip install llama-index-embeddings-openai"
                ) from e

            # get API key from parameter or environment
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning(
                    "No OpenAI API key provided. Set OPENAI_API_KEY environment variable "
                    "or provide api_key in configuration."
                )

            logger.info(f"Creating OpenAI embedding with model: {model}")
            return OpenAIEmbedding(model=model, api_key=api_key, **kwargs)

        elif provider == "huggingface":
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            except ImportError as e:
                raise ImportError(
                    "HuggingFace embedding requires llama-index-embeddings-huggingface. "
                    "Install with: pip install llama-index-embeddings-huggingface"
                ) from e

            logger.info(f"Creating HuggingFace embedding with model: {model}")
            return HuggingFaceEmbedding(model_name=model, **kwargs)

        elif provider == "google":
            try:
                from llama_index.embeddings.google import GoogleEmbedding
            except ImportError as e:
                raise ImportError(
                    "Google embedding requires llama-index-embeddings-google. "
                    "Install with: pip install llama-index-embeddings-google"
                ) from e

            # get API key from parameter or environment
            api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning(
                    "No Google API key provided. Set GOOGLE_API_KEY environment variable "
                    "or provide api_key in configuration."
                )

            logger.info(f"Creating Google embedding with model: {model}")
            return GoogleEmbedding(model=model, api_key=api_key, **kwargs)

        else:
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Supported providers: ollama, openai, huggingface, google"
            )
