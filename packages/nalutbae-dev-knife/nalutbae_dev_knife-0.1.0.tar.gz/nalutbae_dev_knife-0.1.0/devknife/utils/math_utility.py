"""
Mathematical transformation utility module for number base conversion, hash generation, and timestamp conversion.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from devknife.core import UtilityModule, Command, InputData, ProcessingResult


class NumberBaseConverter(UtilityModule):
    """
    Utility for converting numbers between different bases (binary, octal, decimal, hexadecimal).
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting numbers between different bases.

        Args:
            input_data: Input data containing number to convert
            options: Processing options (from_base, to_base)

        Returns:
            ProcessingResult with converted number
        """
        try:
            content = input_data.as_string().strip()
            from_base = options.get("from_base", "auto")
            to_base = options.get("to_base", "all")

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty input provided. Please provide a number to convert.",
                )

            # Parse the input number
            try:
                decimal_value, detected_base = self._parse_number(content, from_base)
            except ValueError as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Invalid number format: {str(e)}",
                )

            # Convert to requested base(s)
            if to_base == "all":
                # Convert to all bases
                conversions = {
                    "decimal": str(decimal_value),
                    "binary": bin(decimal_value)[2:],  # Remove '0b' prefix
                    "octal": oct(decimal_value)[2:],  # Remove '0o' prefix
                    "hexadecimal": hex(decimal_value)[
                        2:
                    ].upper(),  # Remove '0x' prefix and uppercase
                }

                output_lines = [
                    f"Input: {content} (base {detected_base})",
                    f"Decimal: {conversions['decimal']}",
                    f"Binary: {conversions['binary']}",
                    f"Octal: {conversions['octal']}",
                    f"Hexadecimal: {conversions['hexadecimal']}",
                ]

                return ProcessingResult(
                    success=True,
                    output="\n".join(output_lines),
                    metadata={
                        "operation": "base_conversion",
                        "input_base": detected_base,
                        "decimal_value": decimal_value,
                        "conversions": conversions,
                    },
                )
            else:
                # Convert to specific base
                try:
                    converted = self._convert_to_base(decimal_value, to_base)

                    return ProcessingResult(
                        success=True,
                        output=converted,
                        metadata={
                            "operation": "base_conversion",
                            "input_base": detected_base,
                            "output_base": to_base,
                            "decimal_value": decimal_value,
                            "converted_value": converted,
                        },
                    )
                except ValueError as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Invalid target base: {str(e)}",
                    )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to convert number: {str(e)}",
            )

    def _parse_number(self, content: str, from_base: str) -> tuple[int, str]:
        """
        Parse a number string and determine its base.

        Args:
            content: Number string to parse
            from_base: Expected base ('auto', 'binary', 'octal', 'decimal', 'hex')

        Returns:
            Tuple of (decimal_value, detected_base)
        """
        content = content.strip()

        if from_base == "auto":
            # Auto-detect base from prefixes or content
            if content.startswith("0b") or content.startswith("0B"):
                # Binary
                return int(content, 2), "binary"
            elif content.startswith("0o") or content.startswith("0O"):
                # Octal
                return int(content, 8), "octal"
            elif content.startswith("0x") or content.startswith("0X"):
                # Hexadecimal
                return int(content, 16), "hexadecimal"
            elif re.match(r"^[01]+$", content):
                # Looks like binary (only 0s and 1s)
                return int(content, 2), "binary"
            elif (
                re.match(r"^[0-7]+$", content)
                and len(content) > 1
                and content[0] == "0"
            ):
                # Looks like octal (starts with 0 and only contains 0-7)
                return int(content, 8), "octal"
            elif re.match(r"^[0-9a-fA-F]+$", content) and any(
                c in content.lower() for c in "abcdef"
            ):
                # Contains hex digits
                return int(content, 16), "hexadecimal"
            else:
                # Assume decimal
                return int(content, 10), "decimal"
        else:
            # Use specified base
            base_map = {
                "binary": 2,
                "octal": 8,
                "decimal": 10,
                "hex": 16,
                "hexadecimal": 16,
            }

            if from_base not in base_map:
                raise ValueError(f"Unsupported base: {from_base}")

            # Remove common prefixes if present
            clean_content = content
            if from_base in ["hex", "hexadecimal"] and (
                content.startswith("0x") or content.startswith("0X")
            ):
                clean_content = content[2:]
            elif from_base == "binary" and (
                content.startswith("0b") or content.startswith("0B")
            ):
                clean_content = content[2:]
            elif from_base == "octal" and (
                content.startswith("0o") or content.startswith("0O")
            ):
                clean_content = content[2:]

            return int(clean_content, base_map[from_base]), from_base

    def _convert_to_base(self, decimal_value: int, to_base: str) -> str:
        """
        Convert a decimal value to the specified base.

        Args:
            decimal_value: Decimal integer to convert
            to_base: Target base

        Returns:
            String representation in target base
        """
        if to_base == "binary":
            return bin(decimal_value)[2:]
        elif to_base == "octal":
            return oct(decimal_value)[2:]
        elif to_base == "decimal":
            return str(decimal_value)
        elif to_base in ["hex", "hexadecimal"]:
            return hex(decimal_value)[2:].upper()
        else:
            raise ValueError(f"Unsupported target base: {to_base}")

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Number Base Converter

DESCRIPTION:
    Convert numbers between binary, octal, decimal, and hexadecimal bases.

USAGE:
    devknife base [options] <number>
    echo "<number>" | devknife base [options]

OPTIONS:
    --from <base>   Source base (auto, binary, octal, decimal, hex) [default: auto]
    --to <base>     Target base (binary, octal, decimal, hex, all) [default: all]

EXAMPLES:
    devknife base 255
    devknife base 0xFF --from hex --to binary
    devknife base 1010 --from binary
    echo "777" | devknife base --from octal --to decimal
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input contains a valid number
        """
        try:
            content = input_data.as_string().strip()
            if not content:
                return False

            # Try to parse the number
            self._parse_number(content, "auto")
            return True
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="base",
            description="Convert numbers between different bases (binary, octal, decimal, hexadecimal)",
            category="math",
            module="devknife.utils.math_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["from_base", "to_base"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife base 255",
            "devknife base 0xFF --from hex --to binary",
            "devknife base 1010 --from binary",
            'echo "777" | devknife base --from octal --to decimal',
        ]


