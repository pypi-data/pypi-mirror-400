"""
Unified error handling system for DevKnife CLI and TUI interfaces.
"""

import sys
import traceback
from typing import Optional, List, Union, Callable
from enum import Enum

from .models import ProcessingResult


class ErrorSeverity(Enum):
    """Error severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorContext(Enum):
    """Error context types."""

    CLI = "cli"
    TUI = "tui"
    CORE = "core"
    UTILITY = "utility"
    IO = "io"
    CONFIG = "config"


class UnifiedErrorHandler:
    """
    Unified error handler for both CLI and TUI interfaces.
    """

    def __init__(self, context: ErrorContext = ErrorContext.CORE):
        """
        Initialize the error handler.

        Args:
            context: The context where errors are being handled
        """
        self.context = context
        self.error_callbacks: List[Callable] = []

    def add_error_callback(self, callback: Callable) -> None:
        """
        Add a callback function to be called when errors occur.

        Args:
            callback: Function to call with error information
        """
        self.error_callbacks.append(callback)

    def handle_exception(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        user_message: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        show_traceback: bool = False,
    ) -> ProcessingResult:
        """
        Handle an exception and return a ProcessingResult.

        Args:
            error: The exception that occurred
            severity: Severity level of the error
            user_message: Custom user-friendly message
            suggestions: List of suggestions for fixing the error
            show_traceback: Whether to include traceback in error details

        Returns:
            ProcessingResult with error information
        """
        # Generate user-friendly message if not provided
        if user_message is None:
            user_message = self._generate_user_message(error)

        # Generate suggestions if not provided
        if suggestions is None:
            suggestions = self._generate_suggestions(error)

        # Create error details
        error_details = str(error)
        if show_traceback:
            error_details += f"\n\nTraceback:\n{traceback.format_exc()}"

        # Create ProcessingResult
        result = ProcessingResult(
            success=False,
            output=None,
            error_message=user_message,
            warnings=[],
            metadata={
                "error_type": type(error).__name__,
                "error_details": error_details,
                "severity": severity.value,
                "context": self.context.value,
                "suggestions": suggestions,
            },
        )

        # Call error callbacks
        for callback in self.error_callbacks:
            try:
                callback(error, result)
            except Exception:
                # Don't let callback errors break error handling
                pass

        return result

    def _generate_user_message(self, error: Exception) -> str:
        """
        Generate a user-friendly error message.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_str = str(error)

        # Common error patterns and their user-friendly messages
        if isinstance(error, FileNotFoundError):
            return f"파일을 찾을 수 없습니다: {error_str}"
        elif isinstance(error, PermissionError):
            return f"파일 접근 권한이 없습니다: {error_str}"
        elif isinstance(error, UnicodeDecodeError):
            return f"파일 인코딩 오류: {error_str}"
        elif isinstance(error, ValueError):
            if "invalid" in error_str.lower():
                return f"잘못된 입력 값: {error_str}"
            else:
                return f"값 오류: {error_str}"
        elif isinstance(error, KeyError):
            return f"필수 정보가 누락되었습니다: {error_str}"
        elif isinstance(error, ImportError):
            return f"필요한 모듈을 찾을 수 없습니다: {error_str}"
        elif isinstance(error, ConnectionError):
            return f"연결 오류: {error_str}"
        elif isinstance(error, TimeoutError):
            return f"시간 초과: {error_str}"
        else:
            return f"{error_type}: {error_str}"

    def _generate_suggestions(self, error: Exception) -> List[str]:
        """
        Generate suggestions for fixing the error.

        Args:
            error: The exception that occurred

        Returns:
            List of suggestions
        """
        suggestions = []

        if isinstance(error, FileNotFoundError):
            suggestions.extend(
                [
                    "파일 경로가 올바른지 확인하세요",
                    "파일이 존재하는지 확인하세요",
                    "상대 경로 대신 절대 경로를 사용해보세요",
                ]
            )
        elif isinstance(error, PermissionError):
            suggestions.extend(
                [
                    "파일 권한을 확인하세요",
                    "관리자 권한으로 실행해보세요",
                    "파일이 다른 프로그램에서 사용 중인지 확인하세요",
                ]
            )
        elif isinstance(error, UnicodeDecodeError):
            suggestions.extend(
                [
                    "파일 인코딩을 확인하세요 (UTF-8 권장)",
                    "다른 인코딩으로 시도해보세요",
                    "파일이 텍스트 파일인지 확인하세요",
                ]
            )
        elif isinstance(error, ValueError):
            suggestions.extend(
                [
                    "입력 형식을 확인하세요",
                    "예제를 참고하여 올바른 형식으로 입력하세요",
                    "도움말을 확인하세요",
                ]
            )
        elif isinstance(error, ImportError):
            suggestions.extend(
                [
                    "필요한 패키지가 설치되어 있는지 확인하세요",
                    "pip install 명령으로 누락된 패키지를 설치하세요",
                    "가상환경이 활성화되어 있는지 확인하세요",
                ]
            )
        else:
            suggestions.extend(
                [
                    "입력 데이터를 확인하세요",
                    "도움말을 참고하세요",
                    "다른 방법으로 시도해보세요",
                ]
            )

        return suggestions

    def format_error_for_cli(self, result: ProcessingResult) -> str:
        """
        Format error message for CLI display.

        Args:
            result: ProcessingResult with error information

        Returns:
            Formatted error message for CLI
        """
        message = f"오류: {result.error_message}"

        if result.metadata and "suggestions" in result.metadata:
            suggestions = result.metadata["suggestions"]
            if suggestions:
                message += "\n\n제안사항:"
                for i, suggestion in enumerate(suggestions, 1):
                    message += f"\n  {i}. {suggestion}"

        return message

    def format_error_for_tui(self, result: ProcessingResult) -> dict:
        """
        Format error information for TUI display.

        Args:
            result: ProcessingResult with error information

        Returns:
            Dictionary with formatted error information for TUI
        """
        return {
            "title": "오류 발생",
            "message": result.error_message,
            "suggestions": (
                result.metadata.get("suggestions", []) if result.metadata else []
            ),
            "severity": (
                result.metadata.get("severity", "error") if result.metadata else "error"
            ),
            "details": (
                result.metadata.get("error_details", "") if result.metadata else ""
            ),
        }


