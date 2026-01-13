"""Configuration data model."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

LogLevel = Literal["debug", "info", "warning", "error"]


@dataclass
class Config:
    """Configuration for the command wrapper."""

    log_file: Path | None = None
    log_level: LogLevel = "info"
    response_guide: str = "Be concise, around 2-3 sentences"
    prompt_template: str | None = None  # Inline template string
    prompt_file: Path | None = None  # Or path to template file

    @classmethod
    def default(cls) -> "Config":
        """Create default configuration."""
        return cls()

    def merge_with(self, other: "Config") -> "Config":
        """
        Merge with another config (other takes precedence for non-None/default values).

        Used to layer configurations: defaults -> env -> file -> cli.
        """
        return Config(
            log_file=other.log_file if other.log_file is not None else self.log_file,
            log_level=other.log_level if other.log_level != "info" else self.log_level,
            response_guide=(
                other.response_guide
                if other.response_guide != "Be concise, around 2-3 sentences"
                else self.response_guide
            ),
            prompt_template=(
                other.prompt_template if other.prompt_template is not None else self.prompt_template
            ),
            prompt_file=other.prompt_file if other.prompt_file is not None else self.prompt_file,
        )
