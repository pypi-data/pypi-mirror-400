"""
Data format processing utility module for JSON, XML, YAML, CSV, and TSV operations.
"""

import csv
import io
import json
import re
import xml.dom.minidom
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Iterator
import yaml
from devknife.core import UtilityModule, Command, InputData, ProcessingResult
from devknife.core.performance import (
    get_global_memory_optimizer,
    get_global_streaming_handler,
    progress_context,
    ProgressType,
)


class JSONFormatter(UtilityModule):
    """
    Utility for JSON formatting and recovery operations.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by formatting JSON or attempting recovery.

        Args:
            input_data: Input data to process
            options: Processing options (recover flag, indent)

        Returns:
            ProcessingResult with formatted JSON
        """
        try:
            content = input_data.as_string().strip()
            recover_mode = options.get("recover", False)
            indent = options.get("indent", 2)

            if recover_mode:
                # Attempt to recover malformed JSON
                return self._recover_json(content, indent)
            else:
                # Format valid JSON
                return self._format_json(content, indent)

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process JSON: {str(e)}",
            )

    def _format_json(self, content: str, indent: int) -> ProcessingResult:
        """
        Format valid JSON with proper indentation.

        Args:
            content: JSON string to format
            indent: Number of spaces for indentation

        Returns:
            ProcessingResult with formatted JSON
        """
        try:
            # Parse JSON to validate and get structure
            parsed = json.loads(content)

            # Format with proper indentation
            formatted = json.dumps(
                parsed, indent=indent, ensure_ascii=False, sort_keys=False
            )

            return ProcessingResult(
                success=True,
                output=formatted,
                metadata={
                    "operation": "format",
                    "input_length": len(content),
                    "output_length": len(formatted),
                    "indent": indent,
                },
            )

        except json.JSONDecodeError as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Invalid JSON format: {str(e)}. Use --recover flag to attempt automatic repair.",
            )

    def _recover_json(self, content: str, indent: int) -> ProcessingResult:
        """
        Attempt to recover malformed JSON.

        Args:
            content: Potentially malformed JSON string
            indent: Number of spaces for indentation

        Returns:
            ProcessingResult with recovered JSON
        """
        warnings = []

        # Try parsing as-is first
        try:
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)
            return ProcessingResult(
                success=True,
                output=formatted,
                warnings=["JSON was already valid, no recovery needed"],
                metadata={"operation": "recover", "recovery_applied": False},
            )
        except json.JSONDecodeError:
            pass

        # Apply common fixes
        recovered_content = content

        # Fix common issues
        fixes_applied = []

        # Fix trailing commas
        if re.search(r",\s*[}\]]", recovered_content):
            recovered_content = re.sub(r",(\s*[}\]])", r"\1", recovered_content)
            fixes_applied.append("removed trailing commas")

        # Fix single quotes to double quotes
        if "'" in recovered_content:
            # Simple replacement - this is basic recovery
            recovered_content = recovered_content.replace("'", '"')
            fixes_applied.append("converted single quotes to double quotes")

        # Fix unquoted keys (basic pattern)
        unquoted_key_pattern = r"(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:"
        if re.search(unquoted_key_pattern, recovered_content):
            recovered_content = re.sub(
                unquoted_key_pattern, r'\1 "\2":', recovered_content
            )
            fixes_applied.append("quoted unquoted keys")

        # Try parsing the recovered content
        try:
            parsed = json.loads(recovered_content)
            formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)

            if fixes_applied:
                warnings.append(f"Applied fixes: {', '.join(fixes_applied)}")

            return ProcessingResult(
                success=True,
                output=formatted,
                warnings=warnings,
                metadata={
                    "operation": "recover",
                    "recovery_applied": True,
                    "fixes_applied": fixes_applied,
                },
            )

        except json.JSONDecodeError as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Could not recover JSON: {str(e)}. The input may be too malformed to repair automatically.",
            )

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
JSON Formatter

DESCRIPTION:
    Format JSON with proper indentation or attempt to recover malformed JSON.

