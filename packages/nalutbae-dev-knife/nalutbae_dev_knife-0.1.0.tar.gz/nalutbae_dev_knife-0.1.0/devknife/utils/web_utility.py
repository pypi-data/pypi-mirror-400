"""
Web development utility module for GraphQL, CSS, and HTML processing.
"""

import re
import json
from typing import Any, Dict, List
from urllib.parse import urljoin, urlparse
from devknife.core import UtilityModule, Command, InputData, ProcessingResult


class GraphQLFormatter(UtilityModule):
    """
    Utility for formatting and validating GraphQL queries.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by formatting GraphQL query.

        Args:
            input_data: Input data to process
            options: Processing options (indent)

        Returns:
            ProcessingResult with formatted GraphQL query
        """
        try:
            content = input_data.as_string().strip()
            indent = options.get("indent", 2)

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty GraphQL query provided",
                )

            # Basic GraphQL validation and formatting
            try:
                formatted_query = self._format_graphql(content, indent)

                return ProcessingResult(
                    success=True,
                    output=formatted_query,
                    metadata={
                        "operation": "format",
                        "input_length": len(content),
                        "output_length": len(formatted_query),
                        "indent": indent,
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"GraphQL formatting error: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process GraphQL query: {str(e)}",
            )

    def _format_graphql(self, query: str, indent: int) -> str:
        """
        Format GraphQL query with proper indentation.

        Args:
            query: GraphQL query string
            indent: Number of spaces for indentation

        Returns:
            Formatted GraphQL query
        """
        # Remove extra whitespace and normalize
        query = re.sub(r"\s+", " ", query.strip())

        # Basic GraphQL formatting
        formatted = query

        # Add newlines after opening braces
        formatted = re.sub(r"\{\s*", "{\n", formatted)

        # Add newlines before closing braces
        formatted = re.sub(r"\s*\}", "\n}", formatted)

        # Add newlines after commas in field lists
        formatted = re.sub(r",\s*(?=[a-zA-Z_])", ",\n", formatted)

        # Split into lines and apply indentation
        lines = formatted.split("\n")
        indented_lines = []
        current_indent = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Decrease indent for closing braces
            if line.startswith("}"):
                current_indent = max(0, current_indent - indent)

            # Add indentation
            indented_lines.append(" " * current_indent + line)

            # Increase indent for opening braces
            if line.endswith("{"):
                current_indent += indent

        return "\n".join(indented_lines)

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
GraphQL Formatter

DESCRIPTION:
    Format GraphQL queries with proper indentation and validation.

USAGE:
    devknife graphql [options] <query>
    echo 'query { user { name email } }' | devknife graphql [options]

OPTIONS:
    --indent N      Number of spaces for indentation (default: 2)

EXAMPLES:
    devknife graphql 'query { user { name email } }'
    echo 'mutation { createUser(input: { name: "John" }) { id } }' | devknife graphql --indent 4
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

            # Basic GraphQL syntax check - must have both keyword and braces
            has_keyword = any(
                keyword in content.lower()
                for keyword in ["query", "mutation", "subscription"]
            )
            has_braces = "{" in content and "}" in content
            return has_keyword and has_braces
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="graphql",
            description="Format GraphQL queries with proper indentation and validation",
            category="web",
            module="devknife.utils.web_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["indent"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife graphql 'query { user { name email } }'",
            "echo 'mutation { createUser(input: { name: \"John\" }) { id } }' | devknife graphql --indent 4",
        ]


