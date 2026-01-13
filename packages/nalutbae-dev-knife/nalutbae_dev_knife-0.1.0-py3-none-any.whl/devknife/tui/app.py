"""
Main TUI application for the DevKnife system using Textual framework.
"""

from typing import Dict, Any, Optional, List
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    Input,
    TextArea,
    SelectionList,
    Label,
    Collapsible,
    Tabs,
    TabPane,
    ProgressBar,
)
from textual.screen import Screen
from textual.binding import Binding
from textual.message import Message
from textual import events
import asyncio
import threading

from ..core.router import get_global_router, get_global_registry
from ..core.models import InputData, InputSource, ProcessingResult
from ..core.config_manager import get_global_config_manager, get_global_config
from ..core.error_handling import get_tui_error_handler
from ..core.performance import progress_context, ProgressType


class ProgressScreen(Screen):
    """Screen for showing progress of long-running operations."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("q", "cancel", "Cancel"),
    ]

    def __init__(self, operation_name: str, **kwargs):
        super().__init__(**kwargs)
        self.operation_name = operation_name
        self.cancelled = False
        self.result = None
        self.error = None

    def compose(self) -> ComposeResult:
        """Create the progress display interface."""
        yield Header()

        with Container(id="progress-container"):
            yield Static(f"Processing: {self.operation_name}", id="progress-title")

            yield Static("⏳ Starting operation...", id="progress-status")
            yield ProgressBar(id="progress-bar", show_eta=True)

            yield Static("", id="progress-details")

            with Horizontal(id="progress-actions"):
                yield Button("Cancel", variant="error", id="cancel-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize progress display."""
        self.update_status("Initializing...")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "cancel-btn":
            self.action_cancel()

    def update_status(
        self, message: str, progress: Optional[float] = None, details: str = ""
    ) -> None:
        """
        Update progress display.

        Args:
            message: Status message
            progress: Progress percentage (0-100)
            details: Additional details
        """
        try:
            status_widget = self.query_one("#progress-status", Static)
            status_widget.update(f"⏳ {message}")

            if progress is not None:
                progress_bar = self.query_one("#progress-bar", ProgressBar)
                progress_bar.progress = progress

            if details:
                details_widget = self.query_one("#progress-details", Static)
                details_widget.update(details)
        except Exception:
            pass  # Ignore errors if widgets not found

    def set_result(self, result: ProcessingResult) -> None:
        """Set the operation result."""
        self.result = result
        if result.success:
            self.update_status("✓ Operation completed successfully", 100)
        else:
            self.update_status("✗ Operation failed", 100)

        # Auto-close after a short delay
        self.set_timer(1.0, self._auto_close)

    def set_error(self, error: Exception) -> None:
        """Set an error result."""
        self.error = error
        self.update_status(f"✗ Error: {str(error)}", 100)

        # Auto-close after a short delay
        self.set_timer(2.0, self._auto_close)

    def _auto_close(self) -> None:
        """Auto-close the progress screen."""
        if not self.cancelled:
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the operation."""
        self.cancelled = True
        self.update_status("Cancelling operation...", None, "Please wait...")

        # In a real implementation, you would signal the operation to stop
        # For now, just close the screen
        self.set_timer(0.5, lambda: self.app.pop_screen())


class UtilitySelectionScreen(Screen):
    """Screen for selecting utilities by category."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "quit", "Quit"),
        Binding("f1", "show_help", "Help"),
        Binding("/", "search", "Search"),
        Binding("ctrl+f", "search", "Search"),
        Binding("enter", "select_focused", "Select"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.registry = get_global_registry()
        self.selected_utility = None
        self.search_mode = False
        self.search_query = ""

    def compose(self) -> ComposeResult:
        """Create the utility selection interface."""
        yield Header()

        with Container(id="main-container"):
            yield Static("DevKnife - Developer Utility Toolkit", id="title")
            yield Static("Select a utility category and command:", id="subtitle")

            # Search input (initially hidden)
            yield Input(
                placeholder="Type to search commands...",
                id="search-input",
                classes="hidden",
            )

            # Get categories and commands
            categories = self.registry.list_categories()

            with Vertical(id="categories-container"):
                for category in categories:
                    commands = self.registry.get_commands_by_category(category)

                    # Create collapsible section for each category
                    with Collapsible(title=category.upper(), collapsed=False):
                        for command_name in commands:
                            command_info = self.registry.get_command_info(command_name)
                            if command_info and command_info.tui_enabled:
                                yield Button(
                                    f"{command_name} - {command_info.description}",
                                    id=f"cmd-{command_name}",
                                    classes="command-button",
                                )

        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self.search_query = event.value.lower()
            self._filter_commands()

    def _filter_commands(self) -> None:
        """Filter commands based on search query."""
        if not self.search_query:
            # Show all commands
            for button in self.query(".command-button"):
                button.remove_class("hidden")
            return

        # Hide/show commands based on search
        for button in self.query(".command-button"):
            button_text = button.label.lower()
            if self.search_query in button_text:
                button.remove_class("hidden")
            else:
                button.add_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id and event.button.id.startswith("cmd-"):
            command_name = event.button.id[4:]  # Remove "cmd-" prefix
            self.selected_utility = command_name
            self.app.push_screen(UtilityFormScreen(command_name))

    def action_back(self) -> None:
        """Go back to main screen."""
        if self.search_mode:
            self._toggle_search()
        else:
            self.app.pop_screen()

    def action_search(self) -> None:
        """Toggle search mode."""
        self._toggle_search()

    def _toggle_search(self) -> None:
        """Toggle search input visibility and focus."""
        search_input = self.query_one("#search-input", Input)

        if self.search_mode:
            # Exit search mode
            search_input.add_class("hidden")
            search_input.value = ""
            self.search_query = ""
            self._filter_commands()  # Show all commands
            self.search_mode = False
            self.notify("Search mode disabled")
        else:
            # Enter search mode
            search_input.remove_class("hidden")
            search_input.focus()
            self.search_mode = True
            self.notify("Search mode enabled - type to filter commands")

    def action_select_focused(self) -> None:
        """Select the currently focused command."""
        focused = self.focused
        if (
            focused
            and hasattr(focused, "id")
            and focused.id
            and focused.id.startswith("cmd-")
        ):
            command_name = focused.id[4:]
            self.selected_utility = command_name
            self.app.push_screen(UtilityFormScreen(command_name))

    def action_show_help(self) -> None:
        """Show general help."""
        from ..core.router import get_global_router

        router = get_global_router()
        help_text = router.get_general_help()
        self.app.push_screen(HelpScreen("General Help", help_text))

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class UtilityFormScreen(Screen):
    """Screen for inputting parameters for a specific utility."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+r", "run", "Run"),
        Binding("f1", "help", "Help"),
        Binding("ctrl+l", "load_file", "Load File"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, command_name: str, **kwargs):
        super().__init__(**kwargs)
        self.command_name = command_name
        self.registry = get_global_registry()
        self.router = get_global_router()
        self.input_widgets = {}

    def compose(self) -> ComposeResult:
        """Create the utility form interface."""
        yield Header()

        command_info = self.registry.get_command_info(self.command_name)

        with Container(id="form-container"):
            yield Static(f"Configure: {self.command_name}", id="form-title")
            if command_info:
                yield Static(command_info.description, id="form-description")

            # Input data section
            with Collapsible(title="Input Data", collapsed=False):
                yield Label("Enter your input data:")
                yield TextArea(
                    placeholder="Enter text data here or use file input below...",
                    id="input-text",
                )

                with Horizontal():
                    yield Label("Or load from file:")
                    yield Input(placeholder="/path/to/file", id="input-file")
                    yield Button("Load File", id="load-file-btn")

            # Options section
            with Collapsible(title="Options", collapsed=True):
                yield self._create_options_form()

            # Action buttons
            with Horizontal(id="action-buttons"):
                yield Button("Run", variant="primary", id="run-btn")
                yield Button("Back", id="back-btn")
                yield Button("Help", id="help-btn")

        yield Footer()

    def _create_options_form(self) -> Container:
        """Create the options form based on the utility's supported options."""
        container = Container(id="options-form")

        # Get utility instance to check supported options
        utility_class = self.registry.get_utility_class(self.command_name)
        if utility_class:
            try:
                utility = utility_class()
                supported_options = utility.get_supported_options()

                # Create input widgets for common options
                common_options = {
                    "decode": ("Decode mode", "checkbox"),
                    "indent": ("Indentation spaces", "number"),
                    "recover": ("Attempt recovery", "checkbox"),
                    "format": ("Output format", "text"),
                    "algorithm": ("Algorithm", "text"),
                    "length": ("Length", "number"),
                    "version": ("Version", "text"),
                    "base_url": ("Base URL", "text"),
                    "class_name": ("Class name", "text"),
                    "has_header": ("Has header", "checkbox"),
                    "uppercase": ("Include uppercase", "checkbox"),
                    "lowercase": ("Include lowercase", "checkbox"),
                    "digits": ("Include digits", "checkbox"),
                    "symbols": ("Include symbols", "checkbox"),
                    "no_ambiguous": ("Exclude ambiguous chars", "checkbox"),
                    "from_base": ("From base", "text"),
                    "to_base": ("To base", "text"),
                    "utc": ("Use UTC", "checkbox"),
                    "reverse": ("Reverse conversion", "checkbox"),
                    "unique": ("Unique results only", "checkbox"),
                }

                if supported_options:
                    for option in supported_options:
                        if option in common_options:
                            label_text, widget_type = common_options[option]

                            with Horizontal():
                                container.mount(Label(f"{label_text}:"))

                                if widget_type == "checkbox":
                                    # For checkboxes, we'll use a button that toggles
                                    container.mount(
                                        Button(
                                            "☐ False",
                                            id=f"opt-{option}",
                                            classes="checkbox-button",
                                        )
                                    )
                                elif widget_type == "number":
                                    container.mount(
                                        Input(
                                            placeholder="0",
                                            id=f"opt-{option}",
                                            type="integer",
                                        )
                                    )
                                else:  # text
                                    container.mount(
                                        Input(
                                            placeholder=f"Enter {label_text.lower()}",
                                            id=f"opt-{option}",
                                        )
                                    )

                            self.input_widgets[option] = f"opt-{option}"
                else:
                    # If no options are supported, show a message
                    container.mount(
                        Label("No additional options available for this utility.")
                    )

            except Exception:
                container.mount(Label("Unable to load options for this utility."))

        return container

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "run-btn":
            self.action_run()
        elif event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "help-btn":
            self._show_help()
        elif event.button.id == "load-file-btn":
            self._load_file()
        elif (
            event.button.id
            and event.button.id.startswith("opt-")
            and "checkbox-button" in event.button.classes
        ):
            self._toggle_checkbox(event.button)

    def _toggle_checkbox(self, button: Button) -> None:
        """Toggle a checkbox button state."""
        if "☐" in button.label:
            button.label = button.label.replace("☐ False", "☑ True")
        else:
            button.label = button.label.replace("☑ True", "☐ False")

    def _load_file(self) -> None:
        """Load content from file."""
        file_input = self.query_one("#input-file", Input)
        file_path = file_input.value.strip()

        if file_path:
            error_handler = get_tui_error_handler()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                text_area = self.query_one("#input-text", TextArea)
                text_area.text = content

                self.notify(f"Loaded file: {file_path}")
            except Exception as e:
                error_info = error_handler.handle_for_notification(e)
                self.notify(error_info["message"], severity="error")

    def _show_help(self) -> None:
        """Show help for the current utility."""
        help_text = self.router.get_command_help(self.command_name)
        examples = self.router.get_command_examples(self.command_name)

        if help_text:
            # Combine help text with examples
            full_help = help_text
            if examples:
                full_help += "\n\nExamples:\n"
                for i, example in enumerate(examples, 1):
                    full_help += f"{i}. {example}\n"

            self.app.push_screen(HelpScreen(self.command_name, full_help))
        else:
            self.notify("Help not available for this command", severity="warning")

    def _collect_input_data(self) -> Optional[InputData]:
        """Collect input data from the form."""
        text_area = self.query_one("#input-text", TextArea)
        content = text_area.text.strip()

        if not content:
            self.notify("Please enter input data", severity="error")
            return None

        return InputData(content=content, source=InputSource.ARGS)

    def _collect_options(self) -> Dict[str, Any]:
        """Collect options from the form."""
        options = {}

        for option_name, widget_id in self.input_widgets.items():
            try:
                widget = self.query_one(f"#{widget_id}")

                if hasattr(widget, "label") and "checkbox-button" in widget.classes:
                    # Checkbox button
                    options[option_name] = "☑" in widget.label
                elif hasattr(widget, "value"):
                    # Input widget
                    value = widget.value.strip()
                    if value:
                        # Try to convert to appropriate type
                        if widget.type == "integer":
                            try:
                                options[option_name] = int(value)
                            except ValueError:
                                pass
                        else:
                            options[option_name] = value
            except Exception:
                pass

        return options

    def action_run(self) -> None:
        """Run the utility with current input and options."""
        input_data = self._collect_input_data()
        if not input_data:
            return

        options = self._collect_options()
        error_handler = get_tui_error_handler()

        # Check if this is likely to be a long-running operation
        is_large_file = input_data.metadata.get("file_size", 0) > 1024 * 1024  # > 1MB
        is_streaming = input_data.metadata.get("streaming", False)

        if is_large_file or is_streaming:
            # Use progress screen for large operations
            self._run_with_progress(input_data, options)
        else:
            # Run normally for small operations
            self.notify("Processing...", timeout=2)

            try:
                # Execute the command
                result = self.router.route_command(
                    self.command_name, input_data, options
                )

                # Show results
                self.app.push_screen(ResultScreen(self.command_name, result))
            except Exception as e:
                error_info = error_handler.handle_for_notification(e)
                self.notify(error_info["message"], severity="error")
                # Still show result screen with error
                from ..core.models import ProcessingResult

                error_result = ProcessingResult(
                    success=False, output=None, error_message=error_info["message"]
                )
                self.app.push_screen(ResultScreen(self.command_name, error_result))

    def _run_with_progress(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> None:
        """
        Run utility with progress indication for long operations.

        Args:
            input_data: Input data to process
            options: Processing options
        """
        progress_screen = ProgressScreen(f"{self.command_name} operation")
        self.app.push_screen(progress_screen)

        def run_operation():
            """Run the operation in a separate thread."""
            try:
                # Update progress
                progress_screen.update_status("Processing data...", 25)

                # Execute the command
                result = self.router.route_command(
                    self.command_name, input_data, options
                )

                progress_screen.update_status("Finalizing results...", 90)

                # Set the result
                progress_screen.set_result(result)

                # Schedule showing results screen
                self.app.call_later(
                    lambda: self.app.push_screen(
                        ResultScreen(self.command_name, result)
                    )
                )

            except Exception as e:
                progress_screen.set_error(e)

                # Schedule showing error result
                from ..core.models import ProcessingResult

                error_result = ProcessingResult(
                    success=False, output=None, error_message=str(e)
                )
                self.app.call_later(
                    lambda: self.app.push_screen(
                        ResultScreen(self.command_name, error_result)
                    )
                )

        # Start operation in background thread
        thread = threading.Thread(target=run_operation, daemon=True)
        thread.start()

    def action_back(self) -> None:
        """Go back to utility selection."""
        self.app.pop_screen()

    def action_load_file(self) -> None:
        """Load file action via keyboard shortcut."""
        self._load_file()

    def action_help(self) -> None:
        """Show help action via keyboard shortcut."""
        self._show_help()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class ResultScreen(Screen):
    """Screen for displaying command results."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+c", "copy", "Copy"),
        Binding("ctrl+s", "save", "Save"),
        Binding("f5", "run_again", "Run Again"),
        Binding("q", "quit", "Quit"),
        Binding("r", "run_again", "Run Again"),
        Binding("c", "copy", "Copy"),
        Binding("s", "save", "Save"),
    ]

    def __init__(self, command_name: str, result: ProcessingResult, **kwargs):
        super().__init__(**kwargs)
        self.command_name = command_name
        self.result = result

    def compose(self) -> ComposeResult:
        """Create the result display interface."""
        yield Header()

        with Container(id="result-container"):
            yield Static(f"Results: {self.command_name}", id="result-title")

            if self.result.success:
                yield Static("✓ Success", id="status-success", classes="status-success")

                # Output section
                with Collapsible(title="Output", collapsed=False):
                    output_text = (
                        str(self.result.output)
                        if self.result.output is not None
                        else ""
                    )
                    yield TextArea(output_text, read_only=True, id="output-text")

                # Warnings section (if any)
                if self.result.warnings:
                    with Collapsible(title="Warnings", collapsed=True):
                        for warning in self.result.warnings:
                            yield Static(f"⚠ {warning}", classes="warning")

                # Metadata section (if any)
                if self.result.metadata:
                    with Collapsible(title="Metadata", collapsed=True):
                        for key, value in self.result.metadata.items():
                            yield Static(f"{key}: {value}")

            else:
                yield Static("✗ Error", id="status-error", classes="status-error")
                yield Static(
                    self.result.error_message or "Unknown error",
                    id="error-message",
                    classes="error-message",
                )

            # Action buttons
            with Horizontal(id="result-actions"):
                if self.result.success:
                    yield Button("Copy Output (C)", id="copy-btn")
                    yield Button("Save to File (S)", id="save-btn")
                yield Button("Back (ESC)", id="back-btn")
                yield Button("Run Again (R)", id="run-again-btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "copy-btn":
            self.action_copy()
        elif event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "run-again-btn":
            self.action_back()  # Go back to form to run again

    def action_copy(self) -> None:
        """Copy output to clipboard."""
        if self.result.success and self.result.output is not None:
            try:
                # Try to copy to clipboard (this might not work in all terminals)
                import pyperclip

                pyperclip.copy(str(self.result.output))
                self.notify("✓ Output copied to clipboard")
            except ImportError:
                # Fallback: show the output in a way that can be selected
                self.notify(
                    "Clipboard functionality not available. Output is displayed above for manual copying."
                )
            except Exception as e:
                self.notify(f"Failed to copy to clipboard: {str(e)}", severity="error")

    def action_save(self) -> None:
        """Save output to file."""
        if self.result.success and self.result.output is not None:
            self.app.push_screen(SaveFileScreen(str(self.result.output)))

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_run_again(self) -> None:
        """Run the command again."""
        self.action_back()  # Go back to form to run again

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class SaveFileScreen(Screen):
    """Screen for saving output to a file."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "save", "Save"),
    ]

    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.content = content

    def compose(self) -> ComposeResult:
        """Create the save file interface."""
        yield Header()

        with Container(id="save-container"):
            yield Static("Save Output to File", id="save-title")

            yield Label("Enter file path:")
            yield Input(placeholder="/path/to/output.txt", id="file-path")

            with Horizontal():
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Cancel", id="cancel-btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_back()

    def action_save(self) -> None:
        """Save content to the specified file."""
        file_input = self.query_one("#file-path", Input)
        file_path = file_input.value.strip()

        if not file_path:
            self.notify("Please enter a file path", severity="error")
            return

        error_handler = get_tui_error_handler()
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.content)

            self.notify(f"Output saved to: {file_path}")
            self.app.pop_screen()
        except Exception as e:
            error_info = error_handler.handle_for_notification(e)
            self.notify(error_info["message"], severity="error")

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()


class HelpScreen(Screen):
    """Screen for displaying help information."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, command_name: str, help_text: str, **kwargs):
        super().__init__(**kwargs)
        self.command_name = command_name
        self.help_text = help_text

    def compose(self) -> ComposeResult:
        """Create the help display interface."""
        yield Header()

        with Container(id="help-container"):
            yield Static(f"Help: {self.command_name}", id="help-title")

            yield TextArea(self.help_text, read_only=True, id="help-text")

            yield Button("Back", id="back-btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back-btn":
            self.action_back()

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class DevKnifeTUIApp(App):
    """Main TUI application for DevKnife."""

    CSS_PATH = "app.css"
    TITLE = "DevKnife - Developer Utility Toolkit"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "show_help", "Help"),
    ]

    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen(UtilitySelectionScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_show_help(self) -> None:
        """Show general help."""
        from ..core.router import get_global_router

        router = get_global_router()
        help_text = router.get_general_help()
        self.push_screen(HelpScreen("General Help", help_text))


def run_tui() -> None:
    """Run the TUI application."""
    app = DevKnifeTUIApp()
    app.run()


if __name__ == "__main__":
    run_tui()
