"""
Command router and registry system for the DevKnife toolkit.

This module provides the core routing functionality that directs commands
to appropriate utility modules and manages the registry of available utilities.
"""

from typing import Dict, List, Optional, Type, Any
import importlib
import pkgutil
from pathlib import Path

from .interfaces import UtilityModule
from .models import Command, InputData, ProcessingResult


class CommandRegistry:
    """
    Registry for managing available utility modules in the DevKnife system.

    This class maintains a registry of all available utility modules and provides
    methods for registering, discovering, and retrieving utilities.
    """

    def __init__(self):
        """Initialize the command registry."""
        self._utilities: Dict[str, Type[UtilityModule]] = {}
        self._commands: Dict[str, Command] = {}
        self._categories: Dict[str, List[str]] = {}

    def register_utility(self, utility_class: Type[UtilityModule]) -> None:
        """
        Register a utility module in the registry.

        Args:
            utility_class: The utility module class to register

        Raises:
            ValueError: If the utility class is invalid or already registered
        """
        if not issubclass(utility_class, UtilityModule):
            raise ValueError(f"Utility class must inherit from UtilityModule")

        # Create an instance to get command info
        try:
            instance = utility_class()
            command_info = instance.get_command_info()
        except Exception as e:
            raise ValueError(f"Failed to get command info from utility: {e}")

        command_name = command_info.name

        if command_name in self._utilities:
            raise ValueError(f"Utility '{command_name}' is already registered")

        # Register the utility
        self._utilities[command_name] = utility_class
        self._commands[command_name] = command_info

        # Update categories
        category = command_info.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(command_name)

    def unregister_utility(self, command_name: str) -> None:
        """
        Unregister a utility module from the registry.

        Args:
            command_name: Name of the command to unregister
        """
        if command_name in self._utilities:
            command_info = self._commands[command_name]
            category = command_info.category

            # Remove from utilities and commands
            del self._utilities[command_name]
            del self._commands[command_name]

            # Remove from categories
            if category in self._categories:
                self._categories[category].remove(command_name)
                if not self._categories[category]:
                    del self._categories[category]

    def get_utility_class(self, command_name: str) -> Optional[Type[UtilityModule]]:
        """
        Get the utility class for a given command name.

        Args:
            command_name: Name of the command

        Returns:
            Utility class if found, None otherwise
        """
        return self._utilities.get(command_name)

    def get_command_info(self, command_name: str) -> Optional[Command]:
        """
        Get command information for a given command name.

        Args:
            command_name: Name of the command

        Returns:
            Command information if found, None otherwise
        """
        return self._commands.get(command_name)

    def list_commands(
        self,
        category: Optional[str] = None,
        cli_only: bool = False,
        tui_only: bool = False,
    ) -> List[str]:
        """
        List available commands, optionally filtered by category or interface.

        Args:
            category: Filter by category (optional)
            cli_only: Only return CLI-enabled commands
            tui_only: Only return TUI-enabled commands

        Returns:
            List of command names
        """
        commands = []

        for command_name, command_info in self._commands.items():
            # Filter by category
            if category and command_info.category != category:
                continue

            # Filter by interface
            if cli_only and not command_info.cli_enabled:
                continue
            if tui_only and not command_info.tui_enabled:
                continue

            commands.append(command_name)

        return sorted(commands)

    def list_categories(self) -> List[str]:
        """
        List all available categories.

        Returns:
            List of category names
        """
        return sorted(self._categories.keys())

    def get_commands_by_category(self, category: str) -> List[str]:
        """
        Get all commands in a specific category.

        Args:
            category: Category name

        Returns:
            List of command names in the category
        """
        return sorted(self._categories.get(category, []))

    def discover_utilities(self, package_path: str) -> int:
        """
        Automatically discover and register utility modules from a package.

        Args:
            package_path: Python package path to search for utilities

        Returns:
            Number of utilities discovered and registered
        """
        discovered_count = 0

        try:
            package = importlib.import_module(package_path)
            package_dir = Path(package.__file__).parent

            # Walk through all modules in the package
            for importer, modname, ispkg in pkgutil.iter_modules([str(package_dir)]):
                if ispkg:
                    continue

                try:
                    module_path = f"{package_path}.{modname}"
                    module = importlib.import_module(module_path)

                    # Look for classes that inherit from UtilityModule
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        if (
                            isinstance(attr, type)
                            and issubclass(attr, UtilityModule)
                            and attr != UtilityModule
                        ):

                            try:
                                self.register_utility(attr)
                                discovered_count += 1
                            except ValueError:
                                # Skip utilities that can't be registered
                                pass

                except ImportError:
                    # Skip modules that can't be imported
                    pass

        except ImportError:
            # Package doesn't exist or can't be imported
            pass

        return discovered_count