class CSSFormatter(UtilityModule):
    """
    Utility for formatting CSS with proper indentation.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by formatting CSS.

        Args:
            input_data: Input data to process
            options: Processing options (indent)

        Returns:
            ProcessingResult with formatted CSS
        """
        try:
            content = input_data.as_string().strip()
            indent = options.get("indent", 2)

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty CSS content provided",
                )

            # Format CSS
            try:
                formatted_css = self._format_css(content, indent)

                return ProcessingResult(
                    success=True,
                    output=formatted_css,
                    metadata={
                        "operation": "format",
                        "input_length": len(content),
                        "output_length": len(formatted_css),
                        "indent": indent,
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"CSS formatting error: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process CSS: {str(e)}",
            )

    def _format_css(self, css: str, indent: int) -> str:
        """
        Format CSS with proper indentation.

        Args:
            css: CSS string to format
            indent: Number of spaces for indentation

        Returns:
            Formatted CSS string
        """
        # Remove extra whitespace
        css = re.sub(r"\s+", " ", css.strip())

        # Add newlines after opening braces
        css = re.sub(r"\{\s*", " {\n", css)

        # Add newlines before closing braces
        css = re.sub(r"\s*\}", "\n}", css)

        # Add newlines after semicolons
        css = re.sub(r";\s*", ";\n", css)

        # Add newlines after commas in selectors
        css = re.sub(r",\s*(?=[^}]*\{)", ",\n", css)

        # Split into lines and apply indentation
        lines = css.split("\n")
        formatted_lines = []
        current_indent = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle closing braces
            if line == "}":
                current_indent = max(0, current_indent - indent)
                formatted_lines.append(" " * current_indent + line)
                if formatted_lines:  # Add empty line after rule blocks
                    formatted_lines.append("")
                continue

            # Handle opening braces
            if line.endswith("{"):
                formatted_lines.append(" " * current_indent + line)
                current_indent += indent
                continue

            # Handle properties and selectors
            if ":" in line and not line.endswith("{"):
                # CSS property
                formatted_lines.append(" " * current_indent + line)
            else:
                # Selector or other
                formatted_lines.append(" " * current_indent + line)

        # Remove trailing empty lines and join
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()

        return "\n".join(formatted_lines)

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
CSS Formatter

DESCRIPTION:
    Format CSS with proper indentation for better readability.

USAGE:
    devknife css [options] <css_content>
    echo 'body{margin:0;padding:0}h1{color:red}' | devknife css [options]

OPTIONS:
    --indent N      Number of spaces for indentation (default: 2)

EXAMPLES:
    devknife css 'body{margin:0;padding:0}h1{color:red}'
    echo '.container{width:100%;max-width:1200px}' | devknife css --indent 4
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

            # Basic CSS syntax check - look for selectors and properties
            return "{" in content and "}" in content
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="css",
            description="Format CSS with proper indentation for better readability",
            category="web",
            module="devknife.utils.web_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["indent"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife css 'body{margin:0;padding:0}h1{color:red}'",
            "echo '.container{width:100%;max-width:1200px}' | devknife css --indent 4",
        ]


class CSSMinifier(UtilityModule):
    """
    Utility for minifying CSS by removing unnecessary whitespace and comments.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by minifying CSS.

        Args:
            input_data: Input data to process
            options: Processing options

        Returns:
            ProcessingResult with minified CSS
        """
        try:
            content = input_data.as_string().strip()

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty CSS content provided",
                )

            # Minify CSS
            try:
                minified_css = self._minify_css(content)

                compression_ratio = (
                    (1 - len(minified_css) / len(content)) * 100 if content else 0
                )

                return ProcessingResult(
                    success=True,
                    output=minified_css,
                    metadata={
                        "operation": "minify",
                        "input_length": len(content),
                        "output_length": len(minified_css),
                        "compression_ratio": f"{compression_ratio:.1f}%",
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"CSS minification error: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process CSS: {str(e)}",
            )

    def _minify_css(self, css: str) -> str:
        """
        Minify CSS by removing unnecessary whitespace and comments.

        Args:
            css: CSS string to minify

        Returns:
            Minified CSS string
        """
        # Remove comments
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)

        # Remove unnecessary whitespace
        css = re.sub(r"\s+", " ", css)

        # Remove whitespace around specific characters
        css = re.sub(r"\s*{\s*", "{", css)
        css = re.sub(r"\s*}\s*", "}", css)
        css = re.sub(r"\s*;\s*", ";", css)
        css = re.sub(r"\s*:\s*", ":", css)
        css = re.sub(r"\s*,\s*", ",", css)

        # Remove trailing semicolons before closing braces
        css = re.sub(r";}", "}", css)

        # Remove leading/trailing whitespace
        css = css.strip()

        return css

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
CSS Minifier

DESCRIPTION:
    Minify CSS by removing unnecessary whitespace, comments, and optimizing syntax.

USAGE:
    devknife css-min <css_content>
    echo 'body { margin: 0; padding: 0; }' | devknife css-min

