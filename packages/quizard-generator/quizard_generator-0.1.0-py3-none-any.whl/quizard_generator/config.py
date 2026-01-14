"""
Configuration management for Quizard Generator.

Provides centralised configuration with support for:
- YAML configuration files
- Programmatic configuration (library usage)
- Sensible defaults
- Thread-safe Settings management via QuizardContext
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from quizard_generator.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class QuizardConfig:
    """
    Centralised configuration for Quizard Generator.

    Attributes:
        data_dir: Root directory containing domain subdirectories
        storage_dir: Root directory for domain-specific indices
        indexing_llm_model: Model name for indexing stage LLM
        indexing_embedding_model: Model name for embedding generation
        generation_general_llm_model: Model name for general generation tasks
        generation_specialist_llm_model: Model name for specialist tasks (question generation)
        llm_request_timeout: Timeout for LLM requests in seconds
        chunk_size: Size of text chunks for document splitting
        max_concepts: Maximum concepts to extract per chunk
        seeds_per_concept: Number of question seeds per concept
        num_workers: Number of parallel workers for extraction
        retrieval_num_query_variations: Number of query variations for fusion retrieval
        retrieval_use_metadata_filtering: Enable metadata-based topic filtering
        retrieval_min_nodes_per_topic: Minimum nodes required per extracted topic
        llm_provider: LLM provider (ollama, openai, anthropic, google)
        embedding_provider: Embedding provider (ollama, openai, huggingface, google)
        openai_api_key: OpenAI API key (optional, uses OPENAI_API_KEY env var if not set)
        anthropic_api_key: Anthropic API key (optional, uses ANTHROPIC_API_KEY env var if not set)
        google_api_key: Google API key (optional, uses GOOGLE_API_KEY env var if not set)
    """

    # paths
    data_dir: str = "data"
    storage_dir: str = "storage"

    # model configuration
    indexing_llm_model: str = "gemma3:4b"
    indexing_embedding_model: str = "embeddinggemma"
    generation_general_llm_model: str = "gemma3:4b"
    generation_specialist_llm_model: str = "gemma3:4b"

    # provider configuration (new)
    llm_provider: str = "ollama"
    embedding_provider: str = "ollama"

    # API keys for cloud providers (optional - prefer environment variables)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # performance settings
    llm_request_timeout: float = 300.0
    chunk_size: int = 2048
    max_concepts: int = 5
    seeds_per_concept: int = 2
    num_workers: int = 4

    # retrieval settings
    retrieval_num_query_variations: int = 4
    retrieval_use_metadata_filtering: bool = True
    retrieval_min_nodes_per_topic: int = 1

    def __post_init__(self):
        """Validate configuration after initialisation."""
        self._validate()

    def _validate(self):
        """
        Validate configuration values.

        Raises:
            ConfigurationError: If any configuration value is invalid
        """
        # validate paths
        if not self.data_dir:
            raise ConfigurationError("data_dir cannot be empty")
        if not self.storage_dir:
            raise ConfigurationError("storage_dir cannot be empty")

        # validate model names
        if not self.indexing_llm_model:
            raise ConfigurationError("indexing_llm_model cannot be empty")
        if not self.indexing_embedding_model:
            raise ConfigurationError("indexing_embedding_model cannot be empty")
        if not self.generation_general_llm_model:
            raise ConfigurationError("generation_general_llm_model cannot be empty")
        if not self.generation_specialist_llm_model:
            raise ConfigurationError("generation_specialist_llm_model cannot be empty")

        # validate provider names
        valid_llm_providers = {"ollama", "openai", "anthropic", "google"}
        if self.llm_provider.lower() not in valid_llm_providers:
            raise ConfigurationError(
                f"Invalid llm_provider '{self.llm_provider}'. "
                f"Supported: {', '.join(valid_llm_providers)}"
            )

        valid_embedding_providers = {"ollama", "openai", "huggingface", "google"}
        if self.embedding_provider.lower() not in valid_embedding_providers:
            raise ConfigurationError(
                f"Invalid embedding_provider '{self.embedding_provider}'. "
                f"Supported: {', '.join(valid_embedding_providers)}"
            )

        # validate numeric values
        if self.llm_request_timeout <= 0:
            raise ConfigurationError("llm_request_timeout must be positive")
        if self.chunk_size <= 0:
            raise ConfigurationError("chunk_size must be positive")
        if self.max_concepts <= 0:
            raise ConfigurationError("max_concepts must be positive")
        if self.seeds_per_concept <= 0:
            raise ConfigurationError("seeds_per_concept must be positive")
        if self.num_workers <= 0:
            raise ConfigurationError("num_workers must be positive")
        if self.retrieval_num_query_variations <= 0:
            raise ConfigurationError("retrieval_num_query_variations must be positive")
        if self.retrieval_min_nodes_per_topic < 1:
            raise ConfigurationError("retrieval_min_nodes_per_topic must be at least 1")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "QuizardConfig":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            QuizardConfig instance with values from file

        Raises:
            ConfigurationError: If file cannot be read or parsed
            FileNotFoundError: If configuration file doesn't exist
        """
        import yaml

        yaml_path = Path(path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(yaml_path, "r") as f:
                config_data = yaml.safe_load(f)

            if not isinstance(config_data, dict):
                raise ConfigurationError(
                    f"Invalid YAML configuration: expected dictionary, got {type(config_data)}"
                )

            # create config with values from YAML
            return cls(**config_data)

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML configuration: {e}")
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration parameters: {e}")

    def to_yaml(self, path: str | Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            path: Path where YAML file should be saved

        Raises:
            ConfigurationError: If file cannot be written
        """
        import yaml

        yaml_path = Path(path)

        # ensure parent directory exists
        yaml_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # convert dataclass to dict
            config_dict = {
                "data_dir": self.data_dir,
                "storage_dir": self.storage_dir,
                "indexing_llm_model": self.indexing_llm_model,
                "indexing_embedding_model": self.indexing_embedding_model,
                "generation_general_llm_model": self.generation_general_llm_model,
                "generation_specialist_llm_model": self.generation_specialist_llm_model,
                "llm_provider": self.llm_provider,
                "embedding_provider": self.embedding_provider,
                "llm_request_timeout": self.llm_request_timeout,
                "chunk_size": self.chunk_size,
                "max_concepts": self.max_concepts,
                "seeds_per_concept": self.seeds_per_concept,
                "num_workers": self.num_workers,
                "retrieval_num_query_variations": self.retrieval_num_query_variations,
                "retrieval_use_metadata_filtering": self.retrieval_use_metadata_filtering,
                "retrieval_min_nodes_per_topic": self.retrieval_min_nodes_per_topic,
            }

            # only include API keys if they are set (don't write None values)
            if self.openai_api_key:
                config_dict["openai_api_key"] = self.openai_api_key
            if self.anthropic_api_key:
                config_dict["anthropic_api_key"] = self.anthropic_api_key
            if self.google_api_key:
                config_dict["google_api_key"] = self.google_api_key

            with open(yaml_path, "w") as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration saved to {yaml_path}")

        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        result = {
            "data_dir": self.data_dir,
            "storage_dir": self.storage_dir,
            "indexing_llm_model": self.indexing_llm_model,
            "indexing_embedding_model": self.indexing_embedding_model,
            "generation_general_llm_model": self.generation_general_llm_model,
            "generation_specialist_llm_model": self.generation_specialist_llm_model,
            "llm_provider": self.llm_provider,
            "embedding_provider": self.embedding_provider,
            "llm_request_timeout": self.llm_request_timeout,
            "chunk_size": self.chunk_size,
            "max_concepts": self.max_concepts,
            "seeds_per_concept": self.seeds_per_concept,
            "num_workers": self.num_workers,
            "retrieval_num_query_variations": self.retrieval_num_query_variations,
            "retrieval_use_metadata_filtering": self.retrieval_use_metadata_filtering,
            "retrieval_min_nodes_per_topic": self.retrieval_min_nodes_per_topic,
        }

        # only include API keys if they are set
        if self.openai_api_key:
            result["openai_api_key"] = self.openai_api_key
        if self.anthropic_api_key:
            result["anthropic_api_key"] = self.anthropic_api_key
        if self.google_api_key:
            result["google_api_key"] = self.google_api_key

        return result


class QuizardContext:
    """
    Context manager for thread-safe LlamaIndex Settings management.

    This context manager ensures that global Settings changes are isolated
    and restored after use, preventing conflicts in multi-threaded or
    library usage scenarios.

    Example:
        >>> config = QuizardConfig(indexing_llm_model="gemma3:4b")
        >>> with QuizardContext(config):
        ...     # Settings.llm and Settings.embed_model are configured
        ...     pipeline = QuizGenerationPipeline(index)
        ...     quiz = pipeline.generate_quiz(...)
        >>> # Settings restored to previous values
    """

    def __init__(self, config: QuizardConfig):
        """
        Initialise context manager with configuration.

        Args:
            config: QuizardConfig instance with model settings
        """
        self.config = config
        self._original_settings: dict[str, Any] = {}

    def __enter__(self) -> "QuizardContext":
        """
        Enter context: backup current settings and apply configuration.

        Returns:
            Self for context manager protocol
        """
        from llama_index.core import Settings
        from quizard_generator.providers.factory import LLMProviderFactory

        # backup current settings (handle case where they're not set yet)
        self._original_settings = {
            "llm": getattr(Settings, "_llm", None),
            "embed_model": getattr(Settings, "_embed_model", None),
        }

        # determine which API key to use based on provider
        api_key = None
        if self.config.llm_provider == "openai":
            api_key = self.config.openai_api_key
        elif self.config.llm_provider == "anthropic":
            api_key = self.config.anthropic_api_key
        elif self.config.llm_provider == "google":
            api_key = self.config.google_api_key

        # apply new settings for indexing stage using factory
        Settings.llm = LLMProviderFactory.create_llm(
            provider=self.config.llm_provider,
            model=self.config.indexing_llm_model,
            request_timeout=self.config.llm_request_timeout,
            api_key=api_key,
        )

        # determine embedding API key
        embedding_api_key = None
        if self.config.embedding_provider == "openai":
            embedding_api_key = self.config.openai_api_key
        elif self.config.embedding_provider == "google":
            embedding_api_key = self.config.google_api_key

        Settings.embed_model = LLMProviderFactory.create_embedding(
            provider=self.config.embedding_provider,
            model=self.config.indexing_embedding_model,
            api_key=embedding_api_key,
        )

        logger.debug(
            f"QuizardContext: Applied settings with Provider={self.config.llm_provider}, "
            f"LLM={self.config.indexing_llm_model}, Embedding={self.config.indexing_embedding_model}"
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: restore original settings.

        Note: We only restore settings that were previously set (not None).
        Restoring to None would trigger LlamaIndex's MockLLM fallback,
        which prints confusing "LLM is explicitly disabled" messages.
        Since Settings is a global singleton, leaving valid Ollama instances
        in place after context exit is harmless and preferred.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised

        Returns:
            False to propagate exceptions
        """
        from llama_index.core import Settings

        # restore original settings (but don't restore to None, which triggers MockLLM warnings)
        for key, value in self._original_settings.items():
            if value is not None:
                setattr(Settings, key, value)
            # if original was None, leave current valid settings in place

        logger.debug("QuizardContext: Restored original settings")

        # don't suppress exceptions
        return False


def configure_settings(config: QuizardConfig) -> None:
    """
    Configure LlamaIndex global Settings.

    Warning: This modifies global state. For thread-safe operations,
    use QuizardContext instead.

    Args:
        config: QuizardConfig instance with model settings

    Example:
        >>> config = QuizardConfig(indexing_llm_model="gemma3:4b")
        >>> configure_settings(config)
        >>> # Settings.llm and Settings.embed_model are now configured
    """
    from llama_index.core import Settings
    from quizard_generator.providers.factory import LLMProviderFactory

    # determine which API key to use based on provider
    api_key = None
    if config.llm_provider == "openai":
        api_key = config.openai_api_key
    elif config.llm_provider == "anthropic":
        api_key = config.anthropic_api_key
    elif config.llm_provider == "google":
        api_key = config.google_api_key

    Settings.llm = LLMProviderFactory.create_llm(
        provider=config.llm_provider,
        model=config.indexing_llm_model,
        request_timeout=config.llm_request_timeout,
        api_key=api_key,
    )

    # determine embedding API key
    embedding_api_key = None
    if config.embedding_provider == "openai":
        embedding_api_key = config.openai_api_key
    elif config.embedding_provider == "google":
        embedding_api_key = config.google_api_key

    Settings.embed_model = LLMProviderFactory.create_embedding(
        provider=config.embedding_provider,
        model=config.indexing_embedding_model,
        api_key=embedding_api_key,
    )

    logger.info(
        f"Configured Settings: Provider={config.llm_provider}, "
        f"LLM={config.indexing_llm_model}, Embedding={config.indexing_embedding_model}"
    )
