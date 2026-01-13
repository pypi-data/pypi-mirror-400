"""Configuration loader service."""

import json
import os
from pathlib import Path

from lumby.models import Config


class ConfigLoader:
    """Loads configuration from multiple sources with priority handling."""

    def load(
        self,
        cli_config_path: Path | None = None,
        cli_overrides: dict[str, object] | None = None,
    ) -> Config:
        """
        Load configuration with priority: CLI overrides > file > env > defaults.

        Args:
            cli_config_path: Optional path to JSON config file
            cli_overrides: Optional dict of CLI-provided overrides

        Returns:
            Merged configuration
        """
        # Start with defaults
        config = Config.default()

        # Layer environment variables
        env_config = self._load_from_env()
        config = config.merge_with(env_config)

        # Layer config file
        if cli_config_path is not None:
            file_config = self._load_from_file(cli_config_path)
            config = config.merge_with(file_config)

        # Layer CLI overrides
        if cli_overrides:
            cli_config = self._dict_to_config(cli_overrides)
            config = config.merge_with(cli_config)

        return config

    def _load_from_file(self, path: Path) -> Config:
        """Load config from JSON file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = path.read_text()
        data = json.loads(content)
        return self._dict_to_config(data)

    def _load_from_env(self) -> Config:
        """Load config from environment variables."""
        config_dict: dict[str, object] = {}

        if log_file := os.environ.get("LUMBY_LOG_FILE"):
            config_dict["log_file"] = log_file

        if log_level := os.environ.get("LUMBY_LOG_LEVEL"):
            config_dict["log_level"] = log_level

        if response_guide := os.environ.get("LUMBY_RESPONSE_GUIDE"):
            config_dict["response_guide"] = response_guide

        if prompt_file := os.environ.get("LUMBY_PROMPT_FILE"):
            config_dict["prompt_file"] = prompt_file

        return self._dict_to_config(config_dict)

    @staticmethod
    def _dict_to_config(data: dict[str, object]) -> Config:
        """Convert dictionary to Config object."""
        log_file = data.get("log_file")
        prompt_file = data.get("prompt_file")

        return Config(
            log_file=Path(str(log_file)) if log_file else None,
            log_level=str(data.get("log_level", "info")),  # type: ignore[arg-type]
            response_guide=str(data.get("response_guide", "Be concise, around 2-3 sentences")),
            prompt_template=str(data["prompt_template"]) if data.get("prompt_template") else None,
            prompt_file=Path(str(prompt_file)) if prompt_file else None,
        )
