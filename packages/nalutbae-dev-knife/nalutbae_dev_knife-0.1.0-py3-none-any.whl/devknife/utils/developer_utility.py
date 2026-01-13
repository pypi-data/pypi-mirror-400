"""
Developer utility module for UUID generation/decoding, IBAN validation, and password generation.
"""

import re
import secrets
import string
import uuid
from datetime import datetime
from typing import Any, Dict, List
from devknife.core import UtilityModule, Command, InputData, ProcessingResult


class UUIDGenerator(UtilityModule):
    """
    Utility for generating UUIDs.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Generate a new UUID.

        Args:
            input_data: Input data (not used for generation)
            options: Processing options (version type)

        Returns:
            ProcessingResult with generated UUID
        """
        try:
            version = options.get("version", 4)

            if version == 1:
                generated_uuid = uuid.uuid1()
            elif version == 4:
                generated_uuid = uuid.uuid4()
            else:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"Unsupported UUID version: {version}. Supported versions: 1, 4",
                )

            uuid_str = str(generated_uuid)

            return ProcessingResult(
                success=True,
                output=uuid_str,
                metadata={
                    "operation": "generate",
                    "version": version,
                    "format": "standard",
                    "length": len(uuid_str),
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to generate UUID: {str(e)}",
            )

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
UUID Generator

DESCRIPTION:
    Generate new UUIDs (Universally Unique Identifiers).

USAGE:
    devknife uuid-gen [options]

OPTIONS:
    --version <1|4>    UUID version to generate (default: 4)
                      Version 1: Time-based UUID
                      Version 4: Random UUID

EXAMPLES:
    devknife uuid-gen
    devknife uuid-gen --version 1
    devknife uuid-gen --version 4
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data (always valid for UUID generation).

        Args:
            input_data: Input data to validate

        Returns:
            Always True for UUID generation
        """
        return True

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="uuid-gen",
            description="Generate new UUIDs",
            category="developer",
            module="devknife.utils.developer_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["version"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife uuid-gen",
            "devknife uuid-gen --version 1",
            "devknife uuid-gen --version 4",
        ]


class UUIDDecoder(UtilityModule):
    """
    Utility for decoding and analyzing UUIDs.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Decode and analyze a UUID.

        Args:
            input_data: Input data containing UUID string
            options: Processing options

        Returns:
            ProcessingResult with UUID analysis
        """
        try:
            uuid_str = input_data.as_string().strip()

            # Validate UUID format
            if not self._is_valid_uuid(uuid_str):
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Invalid UUID format. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                )

            try:
                parsed_uuid = uuid.UUID(uuid_str)
            except ValueError as e:
                return ProcessingResult(
                    success=False, output=None, error_message=f"Invalid UUID: {str(e)}"
                )

            # Analyze UUID
            analysis = {
                "uuid": str(parsed_uuid),
                "version": parsed_uuid.version,
                "variant": self._get_variant_name(parsed_uuid.variant),
                "hex": parsed_uuid.hex,
                "int": parsed_uuid.int,
                "bytes": parsed_uuid.bytes.hex(),
                "fields": {
                    "time_low": parsed_uuid.time_low,
                    "time_mid": parsed_uuid.time_mid,
                    "time_hi_version": parsed_uuid.time_hi_version,
                    "clock_seq_hi_variant": parsed_uuid.clock_seq_hi_variant,
                    "clock_seq_low": parsed_uuid.clock_seq_low,
                    "node": parsed_uuid.node,
                },
            }

            # Add version-specific information
            if parsed_uuid.version == 1:
                # Time-based UUID
                timestamp = parsed_uuid.time
                # Convert UUID timestamp to Unix timestamp
                # UUID timestamp is 100-nanosecond intervals since October 15, 1582
                unix_timestamp = (timestamp - 0x01B21DD213814000) / 10000000
                analysis["timestamp"] = {
                    "uuid_time": timestamp,
                    "unix_timestamp": unix_timestamp,
                    "datetime": (
                        datetime.fromtimestamp(unix_timestamp).isoformat()
                        if unix_timestamp > 0
                        else "Invalid"
                    ),
                }
                analysis["node"] = f"{parsed_uuid.node:012x}"
                analysis["clock_seq"] = parsed_uuid.clock_seq
            elif parsed_uuid.version == 4:
                analysis["note"] = "Random UUID - no timestamp or node information"

            # Format output
            output_lines = [
                f"UUID: {analysis['uuid']}",
                f"Version: {analysis['version']}",
                f"Variant: {analysis['variant']}",
                f"Hex: {analysis['hex']}",
                f"Integer: {analysis['int']}",
                f"Bytes: {analysis['bytes']}",
            ]

            if "timestamp" in analysis:
                output_lines.extend(
                    [
                        f"Timestamp: {analysis['timestamp']['datetime']}",
                        f"Unix Timestamp: {analysis['timestamp']['unix_timestamp']}",
                        f"Node: {analysis['node']}",
                        f"Clock Sequence: {analysis['clock_seq']}",
                    ]
                )
            elif "note" in analysis:
                output_lines.append(f"Note: {analysis['note']}")

            return ProcessingResult(
                success=True,
                output="\n".join(output_lines),
                metadata={
                    "operation": "decode",
                    "uuid_version": analysis["version"],
                    "analysis": analysis,
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to decode UUID: {str(e)}",
            )

    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """
        Check if a string is a valid UUID format.

        Args:
            uuid_str: String to validate

        Returns:
            True if valid UUID format, False otherwise
        """
        uuid_pattern = re.compile(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
        return uuid_pattern.match(uuid_str) is not None

    def _get_variant_name(self, variant: int) -> str:
        """
        Get human-readable variant name.

        Args:
            variant: UUID variant number

        Returns:
            Variant name string
        """
        if variant == uuid.RFC_4122:
            return "RFC 4122"
        elif variant == uuid.RESERVED_NCS:
            return "Reserved NCS"
        elif variant == uuid.RESERVED_MICROSOFT:
            return "Reserved Microsoft"
        elif variant == uuid.RESERVED_FUTURE:
            return "Reserved Future"
        else:
            return f"Unknown ({variant})"

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
UUID Decoder

DESCRIPTION:
    Decode and analyze UUID strings to extract version, timestamp, and other information.

USAGE:
    devknife uuid-decode <uuid>
    echo "<uuid>" | devknife uuid-decode

EXAMPLES:
    devknife uuid-decode "550e8400-e29b-41d4-a716-446655440000"
    echo "550e8400-e29b-41d4-a716-446655440000" | devknife uuid-decode
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input contains a valid UUID format
        """
        try:
            uuid_str = input_data.as_string().strip()
            return self._is_valid_uuid(uuid_str)
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="uuid-decode",
            description="Decode and analyze UUID strings",
            category="developer",
            module="devknife.utils.developer_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife uuid-decode "550e8400-e29b-41d4-a716-446655440000"',
            'echo "550e8400-e29b-41d4-a716-446655440000" | devknife uuid-decode',
        ]