class CLIErrorHandler(UnifiedErrorHandler):
    """Error handler specifically for CLI interface."""

    def __init__(self):
        super().__init__(ErrorContext.CLI)

    def handle_and_exit(
        self, error: Exception, exit_code: int = 1, show_traceback: bool = False
    ) -> None:
        """
        Handle error and exit the program.

        Args:
            error: The exception that occurred
            exit_code: Exit code to use
            show_traceback: Whether to show traceback
        """
        result = self.handle_exception(error, show_traceback=show_traceback)
        error_message = self.format_error_for_cli(result)

        print(error_message, file=sys.stderr)
        sys.exit(exit_code)


class TUIErrorHandler(UnifiedErrorHandler):
    """Error handler specifically for TUI interface."""

    def __init__(self):
        super().__init__(ErrorContext.TUI)

    def handle_for_notification(self, error: Exception) -> dict:
        """
        Handle error and return notification data.

        Args:
            error: The exception that occurred

        Returns:
            Dictionary with notification data
        """
        result = self.handle_exception(error)
        return self.format_error_for_tui(result)


# Global error handlers
_cli_error_handler: Optional[CLIErrorHandler] = None
_tui_error_handler: Optional[TUIErrorHandler] = None


def get_cli_error_handler() -> CLIErrorHandler:
    """
    Get the global CLI error handler.

    Returns:
        Global CLIErrorHandler instance
    """
    global _cli_error_handler
    if _cli_error_handler is None:
        _cli_error_handler = CLIErrorHandler()
    return _cli_error_handler


def get_tui_error_handler() -> TUIErrorHandler:
    """
    Get the global TUI error handler.

    Returns:
        Global TUIErrorHandler instance
    """
    global _tui_error_handler
    if _tui_error_handler is None:
        _tui_error_handler = TUIErrorHandler()
    return _tui_error_handler
