"""Command registry and discovery system for the CLI.

Provides the plugin-like command system that automatically discovers
and registers available CLI sub-commands.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional


@dataclass
class CommandSpec:
    """Specification for a CLI sub-command containing metadata and registration logic.
    
    This dataclass defines the structure for CLI commands, holding the command name,
    help text, and either a registration function (for simple commands) or a
    subcommand setup function (for command groups with subcommands).
    """

    name: str
    help: str
    register: Optional[Callable[[argparse._SubParsersAction], None]] = None
    subcommand_setup: Optional[Callable[[argparse._SubParsersAction], None]] = None


# Global command registry for dynamic registration
_REGISTERED_COMMANDS: List[CommandSpec] = []
_BUILTIN_LOADED = False


def register_command(spec: CommandSpec) -> None:
    """Register a command spec dynamically."""
    _REGISTERED_COMMANDS.append(spec)


def _load_builtin_commands() -> List[CommandSpec]:
    """Import and return all built-in command specifications.
    
    This function dynamically imports command modules and collects their
    CommandSpec objects for registration with the CLI system.
    """
    global _BUILTIN_LOADED
    
    from .login import LOGIN_COMMAND
    from .catalogs import CATALOGS_COMMAND
    from .logout import LOGOUT_COMMAND
    from .set_catalog_context import SET_CATALOG_CONTEXT_COMMAND
    
    # Register command group modules only once
    if not _BUILTIN_LOADED:
        from .external_providers import register_external_provider_commands
        from .import_jobs import register_import_job_commands
        from .benchmarks import register_benchmark_commands
        
        register_external_provider_commands()
        register_import_job_commands()
        register_benchmark_commands()
        _BUILTIN_LOADED = True

    return [LOGIN_COMMAND, CATALOGS_COMMAND, LOGOUT_COMMAND, SET_CATALOG_CONTEXT_COMMAND]


def iter_commands() -> Iterable[CommandSpec]:
    """Iterate through all available CLI commands.
    
    Yields CommandSpec objects for each registered command, providing
    a centralized way to access all available CLI functionality.
    """

    yield from _load_builtin_commands()
    yield from _REGISTERED_COMMANDS


def get_command(name: str) -> Optional[CommandSpec]:
    """Retrieve a specific command by name.
    
    Searches through all registered commands and returns the CommandSpec
    matching the provided name, or None if no command is found.
    """
    for command in iter_commands():
        if command.name == name:
            return command
    return None


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register all commands with the argparse subparser system.
    
    Iterates through available commands and calls their register function
    to configure argparse with the appropriate sub-commands and options.
    """
    for command in iter_commands():
        if command.register:
            command.register(subparsers)
        elif command.subcommand_setup:
            # Command group with subcommands
            parser = subparsers.add_parser(command.name, help=command.help)
            group_subparsers = parser.add_subparsers(dest="subcommand", required=True)
            command.subcommand_setup(group_subparsers)

