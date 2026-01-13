#!/usr/bin/env python3
"""
Main entry point for DevKnife - chooses between CLI and TUI interfaces.
"""

import sys
import os
from typing import List, Optional

from .core.config_manager import get_global_config_manager, get_global_config
from .core.error_handling import get_cli_error_handler


def detect_interface_preference(args: List[str]) -> str:
    """
    Detect which interface to use based on arguments and configuration.

    Args:
        args: Command line arguments

    Returns:
        'cli' or 'tui' indicating preferred interface
    """
    # Check for explicit TUI flag
    if "--tui" in args or "-t" in args:
        return "tui"

    # Check for explicit CLI flag
    if "--cli" in args or "-c" in args:
        return "cli"

    # If there are command arguments (beyond program name), prefer CLI
    if len(args) > 1:
        # Filter out interface flags
        filtered_args = [
            arg for arg in args[1:] if arg not in ["--tui", "-t", "--cli", "-c"]
        ]
        if filtered_args:
            return "cli"

    # Check configuration preference
    try:
        config = get_global_config()
        interface_pref = getattr(config, "default_interface", "tui")
        return interface_pref if interface_pref in ["cli", "tui"] else "tui"
    except Exception:
        # If config fails, default to TUI
        return "tui"


def setup_environment():
    """Set up the environment for DevKnife."""
    # Ensure configuration directory exists
    try:
        config_manager = get_global_config_manager()
        config_manager.load_config()
    except Exception as e:
        # If config setup fails, warn but continue
        print(f"경고: 설정 초기화 실패: {e}", file=sys.stderr)


def run_cli_interface(args: List[str]):
    """
    Run the CLI interface.

    Args:
        args: Command line arguments
    """
    try:
        from .cli.main import main

        # Remove interface flags from args
        filtered_args = [arg for arg in args if arg not in ["--cli", "-c"]]

        # Replace sys.argv temporarily
        original_argv = sys.argv
        sys.argv = filtered_args

        try:
            main()
        finally:
            sys.argv = original_argv

    except ImportError as e:
        error_handler = get_cli_error_handler()
        error_handler.handle_and_exit(
            ImportError(f"CLI 인터페이스를 로드할 수 없습니다: {e}")
        )
    except Exception as e:
        error_handler = get_cli_error_handler()
        error_handler.handle_and_exit(e)


def run_tui_interface():
    """Run the TUI interface."""
    try:
        from .tui import run_tui

        run_tui()
    except ImportError as e:
        error_handler = get_cli_error_handler()
        error_handler.handle_and_exit(
            ImportError(
                f"TUI 인터페이스를 로드할 수 없습니다: {e}\n"
                "textual 패키지가 설치되어 있는지 확인하세요."
            )
        )
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully in TUI
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        error_handler = get_cli_error_handler()
        error_handler.handle_and_exit(e)


def show_help():
    """Show general help information."""
    help_text = """
DevKnife - Python 개발자 유틸리티 툴킷

사용법:
  devknife                    # TUI 인터페이스 시작 (기본값)
  devknife --tui              # TUI 인터페이스 강제 시작
  devknife --cli              # CLI 모드 강제 사용
  devknife <command> [args]   # CLI 명령 직접 실행
  devknife --help             # 이 도움말 표시
  devknife --version          # 버전 정보 표시

인터페이스:
  TUI (Terminal User Interface): 대화형 메뉴 기반 인터페이스
  CLI (Command Line Interface): 직접 명령어 실행 인터페이스

예제:
  devknife                    # TUI 시작
  devknife base64 "hello"     # CLI로 base64 인코딩
  devknife json --file data.json  # CLI로 JSON 포맷팅
  devknife --tui              # TUI 강제 시작

설정:
  설정 파일: ~/.devknife/config.json
  TUI에서 설정을 변경하거나 직접 파일을 편집할 수 있습니다.

더 많은 정보:
  devknife help               # 사용 가능한 명령어 목록
  devknife help <command>     # 특정 명령어 도움말
"""
    print(help_text.strip())


def show_version():
    """Show version information."""
    try:
        from . import __version__

        print(f"DevKnife v{__version__}")
    except ImportError:
        print("DevKnife v0.1.0")


def main():
    """Main entry point for DevKnife."""
    args = sys.argv

    # Handle special flags first
    if "--help" in args or "-h" in args:
        show_help()
        return

    if "--version" in args or "-v" in args:
        show_version()
        return

    # Set up environment
    setup_environment()

    # Detect interface preference
    interface = detect_interface_preference(args)

    # Run appropriate interface
    if interface == "cli":
        run_cli_interface(args)
    else:
        run_tui_interface()


if __name__ == "__main__":
    main()