class HashGenerator(UtilityModule):
    """
    Utility for generating MD5, SHA1, and SHA256 hashes.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by generating hash values.

        Args:
            input_data: Input data to hash
            options: Processing options (algorithm)

        Returns:
            ProcessingResult with hash values
        """
        try:
            content = input_data.as_string()
            algorithm = options.get("algorithm", "all")

            # Generate hashes
            if algorithm == "all":
                # Generate all supported hashes
                hashes = {
                    "md5": hashlib.md5(content.encode("utf-8")).hexdigest(),
                    "sha1": hashlib.sha1(content.encode("utf-8")).hexdigest(),
                    "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                }

                output_lines = [
                    f"Input: {repr(content)}",
                    f"MD5: {hashes['md5']}",
                    f"SHA1: {hashes['sha1']}",
                    f"SHA256: {hashes['sha256']}",
                ]

                return ProcessingResult(
                    success=True,
                    output="\n".join(output_lines),
                    metadata={
                        "operation": "hash_generation",
                        "input_length": len(content),
                        "hashes": hashes,
                    },
                )
            else:
                # Generate specific hash
                try:
                    hash_value = self._generate_hash(content, algorithm)

                    return ProcessingResult(
                        success=True,
                        output=hash_value,
                        metadata={
                            "operation": "hash_generation",
                            "algorithm": algorithm,
                            "input_length": len(content),
                            "hash_value": hash_value,
                        },
                    )
                except ValueError as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Invalid hash algorithm: {str(e)}",
                    )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to generate hash: {str(e)}",
            )

    def _generate_hash(self, content: str, algorithm: str) -> str:
        """
        Generate a hash using the specified algorithm.

        Args:
            content: Content to hash
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

        Returns:
            Hexadecimal hash string
        """
        content_bytes = content.encode("utf-8")

        if algorithm == "md5":
            return hashlib.md5(content_bytes).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(content_bytes).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(content_bytes).hexdigest()
        else:
            raise ValueError(
                f"Unsupported hash algorithm: {algorithm}. Supported: md5, sha1, sha256"
            )

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Hash Generator

DESCRIPTION:
    Generate MD5, SHA1, and SHA256 hash values for input text.

USAGE:
    devknife hash [options] <text>
    echo "<text>" | devknife hash [options]

OPTIONS:
    --algorithm <alg>   Hash algorithm (md5, sha1, sha256, all) [default: all]

