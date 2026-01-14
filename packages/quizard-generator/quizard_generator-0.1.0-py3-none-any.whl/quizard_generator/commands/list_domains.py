"""List domains command."""

import logging
from typing import Optional

from quizard_generator import DomainManager, QuizardConfig

logger = logging.getLogger(__name__)


def list_domains_command(config_path: Optional[str] = None):
    """
    List all available domains with statistics.

    Args:
        config_path: Optional path to YAML configuration file
    """
    # load configuration
    logger.info("Loading configuration for list-domains")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info(f"Configuration: data_dir={config.data_dir}, storage_dir={config.storage_dir}")

    # create domain manager
    logger.info("Initialising DomainManager")
    domain_manager = DomainManager(config.data_dir, config.storage_dir)

    domains = domain_manager.list_available_domains()
    logger.info(f"Found {len(domains)} available domains")

    # display domains
    print("\n" + "=" * 80)
    print("AVAILABLE DOMAINS")
    print("=" * 80)

    domain_manager.print_available_domains()