USAGE:
    devknife json [options] <json_string>
    echo '{"key":"value"}' | devknife json [options]

OPTIONS:
    --recover       Attempt to recover malformed JSON
    --indent N      Number of spaces for indentation (default: 2)

EXAMPLES:
    devknife json '{"name":"John","age":30}'
    devknife json --recover "{'name':'John','age':30,}"
    echo '{"compressed":"json"}' | devknife json --indent 4
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
            content = input_data.as_string().strip()
            return len(content) > 0
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="json",
            description="Format JSON with proper indentation or recover malformed JSON",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["recover", "indent"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife json \'{"name":"John","age":30}\'',
            "devknife json --recover \"{'name':'John','age':30,}\"",
            'echo \'{"compressed":"json"}\' | devknife json --indent 4',
        ]


class JSONToYAMLConverter(UtilityModule):
    """
    Utility for converting JSON to YAML format.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting JSON to YAML.

        Args:
            input_data: Input data to process
            options: Processing options

        Returns:
            ProcessingResult with YAML output
        """
        try:
            content = input_data.as_string().strip()

            # Parse JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Invalid JSON input: {str(e)}",
                )

            # Convert to YAML
            try:
                yaml_output = yaml.dump(
                    parsed,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                )

                return ProcessingResult(
                    success=True,
                    output=yaml_output.rstrip(),  # Remove trailing newline
                    metadata={
                        "operation": "json_to_yaml",
                        "input_length": len(content),
                        "output_length": len(yaml_output),
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Failed to convert to YAML: {str(e)}",
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
JSON to YAML Converter

DESCRIPTION:
    Convert JSON format to equivalent YAML format.

USAGE:
    devknife json2yaml <json_string>
    echo '{"key":"value"}' | devknife json2yaml

EXAMPLES:
    devknife json2yaml '{"name":"John","age":30,"hobbies":["reading","coding"]}'
    echo '{"database":{"host":"localhost","port":5432}}' | devknife json2yaml
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False
            # Try to parse as JSON to validate
            json.loads(content)
            return True
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="json2yaml",
            description="Convert JSON format to equivalent YAML format",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife json2yaml \'{"name":"John","age":30}\'',
            'echo \'{"database":{"host":"localhost","port":5432}}\' | devknife json2yaml',
        ]


class XMLFormatter(UtilityModule):
    """
    Utility for XML formatting operations.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by formatting XML with proper indentation.

        Args:
            input_data: Input data to process
            options: Processing options (indent)

        Returns:
            ProcessingResult with formatted XML
        """
        try:
            content = input_data.as_string().strip()
            indent = options.get("indent", 2)

            # Parse XML
            try:
                # Parse the XML
                root = ET.fromstring(content)

                # Create a formatted string using minidom for pretty printing
                rough_string = ET.tostring(root, encoding="unicode")
                reparsed = xml.dom.minidom.parseString(rough_string)

                # Get pretty printed XML
                formatted = reparsed.toprettyxml(indent=" " * indent)

                # Clean up the output - remove extra blank lines and XML declaration if not needed
                lines = [line for line in formatted.split("\n") if line.strip()]
                if lines and lines[0].startswith("<?xml"):
                    # Keep XML declaration
                    formatted_output = "\n".join(lines)
                else:
                    # Remove XML declaration that minidom adds
                    formatted_output = (
                        "\n".join(lines[1:])
                        if lines and lines[0].startswith("<?xml")
                        else "\n".join(lines)
                    )

                return ProcessingResult(
                    success=True,
                    output=formatted_output,
                    metadata={
                        "operation": "format",
                        "input_length": len(content),
                        "output_length": len(formatted_output),
                        "indent": indent,
                    },
                )

            except ET.ParseError as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Invalid XML format: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process XML: {str(e)}",
            )

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
XML Formatter

DESCRIPTION:
    Format XML with proper indentation for better readability.

USAGE:
    devknife xml [options] <xml_string>
    echo '<root><item>value</item></root>' | devknife xml [options]

