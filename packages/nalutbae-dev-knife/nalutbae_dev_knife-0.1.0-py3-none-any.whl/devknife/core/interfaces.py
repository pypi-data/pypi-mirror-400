"""
Core interfaces and abstract base classes for the DevKnife system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .models import InputData, ProcessingResult


class UtilityModule(ABC):
    """
    Abstract base class for all utility modules in the DevKnife system.

    Each utility module must implement this interface to be compatible
    with both CLI and TUI interfaces.
    """

    @abstractmethod
    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process the input data with given options and return the result.

        Args:
            input_data: The input data to process
            options: Dictionary of options/parameters for processing

        Returns:
            ProcessingResult containing the output and metadata
        """
        pass

    @abstractmethod
    def get_help(self) -> str:
        """
        Get help text for this utility module.

        Returns:
            String containing usage instructions and examples
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate if the input data is suitable for this utility.

        Args:
            input_data: The input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_command_info(self) -> "Command":
        """
        Get command information for this utility module.

        Returns:
            Command object with metadata about this utility
        """
        pass

    def get_supported_options(self) -> List[str]:
        """
        Get list of supported options for this utility.

        Returns:
            List of option names supported by this utility
        """
        return []

    def get_examples(self) -> List[str]:
        """
        Get usage examples for this utility.

        Returns:
            List of example usage strings
        """
        return []
