"""
Main CLI entry point for the DevKnife system.
"""

import sys
import click
from typing import Dict, Any
from devknife.core import InputData, InputSource
from devknife.core.router import get_global_registry, get_global_router
from devknife.core.config_manager import get_global_config_manager, get_global_config
from devknife.core.error_handling import get_cli_error_handler

# Import all utility modules
from devknife.utils.encoding_utility import Base64EncoderDecoder, URLEncoderDecoder
from devknife.utils.data_format_utility import (
    JSONFormatter,
    JSONToYAMLConverter,
    XMLFormatter,
    JSONToPythonClassGenerator,
    CSVToMarkdownConverter,
    TSVToMarkdownConverter,
    CSVToJSONConverter,
)
from devknife.utils.developer_utility import (
    UUIDGenerator,
    UUIDDecoder,
    IBANValidator,
    PasswordGenerator,
)
from devknife.utils.math_utility import (
    NumberBaseConverter,
    HashGenerator,
    TimestampConverter,
)
from devknife.utils.web_utility import (
    GraphQLFormatter,
    CSSFormatter,
    CSSMinifier,
    URLExtractor,
)


def setup_utilities():
    """Register all available utilities."""
    registry = get_global_registry()

    # Register encoding utilities
    registry.register_utility(Base64EncoderDecoder)
    registry.register_utility(URLEncoderDecoder)

    # Register data format utilities
    registry.register_utility(JSONFormatter)
    registry.register_utility(JSONToYAMLConverter)
    registry.register_utility(XMLFormatter)
    registry.register_utility(JSONToPythonClassGenerator)
    registry.register_utility(CSVToMarkdownConverter)
    registry.register_utility(TSVToMarkdownConverter)
    registry.register_utility(CSVToJSONConverter)

    # Register developer utilities
    registry.register_utility(UUIDGenerator)
    registry.register_utility(UUIDDecoder)
    registry.register_utility(IBANValidator)
    registry.register_utility(PasswordGenerator)

    # Register math utilities
    registry.register_utility(NumberBaseConverter)
    registry.register_utility(HashGenerator)
    registry.register_utility(TimestampConverter)

    # Register web utilities
    registry.register_utility(GraphQLFormatter)
    registry.register_utility(CSSFormatter)
    registry.register_utility(CSSMinifier)
    registry.register_utility(URLExtractor)


def get_input_data(text: str = None, file_path: str = None) -> InputData:
    """
    Get input data from various sources (args, file, stdin).

    Args:
        text: Text argument from command line
        file_path: Path to input file

    Returns:
        InputData object

    Raises:
        click.ClickException: If no input is provided
    """
    error_handler = get_cli_error_handler()

    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return InputData(content=content, source=InputSource.FILE)
        except Exception as e:
            result = error_handler.handle_exception(e)
            raise click.ClickException(error_handler.format_error_for_cli(result))
    elif text:
        return InputData(content=text, source=InputSource.ARGS)
    elif not sys.stdin.isatty():
        # stdin에서 읽기
        try:
            content = sys.stdin.read().strip()
            return InputData(content=content, source=InputSource.STDIN)
        except Exception as e:
            result = error_handler.handle_exception(e)
            raise click.ClickException(error_handler.format_error_for_cli(result))
    else:
        raise click.ClickException(
            "입력이 필요합니다. 텍스트 인수, 파일 또는 파이프를 통한 입력을 제공하세요."
        )