class IBANValidator(UtilityModule):
    """
    Utility for validating IBAN (International Bank Account Number) codes.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Validate an IBAN code.

        Args:
            input_data: Input data containing IBAN string
            options: Processing options

        Returns:
            ProcessingResult with validation result
        """
        try:
            iban = input_data.as_string().strip().upper().replace(" ", "")

            # Basic format validation
            if not self._is_valid_iban_format(iban):
                return ProcessingResult(
                    success=True,
                    output="Invalid IBAN format",
                    metadata={
                        "operation": "validate",
                        "valid": False,
                        "iban": iban,
                        "error": "Invalid format",
                    },
                )

            # Length validation
            country_code = iban[:2]
            expected_length = self._get_iban_length(country_code)
            if expected_length and len(iban) != expected_length:
                return ProcessingResult(
                    success=True,
                    output=f"Invalid IBAN length for {country_code}. Expected {expected_length}, got {len(iban)}",
                    metadata={
                        "operation": "validate",
                        "valid": False,
                        "iban": iban,
                        "country_code": country_code,
                        "expected_length": expected_length,
                        "actual_length": len(iban),
                        "error": "Invalid length",
                    },
                )

            # Checksum validation using mod-97 algorithm
            is_valid = self._validate_iban_checksum(iban)

            if is_valid:
                output = f"Valid IBAN: {iban}"
                formatted_iban = self._format_iban(iban)
                if formatted_iban != iban:
                    output += f"\nFormatted: {formatted_iban}"
            else:
                output = f"Invalid IBAN checksum: {iban}"

            return ProcessingResult(
                success=True,
                output=output,
                metadata={
                    "operation": "validate",
                    "valid": is_valid,
                    "iban": iban,
                    "country_code": country_code,
                    "formatted": self._format_iban(iban) if is_valid else None,
                    "length": len(iban),
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to validate IBAN: {str(e)}",
            )

    def _is_valid_iban_format(self, iban: str) -> bool:
        """
        Check if IBAN has valid basic format.

        Args:
            iban: IBAN string to validate

        Returns:
            True if format is valid, False otherwise
        """
        # IBAN should be 15-34 characters, start with 2 letters, followed by 2 digits, then alphanumeric
        iban_pattern = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$")
        return (
            len(iban) >= 15 and len(iban) <= 34 and iban_pattern.match(iban) is not None
        )

    def _get_iban_length(self, country_code: str) -> int:
        """
        Get expected IBAN length for a country code.

        Args:
            country_code: Two-letter country code

        Returns:
            Expected IBAN length or 0 if unknown
        """
        # Common IBAN lengths by country
        lengths = {
            "AD": 24,
            "AE": 23,
            "AL": 28,
            "AT": 20,
            "AZ": 28,
            "BA": 20,
            "BE": 16,
            "BG": 22,
            "BH": 22,
            "BR": 29,
            "BY": 28,
            "CH": 21,
            "CR": 22,
            "CY": 28,
            "CZ": 24,
            "DE": 22,
            "DK": 18,
            "DO": 28,
            "EE": 20,
            "EG": 29,
            "ES": 24,
            "FI": 18,
            "FO": 18,
            "FR": 27,
            "GB": 22,
            "GE": 22,
            "GI": 23,
            "GL": 18,
            "GR": 27,
            "GT": 28,
            "HR": 21,
            "HU": 28,
            "IE": 22,
            "IL": 23,
            "IS": 26,
            "IT": 27,
            "JO": 30,
            "KW": 30,
            "KZ": 20,
            "LB": 28,
            "LC": 32,
            "LI": 21,
            "LT": 20,
            "LU": 20,
            "LV": 21,
            "MC": 27,
            "MD": 24,
            "ME": 22,
            "MK": 19,
            "MR": 27,
            "MT": 31,
            "MU": 30,
            "NL": 18,
            "NO": 15,
            "PK": 24,
            "PL": 28,
            "PS": 29,
            "PT": 25,
            "QA": 29,
            "RO": 24,
            "RS": 22,
            "SA": 24,
            "SE": 24,
            "SI": 19,
            "SK": 24,
            "SM": 27,
            "TN": 24,
            "TR": 26,
            "UA": 29,
            "VG": 24,
            "XK": 20,
        }
        return lengths.get(country_code, 0)

    def _validate_iban_checksum(self, iban: str) -> bool:
        """
        Validate IBAN using mod-97 checksum algorithm.

        Args:
            iban: IBAN string to validate

        Returns:
            True if checksum is valid, False otherwise
        """
        # Move first 4 characters to end
        rearranged = iban[4:] + iban[:4]

        # Replace letters with numbers (A=10, B=11, ..., Z=35)
        numeric_string = ""
        for char in rearranged:
            if char.isalpha():
                numeric_string += str(ord(char) - ord("A") + 10)
            else:
                numeric_string += char

        # Calculate mod 97
        return int(numeric_string) % 97 == 1

    def _format_iban(self, iban: str) -> str:
        """
        Format IBAN with spaces for readability.

        Args:
            iban: IBAN string to format

        Returns:
            Formatted IBAN string
        """
        # Add space every 4 characters
        return " ".join(iban[i : i + 4] for i in range(0, len(iban), 4))

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
IBAN Validator

DESCRIPTION:
    Validate International Bank Account Number (IBAN) codes using checksum verification.

USAGE:
    devknife iban <iban>
    echo "<iban>" | devknife iban

EXAMPLES:
    devknife iban "GB82WEST12345698765432"
    devknife iban "DE89 3704 0044 0532 0130 00"
    echo "GB82WEST12345698765432" | devknife iban
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if input contains potential IBAN
        """
        try:
            iban = input_data.as_string().strip().upper().replace(" ", "")
            return (
                len(iban) >= 15
                and len(iban) <= 34
                and iban[:2].isalpha()
                and iban[2:4].isdigit()
            )
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="iban",
            description="Validate IBAN codes with checksum verification",
            category="developer",
            module="devknife.utils.developer_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife iban "GB82WEST12345698765432"',
            'devknife iban "DE89 3704 0044 0532 0130 00"',
            'echo "GB82WEST12345698765432" | devknife iban',
        ]


class PasswordGenerator(UtilityModule):
    """
    Utility for generating secure passwords with customizable complexity.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Generate a secure password.

        Args:
            input_data: Input data (not used for generation)
            options: Processing options (length, complexity settings)

        Returns:
            ProcessingResult with generated password
        """
        try:
            # Parse options
            length = options.get("length", 16)
            include_uppercase = options.get("uppercase", True)
            include_lowercase = options.get("lowercase", True)
            include_digits = options.get("digits", True)
            include_symbols = options.get("symbols", True)
            exclude_ambiguous = options.get("no_ambiguous", False)

            # Validate length
            if length < 4:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Password length must be at least 4 characters",
                )

            if length > 256:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Password length cannot exceed 256 characters",
                )

            # Build character set
            charset = ""
            required_chars = []

            if include_lowercase:
                lowercase = string.ascii_lowercase
                if exclude_ambiguous:
                    lowercase = lowercase.replace("l", "").replace("o", "")
                charset += lowercase
                if lowercase:
                    required_chars.append(secrets.choice(lowercase))

            if include_uppercase:
                uppercase = string.ascii_uppercase
                if exclude_ambiguous:
                    uppercase = uppercase.replace("I", "").replace("O", "")
                charset += uppercase
                if uppercase:
                    required_chars.append(secrets.choice(uppercase))

            if include_digits:
                digits = string.digits
                if exclude_ambiguous:
                    digits = digits.replace("0", "").replace("1", "")
                charset += digits
                if digits:
                    required_chars.append(secrets.choice(digits))

            if include_symbols:
                symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                if exclude_ambiguous:
                    # Remove potentially ambiguous symbols
                    symbols = (
                        symbols.replace("|", "")
                        .replace("l", "")
                        .replace("1", "")
                        .replace("0", "")
                        .replace("O", "")
                    )
                charset += symbols
                if symbols:
                    required_chars.append(secrets.choice(symbols))

            if not charset:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="No character types selected. At least one character type must be enabled.",
                )

            # Generate password
            password_chars = required_chars[:]
            remaining_length = length - len(required_chars)

            # Fill remaining positions with random characters
            for _ in range(remaining_length):
                password_chars.append(secrets.choice(charset))

            # Shuffle to avoid predictable patterns
            secrets.SystemRandom().shuffle(password_chars)
            password = "".join(password_chars)

            # Calculate strength score
            strength_score = self._calculate_strength(password)
            strength_level = self._get_strength_level(strength_score)

            return ProcessingResult(
                success=True,
                output=password,
                metadata={
                    "operation": "generate",
                    "length": len(password),
                    "charset_size": len(charset),
                    "strength_score": strength_score,
                    "strength_level": strength_level,
                    "character_types": {
                        "uppercase": include_uppercase,
                        "lowercase": include_lowercase,
                        "digits": include_digits,
                        "symbols": include_symbols,
                    },
                    "exclude_ambiguous": exclude_ambiguous,
                },
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to generate password: {str(e)}",
            )

    def _calculate_strength(self, password: str) -> int:
        """
        Calculate password strength score.

        Args:
            password: Password to analyze

        Returns:
            Strength score (0-100)
        """
        score = 0

        # Length bonus
        score += min(password.__len__() * 2, 50)

        # Character variety bonus
        if any(c.islower() for c in password):
            score += 5
        if any(c.isupper() for c in password):
            score += 5
        if any(c.isdigit() for c in password):
            score += 5
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 10

        # Unique characters bonus
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 25)

        return min(score, 100)

    def _get_strength_level(self, score: int) -> str:
        """
        Get strength level description.

        Args:
            score: Strength score

        Returns:
            Strength level string
        """
        if score >= 80:
            return "Very Strong"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak"

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Password Generator

DESCRIPTION:
    Generate secure passwords with customizable length and complexity requirements.

USAGE:
    devknife password [options]

OPTIONS:
    --length <n>        Password length (default: 16, min: 4, max: 256)
    --no-uppercase      Exclude uppercase letters
    --no-lowercase      Exclude lowercase letters
    --no-digits         Exclude digits
    --no-symbols        Exclude symbols
    --no-ambiguous      Exclude ambiguous characters (0, O, l, 1, |)

EXAMPLES:
    devknife password
    devknife password --length 32
    devknife password --length 12 --no-symbols
    devknife password --length 20 --no-ambiguous
        """.strip()

    def validate_input(self, input_data: InputData) -> bool:
        """
        Validate input data (always valid for password generation).

        Args:
            input_data: Input data to validate

        Returns:
            Always True for password generation
        """
        return True

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="password",
            description="Generate secure passwords with customizable complexity",
            category="developer",
            module="devknife.utils.developer_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["length", "uppercase", "lowercase", "digits", "symbols", "no_ambiguous"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife password",
            "devknife password --length 32",
            "devknife password --length 12 --no-symbols",
            "devknife password --length 20 --no-ambiguous",
        ]
