"""
Input/Output handling components for the DevKnife system.

This module provides classes for handling various input sources (args, stdin, files)
and formatting output in different formats.
"""

import os
import sys
import chardet
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO, Iterator
from enum import Enum

from .models import InputData, InputSource, ProcessingResult, Config
from .performance import (
    get_global_streaming_handler,
    get_global_memory_optimizer,
    progress_context,
    ProgressType,
)


class OutputFormat(Enum):
    """Supported output formats."""

    AUTO = "auto"
    PLAIN = "plain"
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"


class InputHandler:
    """
    Handles input from various sources: command line arguments, stdin, and files.

    This class provides methods to read and process input data from different sources
    while handling encoding detection and validation.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the InputHandler.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()

    def read_from_args(self, args: List[str]) -> InputData:
        """
        Read input data from command line arguments.

        Args:
            args: List of command line arguments

        Returns:
            InputData object containing the processed arguments

        Raises:
            ValueError: If args is empty or None
        """
        if not args:
            raise ValueError("No arguments provided")

        # Join all arguments with spaces to form the input content
        content = " ".join(args)

        return InputData(
            content=content,
            source=InputSource.ARGS,
            encoding=self.config.default_encoding,
            metadata={"arg_count": len(args)},
        )

    def read_from_stdin(self, stdin: Optional[TextIO] = None) -> InputData:
        """
        Read input data from stdin.

        Args:
            stdin: Optional stdin stream, uses sys.stdin if None

        Returns:
            InputData object containing the stdin content

        Raises:
            ValueError: If stdin is empty or unavailable
        """
        if stdin is None:
            stdin = sys.stdin

        # Check if stdin has data available
        if stdin.isatty():
            raise ValueError("No data available from stdin")

        try:
            content = stdin.read()
            if not content:
                raise ValueError("Empty input from stdin")

            return InputData(
                content=content,
                source=InputSource.STDIN,
                encoding=self.config.default_encoding,
                metadata={"length": len(content)},
            )
        except Exception as e:
            raise ValueError(f"Failed to read from stdin: {str(e)}")

    def read_from_file(self, file_path: Union[str, Path]) -> InputData:
        """
        Read input data from a file with streaming optimization for large files.

        Args:
            file_path: Path to the file to read

        Returns:
            InputData object containing the file content or streaming metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            ValueError: If file is too large or empty
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Check file size
        file_size = path.stat().st_size
        if not self.config.validate_file_size(file_size):
            raise ValueError(
                f"File too large: {file_size} bytes (max: {self.config.max_file_size})"
            )

        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        # Get memory optimizer to determine if streaming should be used
        memory_optimizer = get_global_memory_optimizer()
        should_stream = memory_optimizer.should_use_streaming(file_size)

        try:
            if should_stream:
                # For large files, use streaming approach
                # Store file path and metadata instead of loading content
                return InputData(
                    content=str(path),  # Store path as content for streaming
                    source=InputSource.FILE,
                    encoding=self.config.default_encoding,
                    metadata={
                        "file_path": str(path.absolute()),
                        "file_size": file_size,
                        "streaming": True,
                        "requires_streaming": True,
                    },
                )
            else:
                # For smaller files, read normally with progress indication
                with progress_context(
                    ProgressType.SPINNER, f"Reading {path.name}"
                ) as progress:
                    # Read file in binary mode first for encoding detection
                    with open(path, "rb") as f:
                        raw_content = f.read()

                    progress.update(message="Detecting encoding...")

                    # Detect encoding
                    encoding = self.detect_encoding(raw_content)

                    progress.update(message="Decoding content...")

                    # Decode content
                    content = raw_content.decode(encoding)

                    progress.finish("File loaded successfully")

                return InputData(
                    content=content,
                    source=InputSource.FILE,
                    encoding=encoding,
                    metadata={
                        "file_path": str(path.absolute()),
                        "file_size": file_size,
                        "detected_encoding": encoding,
                        "streaming": False,
                    },
                )
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode file {file_path}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}: {str(e)}")

    def detect_encoding(self, raw_data: bytes) -> str:
        """
        Detect the encoding of raw byte data.

        Args:
            raw_data: Raw byte data to analyze

        Returns:
            Detected encoding name, falls back to default encoding
        """
        if not raw_data:
            return self.config.default_encoding

        try:
            # Use chardet to detect encoding
            result = chardet.detect(raw_data)
            if result and result["encoding"] and result["confidence"] > 0.7:
                return result["encoding"]
        except Exception:
            # Fall back to default if detection fails
            pass

        return self.config.default_encoding

    def validate_encoding(self, content: Union[str, bytes], encoding: str) -> bool:
        """
        Validate that content can be properly encoded/decoded with the given encoding.

        Args:
            content: Content to validate
            encoding: Encoding to test

        Returns:
            True if encoding is valid for the content, False otherwise
        """
        try:
            if isinstance(content, str):
                # Try to encode and decode
                content.encode(encoding).decode(encoding)
            elif isinstance(content, bytes):
                # Try to decode and encode
                content.decode(encoding).encode(encoding)
            return True
        except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
            return False

    def get_streaming_content(self, input_data: InputData) -> Union[str, Iterator[str]]:
        """
        Get content from InputData, handling streaming if needed.

        Args:
            input_data: InputData object that may contain streaming metadata

        Returns:
            Content string for small data, or iterator for streaming data
        """
        if input_data.metadata.get("streaming", False):
            # This is streaming data, return iterator
            streaming_handler = get_global_streaming_handler()
            file_path = input_data.metadata.get("file_path", input_data.content)
            return streaming_handler.stream_file_lines(file_path, input_data.encoding)
        else:
            # Regular data, return as string
            return input_data.as_string()

    def is_streaming_data(self, input_data: InputData) -> bool:
        """
        Check if InputData requires streaming processing.

        Args:
            input_data: InputData object to check

        Returns:
            True if data should be processed in streaming mode
        """
        return input_data.metadata.get("streaming", False)