OPTIONS:
    --indent N      Number of spaces for indentation (default: 2)

EXAMPLES:
    devknife xml '<root><item>value</item></root>'
    echo '<config><database><host>localhost</host></database></config>' | devknife xml --indent 4
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False
            # Try to parse as XML to validate
            ET.fromstring(content)
            return True
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="xml",
            description="Format XML with proper indentation for better readability",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["indent"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife xml '<root><item>value</item></root>'",
            "echo '<config><database><host>localhost</host></database></config>' | devknife xml --indent 4",
        ]


class JSONToPythonClassGenerator(UtilityModule):
    """
    Utility for generating Python data classes from JSON schema.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by generating Python data classes from JSON.

        Args:
            input_data: Input data to process
            options: Processing options (class_name)

        Returns:
            ProcessingResult with Python class code
        """
        try:
            content = input_data.as_string().strip()
            class_name = options.get("class_name", "GeneratedClass")

            # Parse JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Invalid JSON input: {str(e)}",
                )

            # Generate Python class
            try:
                class_code = self._generate_dataclass(parsed, class_name)

                return ProcessingResult(
                    success=True,
                    output=class_code,
                    metadata={
                        "operation": "json_to_python_class",
                        "class_name": class_name,
                        "input_length": len(content),
                        "output_length": len(class_code),
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Failed to generate Python class: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process input: {str(e)}",
            )

    def _generate_dataclass(self, data: Any, class_name: str) -> str:
        """
        Generate a Python dataclass from JSON data.

        Args:
            data: Parsed JSON data
            class_name: Name for the generated class

        Returns:
            Python dataclass code as string
        """
        imports = [
            "from dataclasses import dataclass",
            "from typing import Any, List, Dict, Optional",
        ]

        if isinstance(data, dict):
            class_def = self._generate_dict_class(data, class_name)
        elif isinstance(data, list) and data:
            # Generate class for list items if they're objects
            if isinstance(data[0], dict):
                class_def = self._generate_dict_class(data[0], class_name + "Item")
                class_def += f"\n\n# Usage: List[{class_name}Item] for the array"
            else:
                class_def = f"# Simple list of {type(data[0]).__name__} values\n# Usage: List[{self._python_type(data[0])}]"
        else:
            class_def = f"# Simple value of type {self._python_type(data)}"

        return "\n".join(imports) + "\n\n" + class_def

    def _generate_dict_class(self, data: Dict[str, Any], class_name: str) -> str:
        """
        Generate a dataclass for a dictionary.

        Args:
            data: Dictionary data
            class_name: Name for the class

        Returns:
            Dataclass definition as string
        """
        lines = [f"@dataclass", f"class {class_name}:"]

        if not data:
            lines.append("    pass")
            return "\n".join(lines)

        for key, value in data.items():
            python_type = self._python_type(value)
            safe_key = self._safe_identifier(key)

            if safe_key != key:
                lines.append(f"    {safe_key}: {python_type}  # Original key: '{key}'")
            else:
                lines.append(f"    {safe_key}: {python_type}")

        return "\n".join(lines)

    def _python_type(self, value: Any) -> str:
        """
        Determine the Python type annotation for a value.

        Args:
            value: Value to analyze

        Returns:
            Python type annotation string
        """
        if value is None:
            return "Optional[Any]"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, list):
            if not value:
                return "List[Any]"
            # Analyze first item to determine list type
            first_type = self._python_type(value[0])
            return f"List[{first_type}]"
        elif isinstance(value, dict):
            return "Dict[str, Any]"
        else:
            return "Any"

    def _safe_identifier(self, name: str) -> str:
        """
        Convert a string to a safe Python identifier.

        Args:
            name: Original name

        Returns:
            Safe Python identifier
        """
        # Replace invalid characters with underscores
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)

        # Ensure it doesn't start with a number
        if safe and safe[0].isdigit():
            safe = f"field_{safe}"

        # Handle Python keywords
        python_keywords = {
            "and",
            "as",
            "assert",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "exec",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "not",
            "or",
            "pass",
            "print",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        }

        if safe.lower() in python_keywords:
            safe = f"{safe}_field"

        return safe or "unknown_field"

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
JSON to Python Class Generator

