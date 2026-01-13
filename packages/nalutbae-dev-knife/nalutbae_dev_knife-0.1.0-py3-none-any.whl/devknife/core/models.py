"""
Core data models for the DevKnife system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class InputSource(Enum):
    """Enumeration of possible input sources."""

    ARGS = "args"
    STDIN = "stdin"
    FILE = "file"


@dataclass
class Command:
    """
    Represents a command that can be executed in the DevKnife system.
    """

    name: str
    description: str
    category: str
    module: str
    cli_enabled: bool = True
    tui_enabled: bool = True

    def __post_init__(self):
        """Validate command data after initialization."""
        if not self.name:
            raise ValueError("Command name cannot be empty")
        if not self.description:
            raise ValueError("Command description cannot be empty")
        if not self.category:
            raise ValueError("Command category cannot be empty")
        if not self.module:
            raise ValueError("Command module cannot be empty")


@dataclass
class InputData:
    """
    Represents input data from various sources.
    """

    content: Union[str, bytes]
    source: InputSource
    encoding: str = "utf-8"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate input data after initialization."""
        if self.content is None:
            raise ValueError("Content cannot be None")
        if not isinstance(self.source, InputSource):
            raise ValueError("Source must be an InputSource enum value")
        if not self.encoding:
            raise ValueError("Encoding cannot be empty")

    def as_string(self) -> str:
        """
        Convert content to string using the specified encoding.

        Returns:
            String representation of the content
        """
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, bytes):
            return self.content.decode(self.encoding)
        else:
            return str(self.content)

    def as_bytes(self) -> bytes:
        """
        Convert content to bytes using the specified encoding.

        Returns:
            Bytes representation of the content
        """
        if isinstance(self.content, bytes):
            return self.content
        elif isinstance(self.content, str):
            return self.content.encode(self.encoding)
        else:
            return str(self.content).encode(self.encoding)


@dataclass
class ProcessingResult:
    """
    Represents the result of processing input data.
    """

    success: bool
    output: Any
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate processing result after initialization."""
        if not self.success and not self.error_message:
            raise ValueError("Error message is required when success is False")

    def add_warning(self, warning: str) -> None:
        """
        Add a warning message to the result.

        Args:
            warning: Warning message to add
        """
        if warning and warning not in self.warnings:
            self.warnings.append(warning)

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)


@dataclass
class Config:
    """
    Configuration settings for the DevKnife system.
    """

    default_encoding: str = "utf-8"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    output_format: str = "auto"
    tui_theme: str = "default"
    default_interface: str = "tui"  # 'cli' or 'tui'

    # Performance settings
    streaming_threshold: int = (
        10 * 1024 * 1024
    )  # 10MB - files larger than this use streaming
    chunk_size: int = 8192  # 8KB chunks for streaming
    max_memory_usage: int = 50 * 1024 * 1024  # 50MB max memory usage
    progress_update_interval: float = 0.1  # Update progress every 100ms

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.default_encoding:
            raise ValueError("Default encoding cannot be empty")
        if self.max_file_size <= 0:
            raise ValueError("Max file size must be positive")
        if not self.output_format:
            raise ValueError("Output format cannot be empty")
        if not self.tui_theme:
            raise ValueError("TUI theme cannot be empty")
        if self.default_interface not in ["cli", "tui"]:
            raise ValueError("Default interface must be 'cli' or 'tui'")
        if self.streaming_threshold <= 0:
            raise ValueError("Streaming threshold must be positive")
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if self.max_memory_usage <= 0:
            raise ValueError("Max memory usage must be positive")
        if self.progress_update_interval <= 0:
            raise ValueError("Progress update interval must be positive")

    def validate_file_size(self, size: int) -> bool:
        """
        Check if a file size is within the configured limit.

        Args:
            size: File size in bytes

        Returns:
            True if size is within limit, False otherwise
        """
        return 0 <= size <= self.max_file_size

    def should_use_streaming(self, size: int) -> bool:
        """
        Check if streaming should be used for a given data size.

        Args:
            size: Data size in bytes

        Returns:
            True if streaming should be used
        """
        return size > self.streaming_threshold