def execute_command(command_name: str, input_data: InputData, options: Dict[str, Any]):
    """
    Execute a command using the router.

    Args:
        command_name: Name of the command to execute
        input_data: Input data to process
        options: Command options
    """
    error_handler = get_cli_error_handler()

    try:
        router = get_global_router()
        result = router.route_command(command_name, input_data, options)

        if result.success:
            click.echo(result.output)
            if result.warnings:
                for warning in result.warnings:
                    click.echo(f"경고: {warning}", err=True)
        else:
            click.echo(f"오류: {result.error_message}", err=True)
            sys.exit(1)
    except Exception as e:
        result = error_handler.handle_exception(e)
        click.echo(error_handler.format_error_for_cli(result), err=True)
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0")
@click.option("--tui", is_flag=True, help="TUI 인터페이스를 강제로 시작합니다")
@click.pass_context
def main(ctx, tui):
    """
    Nalutbae DevKnife Toolkit - 개발자를 위한 올인원 터미널 유틸리티 툴킷

    사용법:
      devknife <command> [options] [input]
      devknife help <command>  - 특정 명령어 도움말
      devknife                 - TUI 인터페이스 시작
      devknife --tui           - TUI 인터페이스를 강제로 시작
    """
    error_handler = get_cli_error_handler()

    try:
        setup_utilities()

        # If no command is provided or --tui flag is used, start TUI
        if ctx.invoked_subcommand is None or tui:
            try:
                from ..tui import run_tui

                run_tui()
            except ImportError as e:
                result = error_handler.handle_exception(
                    ImportError(
                        f"TUI 인터페이스를 시작할 수 없습니다: {str(e)}\n"
                        "textual 패키지가 설치되어 있는지 확인하세요."
                    )
                )
                click.echo(error_handler.format_error_for_cli(result), err=True)
                click.echo(
                    "사용 가능한 명령어를 보려면 'devknife --help'를 실행하세요."
                )
            except Exception as e:
                result = error_handler.handle_exception(e)
                click.echo(error_handler.format_error_for_cli(result), err=True)
                click.echo(
                    "사용 가능한 명령어를 보려면 'devknife --help'를 실행하세요."
                )
    except Exception as e:
        result = error_handler.handle_exception(e)
        click.echo(error_handler.format_error_for_cli(result), err=True)
        sys.exit(1)


# Encoding utilities
@main.command()
@click.argument("text", required=False)
@click.option("--decode", is_flag=True, help="Base64 문자열을 디코딩합니다")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def base64(text, decode, file):
    """Base64 인코딩/디코딩을 수행합니다."""
    input_data = get_input_data(text, file)
    options = {"decode": decode}
    execute_command("base64", input_data, options)


@main.command()
@click.argument("text", required=False)
@click.option("--decode", is_flag=True, help="URL 인코딩된 문자열을 디코딩합니다")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def url(text, decode, file):
    """URL 인코딩/디코딩을 수행합니다."""
    input_data = get_input_data(text, file)
    options = {"decode": decode}
    execute_command("url", input_data, options)


