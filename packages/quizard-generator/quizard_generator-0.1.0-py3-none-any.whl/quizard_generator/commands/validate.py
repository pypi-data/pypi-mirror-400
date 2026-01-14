"""Validate index command implementation."""

import logging
import os
from pathlib import Path
from typing import List, Optional

from llama_index.core import load_index_from_storage, StorageContext

from quizard_generator import DomainManager, QuizardConfig, QuizardContext
from quizard_generator.exceptions import DomainNotFoundError
from quizard_generator.indexing import IndexManifest

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = ["txt", "pdf", "docx", "pptx"]


def get_all_files_in_domain(data_path: str) -> List[str]:
    """
    Get all supported files in domain data directory.

    Args:
        data_path: Path to domain data directory

    Returns:
        List of file paths
    """
    files = []

    for file_path in Path(data_path).rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            file_ext = file_path.suffix[1:].lower()
            if not file_ext or file_ext in SUPPORTED_EXTENSIONS:
                files.append(str(file_path))

    return sorted(files)


async def validate_index_command(domain: str, config_path: Optional[str] = None):
    """
    Validate index health for a domain.

    Args:
        domain: Domain name to validate
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print(f"VALIDATE INDEX: Checking Domain '{domain}'")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration for index validation")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

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

    # get paths
    data_path = domain_manager.get_data_path(domain)
    storage_path = domain_manager.get_storage_path(domain)
    logger.info(f"Data path: {data_path}")
    logger.info(f"Storage path: {storage_path}")

    issues = []
    warnings = []

    # check if storage directory exists
    logger.info("Checking if storage directory exists")
    if not os.path.exists(storage_path):
        logger.error(f"Storage directory does not exist: {storage_path}")
        issues.append("Storage directory does not exist")
    else:
        logger.info("Storage directory exists")
        # check for required index files
        required_files = ["docstore.json", "default__vector_store.json", "index_store.json"]
        for req_file in required_files:
            if not os.path.exists(os.path.join(storage_path, req_file)):
                issues.append(f"Missing required file: {req_file}")

    # check manifest
    manifest = IndexManifest(storage_path)
    try:
        manifest_data = manifest.load()
        stats = manifest.get_stats()

        print(f"Manifest statistics:")
        print(f"  Files tracked: {stats['total_files']}")
        print(f"  Total nodes: {stats['total_nodes']}")
        print(f"  Last updated: {stats['last_updated'] or 'Unknown'}")
        print()

    except Exception as e:
        issues.append(f"Failed to load manifest: {e}")

    # check for deleted files
    all_files = get_all_files_in_domain(data_path)
    deleted_files = manifest.get_deleted_files(all_files)

    if deleted_files:
        warnings.append(f"{len(deleted_files)} file(s) in index but deleted from disk")

    # check for new files
    new_files = manifest.get_new_files(all_files)
    if new_files:
        warnings.append(f"{len(new_files)} new file(s) not in index")

    # check for modified files
    modified_files = manifest.get_modified_files(all_files)
    if modified_files:
        warnings.append(f"{len(modified_files)} file(s) modified since indexing")

    # try to load index
    if not issues:
        with QuizardContext(config):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=storage_path)
                index = load_index_from_storage(storage_context)
                print("✓ Index loaded successfully")

                # basic query test
                query_engine = index.as_query_engine()
                test_response = query_engine.query("test")
                print("✓ Query engine test passed")

            except Exception as e:
                issues.append(f"Failed to load or query index: {e}")
                logger.exception("Index validation failed")

    # report results
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    if not issues and not warnings:
        print("✓ Index is healthy - no issues found")
    else:
        if issues:
            print(f"✗ Found {len(issues)} critical issue(s):")
            for issue in issues:
                print(f"  - {issue}")
            print()

        if warnings:
            print(f"⚠ Found {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")
            print()

        if warnings and not issues:
            print("Recommendations:")
            if new_files or modified_files:
                print("  - Run 'quizard index-refresh --domain {domain}' to update index")
            if deleted_files:
                print("  - Consider running 'quizard index --domain {domain}' to rebuild")

    print("=" * 80 + "\n")
