"""Index command implementations."""

import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional, Sequence

from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import SimpleVectorStore

from quizard_generator import DomainManager, QuizardConfig, QuizardContext
from quizard_generator.exceptions import DomainNotFoundError, ValidationError
from quizard_generator.extractors import ConceptExtractor, QuestionSeedExtractor
from quizard_generator.indexing import IndexManifest

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = ["txt", "pdf", "docx", "pptx"]


# helper functions


def validate_file_extensions(data_path: str):
    """
    Validate that all files in data directory have supported extensions.

    Args:
        data_path: Path to data directory

    Raises:
        ValidationError: If unsupported file types are found
    """
    unsupported_files = []

    for file_path in Path(data_path).rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            file_ext = file_path.suffix[1:].lower()
            if file_ext and file_ext not in SUPPORTED_EXTENSIONS:
                unsupported_files.append(str(file_path))

    if unsupported_files:
        print(f"\nError: Found unsupported file types:")
        for file_path in unsupported_files[:5]:
            print(f"  - {file_path}")
        if len(unsupported_files) > 5:
            print(f"  ... and {len(unsupported_files) - 5} more")

        print(f"\nSupported extensions: {', '.join(SUPPORTED_EXTENSIONS)}")
        raise ValidationError("Unsupported file types found")


def load_documents_from_paths(file_paths: List[str]) -> List[Document]:
    """
    Load specific documents from file paths.

    Args:
        file_paths: List of file paths to load

    Returns:
        List of loaded documents
    """
    documents = []

    for file_path in file_paths:
        try:
            reader = SimpleDirectoryReader(input_files=[file_path])
            file_docs = reader.load_data()
            documents.extend(file_docs)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            continue

    # exclude metadata from embedding
    exclusion_keys = [
        "file_path",
        "file_size",
        "creation_date",
        "last_modified_date",
    ]

    for doc in documents:
        doc.excluded_llm_metadata_keys = exclusion_keys
        doc.excluded_embed_metadata_keys = exclusion_keys

    logger.info(f"Loaded {len(documents)} document(s) from {len(file_paths)} file(s)")
    return documents


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


async def process_documents_with_extractors(
    documents: List[Document], config: QuizardConfig
) -> Sequence[BaseNode]:
    """
    Process documents with concept and question seed extractors.

    Args:
        documents: Documents to process
        config: Configuration with extraction parameters

    Returns:
        Processed nodes with metadata
    """
    transformations = [
        SentenceSplitter(chunk_size=config.chunk_size),
        ConceptExtractor(max_concepts=config.max_concepts, num_workers=config.num_workers),
        QuestionSeedExtractor(
            seeds_per_concept=config.seeds_per_concept, num_workers=config.num_workers
        ),
    ]

    pipeline = IngestionPipeline(transformations=transformations)
    nodes = await pipeline.arun(documents=documents, show_progress=False)

    logger.info(f"Generated {len(nodes)} node(s) with metadata")
    return nodes


async def build_and_persist_index(
    nodes: Sequence[BaseNode],
    storage_path: str,
    existing_index: Optional[VectorStoreIndex] = None,
) -> VectorStoreIndex:
    """
    Build vector index and persist to storage.

    Args:
        nodes: Nodes to index
        storage_path: Path to persist storage
        existing_index: Existing index to update (for incremental indexing)

    Returns:
        Created or updated vector store index
    """
    if existing_index is not None:
        # incremental update: add nodes to existing index
        for node in nodes:
            existing_index.insert_nodes([node])

        # persist updated index
        existing_index.storage_context.persist(persist_dir=storage_path)
        logger.info(f"Updated existing index with {len(nodes)} new nodes")
        return existing_index
    else:
        # create new index
        doc_store = SimpleDocumentStore()
        vec_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(
            docstore=doc_store,
            vector_store=vec_store,
        )

        index = VectorStoreIndex(nodes, storage_context=storage_context)
        storage_context.persist(persist_dir=storage_path)
        logger.info(f"Created new index with {len(nodes)} nodes")
        return index