# Data format utilities
@main.command()
@click.argument("json_text", required=False)
@click.option("--recover", is_flag=True, help="손상된 JSON 복구를 시도합니다")
@click.option("--indent", type=int, default=2, help="들여쓰기 공백 수 (기본값: 2)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def json(json_text, recover, indent, file):
    """JSON을 포맷팅하거나 손상된 JSON을 복구합니다."""
    input_data = get_input_data(json_text, file)
    options = {"recover": recover, "indent": indent}
    execute_command("json", input_data, options)


@main.command()
@click.argument("json_text", required=False)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def json2yaml(json_text, file):
    """JSON을 YAML 형식으로 변환합니다."""
    input_data = get_input_data(json_text, file)
    execute_command("json2yaml", input_data, {})


@main.command()
@click.argument("xml_text", required=False)
@click.option("--indent", type=int, default=2, help="들여쓰기 공백 수 (기본값: 2)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def xml(xml_text, indent, file):
    """XML을 적절한 들여쓰기로 포맷팅합니다."""
    input_data = get_input_data(xml_text, file)
    options = {"indent": indent}
    execute_command("xml", input_data, options)


@main.command()
@click.argument("json_text", required=False)
@click.option(
    "--class-name",
    default="GeneratedClass",
    help="생성할 클래스 이름 (기본값: GeneratedClass)",
)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def json2py(json_text, class_name, file):
    """JSON 구조에서 Python 데이터클래스를 생성합니다."""
    input_data = get_input_data(json_text, file)
    options = {"class_name": class_name}
    execute_command("json2py", input_data, options)


@main.command()
@click.argument("csv_text", required=False)
@click.option("--no-header", is_flag=True, help="모든 행을 데이터로 처리 (헤더 없음)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def csv2md(csv_text, no_header, file):
    """CSV 데이터를 마크다운 테이블로 변환합니다."""
    input_data = get_input_data(csv_text, file)
    options = {"has_header": not no_header}
    execute_command("csv2md", input_data, options)


@main.command()
@click.argument("tsv_text", required=False)
@click.option("--no-header", is_flag=True, help="모든 행을 데이터로 처리 (헤더 없음)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def tsv2md(tsv_text, no_header, file):
    """TSV 데이터를 마크다운 테이블로 변환합니다."""
    input_data = get_input_data(tsv_text, file)
    options = {"has_header": not no_header}
    execute_command("tsv2md", input_data, options)


@main.command()
@click.argument("csv_text", required=False)
@click.option(
    "--no-header", is_flag=True, help="모든 행을 데이터로 처리 (배열의 배열 생성)"
)
@click.option("--indent", type=int, default=2, help="JSON 들여쓰기 공백 수 (기본값: 2)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def csv2json(csv_text, no_header, indent, file):
    """CSV 데이터를 JSON 배열로 변환합니다."""
    input_data = get_input_data(csv_text, file)
    options = {"has_header": not no_header, "indent": indent}
    execute_command("csv2json", input_data, options)


# Developer utilities
@main.command(name="uuid-gen")
@click.option(
    "--version",
    type=click.Choice(["1", "4"]),
    default="4",
    help="UUID 버전 (기본값: 4)",
)
def uuid_gen(version):
    """새로운 UUID를 생성합니다."""
    # UUID generation doesn't need input data
    input_data = InputData(content="", source=InputSource.ARGS)
    options = {"version": int(version)}
    execute_command("uuid-gen", input_data, options)


@main.command(name="uuid-decode")
@click.argument("uuid_text", required=False)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def uuid_decode(uuid_text, file):
    """UUID를 디코딩하고 분석합니다."""
    input_data = get_input_data(uuid_text, file)
    execute_command("uuid-decode", input_data, {})


@main.command()
@click.argument("iban_text", required=False)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def iban(iban_text, file):
    """IBAN 코드를 체크섬 검증으로 유효성을 검사합니다."""
    input_data = get_input_data(iban_text, file)
    execute_command("iban", input_data, {})


@main.command()
@click.option(
    "--length",
    type=int,
    default=16,
    help="패스워드 길이 (기본값: 16, 최소: 4, 최대: 256)",
)
@click.option("--no-uppercase", is_flag=True, help="대문자 제외")
@click.option("--no-lowercase", is_flag=True, help="소문자 제외")
@click.option("--no-digits", is_flag=True, help="숫자 제외")
@click.option("--no-symbols", is_flag=True, help="기호 제외")
@click.option(
    "--no-ambiguous", is_flag=True, help="혼동하기 쉬운 문자 제외 (0, O, l, 1, |)"
)
def password(length, no_uppercase, no_lowercase, no_digits, no_symbols, no_ambiguous):
    """사용자 정의 가능한 복잡도로 안전한 패스워드를 생성합니다."""
    # Password generation doesn't need input data
    input_data = InputData(content="", source=InputSource.ARGS)
    options = {
        "length": length,
        "uppercase": not no_uppercase,
        "lowercase": not no_lowercase,
        "digits": not no_digits,
        "symbols": not no_symbols,
        "no_ambiguous": no_ambiguous,
    }
    execute_command("password", input_data, options)


# Math utilities
@main.command()
@click.argument("number", required=False)
@click.option(
    "--from",
    "from_base",
    type=click.Choice(["auto", "binary", "octal", "decimal", "hex"]),
    default="auto",
    help="소스 진법 (기본값: auto)",
)
@click.option(
    "--to",
    "to_base",
    type=click.Choice(["binary", "octal", "decimal", "hex", "all"]),
    default="all",
    help="대상 진법 (기본값: all)",
)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def base(number, from_base, to_base, file):
    """숫자를 다른 진법 간에 변환합니다 (2진수, 8진수, 10진수, 16진수)."""
    input_data = get_input_data(number, file)
    options = {"from_base": from_base, "to_base": to_base}
    execute_command("base", input_data, options)


@main.command()
@click.argument("text", required=False)
@click.option(
    "--algorithm",
    type=click.Choice(["md5", "sha1", "sha256", "all"]),
    default="all",
    help="해시 알고리즘 (기본값: all)",
)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def hash(text, algorithm, file):
    """MD5, SHA1, SHA256 해시 값을 생성합니다."""
    input_data = get_input_data(text, file)
    options = {"algorithm": algorithm}
    execute_command("hash", input_data, options)


@main.command()
@click.argument("timestamp_or_date", required=False)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["iso", "readable"]),
    default="iso",
    help="출력 형식 (기본값: iso)",
)
@click.option("--utc", is_flag=True, help="로컬 대신 UTC 시간대 사용")
@click.option("--reverse", is_flag=True, help="날짜 문자열을 Unix 타임스탬프로 변환")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def timestamp(timestamp_or_date, output_format, utc, reverse, file):
    """Unix 타임스탬프를 사람이 읽을 수 있는 형식으로 변환하거나 그 반대로 변환합니다."""
    input_data = get_input_data(timestamp_or_date, file)
    options = {"format": output_format, "utc": utc, "reverse": reverse}
    execute_command("timestamp", input_data, options)


# Web utilities
@main.command()
@click.argument("query", required=False)
@click.option("--indent", type=int, default=2, help="들여쓰기 공백 수 (기본값: 2)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def graphql(query, indent, file):
    """GraphQL 쿼리를 적절한 들여쓰기로 포맷팅하고 검증합니다."""
    input_data = get_input_data(query, file)
    options = {"indent": indent}
    execute_command("graphql", input_data, options)


@main.command()
@click.argument("css_content", required=False)
@click.option("--indent", type=int, default=2, help="들여쓰기 공백 수 (기본값: 2)")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def css(css_content, indent, file):
    """CSS를 가독성을 위해 적절한 들여쓰기로 포맷팅합니다."""
    input_data = get_input_data(css_content, file)
    options = {"indent": indent}
    execute_command("css", input_data, options)


@main.command(name="css-min")
@click.argument("css_content", required=False)
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def css_min(css_content, file):
    """불필요한 공백과 주석을 제거하여 CSS를 압축합니다."""
    input_data = get_input_data(css_content, file)
    execute_command("css-min", input_data, {})


@main.command(name="url-extract")
@click.argument("html_content", required=False)
@click.option("--base-url", help="상대 URL 해결을 위한 기본 URL")
@click.option("--no-unique", is_flag=True, help="출력에 중복 URL 포함")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="파일에서 입력을 읽습니다"
)
def url_extract(html_content, base_url, no_unique, file):
    """HTML 콘텐츠에서 모든 URL을 추출합니다."""
    input_data = get_input_data(html_content, file)
    options = {"base_url": base_url or "", "unique": not no_unique}
    execute_command("url-extract", input_data, options)


# Help and utility commands
@main.command()
@click.argument("command_name", required=False)
def help(command_name):
    """특정 명령어에 대한 도움말을 표시합니다."""
    router = get_global_router()

    if command_name:
        help_text = router.get_command_help(command_name)
        if help_text:
            click.echo(help_text)
        else:
            click.echo(f"명령어 '{command_name}'을 찾을 수 없습니다.")
            click.echo("사용 가능한 명령어를 보려면 'devknife list'를 실행하세요.")
    else:
        click.echo(router.get_general_help())


@main.command()
def list():
    """사용 가능한 모든 명령어를 나열합니다."""
    router = get_global_router()
    click.echo(router.get_general_help())


if __name__ == "__main__":
    main()
