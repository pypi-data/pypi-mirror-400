"""CLI command implementations."""

from quizard_generator.commands.generate import generate_command
from quizard_generator.commands.index import (
    index_all_command,
    index_command,
    index_refresh_command,
    index_update_command,
)
from quizard_generator.commands.list_domains import list_domains_command
from quizard_generator.commands.validate import validate_index_command

__all__ = [
    "index_command",
    "index_update_command",
    "index_refresh_command",
    "index_all_command",
    "generate_command",
    "list_domains_command",
    "validate_index_command",
]