def load_existing_index(storage_path: str) -> VectorStoreIndex:
    """
    Load existing index from storage.

    Args:
        storage_path: Path to stored index

    Returns:
        Loaded vector store index

    Raises:
        FileNotFoundError: If storage path doesn't exist
    """
    if not os.path.exists(storage_path):
        raise FileNotFoundError(f"Storage path '{storage_path}' does not exist")

    storage_context = StorageContext.from_defaults(persist_dir=storage_path)
    index = load_index_from_storage(storage_context)
    logger.info(f"Loaded existing index from {storage_path}")

    return index  # type: ignore


def confirm_destructive_operation(message: str) -> bool:
    """
    Ask user for confirmation before destructive operations.

    Args:
        message: Warning message to display

    Returns:
        True if user confirms, False otherwise
    """
    print(f"\nWarning: {message}")
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    return response == "yes"


def update_manifest_with_nodes(
    manifest: IndexManifest, all_files: List[str], nodes: Sequence[BaseNode]
):
    """
    Update manifest with indexed files and node counts.

    Args:
        manifest: IndexManifest to update
        all_files: List of all file paths
        nodes: Processed nodes
    """
    for file_path in all_files:
        # find nodes for this file (match by filename in metadata)
        file_nodes = []
        filename = Path(file_path).name

        for node in nodes:
            node_filename = None
            if hasattr(node, "metadata") and "file_name" in node.metadata:
                node_filename = node.metadata["file_name"]
            elif hasattr(node, "metadata") and "file_path" in node.metadata:
                node_filename = Path(node.metadata["file_path"]).name

            if node_filename == filename:
                file_nodes.append(node)

        # get document IDs for this file
        doc_ids = list(
            set(
                getattr(node, "ref_doc_id", "")
                for node in file_nodes
                if hasattr(node, "ref_doc_id")
            )
        )
        doc_ids = [doc_id for doc_id in doc_ids if doc_id]

        manifest.add_indexed_file(file_path, doc_ids, len(file_nodes))


# command implementations


