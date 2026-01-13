"""
Core module containing interfaces, data models, and base classes.
"""

from .interfaces import UtilityModule
from .models import Command, InputData, ProcessingResult, Config, InputSource
from .io_handler import InputHandler, OutputFormatter, ErrorHandler, OutputFormat
from .router import (
    CommandRegistry,
    CommandRouter,
    get_global_registry,
    get_global_router,
    register_utility,
    discover_utilities,
)
from .config_manager import ConfigManager, get_global_config_manager, get_global_config
from .error_handling import (
    UnifiedErrorHandler,
    CLIErrorHandler,
    TUIErrorHandler,
    get_cli_error_handler,
    get_tui_error_handler,
    ErrorSeverity,
    ErrorContext,
)

__all__ = [
    "UtilityModule",
    "Command",
    "InputData",
    "ProcessingResult",
    "Config",
    "InputSource",
    "InputHandler",
    "OutputFormatter",
    "ErrorHandler",
    "OutputFormat",
    "CommandRegistry",
    "CommandRouter",
    "get_global_registry",
    "get_global_router",
    "register_utility",
    "discover_utilities",
    # Configuration
    "ConfigManager",
    "get_global_config_manager",
    "get_global_config",
    # Error Handling
    "UnifiedErrorHandler",
    "CLIErrorHandler",
    "TUIErrorHandler",
    "get_cli_error_handler",
    "get_tui_error_handler",
    "ErrorSeverity",
    "ErrorContext",
]