DESCRIPTION:
    Generate Python dataclass definitions from JSON structure.

USAGE:
    devknife json2py [options] <json_string>
    echo '{"name":"John","age":30}' | devknife json2py [options]

OPTIONS:
    --class-name NAME   Name for the generated class (default: GeneratedClass)

EXAMPLES:
    devknife json2py '{"name":"John","age":30}' --class-name Person
    echo '{"id":1,"title":"Task","completed":false}' | devknife json2py --class-name Task
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False
            # Try to parse as JSON to validate
            json.loads(content)
            return True
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="json2py",
            description="Generate Python dataclass definitions from JSON structure",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["class_name"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife json2py \'{"name":"John","age":30}\' --class-name Person',
            'echo \'{"id":1,"title":"Task","completed":false}\' | devknife json2py --class-name Task',
        ]


class CSVToMarkdownConverter(UtilityModule):
    """
    Utility for converting CSV data to Markdown table format.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting CSV to Markdown table with streaming support for large files.

        Args:
            input_data: Input data to process
            options: Processing options (has_header)

        Returns:
            ProcessingResult with Markdown table output
        """
        try:
            has_header = options.get("has_header", True)
            memory_optimizer = get_global_memory_optimizer()

            # Check if we should use streaming
            if input_data.metadata.get("streaming", False):
                return self._process_streaming(input_data, has_header)

            content = input_data.as_string().strip()

            if not content:
                return ProcessingResult(
                    success=False, output=None, error_message="Empty CSV input provided"
                )

            # Check if content is large enough to warrant streaming
            if memory_optimizer.optimize_csv_processing(content):
                return self._process_large_csv(content, has_header)

            # Parse CSV normally for smaller files
            try:
                with progress_context(
                    ProgressType.SPINNER, "Parsing CSV data"
                ) as progress:
                    csv_reader = csv.reader(io.StringIO(content))
                    rows = list(csv_reader)

                    progress.update(message="Converting to Markdown")

                    if not rows:
                        return ProcessingResult(
                            success=False,
                            output=None,
                            error_message="No data found in CSV input",
                        )

                    # Generate Markdown table
                    markdown_output = self._generate_markdown_table(rows, has_header)

                    progress.finish("CSV conversion completed")

                return ProcessingResult(
                    success=True,
                    output=markdown_output,
                    metadata={
                        "operation": "csv_to_markdown",
                        "rows_processed": len(rows),
                        "columns": len(rows[0]) if rows else 0,
                        "has_header": has_header,
                        "streaming_used": False,
                    },
                )

            except csv.Error as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"CSV parsing error: {str(e)}. Please check the CSV format and ensure proper quoting of fields containing commas or newlines.",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process CSV input: {str(e)}",
            )

    def _process_streaming(
        self, input_data: InputData, has_header: bool
    ) -> ProcessingResult:
        """
        Process CSV data using streaming for large files.

        Args:
            input_data: Streaming input data
            has_header: Whether the first row is a header

        Returns:
            ProcessingResult with Markdown table output
        """
        try:
            streaming_handler = get_global_streaming_handler()
            file_path = input_data.metadata.get("file_path", input_data.content)

            rows = []
            row_count = 0

            with progress_context(
                ProgressType.COUNTER, "Processing CSV file"
            ) as progress:
                for line in streaming_handler.stream_file_lines(
                    file_path, input_data.encoding
                ):
                    try:
                        # Parse each line as CSV
                        csv_reader = csv.reader([line])
                        row = next(csv_reader)
                        rows.append(row)
                        row_count += 1

                        progress.update(row_count, f"Processed {row_count} rows")

                        # Limit memory usage by processing in chunks
                        if len(rows) > 10000:  # Process in chunks of 10k rows
                            break

                    except csv.Error:
                        # Skip malformed rows
                        continue

                progress.update(message="Converting to Markdown")

                if not rows:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message="No valid CSV data found in file",
                    )

                markdown_output = self._generate_markdown_table(rows, has_header)
                progress.finish(f"Processed {row_count} rows successfully")

            return ProcessingResult(
                success=True,
                output=markdown_output,
                metadata={
                    "operation": "csv_to_markdown",
                    "rows_processed": len(rows),
                    "columns": len(rows[0]) if rows else 0,
                    "has_header": has_header,
                    "streaming_used": True,
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process streaming CSV: {str(e)}",
            )

    def _process_large_csv(self, content: str, has_header: bool) -> ProcessingResult:
        """
        Process large CSV content with memory optimization.

        Args:
            content: CSV content string
            has_header: Whether the first row is a header

        Returns:
            ProcessingResult with Markdown table output
        """
        try:
            rows = []
            row_count = 0

            with progress_context(
                ProgressType.COUNTER, "Processing large CSV"
            ) as progress:
                csv_reader = csv.reader(io.StringIO(content))

                for row in csv_reader:
                    rows.append(row)
                    row_count += 1

                    if row_count % 1000 == 0:
                        progress.update(row_count, f"Processed {row_count} rows")

                    # Limit memory usage
                    if len(rows) > 50000:  # Limit to 50k rows for memory
                        progress.update(
                            message="Limiting to first 50,000 rows for memory efficiency"
                        )
                        break

                progress.update(message="Converting to Markdown")

                if not rows:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message="No data found in CSV input",
                    )

                markdown_output = self._generate_markdown_table(rows, has_header)
                progress.finish(f"Processed {len(rows)} rows successfully")

            warnings = []
            if len(rows) >= 50000:
                warnings.append(
                    "Output limited to first 50,000 rows for memory efficiency"
                )

            return ProcessingResult(
                success=True,
                output=markdown_output,
                warnings=warnings,
                metadata={
                    "operation": "csv_to_markdown",
                    "rows_processed": len(rows),
                    "columns": len(rows[0]) if rows else 0,
                    "has_header": has_header,
                    "streaming_used": False,
                    "memory_optimized": True,
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process large CSV: {str(e)}",
            )

    def _generate_markdown_table(self, rows: List[List[str]], has_header: bool) -> str:
        """
        Generate a Markdown table from CSV rows.

        Args:
            rows: List of CSV rows
            has_header: Whether the first row is a header

        Returns:
            Markdown table as string
        """
        if not rows:
            return ""

        # Escape pipe characters in cell content
        escaped_rows = []
        for row in rows:
            escaped_row = [cell.replace("|", "\\|") for cell in row]
            escaped_rows.append(escaped_row)

        # Determine column count
        max_cols = max(len(row) for row in escaped_rows)

        # Pad rows to have the same number of columns
        for row in escaped_rows:
            while len(row) < max_cols:
                row.append("")

        markdown_lines = []

        if has_header and escaped_rows:
            # Header row
            header_row = escaped_rows[0]
            markdown_lines.append("| " + " | ".join(header_row) + " |")

            # Separator row
            separator = "| " + " | ".join(["---"] * len(header_row)) + " |"
            markdown_lines.append(separator)

            # Data rows
            for row in escaped_rows[1:]:
                markdown_lines.append("| " + " | ".join(row) + " |")
        else:
            # No header, treat all rows as data
            for row in escaped_rows:
                markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
CSV to Markdown Converter

DESCRIPTION:
    Convert CSV data to Markdown table format.

USAGE:
    devknife csv2md [options] <csv_string>
    echo 'name,age,city\nJohn,30,NYC\nJane,25,LA' | devknife csv2md [options]

OPTIONS:
    --no-header     Treat all rows as data (no header row)

EXAMPLES:
    devknife csv2md 'name,age\nJohn,30\nJane,25'
    echo 'apple,red\nbanana,yellow' | devknife csv2md --no-header
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False

            # Try to parse as CSV to validate
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            return len(rows) > 0

        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="csv2md",
            description="Convert CSV data to Markdown table format",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["has_header"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife csv2md 'name,age\\nJohn,30\\nJane,25'",
            "echo 'apple,red\\nbanana,yellow' | devknife csv2md --no-header",
        ]


class TSVToMarkdownConverter(UtilityModule):
    """
    Utility for converting TSV data to Markdown table format.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting TSV to Markdown table.

        Args:
            input_data: Input data to process
            options: Processing options (has_header)

        Returns:
            ProcessingResult with Markdown table output
        """
        try:
            content = input_data.as_string().strip()
            has_header = options.get("has_header", True)

            if not content:
                return ProcessingResult(
                    success=False, output=None, error_message="Empty TSV input provided"
                )

            # Parse TSV
            try:
                csv_reader = csv.reader(io.StringIO(content), delimiter="\t")
                rows = list(csv_reader)

                if not rows:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message="No data found in TSV input",
                    )

                # Generate Markdown table
                markdown_output = self._generate_markdown_table(rows, has_header)

                return ProcessingResult(
                    success=True,
                    output=markdown_output,
                    metadata={
                        "operation": "tsv_to_markdown",
                        "rows_processed": len(rows),
                        "columns": len(rows[0]) if rows else 0,
                        "has_header": has_header,
                    },
                )

            except csv.Error as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"TSV parsing error: {str(e)}. Please check the TSV format and ensure proper tab separation.",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process TSV input: {str(e)}",
            )

    def _generate_markdown_table(self, rows: List[List[str]], has_header: bool) -> str:
        """
        Generate a Markdown table from TSV rows.

        Args:
            rows: List of TSV rows
            has_header: Whether the first row is a header

        Returns:
            Markdown table as string
        """
        if not rows:
            return ""

        # Escape pipe characters in cell content
        escaped_rows = []
        for row in rows:
            escaped_row = [cell.replace("|", "\\|") for cell in row]
            escaped_rows.append(escaped_row)

        # Determine column count
        max_cols = max(len(row) for row in escaped_rows)

        # Pad rows to have the same number of columns
        for row in escaped_rows:
            while len(row) < max_cols:
                row.append("")

        markdown_lines = []

        if has_header and escaped_rows:
            # Header row
            header_row = escaped_rows[0]
            markdown_lines.append("| " + " | ".join(header_row) + " |")

            # Separator row
            separator = "| " + " | ".join(["---"] * len(header_row)) + " |"
            markdown_lines.append(separator)

            # Data rows
            for row in escaped_rows[1:]:
                markdown_lines.append("| " + " | ".join(row) + " |")
        else:
            # No header, treat all rows as data
            for row in escaped_rows:
                markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
