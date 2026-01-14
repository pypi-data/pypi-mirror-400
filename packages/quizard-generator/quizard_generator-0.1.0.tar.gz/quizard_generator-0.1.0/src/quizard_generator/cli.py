"""
Quizard Generator CLI - Main entry point.

Usage:
    quizard list-domains
    quizard index --domain <name>
    quizard index-update --domain <name>
    quizard index-refresh --domain <name>
    quizard index-all
    quizard generate --domain <name> [options]
    quizard validate-index --domain <name>
"""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with subcommands."""
    # create parent parser with global flags (will be inherited by all subcommands)
    # NOTE: Global flags work AFTER the subcommand (e.g., quizard list-domains --verbose)
    # This is standard CLI behaviour (like git, docker, kubectl, etc.)
    global_parser = argparse.ArgumentParser(add_help=False)
    global_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (default: quiet)",
    )
    global_parser.add_argument("--config", type=str, help="Path to YAML configuration file")

    # create main parser
    parser = argparse.ArgumentParser(
        prog="quizard",
        description="Generate multiple-choice quizzes from documents using local LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-domains command
    subparsers.add_parser(
        "list-domains",
        help="Show all available domains with statistics",
        parents=[global_parser],
    )

    # index command
    index_parser = subparsers.add_parser(
        "index", help="Full rebuild index for domain", parents=[global_parser]
    )
    index_parser.add_argument("--domain", required=True, help="Domain name")

    # index-update command
    index_update_parser = subparsers.add_parser(
        "index-update",
        help="Incremental index: only new files",
        parents=[global_parser],
    )
    index_update_parser.add_argument("--domain", required=True, help="Domain name")

    # index-refresh command
    index_refresh_parser = subparsers.add_parser(
        "index-refresh",
        help="Index new + re-index modified files",
        parents=[global_parser],
    )
    index_refresh_parser.add_argument("--domain", required=True, help="Domain name")

    # index-all command
    subparsers.add_parser(
        "index-all", help="Index all domains sequentially", parents=[global_parser]
    )

    # generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate quiz for domain", parents=[global_parser]
    )
    generate_parser.add_argument("--domain", required=True, help="Domain name")
    generate_parser.add_argument(
        "--num-questions", type=int, default=5, help="Number of questions (default: 5)"
    )
    generate_parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)",
    )
    generate_parser.add_argument(
        "--instruction", type=str, help="Natural language instruction for quiz generation"
    )

    # validate-index command
    validate_parser = subparsers.add_parser(
        "validate-index", help="Check index health for domain", parents=[global_parser]
    )
    validate_parser.add_argument("--domain", required=True, help="Domain name")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (None uses sys.argv)

    Returns:
        Exit code (0=success, 1=error, 130=interrupted)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # configure logging based on verbosity
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        # quiet mode - only show warnings and errors
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if not args.command:
        parser.print_help()
        return 1

    # import commands (lazy import to speed up --help)
    from quizard_generator.commands import (
        generate_command,
        index_all_command,
        index_command,
        index_refresh_command,
        index_update_command,
        list_domains_command,
        validate_index_command,
    )

    # route to appropriate command
    try:
        if args.command == "list-domains":
            list_domains_command(config_path=args.config)
        elif args.command == "index":
            asyncio.run(index_command(args.domain, config_path=args.config))
        elif args.command == "index-update":
            asyncio.run(index_update_command(args.domain, config_path=args.config))
        elif args.command == "index-refresh":
            asyncio.run(index_refresh_command(args.domain, config_path=args.config))
        elif args.command == "index-all":
            asyncio.run(index_all_command(config_path=args.config))
        elif args.command == "generate":
            generate_command(
                domain=args.domain,
                num_questions=args.num_questions,
                difficulty=args.difficulty,
                instruction=args.instruction,
                config_path=args.config,
            )
        elif args.command == "validate-index":
            asyncio.run(validate_index_command(args.domain, config_path=args.config))
        else:
            parser.print_help()
            return 1

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130  # standard exit code for SIGINT
    except Exception as e:
        print(f"\nError: {e}")
        logger.exception("Command failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
