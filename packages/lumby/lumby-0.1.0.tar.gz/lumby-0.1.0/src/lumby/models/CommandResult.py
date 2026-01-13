"""Command execution result data model."""

from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of executing a command."""

    command: list[str]
    exit_code: int
    output: str
    duration_ms: int

    @property
    def succeeded(self) -> bool:
        """Check if command succeeded (exit code 0)."""
        return self.exit_code == 0

    @property
    def failed(self) -> bool:
        """Check if command failed (non-zero exit code)."""
        return self.exit_code != 0

    @property
    def command_string(self) -> str:
        """Get command as a single string."""
        return " ".join(self.command)