async def index_command(domain: str, config_path: Optional[str] = None):
    """
    Full rebuild index for domain.

    Args:
        domain: Domain name to index
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print(f"INDEX: Full Rebuild for Domain '{domain}'")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration for indexing")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info(
        f"Indexing configuration: LLM={config.indexing_llm_model}, Embedding={config.indexing_embedding_model}"
    )
    logger.info(f"Chunk size: {config.chunk_size}, Max concepts: {config.max_concepts}")

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

    # check if index already exists
    if os.path.exists(storage_path):
        logger.info(f"Existing index found at {storage_path}")
        if not confirm_destructive_operation(
            f"This will delete the existing index for domain '{domain}' and rebuild from scratch."
        ):
            print("Operation cancelled")
            return

        logger.info(f"Removing existing index directory: {storage_path}")
        shutil.rmtree(storage_path)
        print(f"Removed existing index at {storage_path}\n")

    # validate file types
    print("Validating file types...")
    logger.info("Validating file extensions")
    validate_file_extensions(data_path)
    logger.info("File validation passed")
    print("File validation passed\n")

    # get all files
    logger.info(f"Scanning for files in {data_path}")
    all_files = get_all_files_in_domain(data_path)
    if not all_files:
        logger.warning(f"No supported files found in {data_path}")
        print(f"No supported files found in {data_path}")
        return

    logger.info(f"Found {len(all_files)} file(s) to index")
    print(f"Found {len(all_files)} file(s) to index\n")

    # use QuizardContext for Settings management
    with QuizardContext(config):
        # load documents
        print("Loading documents...")
        documents = load_documents_from_paths(all_files)

        if not documents:
            print("No documents could be loaded")
            return

        # process with extractors
        print("\nProcessing with extractors (Concept + Question Seed)...")
        nodes = await process_documents_with_extractors(documents, config)

        # ensure storage directory exists
        domain_manager.ensure_storage_directory(domain)

        # build and persist index
        print("\nBuilding and persisting vector index...")
        await build_and_persist_index(nodes, storage_path)

        # update manifest
        print("\nUpdating index manifest...")
        manifest = IndexManifest(storage_path)
        manifest.clear()
        update_manifest_with_nodes(manifest, all_files, nodes)

        print("Index manifest updated\n")

    # show completion summary
    stats = manifest.get_stats()
    print("=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)
    print(f"Domain: {domain}")
    print(f"Files indexed: {stats['total_files']}")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Storage location: {storage_path}")
    print("=" * 80 + "\n")


async def index_update_command(domain: str, config_path: Optional[str] = None):
    """
    Incremental index: only new files.

    Args:
        domain: Domain name to update
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print(f"INDEX UPDATE: Incremental Update for Domain '{domain}'")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration for incremental update")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info("Initialising DomainManager")
    domain_manager = DomainManager(config.data_dir, config.storage_dir)

    # validate domain exists
    try:
        domain_manager.validate_or_raise(domain)
    except DomainNotFoundError as e:
        print(f"\n{e}\n")
        return

    # get paths
    data_path = domain_manager.get_data_path(domain)
    storage_path = domain_manager.get_storage_path(domain)

    # check if index exists
    if not os.path.exists(storage_path):
        print(f"No existing index found for domain '{domain}'")
        print("Use 'quizard index --domain {domain}' to create initial index")
        return

    # validate file types
    print("Validating file types...")
    validate_file_extensions(data_path)
    print("File validation passed\n")

    # load manifest and find new files
    manifest = IndexManifest(storage_path)
    all_files = get_all_files_in_domain(data_path)
    new_files = manifest.get_new_files(all_files)

    if not new_files:
        print("No new files to index")
        return

    print(f"Found {len(new_files)} new file(s) to index:")
    for file_path in new_files:
        print(f"  - {Path(file_path).name}")
    print()

    with QuizardContext(config):
        # load and process new documents
        print("Loading new documents...")
        documents = load_documents_from_paths(new_files)

        if not documents:
            print("No new documents could be loaded")
            return

        print("Processing with extractors...")
        nodes = await process_documents_with_extractors(documents, config)

        # load existing index and add new nodes
        print("Loading existing index...")
        existing_index = load_existing_index(storage_path)

        print("Adding new nodes to existing index...")
        await build_and_persist_index(nodes, storage_path, existing_index)

        # update manifest
        print("Updating index manifest...")
        update_manifest_with_nodes(manifest, new_files, nodes)

    # show completion summary
    stats = manifest.get_stats()
    print("\n" + "=" * 80)
    print("INDEX UPDATE COMPLETE")
    print("=" * 80)
    print(f"Domain: {domain}")
    print(f"New files added: {len(new_files)}")
    print(f"Total files indexed: {stats['total_files']}")
    print(f"Total nodes: {stats['total_nodes']}")
    print("=" * 80 + "\n")


