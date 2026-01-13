"""CLI entry point for lumby."""

import argparse
import asyncio
import sys
from argparse import Namespace
from pathlib import Path

from lumby.logging import AppLogger
from lumby.models import Config
from lumby.services import CommandExecutor, ConfigLoader, DiagnosisService, PromptRenderer


def get_default_prompt_path() -> Path:
    """Get the path to the default prompt template."""
    # The prompts directory is inside the package
    return Path(__file__).parent / "prompts" / "default.md"


def parse_args(argv: list[str]) -> tuple[Namespace, list[str]]:
    """
    Parse CLI arguments.

    Everything before '--' is for lumby, everything after is the command.

    Args:
        argv: Command line arguments (excluding program name)

    Returns:
        Tuple of (parsed args namespace, command list)
    """
    # Handle --help and --version before separator logic
    if "--help" in argv or "-h" in argv:
        # Let argparse handle help
        lumby_args = ["--help"]
        command = []
    elif "--version" in argv:
        print("lumby 0.1.1")
        raise SystemExit(0)
    elif "--" in argv:
        # Find the '--' separator
        separator_idx = argv.index("--")
        lumby_args = argv[:separator_idx]
        command = argv[separator_idx + 1 :]
    else:
        lumby_args = []
        command = argv

    parser = argparse.ArgumentParser(
        prog="lumby",
        description="Smart command wrapper with AI-powered failure diagnosis",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON config file",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to log file",
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Log level (default: info)",
    )
    parser.add_argument(
        "--response-guide",
        type=str,
        help="Response guideline for AI diagnosis",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Path to custom prompt template",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (shortcut for detailed diagnosis)",
    )

    args = parser.parse_args(lumby_args)
    return args, command


def build_cli_overrides(args: Namespace) -> dict[str, object]:
    """Build CLI overrides dictionary from parsed arguments."""
    overrides: dict[str, object] = {}

    if args.log_file:
        overrides["log_file"] = args.log_file
    if args.log_level and args.log_level != "info":
        overrides["log_level"] = args.log_level
    if args.response_guide:
        overrides["response_guide"] = args.response_guide
    if args.prompt_file:
        overrides["prompt_file"] = args.prompt_file
    if args.verbose:
        overrides["response_guide"] = "Provide a detailed diagnosis with step-by-step analysis"

    return overrides


async def run_async(command: list[str], config: Config, logger: AppLogger) -> int:
    """
    Run the command and diagnose failures.

    Args:
        command: Command to execute
        config: Configuration
        logger: Logger instance

    Returns:
        Exit code from the command
    """
    # Execute the command
    executor = CommandExecutor(logger)
    result = executor.execute(command)

    # If succeeded, exit immediately
    if result.succeeded:
        logger.debug("Command succeeded", exit_code=0, duration_ms=result.duration_ms)
        return 0

    # On failure, diagnose
    logger.info("Command failed, starting diagnosis", exit_code=result.exit_code)

    prompt_path = config.prompt_file or get_default_prompt_path()
    if not prompt_path.exists():
        logger.error(f"Prompt template not found: {prompt_path}")
        return result.exit_code

    prompt_renderer = PromptRenderer(prompt_path)
    diagnosis_service = DiagnosisService(prompt_renderer, logger)

    diagnosis_result = await diagnosis_service.diagnose(result, config)

    # Display diagnosis
    duration_sec = diagnosis_result.duration_ms / 1000
    print()
    print("═" * 68)
    print(f"   Diagnosis ({duration_sec:.1f}s)")
    print("═" * 68)
    print()
    print(diagnosis_result.diagnosis)
    print()
    print("═" * 68)

    logger.debug(
        "Diagnosis complete",
        input_tokens=diagnosis_result.input_tokens,
        output_tokens=diagnosis_result.output_tokens,
        duration_ms=diagnosis_result.duration_ms,
    )

    return result.exit_code


def main() -> int:
    """Main entry point."""
    args, command = parse_args(sys.argv[1:])

    if not command:
        print("Error: No command specified", file=sys.stderr)
        print("Usage: lumby [options] -- command [args...]", file=sys.stderr)
        return 1

    # Load configuration
    loader = ConfigLoader()
    cli_overrides = build_cli_overrides(args)
    config = loader.load(
        cli_config_path=args.config,
        cli_overrides=cli_overrides if cli_overrides else None,
    )

    # Create logger
    logger = AppLogger(
        name="lumby",
        log_file=config.log_file,
        log_level=config.log_level,
    )

    try:
        return asyncio.run(run_async(command, config, logger))
    finally:
        logger.close()


def run() -> None:
    """CLI entry point (called by `lumby` command)."""
    sys.exit(main())


if __name__ == "__main__":
    run()
