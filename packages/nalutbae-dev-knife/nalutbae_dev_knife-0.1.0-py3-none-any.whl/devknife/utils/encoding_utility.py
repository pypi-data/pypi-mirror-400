"""
Encoding and decoding utility module for Base64 and URL encoding.
"""

import base64
import re
import urllib.parse
from typing import Any, Dict, List
from devknife.core import UtilityModule, Command, InputData, ProcessingResult


class Base64EncoderDecoder(UtilityModule):
    """
    Utility for Base64 encoding and decoding operations.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by encoding or decoding Base64.

        Args:
            input_data: Input data to process
            options: Processing options (decode flag)

        Returns:
            ProcessingResult with encoded/decoded content
        """
        try:
            content = input_data.as_string().strip()
            decode_mode = options.get("decode", False)

            if decode_mode:
                # Decode Base64
                try:
                    # Validate Base64 format
                    if not self._is_valid_base64(content):
                        return ProcessingResult(
                            success=False,
                            output=None,
                            error_message="Invalid Base64 format. Base64 strings should only contain A-Z, a-z, 0-9, +, /, and = for padding.",
                        )

                    decoded_bytes = base64.b64decode(content)
                    decoded_text = decoded_bytes.decode("utf-8")

                    return ProcessingResult(
                        success=True,
                        output=decoded_text,
                        metadata={
                            "operation": "decode",
                            "input_length": len(content),
                            "output_length": len(decoded_text),
                        },
                    )

                except Exception as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Failed to decode Base64: {str(e)}",
                    )
            else:
                # Encode to Base64
                try:
                    content_bytes = content.encode("utf-8")
                    encoded = base64.b64encode(content_bytes).decode("ascii")

                    return ProcessingResult(
                        success=True,
                        output=encoded,
                        metadata={
                            "operation": "encode",
                            "input_length": len(content),
                            "output_length": len(encoded),
                        },
                    )

                except Exception as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Failed to encode to Base64: {str(e)}",
                    )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process input: {str(e)}",
            )

    def _is_valid_base64(self, s: str) -> bool:
        """
        Check if a string is valid Base64 format.

        Args:
            s: String to validate

        Returns:
            True if valid Base64, False otherwise
        """
        # Base64 pattern: only A-Z, a-z, 0-9, +, / and = for padding
        base64_pattern = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")

        if not base64_pattern.match(s):
            return False

        # Check length (must be multiple of 4)
        if len(s) % 4 != 0:
            return False

        # Check padding
        padding_count = s.count("=")
        if padding_count > 2:
            return False

        # If there's padding, it should only be at the end
        if padding_count > 0:
            if not s.endswith("=" * padding_count):
                return False
            # Remove padding and check if remaining length is correct
            s_no_padding = s.rstrip("=")
            if len(s_no_padding) % 4 == 1:  # Invalid padding scenario
                return False

        return True

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
Base64 Encoder/Decoder

DESCRIPTION:
    Encode text to Base64 or decode Base64 strings back to text.

USAGE:
    devknife base64 [options] <text>
    echo "text" | devknife base64 [options]

OPTIONS:
    --decode    Decode Base64 input instead of encoding

EXAMPLES:
    devknife base64 "Hello World"
    devknife base64 --decode "SGVsbG8gV29ybGQ="
    echo "Hello World" | devknife base64
    echo "SGVsbG8gV29ybGQ=" | devknife base64 --decode
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
            name="base64",
            description="Encode text to Base64 or decode Base64 strings",
            category="encoding",
            module="devknife.utils.encoding_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["decode"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife base64 "Hello World"',
            'devknife base64 --decode "SGVsbG8gV29ybGQ="',
            'echo "Hello World" | devknife base64',
            'echo "SGVsbG8gV29ybGQ=" | devknife base64 --decode',
        ]


class URLEncoderDecoder(UtilityModule):
    """
    Utility for URL encoding and decoding operations.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by URL encoding or decoding.

        Args:
            input_data: Input data to process
            options: Processing options (decode flag)

        Returns:
            ProcessingResult with encoded/decoded content
        """
        try:
            content = input_data.as_string().strip()
            decode_mode = options.get("decode", False)

            if decode_mode:
                # Decode URL
                try:
                    decoded = urllib.parse.unquote(content)

                    return ProcessingResult(
                        success=True,
                        output=decoded,
                        metadata={
                            "operation": "decode",
                            "input_length": len(content),
                            "output_length": len(decoded),
                        },
                    )

                except Exception as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Failed to decode URL: {str(e)}",
                    )
            else:
                # Encode URL
                try:
                    encoded = urllib.parse.quote(content, safe="")

                    # Validate that encoded string contains only URL-safe characters
                    if not self._is_url_safe(encoded):
                        return ProcessingResult(
                            success=False,
                            output=None,
                            error_message="URL encoding produced unsafe characters",
                        )

                    return ProcessingResult(
                        success=True,
                        output=encoded,
                        metadata={
                            "operation": "encode",
                            "input_length": len(content),
                            "output_length": len(encoded),
                        },
                    )

                except Exception as e:
                    return ProcessingResult(
                        success=False,
                        output=None,
                        error_message=f"Failed to encode URL: {str(e)}",
                    )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process input: {str(e)}",
            )

    def _is_url_safe(self, s: str) -> bool:
        """
        Check if a string contains only URL-safe characters.

        Args:
            s: String to validate

        Returns:
            True if URL-safe, False otherwise
        """
        # URL-safe characters: A-Z, a-z, 0-9, -, _, ., ~, and % for percent encoding
        url_safe_pattern = re.compile(r"^[A-Za-z0-9\-_.~%]*$")
        return url_safe_pattern.match(s) is not None

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
URL Encoder/Decoder

DESCRIPTION:
    Encode text for safe use in URLs or decode URL-encoded strings.

USAGE:
    devknife url [options] <text>
    echo "text" | devknife url [options]

OPTIONS:
    --decode    Decode URL-encoded input instead of encoding

EXAMPLES:
    devknife url "Hello World!"
    devknife url --decode "Hello%20World%21"
    echo "Hello World!" | devknife url
    echo "Hello%20World%21" | devknife url --decode
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
            name="url",
            description="Encode text for URLs or decode URL-encoded strings",
            category="encoding",
            module="devknife.utils.encoding_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["decode"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            'devknife url "Hello World!"',
            'devknife url --decode "Hello%20World%21"',
            'echo "Hello World!" | devknife url',
            'echo "Hello%20World%21" | devknife url --decode',
        ]
