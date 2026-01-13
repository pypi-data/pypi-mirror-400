"""
Performance optimization components for the DevKnife system.

This module provides streaming I/O, progress indicators, and memory optimization
utilities for handling large files and long-running operations efficiently.
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Callable, Union, TextIO, BinaryIO
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from .models import InputData, InputSource, ProcessingResult, Config


class ProgressType(Enum):
    """Types of progress indicators."""

    SPINNER = "spinner"
    PERCENTAGE = "percentage"
    BAR = "bar"
    COUNTER = "counter"


@dataclass
class ProgressInfo:
    """Information about operation progress."""

    current: int = 0
    total: Optional[int] = None
    message: str = "Processing..."
    percentage: Optional[float] = None
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None


class ProgressIndicator:
    """
    Progress indicator for long-running operations.

    Supports different types of progress display including spinners,
    percentage bars, and counters.
    """

    SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧"]

    def __init__(
        self,
        progress_type: ProgressType = ProgressType.SPINNER,
        message: str = "Processing...",
        total: Optional[int] = None,
        show_elapsed: bool = True,
        show_eta: bool = True,
    ):
        """
        Initialize progress indicator.

        Args:
            progress_type: Type of progress indicator
            message: Message to display
            total: Total number of items (for percentage/bar types)
            show_elapsed: Whether to show elapsed time
            show_eta: Whether to show estimated time remaining
        """
        self.progress_type = progress_type
        self.message = message
        self.total = total
        self.show_elapsed = show_elapsed
        self.show_eta = show_eta

        self.current = 0
        self.start_time = None
        self.last_update = 0
        self.spinner_index = 0
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the progress indicator."""
        if self.running:
            return

        self.running = True
        self.start_time = time.time()
        self.last_update = self.start_time

        if self.progress_type == ProgressType.SPINNER:
            self.thread = threading.Thread(target=self._spinner_loop, daemon=True)
            self.thread.start()

    def update(
        self, current: Optional[int] = None, message: Optional[str] = None
    ) -> None:
        """
        Update progress information.

        Args:
            current: Current progress value
            message: Updated message
        """
        with self._lock:
            if current is not None:
                self.current = current
            if message is not None:
                self.message = message

            current_time = time.time()
            if (
                current_time - self.last_update >= 0.1
            ):  # Update at most 10 times per second
                self._display_progress()
                self.last_update = current_time

    def increment(self, amount: int = 1, message: Optional[str] = None) -> None:
        """
        Increment progress by specified amount.

        Args:
            amount: Amount to increment
            message: Updated message
        """
        self.update(self.current + amount, message)

    def finish(self, message: Optional[str] = None) -> None:
        """
        Finish the progress indicator.

        Args:
            message: Final message to display
        """
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)

        if message:
            self.message = message

        self._display_final()

    def _spinner_loop(self) -> None:
        """Main loop for spinner animation."""
        while self.running:
            with self._lock:
                self._display_spinner()
            time.sleep(0.1)

    def _display_progress(self) -> None:
        """Display current progress based on type."""
        if self.progress_type == ProgressType.PERCENTAGE and self.total:
            self._display_percentage()
        elif self.progress_type == ProgressType.BAR and self.total:
            self._display_bar()
        elif self.progress_type == ProgressType.COUNTER:
            self._display_counter()
        else:
            self._display_spinner()

    def _display_spinner(self) -> None:
        """Display spinner animation."""
        spinner_char = self.SPINNER_CHARS[self.spinner_index % len(self.SPINNER_CHARS)]
        self.spinner_index += 1

        elapsed = self._get_elapsed_time()
        time_info = f" ({elapsed})" if self.show_elapsed else ""

        sys.stderr.write(f"\r{spinner_char} {self.message}{time_info}")
        sys.stderr.flush()

    def _display_percentage(self) -> None:
        """Display percentage progress."""
        if not self.total:
            return

        percentage = (self.current / self.total) * 100
        elapsed = self._get_elapsed_time()
        eta = self._get_eta()

        time_info = ""
        if self.show_elapsed:
            time_info += f" ({elapsed}"
            if self.show_eta and eta:
                time_info += f", ETA: {eta}"
            time_info += ")"

        sys.stderr.write(
            f"\r{self.message} {percentage:.1f}% ({self.current}/{self.total}){time_info}"
        )
        sys.stderr.flush()

    def _display_bar(self) -> None:
        """Display progress bar."""
        if not self.total:
            return

        bar_width = 30
        filled = int((self.current / self.total) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        percentage = (self.current / self.total) * 100

        elapsed = self._get_elapsed_time()
        eta = self._get_eta()

        time_info = ""
        if self.show_elapsed:
            time_info += f" ({elapsed}"
            if self.show_eta and eta:
                time_info += f", ETA: {eta}"
            time_info += ")"

        sys.stderr.write(f"\r{self.message} [{bar}] {percentage:.1f}%{time_info}")
        sys.stderr.flush()

    def _display_counter(self) -> None:
        """Display counter progress."""
        elapsed = self._get_elapsed_time()
        time_info = f" ({elapsed})" if self.show_elapsed else ""

        if self.total:
            sys.stderr.write(f"\r{self.message} {self.current}/{self.total}{time_info}")
        else:
            sys.stderr.write(f"\r{self.message} {self.current}{time_info}")
        sys.stderr.flush()

    def _display_final(self) -> None:
        """Display final completion message."""
        elapsed = self._get_elapsed_time()
        time_info = f" (completed in {elapsed})" if self.show_elapsed else ""

        sys.stderr.write(f"\r{self.message}{time_info}\n")
        sys.stderr.flush()

    def _get_elapsed_time(self) -> str:
        """Get formatted elapsed time."""
        if not self.start_time:
            return "0s"

        elapsed = time.time() - self.start_time
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        elif elapsed < 3600:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            return f"{hours}h {minutes}m"

    def _get_eta(self) -> Optional[str]:
        """Get estimated time remaining."""
        if not self.start_time or not self.total or self.current == 0:
            return None

        elapsed = time.time() - self.start_time
        rate = self.current / elapsed
        remaining_items = self.total - self.current

        if rate > 0:
            eta_seconds = remaining_items / rate
            if eta_seconds < 60:
                return f"{eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                minutes = int(eta_seconds // 60)
                seconds = int(eta_seconds % 60)
                return f"{minutes}m {seconds}s"
            else:
                hours = int(eta_seconds // 3600)
                minutes = int((eta_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"

        return None


@contextmanager
def progress_context(
    progress_type: ProgressType = ProgressType.SPINNER,
    message: str = "Processing...",
    total: Optional[int] = None,
):
    """
    Context manager for progress indicators.

    Args:
        progress_type: Type of progress indicator
        message: Message to display
        total: Total number of items

    Yields:
        ProgressIndicator instance
    """
    indicator = ProgressIndicator(progress_type, message, total)
    indicator.start()
    try:
        yield indicator
    finally:
        indicator.finish()


class StreamingInputHandler:
    """
    Handles streaming input from large files to optimize memory usage.

    This class provides methods to read large files in chunks rather than
    loading everything into memory at once.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the streaming input handler.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()
        self.chunk_size = 8192  # 8KB chunks by default
        self.max_memory_usage = 50 * 1024 * 1024  # 50MB max memory usage

    def stream_file_lines(
        self, file_path: Union[str, Path], encoding: str = "utf-8"
    ) -> Iterator[str]:
        """
        Stream file content line by line.

        Args:
            file_path: Path to the file
            encoding: File encoding

        Yields:
            Individual lines from the file

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            with open(path, "r", encoding=encoding, buffering=self.chunk_size) as f:
                for line in f:
                    yield line.rstrip("\n\r")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode file {file_path}: {str(e)}")

    def stream_file_chunks(
        self,
        file_path: Union[str, Path],
        chunk_size: Optional[int] = None,
        encoding: str = "utf-8",
    ) -> Iterator[str]:
        """
        Stream file content in chunks.

        Args:
            file_path: Path to the file
            chunk_size: Size of each chunk in bytes
            encoding: File encoding

        Yields:
            Chunks of file content

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        path = Path(file_path)
        chunk_size = chunk_size or self.chunk_size

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            with open(path, "r", encoding=encoding, buffering=chunk_size) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode file {file_path}: {str(e)}")

    def process_large_file(
        self,
        file_path: Union[str, Path],
        processor: Callable[[str], Any],
        encoding: str = "utf-8",
        show_progress: bool = True,
    ) -> Iterator[Any]:
        """
        Process a large file with progress indication.

        Args:
            file_path: Path to the file
            processor: Function to process each line
            encoding: File encoding
            show_progress: Whether to show progress indicator

        Yields:
            Processed results for each line
        """
        path = Path(file_path)

        # Get file size for progress calculation
        file_size = path.stat().st_size
        total_lines = None

        # Estimate line count for better progress indication
        if show_progress and file_size > 0:
            try:
                # Quick line count estimation
                with open(path, "rb") as f:
                    sample_size = min(file_size, 1024 * 1024)  # 1MB sample
                    sample = f.read(sample_size)
                    line_count_in_sample = sample.count(b"\n")
                    if line_count_in_sample > 0:
                        total_lines = int(
                            (file_size / sample_size) * line_count_in_sample
                        )
            except Exception:
                pass

        progress_type = ProgressType.COUNTER if total_lines else ProgressType.SPINNER

        with progress_context(
            progress_type, f"Processing {path.name}", total_lines
        ) as progress:
            line_count = 0
            for line in self.stream_file_lines(file_path, encoding):
                try:
                    result = processor(line)
                    yield result
                    line_count += 1

                    if show_progress:
                        progress.update(line_count)

                except Exception as e:
                    # Continue processing other lines even if one fails
                    yield ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Error processing line {line_count + 1}: {str(e)}",
                    )
                    line_count += 1

                    if show_progress:
                        progress.update(line_count)


class MemoryOptimizer:
    """
    Memory optimization utilities for data processing operations.

    Provides methods to optimize memory usage during data transformations
    and processing operations.
    """

    def __init__(self, max_memory_mb: int = 100):
        """
        Initialize memory optimizer.

        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.chunk_size = 8192

    def get_memory_usage(self) -> int:
        """
        Get current memory usage of the process.

        Returns:
            Memory usage in bytes
        """
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback: estimate based on object sizes
            return 0

    def should_use_streaming(self, data_size: int) -> bool:
        """
        Determine if streaming should be used based on data size.

        Args:
            data_size: Size of data in bytes

        Returns:
            True if streaming should be used
        """
        return data_size > self.max_memory_bytes // 2

    def optimize_json_processing(
        self, data: Union[str, Dict, list]
    ) -> Union[str, Dict, list]:
        """
        Optimize JSON processing for large data structures.

        Args:
            data: JSON data to optimize

        Returns:
            Optimized data structure
        """
        if isinstance(data, str):
            # For large JSON strings, consider streaming parsing
            if len(data.encode("utf-8")) > self.max_memory_bytes:
                # Return as-is for now, could implement streaming JSON parser
                return data

        return data

    def optimize_csv_processing(self, content: str) -> bool:
        """
        Determine if CSV should be processed in streaming mode.

        Args:
            content: CSV content

        Returns:
            True if streaming mode should be used
        """
        content_size = len(content.encode("utf-8"))
        return self.should_use_streaming(content_size)

    def chunk_data(self, data: str, chunk_size: Optional[int] = None) -> Iterator[str]:
        """
        Split data into chunks for processing.

        Args:
            data: Data to chunk
            chunk_size: Size of each chunk

        Yields:
            Data chunks
        """
        chunk_size = chunk_size or self.chunk_size

        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    @contextmanager
    def memory_limit_context(self, limit_mb: int):
        """
        Context manager for temporary memory limit adjustment.

        Args:
            limit_mb: Memory limit in MB
        """
        old_limit = self.max_memory_bytes
        self.max_memory_bytes = limit_mb * 1024 * 1024
        try:
            yield
        finally:
            self.max_memory_bytes = old_limit


def create_optimized_input_data(
    file_path: Union[str, Path], config: Optional[Config] = None
) -> InputData:
    """
    Create InputData with streaming optimization for large files.

    Args:
        file_path: Path to the file
        config: Configuration object

    Returns:
        InputData object optimized for the file size
    """
    path = Path(file_path)
    config = config or Config()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = path.stat().st_size

    # Use config's streaming threshold
    should_stream = config.should_use_streaming(file_size)

    if not should_stream:
        # For small files, read normally
        with open(path, "r", encoding=config.default_encoding) as f:
            content = f.read()

        return InputData(
            content=content,
            source=InputSource.FILE,
            encoding=config.default_encoding,
            metadata={
                "file_path": str(path.absolute()),
                "file_size": file_size,
                "streaming": False,
            },
        )

    # For large files, use streaming approach
    return InputData(
        content=str(path),  # Store path instead of content
        source=InputSource.FILE,
        encoding=config.default_encoding,
        metadata={
            "file_path": str(path.absolute()),
            "file_size": file_size,
            "streaming": True,
            "requires_streaming": True,
        },
    )


# Global instances for easy access
_global_memory_optimizer = None
_global_streaming_handler = None


def get_global_memory_optimizer() -> MemoryOptimizer:
    """Get the global memory optimizer instance."""
    global _global_memory_optimizer
    if _global_memory_optimizer is None:
        _global_memory_optimizer = MemoryOptimizer()
    return _global_memory_optimizer


def get_global_streaming_handler() -> StreamingInputHandler:
    """Get the global streaming input handler instance."""
    global _global_streaming_handler
    if _global_streaming_handler is None:
        _global_streaming_handler = StreamingInputHandler()
    return _global_streaming_handler
