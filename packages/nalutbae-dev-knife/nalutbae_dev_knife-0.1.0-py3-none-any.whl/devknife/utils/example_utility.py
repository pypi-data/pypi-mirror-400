"""
Example utility module for testing the command router and registry system.
"""

from typing import Any, Dict, List
from devknife.core import UtilityModule, Command, InputData, ProcessingResult


class ExampleUtility(UtilityModule):
    """
    Example utility that echoes input with optional prefix.
    Used for testing the command router and registry system.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by echoing it with optional prefix.

        Args:
            input_data: Input data to echo
            options: Processing options (prefix)

        Returns:
            ProcessingResult with echoed content
        """
        try:
            content = input_data.as_string().strip()
            prefix = options.get("prefix", "Echo: ")

            output = f"{prefix}{content}"

            return ProcessingResult(
                success=True,
                output=output,
                metadata={
                    "original_length": len(content),
                    "output_length": len(output),
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process input: {str(e)}",
            )

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Example Echo Utility

DESCRIPTION:
    Echoes the input text with an optional prefix.

USAGE:
    devknife echo [options] <text>
    echo "text" | devknife echo [options]

OPTIONS:
    --prefix <text>    Prefix to add before the echoed text (default: "Echo: ")

EXAMPLES:
    devknife echo "Hello World"
    devknife echo --prefix "Output: " "Hello World"
    echo "Hello World" | devknife echo
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid
        """
        try:
            content = input_data.as_string()
            return len(content.strip()) > 0
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="echo",
            description="Echo input text with optional prefix",
            category="example",
            module="devknife.utils.example_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["prefix"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife echo "Hello World"',
            'devknife echo --prefix "Output: " "Hello World"',
            'echo "Hello World" | devknife echo',
        ]
