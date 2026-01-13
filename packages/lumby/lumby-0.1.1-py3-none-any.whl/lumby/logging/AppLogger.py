"""Application logger service."""

import logging as stdlib_logging
from pathlib import Path


class AppLogger:
    """Structured logging service for the application."""

    def __init__(
        self,
        name: str,
        log_file: Path | None = None,
        log_level: str = "info",
    ) -> None:
        """
        Initialize the logger.

        Args:
            name: Logger name (typically module/service name)
            log_file: Optional path to log file
            log_level: Logging level (debug, info, warning, error)
        """
        self._name = name
        self._log_file = log_file
        self._log_level = log_level
        self._logger: stdlib_logging.Logger | None = None
        self._handler: stdlib_logging.Handler | None = None

    def _ensure_initialized(self) -> stdlib_logging.Logger:
        """Lazy initialization of the logger."""
        if self._logger is not None:
            return self._logger

        self._logger = stdlib_logging.getLogger(f"lumby.{self._name}")
        self._logger.setLevel(self._get_level(self._log_level))

        # Add handler if not already configured
        if not self._logger.handlers:
            if self._log_file is not None:
                self._handler = stdlib_logging.FileHandler(self._log_file)
            else:
                self._handler = stdlib_logging.StreamHandler()

            formatter = stdlib_logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            self._handler.setFormatter(formatter)
            self._logger.addHandler(self._handler)

        return self._logger

    @staticmethod
    def _get_level(level: str) -> int:
        """Convert string level to logging constant."""
        levels = {
            "debug": stdlib_logging.DEBUG,
            "info": stdlib_logging.INFO,
            "warning": stdlib_logging.WARNING,
            "error": stdlib_logging.ERROR,
        }
        return levels.get(level.lower(), stdlib_logging.INFO)

    def debug(self, message: str, **kwargs: object) -> None:
        """Log debug message."""
        self._ensure_initialized().debug(self._format_message(message, kwargs))

    def info(self, message: str, **kwargs: object) -> None:
        """Log info message."""
        self._ensure_initialized().info(self._format_message(message, kwargs))

    def warning(self, message: str, **kwargs: object) -> None:
        """Log warning message."""
        self._ensure_initialized().warning(self._format_message(message, kwargs))

    def error(self, message: str, **kwargs: object) -> None:
        """Log error message."""
        self._ensure_initialized().error(self._format_message(message, kwargs))

    @staticmethod
    def _format_message(message: str, extra: dict[str, object]) -> str:
        """Format message with extra context."""
        if not extra:
            return message
        context = " ".join(f"{k}={v}" for k, v in extra.items())
        return f"{message} | {context}"

    def close(self) -> None:
        """Close handlers and cleanup."""
        if self._handler is not None:
            self._handler.close()
            if self._logger is not None:
                self._logger.removeHandler(self._handler)
            self._handler = None

    def __enter__(self) -> "AppLogger":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - cleanup resources."""
        self.close()