class OutputFormatter:
    """
    Formats output data in various formats for display or further processing.

    This class provides methods to format data in different output formats
    such as plain text, JSON, YAML, and tables.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the OutputFormatter.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()

    def format_output(
        self, data: Any, format_type: Union[str, OutputFormat] = OutputFormat.AUTO
    ) -> str:
        """
        Format data according to the specified format type.

        Args:
            data: Data to format
            format_type: Output format to use

        Returns:
            Formatted string representation of the data
        """
        if isinstance(format_type, str):
            try:
                format_type = OutputFormat(format_type.lower())
            except ValueError:
                format_type = OutputFormat.AUTO

        if format_type == OutputFormat.AUTO:
            format_type = self._detect_format(data)

        if format_type == OutputFormat.JSON:
            return self._format_json(data)
        elif format_type == OutputFormat.YAML:
            return self._format_yaml(data)
        elif format_type == OutputFormat.TABLE:
            return self._format_table(data)
        else:  # PLAIN or fallback
            return self._format_plain(data)

    def _detect_format(self, data: Any) -> OutputFormat:
        """
        Automatically detect the best format for the given data.

        Args:
            data: Data to analyze

        Returns:
            Detected output format
        """
        if isinstance(data, (dict, list)):
            return OutputFormat.JSON
        elif isinstance(data, str) and (data.startswith("{") or data.startswith("[")):
            return OutputFormat.JSON
        else:
            return OutputFormat.PLAIN

    def _format_plain(self, data: Any) -> str:
        """Format data as plain text."""
        if isinstance(data, str):
            return data
        elif data is None:
            return ""
        else:
            return str(data)

    def _format_json(self, data: Any) -> str:
        """Format data as JSON."""
        import json

        try:
            if isinstance(data, str):
                # Try to parse as JSON first
                try:
                    parsed = json.loads(data)
                    return json.dumps(parsed, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    # If not JSON, wrap in quotes
                    return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        except Exception:
            return self._format_plain(data)

    def _format_yaml(self, data: Any) -> str:
        """Format data as YAML."""
        try:
            import yaml

            if isinstance(data, str):
                try:
                    # Try to parse as JSON first
                    import json

                    parsed = json.loads(data)
                    return yaml.dump(
                        parsed, default_flow_style=False, allow_unicode=True
                    )
                except json.JSONDecodeError:
                    return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            else:
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            # Fall back to JSON if YAML not available
            return self._format_json(data)
        except Exception:
            return self._format_plain(data)

    def _format_table(self, data: Any) -> str:
        """Format data as a table."""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Format list of dictionaries as table
            return self._format_dict_list_table(data)
        elif isinstance(data, dict):
            # Format dictionary as key-value table
            return self._format_dict_table(data)
        else:
            return self._format_plain(data)

    def _format_dict_list_table(self, data: List[Dict]) -> str:
        """Format a list of dictionaries as a table."""
        if not data:
            return ""

        # Get all unique keys
        keys = set()
        for item in data:
            keys.update(item.keys())
        keys = sorted(keys)

        # Calculate column widths
        widths = {}
        for key in keys:
            widths[key] = len(str(key))
            for item in data:
                value = str(item.get(key, ""))
                widths[key] = max(widths[key], len(value))

        # Build table
        lines = []

        # Header
        header = " | ".join(str(key).ljust(widths[key]) for key in keys)
        lines.append(header)

        # Separator
        separator = " | ".join("-" * widths[key] for key in keys)
        lines.append(separator)

        # Data rows
        for item in data:
            row = " | ".join(str(item.get(key, "")).ljust(widths[key]) for key in keys)
            lines.append(row)

        return "\n".join(lines)

    def _format_dict_table(self, data: Dict) -> str:
        """Format a dictionary as a key-value table."""
        if not data:
            return ""

        # Calculate column widths
        key_width = max(len(str(key)) for key in data.keys())
        value_width = max(len(str(value)) for value in data.values())

        # Build table
        lines = []

        # Header
        header = f"{'Key'.ljust(key_width)} | {'Value'.ljust(value_width)}"
        lines.append(header)

        # Separator
        separator = f"{'-' * key_width} | {'-' * value_width}"
        lines.append(separator)

        # Data rows
        for key, value in data.items():
            row = f"{str(key).ljust(key_width)} | {str(value).ljust(value_width)}"
            lines.append(row)

        return "\n".join(lines)


class ErrorHandler:
    """
    Handles errors and provides user-friendly error messages.

    This class provides methods to format and handle various types of errors
    that can occur during input processing and utility execution.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the ErrorHandler.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()

    def handle_file_error(self, error: Exception, file_path: str) -> ProcessingResult:
        """
        Handle file-related errors and return a user-friendly result.

        Args:
            error: The exception that occurred
            file_path: Path to the file that caused the error

        Returns:
            ProcessingResult with appropriate error message
        """
        if isinstance(error, FileNotFoundError):
            message = f"File not found: '{file_path}'"
            suggestions = [
                "Check if the file path is correct",
                "Ensure the file exists",
                "Use absolute path if relative path fails",
            ]
        elif isinstance(error, PermissionError):
            message = f"Permission denied accessing file: '{file_path}'"
            suggestions = [
                "Check file permissions",
                "Run with appropriate privileges",
                "Ensure file is not locked by another process",
            ]
        elif isinstance(error, ValueError) and "too large" in str(error).lower():
            message = f"File too large: '{file_path}' (max size: {self.config.max_file_size} bytes)"
            suggestions = [
                "Use a smaller file",
                "Process file in chunks",
                "Increase max_file_size in configuration",
            ]
        elif isinstance(error, UnicodeDecodeError):
            message = f"Cannot decode file '{file_path}': {str(error)}"
            suggestions = [
                "Check file encoding",
                "Try specifying a different encoding",
                "Ensure file is a text file",
            ]
        else:
            message = f"Error reading file '{file_path}': {str(error)}"
            suggestions = [
                "Check file accessibility",
                "Verify file format",
                "Try with a different file",
            ]

        return ProcessingResult(
            success=False,
            output=None,
            error_message=message,
            metadata={
                "error_type": type(error).__name__,
                "file_path": file_path,
                "suggestions": suggestions,
            },
        )

    def handle_parsing_error(
        self, error: Exception, data_type: str, position: Optional[int] = None
    ) -> ProcessingResult:
        """
        Handle data parsing errors and return a user-friendly result.

        Args:
            error: The exception that occurred
            data_type: Type of data being parsed (e.g., "JSON", "CSV", "XML")
            position: Optional position where error occurred

        Returns:
            ProcessingResult with appropriate error message
        """
        base_message = f"Failed to parse {data_type} data"

        if position is not None:
            message = f"{base_message} at position {position}: {str(error)}"
        else:
            message = f"{base_message}: {str(error)}"

        suggestions = [
            f"Check {data_type} syntax",
            "Validate data format",
            "Remove invalid characters",
            "Use a {data_type} validator tool",
        ]

        # Add specific suggestions based on data type
        if data_type.upper() == "JSON":
            suggestions.extend(
                [
                    "Check for missing quotes around strings",
                    "Ensure proper comma placement",
                    "Validate bracket/brace matching",
                ]
            )
        elif data_type.upper() == "CSV":
            suggestions.extend(
                [
                    "Check for unescaped quotes",
                    "Ensure consistent column count",
                    "Validate delimiter usage",
                ]
            )
        elif data_type.upper() == "XML":
            suggestions.extend(
                [
                    "Check for unclosed tags",
                    "Validate attribute syntax",
                    "Ensure proper nesting",
                ]
            )

        return ProcessingResult(
            success=False,
            output=None,
            error_message=message,
            metadata={
                "error_type": type(error).__name__,
                "data_type": data_type,
                "position": position,
                "suggestions": suggestions,
            },
        )

    def handle_input_error(
        self, error: Exception, input_source: str
    ) -> ProcessingResult:
        """
        Handle input-related errors and return a user-friendly result.

        Args:
            error: The exception that occurred
            input_source: Source of input that caused the error

        Returns:
            ProcessingResult with appropriate error message
        """
        if "empty" in str(error).lower():
            message = f"No input data provided from {input_source}"
            suggestions = [
                "Provide input data",
                "Check input source",
                "Use a different input method",
            ]
        elif "unavailable" in str(error).lower():
            message = f"Input source {input_source} is not available"
            suggestions = [
                "Check input source availability",
                "Use a different input method",
                "Verify system configuration",
            ]
        else:
            message = f"Error reading from {input_source}: {str(error)}"
            suggestions = [
                "Check input format",
                "Verify input source",
                "Try with different input",
            ]

        return ProcessingResult(
            success=False,
            output=None,
            error_message=message,
            metadata={
                "error_type": type(error).__name__,
                "input_source": input_source,
                "suggestions": suggestions,
            },
        )

    def handle_generic_error(
        self, error: Exception, context: str = "operation"
    ) -> ProcessingResult:
        """
        Handle generic errors and return a user-friendly result.

        Args:
            error: The exception that occurred
            context: Context where the error occurred

        Returns:
            ProcessingResult with appropriate error message
        """
        message = f"Error during {context}: {str(error)}"
        suggestions = [
            "Check input data",
            "Verify operation parameters",
            "Try with different input",
            "Contact support if issue persists",
        ]

        return ProcessingResult(
            success=False,
            output=None,
            error_message=message,
            metadata={
                "error_type": type(error).__name__,
                "context": context,
                "suggestions": suggestions,
            },
        )