async def index_refresh_command(domain: str, config_path: Optional[str] = None):
    """
    Index new + re-index modified files.

    Args:
        domain: Domain name to refresh
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print(f"INDEX REFRESH: Refresh Index for Domain '{domain}'")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration for index refresh")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info("Initialising DomainManager")
    domain_manager = DomainManager(config.data_dir, config.storage_dir)

    # validate domain exists
    try:
        domain_manager.validate_or_raise(domain)
    except DomainNotFoundError as e:
        print(f"\n{e}\n")
        return

    # get paths
    data_path = domain_manager.get_data_path(domain)
    storage_path = domain_manager.get_storage_path(domain)

    # check if index exists
    if not os.path.exists(storage_path):
        print(f"No existing index found for domain '{domain}'")
        print(f"Use 'quizard index --domain {domain}' to create initial index")
        return

    # validate file types
    print("Validating file types...")
    validate_file_extensions(data_path)
    print("File validation passed\n")

    # load manifest and find files to process
    manifest = IndexManifest(storage_path)
    all_files = get_all_files_in_domain(data_path)
    new_files = manifest.get_new_files(all_files)
    modified_files = manifest.get_modified_files(all_files)
    deleted_files = manifest.get_deleted_files(all_files)

    files_to_process = new_files + modified_files

    # report findings
    print(f"Analysis results:")
    print(f"  New files: {len(new_files)}")
    print(f"  Modified files: {len(modified_files)}")
    print(f"  Deleted files: {len(deleted_files)}")
    print(f"  Files to process: {len(files_to_process)}")
    print()

    # warn about deleted files but don't remove them
    if deleted_files:
        print("Warning: The following files are in the index but no longer exist:")
        for filename in deleted_files:
            print(f"  - {filename}")
        print("These files will remain in the index (not removed)")
        print()

    if not files_to_process:
        print("No files need processing")
        return

    # show files to process
    if new_files:
        print("New files to index:")
        for file_path in new_files:
            print(f"  + {Path(file_path).name}")

    if modified_files:
        print("Modified files to re-index:")
        for file_path in modified_files:
            print(f"  * {Path(file_path).name}")
    print()

    with QuizardContext(config):
        # load and process documents
        print("Loading documents...")
        documents = load_documents_from_paths(files_to_process)

        if not documents:
            print("No documents could be loaded")
            return

        print("Processing with extractors...")
        nodes = await process_documents_with_extractors(documents, config)

        # for modified files, we need to remove old nodes first
        if modified_files:
            print("Removing old nodes for modified files...")
            print("Note: Full rebuild required for modified files with SimpleVectorStore")

            # get all files that should remain
            remaining_files = [f for f in all_files if f not in modified_files]

            if remaining_files:
                # load documents for remaining files
                remaining_docs = load_documents_from_paths(remaining_files)
                remaining_nodes = await process_documents_with_extractors(remaining_docs, config)

                # combine with new/modified nodes
                all_nodes = list(remaining_nodes) + list(nodes)
            else:
                all_nodes = nodes

            # rebuild index completely
            if os.path.exists(storage_path):
                shutil.rmtree(storage_path)

            domain_manager.ensure_storage_directory(domain)
            await build_and_persist_index(all_nodes, storage_path)

            # rebuild manifest
            manifest.clear()
            update_manifest_with_nodes(
                manifest, [f for f in all_files if f not in deleted_files], all_nodes
            )
        else:
            # only new files, can do incremental update
            existing_index = load_existing_index(storage_path)
            await build_and_persist_index(nodes, storage_path, existing_index)

            # update manifest for new files only
            update_manifest_with_nodes(manifest, new_files, nodes)

    # show completion summary
    stats = manifest.get_stats()
    print("\n" + "=" * 80)
    print("INDEX REFRESH COMPLETE")
    print("=" * 80)
    print(f"Domain: {domain}")
    print(f"Files processed: {len(files_to_process)}")
    print(f"Total files indexed: {stats['total_files']}")
    print(f"Total nodes: {stats['total_nodes']}")
    print("=" * 80 + "\n")


async def index_all_command(config_path: Optional[str] = None):
    """
    Index all domains sequentially.

    Args:
        config_path: Optional path to YAML configuration file
    """
    print("\n" + "=" * 80)
    print("INDEX ALL: Indexing All Domains")
    print("=" * 80 + "\n")

    # load configuration
    logger.info("Loading configuration for index-all")
    if config_path:
        logger.info(f"Using configuration file: {config_path}")
        config = QuizardConfig.from_yaml(config_path)
    else:
        logger.info("Using default configuration")
        config = QuizardConfig()

    logger.info("Initialising DomainManager")
    domain_manager = DomainManager(config.data_dir, config.storage_dir)
    domains = domain_manager.list_available_domains()
    logger.info(f"Found {len(domains)} domains to index")

    if not domains:
        logger.warning("No domains found to index")
        print("No domains found to index")
        return

    print(f"Found {len(domains)} domain(s) to index:")
    for domain in domains:
        print(f"  - {domain}")
    print()

    if not confirm_destructive_operation(
        "This will rebuild indexes for ALL domains. Existing indexes will be deleted."
    ):
        print("Operation cancelled")
        return

    successful = 0
    failed = 0

    for i, domain in enumerate(domains, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing domain {i}/{len(domains)}: {domain}")
        print(f"{'=' * 60}")

        try:
            await index_command(domain, config_path)
            successful += 1
            print(f"✓ Successfully indexed domain '{domain}'")
        except Exception as e:
            failed += 1
            print(f"✗ Failed to index domain '{domain}': {e}")
            logger.exception(f"Failed to index domain '{domain}'")

    print("\n" + "=" * 80)
    print("INDEX ALL COMPLETE")
    print("=" * 80)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(domains)}")
    print("=" * 80 + "\n")
