"""Command executor service with live streaming."""

import subprocess
import sys
import time

from lumby.logging import AppLogger
from lumby.models import CommandResult


class CommandExecutor:
    """Executes commands with live output streaming."""

    def __init__(self, logger: AppLogger) -> None:
        """
        Initialize the executor.

        Args:
            logger: Logger instance for debug output
        """
        self._logger = logger

    def execute(self, command: list[str]) -> CommandResult:
        """
        Execute command with live streaming output.

        Streams output to terminal in real-time while capturing
        the full output for potential diagnosis.

        Args:
            command: Command and arguments as list

        Returns:
            CommandResult with exit code and captured output
        """
        self._logger.debug("Executing command", command=" ".join(command))
        captured_lines: list[str] = []
        start_time = time.monotonic()

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
            )

            # Stream output line by line
            if process.stdout is not None:
                for line in process.stdout:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    captured_lines.append(line)

            # Wait for process to complete
            exit_code = process.wait()

        except FileNotFoundError:
            # Command not found
            error_message = f"Command not found: {command[0]}\n"
            sys.stderr.write(error_message)
            sys.stderr.flush()
            exit_code = 127
            captured_lines.append(error_message)

        except Exception as e:
            # Other execution errors
            error_message = f"Error executing command: {e}\n"
            sys.stderr.write(error_message)
            sys.stderr.flush()
            exit_code = 1
            captured_lines.append(error_message)

        duration_ms = int((time.monotonic() - start_time) * 1000)
        output = "".join(captured_lines)

        self._logger.debug(
            "Command finished",
            exit_code=exit_code,
            duration_ms=duration_ms,
            output_lines=len(captured_lines),
        )

        return CommandResult(
            command=command,
            exit_code=exit_code,
            output=output,
            duration_ms=duration_ms,
        )