EXAMPLES:
    devknife hash "Hello, World!"
    devknife hash "password123" --algorithm sha256
    echo "secret data" | devknife hash --algorithm md5
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data (always valid for hashing).

        Args:
            input_data: Input data to validate

        Returns:
            Always True for hash generation
        """
        return True

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="hash",
            description="Generate MD5, SHA1, and SHA256 hash values",
            category="math",
            module="devknife.utils.math_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["algorithm"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife hash "Hello, World!"',
            'devknife hash "password123" --algorithm sha256',
            'echo "secret data" | devknife hash --algorithm md5',
        ]


class TimestampConverter(UtilityModule):
    """
    Utility for converting Unix timestamps to human-readable format and vice versa.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by converting timestamps.

        Args:
            input_data: Input data containing timestamp
            options: Processing options (format, timezone)

        Returns:
            ProcessingResult with converted timestamp
        """
        try:
            content = input_data.as_string().strip()
            output_format = options.get("format", "iso")
            use_utc = options.get("utc", False)
            reverse = options.get("reverse", False)

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty input provided. Please provide a timestamp to convert.",
                )

            if reverse:
                # Convert human-readable date to Unix timestamp
                return self._convert_to_timestamp(content)
            else:
                # Convert Unix timestamp to human-readable format
                return self._convert_from_timestamp(content, output_format, use_utc)

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to convert timestamp: {str(e)}",
            )

    def _convert_from_timestamp(
        self, content: str, output_format: str, use_utc: bool
    ) -> ProcessingResult:
        """
        Convert Unix timestamp to human-readable format.

        Args:
            content: Unix timestamp string
            output_format: Output format ('iso', 'readable', 'custom')
            use_utc: Whether to use UTC timezone

        Returns:
            ProcessingResult with converted timestamp
        """
        try:
            # Parse timestamp (handle both seconds and milliseconds)
            if "." in content:
                timestamp = float(content)
            else:
                timestamp = int(content)
                # If timestamp is very large, it might be in milliseconds
                if timestamp > 1e10:
                    timestamp = timestamp / 1000

            # Create datetime object
            if use_utc:
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            else:
                dt = datetime.fromtimestamp(timestamp)

            # Format output
            if output_format == "iso":
                formatted = dt.isoformat()
            elif output_format == "readable":
                formatted = dt.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
            else:
                # Default to ISO format for unknown formats
                formatted = dt.isoformat()

            # Additional information
            output_lines = [
                f"Unix Timestamp: {timestamp}",
                f"Formatted: {formatted}",
                f"Timezone: {'UTC' if use_utc else 'Local'}",
                f"Day of Week: {dt.strftime('%A')}",
                f"Relative: {self._get_relative_time(dt)}",
            ]

            return ProcessingResult(
                success=True,
                output="\n".join(output_lines),
                metadata={
                    "operation": "timestamp_to_date",
                    "input_timestamp": timestamp,
                    "formatted_date": formatted,
                    "timezone": "UTC" if use_utc else "Local",
                    "format": output_format,
                },
            )

        except (ValueError, OSError) as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Invalid timestamp format: {str(e)}. Please provide a valid Unix timestamp.",
            )

    def _convert_to_timestamp(self, content: str) -> ProcessingResult:
        """
        Convert human-readable date to Unix timestamp.

        Args:
            content: Date string to convert

        Returns:
            ProcessingResult with Unix timestamp
        """
        try:
            # Try common date formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%m/%d/%Y %H:%M:%S",
                "%m/%d/%Y",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
            ]

            dt = None
            used_format = None

            for fmt in formats:
                try:
                    dt = datetime.strptime(content, fmt)
                    used_format = fmt
                    break
                except ValueError:
                    continue

            if dt is None:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Could not parse date format: {content}. Try formats like 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'.",
                )

            # Convert to timestamp
            timestamp = dt.timestamp()

            output_lines = [
                f"Input: {content}",
                f"Parsed Format: {used_format}",
                f"Unix Timestamp: {int(timestamp)}",
                f"Unix Timestamp (float): {timestamp}",
                f"ISO Format: {dt.isoformat()}",
            ]

            return ProcessingResult(
                success=True,
                output="\n".join(output_lines),
                metadata={
                    "operation": "date_to_timestamp",
                    "input_date": content,
                    "parsed_format": used_format,
                    "timestamp": timestamp,
                    "timestamp_int": int(timestamp),
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to parse date: {str(e)}",
            )

    def _get_relative_time(self, dt: datetime) -> str:
        """
        Get relative time description.

        Args:
            dt: Datetime object

        Returns:
            Relative time string
        """
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        elif diff.seconds > 0:
            return f"{diff.seconds} seconds ago"
        else:
            future_diff = dt - now
            if future_diff.days > 0:
                return f"in {future_diff.days} days"
            elif future_diff.seconds > 3600:
                hours = future_diff.seconds // 3600
                return f"in {hours} hours"
            elif future_diff.seconds > 60:
                minutes = future_diff.seconds // 60
                return f"in {minutes} minutes"
            else:
                return "now"

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Timestamp Converter

DESCRIPTION:
    Convert Unix timestamps to human-readable format and vice versa.

USAGE:
    devknife timestamp [options] <timestamp_or_date>
    echo "<timestamp>" | devknife timestamp [options]

OPTIONS:
    --format <fmt>      Output format (iso, readable) [default: iso]
    --utc              Use UTC timezone instead of local
    --reverse          Convert date string to Unix timestamp

EXAMPLES:
    devknife timestamp 1640995200
    devknife timestamp 1640995200 --utc --format readable
    devknife timestamp "2022-01-01 00:00:00" --reverse
    echo "1640995200" | devknife timestamp --format readable
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input contains a valid timestamp or date
        """
        try:
            content = input_data.as_string().strip()
            if not content:
                return False

            # Try to parse as timestamp first
            try:
                if "." in content:
                    float(content)
                else:
                    int(content)
                return True
            except ValueError:
                pass

            # Try to parse as date
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
            ]

            for fmt in formats:
                try:
                    datetime.strptime(content, fmt)
                    return True
                except ValueError:
                    continue

            return False
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="timestamp",
            description="Convert Unix timestamps to human-readable format and vice versa",
            category="math",
            module="devknife.utils.math_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["format", "utc", "reverse"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife timestamp 1640995200",
            "devknife timestamp 1640995200 --utc --format readable",
            'devknife timestamp "2022-01-01 00:00:00" --reverse',
            'echo "1640995200" | devknife timestamp --format readable',
        ]