TSV to Markdown Converter

DESCRIPTION:
    Convert TSV (Tab-Separated Values) data to Markdown table format.

USAGE:
    devknife tsv2md [options] <tsv_string>
    echo -e 'name\tage\tcity\nJohn\t30\tNYC\nJane\t25\tLA' | devknife tsv2md [options]

OPTIONS:
    --no-header     Treat all rows as data (no header row)

EXAMPLES:
    devknife tsv2md 'name\tage\nJohn\t30\nJane\t25'
    echo -e 'apple\tred\nbanana\tyellow' | devknife tsv2md --no-header
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False

            # Try to parse as TSV to validate
            csv_reader = csv.reader(io.StringIO(content), delimiter="\t")
            rows = list(csv_reader)
            return len(rows) > 0

        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="tsv2md",
            description="Convert TSV (Tab-Separated Values) data to Markdown table format",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["has_header"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife tsv2md 'name\\tage\\nJohn\\t30\\nJane\\t25'",
            "echo -e 'apple\\tred\\nbanana\\tyellow' | devknife tsv2md --no-header",
        ]


class CSVToJSONConverter(UtilityModule):
    """
    Utility for converting CSV data to JSON format.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting CSV to JSON array.

        Args:
            input_data: Input data to process
            options: Processing options (has_header, indent)

        Returns:
            ProcessingResult with JSON array output
        """
        try:
            content = input_data.as_string().strip()
            has_header = options.get("has_header", True)
            indent = options.get("indent", 2)

            if not content:
                return ProcessingResult(
                    success=False, output=None, error_message="Empty CSV input provided"
                )

            # Parse CSV
            try:
                csv_reader = csv.reader(io.StringIO(content))
                rows = list(csv_reader)

                if not rows:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message="No data found in CSV input",
                    )

                # Convert to JSON
                json_output = self._convert_to_json(rows, has_header, indent)

                return ProcessingResult(
                    success=True,
                    output=json_output,
                    metadata={
                        "operation": "csv_to_json",
                        "rows_processed": len(rows),
                        "columns": len(rows[0]) if rows else 0,
                        "has_header": has_header,
                        "indent": indent,
                    },
                )

            except csv.Error as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"CSV parsing error at line {csv_reader.line_num if 'csv_reader' in locals() else 'unknown'}: {str(e)}. Please check the CSV format and ensure proper quoting of fields containing commas or newlines.",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process CSV input: {str(e)}",
            )

    def _convert_to_json(
        self, rows: List[List[str]], has_header: bool, indent: int
    ) -> str:
        """
        Convert CSV rows to JSON array.

        Args:
            rows: List of CSV rows
            has_header: Whether the first row is a header
            indent: JSON indentation

        Returns:
            JSON array as string
        """
        if not rows:
            return "[]"

        if has_header and len(rows) > 1:
            # Use first row as keys for objects
            headers = rows[0]
            data_rows = rows[1:]

            json_objects = []
            for row in data_rows:
                # Pad row to match header length
                padded_row = row + [""] * (len(headers) - len(row))

                # Create object with headers as keys
                obj = {}
                for i, header in enumerate(headers):
                    value = padded_row[i] if i < len(padded_row) else ""

                    # Try to convert numeric values
                    if value.strip():
                        # Try integer first
                        try:
                            obj[header] = int(value)
                            continue
                        except ValueError:
                            pass

                        # Try float
                        try:
                            obj[header] = float(value)
                            continue
                        except ValueError:
                            pass

                        # Try boolean
                        if value.lower() in ("true", "false"):
                            obj[header] = value.lower() == "true"
                            continue

                    # Keep as string
                    obj[header] = value

                json_objects.append(obj)

            return json.dumps(json_objects, indent=indent, ensure_ascii=False)
        else:
            # No header or only one row, convert to array of arrays
            return json.dumps(rows, indent=indent, ensure_ascii=False)

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
CSV to JSON Converter

DESCRIPTION:
    Convert CSV data to JSON array format. With headers, creates array of objects.
    Without headers, creates array of arrays.

USAGE:
    devknife csv2json [options] <csv_string>
    echo 'name,age,city\nJohn,30,NYC\nJane,25,LA' | devknife csv2json [options]

OPTIONS:
    --no-header     Treat all rows as data (creates array of arrays)
    --indent N      Number of spaces for JSON indentation (default: 2)

EXAMPLES:
    devknife csv2json 'name,age\nJohn,30\nJane,25'
    echo 'apple,red\nbanana,yellow' | devknife csv2json --no-header
    devknife csv2json 'id,name\n1,John\n2,Jane' --indent 4
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
            content = input_data.as_string().strip()
            if len(content) == 0:
                return False

            # Try to parse as CSV to validate
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)
            return len(rows) > 0

        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="csv2json",
            description="Convert CSV data to JSON array format",
            category="data_format",
            module="devknife.utils.data_format_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["has_header", "indent"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife csv2json 'name,age\\nJohn,30\\nJane,25'",
            "echo 'apple,red\\nbanana,yellow' | devknife csv2json --no-header",
            "devknife csv2json 'id,name\\n1,John\\n2,Jane' --indent 4",
        ]