class CommandRouter:
    """
    Routes commands to appropriate utility modules and handles command execution.

    This class serves as the central dispatcher for all commands in the DevKnife system,
    providing validation, routing, and execution capabilities.
    """

    def __init__(self, registry: Optional[CommandRegistry] = None):
        """
        Initialize the command router.

        Args:
            registry: Command registry to use (creates new one if None)
        """
        self.registry = registry or CommandRegistry()
        self._utility_instances: Dict[str, UtilityModule] = {}

    def route_command(
        self,
        command_name: str,
        input_data: InputData,
        options: Optional[Dict[str, Any]] = None,
    ) -> ProcessingResult:
        """
        Route a command to the appropriate utility module and execute it.

        Args:
            command_name: Name of the command to execute
            input_data: Input data to process
            options: Optional parameters for the command

        Returns:
            ProcessingResult containing the execution result
        """
        if options is None:
            options = {}

        # Validate command exists
        if not self.is_valid_command(command_name):
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Unknown command: '{command_name}'. Use 'help' to see available commands.",
            )

        # Get utility instance
        utility = self._get_utility_instance(command_name)
        if not utility:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to load utility for command: '{command_name}'",
            )

        # Validate input
        try:
            if not utility.validate_input(input_data):
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Invalid input for command '{command_name}'. Use 'help {command_name}' for usage information.",
                )
        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Input validation failed for command '{command_name}': {str(e)}",
            )

        # Execute the command
        try:
            result = utility.process(input_data, options)
            return result
        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Command execution failed for '{command_name}': {str(e)}",
            )

    def is_valid_command(self, command_name: str) -> bool:
        """
        Check if a command name is valid and registered.

        Args:
            command_name: Name of the command to check

        Returns:
            True if command is valid, False otherwise
        """
        return command_name in self.registry._commands

    def get_command_help(self, command_name: str) -> Optional[str]:
        """
        Get help text for a specific command.

        Args:
            command_name: Name of the command

        Returns:
            Help text if command exists, None otherwise
        """
        if not self.is_valid_command(command_name):
            return None

        utility = self._get_utility_instance(command_name)
        if not utility:
            return None

        try:
            return utility.get_help()
        except Exception:
            return f"Help not available for command '{command_name}'"

    def get_general_help(self) -> str:
        """
        Generate general help text showing all available commands.

        Returns:
            Formatted help text
        """
        help_lines = [
            "DevKnife - Developer Utility Toolkit",
            "=" * 40,
            "",
            "Available commands by category:",
            "",
        ]

        categories = self.registry.list_categories()

        for category in categories:
            help_lines.append(f"{category.upper()}:")
            commands = self.registry.get_commands_by_category(category)

            for command_name in commands:
                command_info = self.registry.get_command_info(command_name)
                if command_info:
                    help_lines.append(
                        f"  {command_name:<15} - {command_info.description}"
                    )

            help_lines.append("")

        help_lines.extend(
            [
                "Usage:",
                "  devknife <command> [options] [input]",
                "  devknife help <command>  - Get help for specific command",
                "  devknife                 - Start TUI interface",
                "",
            ]
        )

        return "\n".join(help_lines)

    def validate_command_options(
        self, command_name: str, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Validate options for a specific command.

        Args:
            command_name: Name of the command
            options: Options to validate

        Returns:
            ProcessingResult indicating validation success/failure
        """
        if not self.is_valid_command(command_name):
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Unknown command: '{command_name}'",
            )

        utility = self._get_utility_instance(command_name)
        if not utility:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to load utility for command: '{command_name}'",
            )

        # Get supported options
        supported_options = utility.get_supported_options()

        # Check for unsupported options
        unsupported = [opt for opt in options.keys() if opt not in supported_options]

        if unsupported:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Unsupported options for command '{command_name}': {', '.join(unsupported)}",
            )

        return ProcessingResult(success=True, output=None)

    def _get_utility_instance(self, command_name: str) -> Optional[UtilityModule]:
        """
        Get or create a utility instance for the given command.

        Args:
            command_name: Name of the command

        Returns:
            Utility instance if available, None otherwise
        """
        # Return cached instance if available
        if command_name in self._utility_instances:
            return self._utility_instances[command_name]

        # Get utility class from registry
        utility_class = self.registry.get_utility_class(command_name)
        if not utility_class:
            return None

        # Create and cache instance
        try:
            instance = utility_class()
            self._utility_instances[command_name] = instance
            return instance
        except Exception:
            return None

    def clear_cache(self) -> None:
        """Clear the utility instance cache."""
        self._utility_instances.clear()

    def get_command_examples(self, command_name: str) -> List[str]:
        """
        Get usage examples for a specific command.

        Args:
            command_name: Name of the command

        Returns:
            List of example usage strings
        """
        if not self.is_valid_command(command_name):
            return []

        utility = self._get_utility_instance(command_name)
        if not utility:
            return []

        try:
            return utility.get_examples()
        except Exception:
            return []


# Global registry instance for easy access
_global_registry = CommandRegistry()
_global_router = CommandRouter(_global_registry)


def get_global_registry() -> CommandRegistry:
    """Get the global command registry instance."""
    return _global_registry


def get_global_router() -> CommandRouter:
    """Get the global command router instance."""
    return _global_router


def register_utility(utility_class: Type[UtilityModule]) -> None:
    """
    Register a utility in the global registry.

    Args:
        utility_class: The utility class to register
    """
    _global_registry.register_utility(utility_class)


def discover_utilities(package_path: str) -> int:
    """
    Discover utilities in the global registry.

    Args:
        package_path: Package path to search

    Returns:
        Number of utilities discovered
    """
    return _global_registry.discover_utilities(package_path)