EXAMPLES:
    devknife css-min 'body { margin: 0; padding: 0; } /* comment */'
    echo '.container { width: 100%; max-width: 1200px; }' | devknife css-min
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

            # Basic CSS syntax check - look for selectors and properties
            return "{" in content and "}" in content
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information for this utility."""
        return Command(
            name="css-min",
            description="Minify CSS by removing unnecessary whitespace and comments",
            category="web",
            module="devknife.utils.web_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife css-min 'body { margin: 0; padding: 0; } /* comment */'",
            "echo '.container { width: 100%; max-width: 1200px; }' | devknife css-min",
        ]


class URLExtractor(UtilityModule):
    """
    Utility for extracting URLs from HTML content.
    """

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process input by extracting URLs from HTML.

        Args:
            input_data: Input data to process
            options: Processing options (base_url, unique)

        Returns:
            ProcessingResult with extracted URLs
        """
        try:
            content = input_data.as_string().strip()
            base_url = options.get("base_url", "")
            unique_only = options.get("unique", True)

            if not content:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message="Empty HTML content provided",
                )

            # Extract URLs
            try:
                urls = self._extract_urls(content, base_url, unique_only)

                if not urls:
                    output = "No URLs found in the provided HTML content"
                else:
                    output = "\n".join(urls)

                return ProcessingResult(
                    success=True,
                    output=output,
                    metadata={
                        "operation": "extract_urls",
                        "input_length": len(content),
                        "urls_found": len(urls),
                        "unique_only": unique_only,
                        "base_url": base_url,
                    },
                )

            except Exception as e:
                return ProcessingResult(
                    success=False,
                    output=None,
                    error_message=f"URL extraction error: {str(e)}",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                output=None,
                error_message=f"Failed to process HTML: {str(e)}",
            )

    def _extract_urls(self, html: str, base_url: str, unique_only: bool) -> List[str]:
        """
        Extract URLs from HTML content.

        Args:
            html: HTML content to process
            base_url: Base URL for resolving relative URLs
            unique_only: Whether to return only unique URLs

        Returns:
            List of extracted URLs
        """
        urls = []

        # Patterns for different URL types
        patterns = [
            # href attributes
            r'href\s*=\s*["\']([^"\']+)["\']',
            # src attributes
            r'src\s*=\s*["\']([^"\']+)["\']',
            # action attributes
            r'action\s*=\s*["\']([^"\']+)["\']',
            # url() in CSS
            r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)',
        ]

        # Extract URLs from attributes first
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.strip()

                # Skip empty URLs, fragments, and javascript/mailto links
                if (
                    not url
                    or url.startswith("#")
                    or url.startswith("javascript:")
                    or url.startswith("mailto:")
                ):
                    continue

                # Resolve relative URLs if base_url is provided
                if base_url and not url.startswith(("http://", "https://", "//")):
                    try:
                        url = urljoin(base_url, url)
                    except Exception:
                        continue

                # Validate URL format
                try:
                    parsed = urlparse(url)
                    if (
                        parsed.scheme in ("http", "https", "ftp", "ftps")
                        or not parsed.scheme
                    ):
                        urls.append(url)
                except Exception:
                    continue

        # Then extract plain URLs from text (only if no attributes found)
        if not urls:
            plain_url_pattern = r'https?://[^\s<>"\']+'
            matches = re.findall(plain_url_pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.strip()
                try:
                    parsed = urlparse(url)
                    if parsed.scheme in ("http", "https"):
                        urls.append(url)
                except Exception:
                    continue

        # Remove duplicates if requested
        if unique_only:
            urls = list(
                dict.fromkeys(urls)
            )  # Preserves order while removing duplicates

        return urls

    def get_help(self) -> str:
        """Get help text for this utility."""
        return """
URL Extractor

DESCRIPTION:
    Extract all URLs from HTML content including href, src, and other URL attributes.

USAGE:
    devknife url-extract [options] <html_content>
    echo '<a href="https://example.com">Link</a>' | devknife url-extract [options]

OPTIONS:
    --base-url URL      Base URL for resolving relative URLs
    --no-unique         Include duplicate URLs in output

EXAMPLES:
    devknife url-extract '<a href="https://example.com">Link</a>'
    echo '<img src="/image.jpg">' | devknife url-extract --base-url https://example.com
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
            name="url-extract",
            description="Extract all URLs from HTML content",
            category="web",
            module="devknife.utils.web_utility",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> List[str]:
        """Get list of supported options."""
        return ["base_url", "unique"]

    def get_examples(self) -> List[str]:
        """Get usage examples."""
        return [
            "devknife url-extract '<a href=\"https://example.com\">Link</a>'",
            "echo '<img src=\"/image.jpg\">' | devknife url-extract --base-url https://example.com",
        ]
