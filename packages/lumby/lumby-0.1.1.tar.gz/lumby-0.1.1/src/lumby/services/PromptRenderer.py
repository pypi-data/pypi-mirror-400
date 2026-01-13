"""Prompt renderer service."""

from pathlib import Path

from lumby.models import Config


class PromptRenderer:
    """Renders prompt templates with variable substitution."""

    def __init__(self, default_template_path: Path) -> None:
        """
        Initialize the renderer.

        Args:
            default_template_path: Path to the default prompt template file
        """
        self._default_template_path = default_template_path
        self._default_template_cache: str | None = None

    def render(
        self,
        command: str,
        exit_code: int,
        output: str,
        response_guide: str,
        config: Config,
    ) -> str:
        """
        Render prompt template with command result data.

        Template variables:
        - {command} - The command that was run
        - {exit_code} - The exit code
        - {output} - The captured output
        - {response_guide} - The response guideline

        Priority for template source:
        1. config.prompt_template (inline string)
        2. config.prompt_file (path to template file)
        3. default_template_path (fallback)

        Args:
            command: The command string that was executed
            exit_code: The exit code from the command
            output: The captured stdout/stderr output
            response_guide: Guidelines for the AI response
            config: Configuration that may contain template overrides

        Returns:
            Rendered prompt string with all variables substituted
        """
        template = self._get_template(config)
        return self._substitute_variables(
            template,
            command=command,
            exit_code=exit_code,
            output=output,
            response_guide=response_guide,
        )

    def _get_template(self, config: Config) -> str:
        """Get the template string based on config priority."""
        # Priority 1: Inline template from config
        if config.prompt_template is not None:
            return config.prompt_template

        # Priority 2: Custom template file from config
        if config.prompt_file is not None:
            return self._load_template_file(config.prompt_file)

        # Priority 3: Default template (cached)
        return self._load_default_template()

    def _load_default_template(self) -> str:
        """Load and cache the default template."""
        if self._default_template_cache is None:
            self._default_template_cache = self._load_template_file(self._default_template_path)
        return self._default_template_cache

    @staticmethod
    def _load_template_file(path: Path) -> str:
        """Load template from file."""
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        return path.read_text()

    @staticmethod
    def _substitute_variables(
        template: str,
        *,
        command: str,
        exit_code: int,
        output: str,
        response_guide: str,
    ) -> str:
        """Substitute template variables."""
        return (
            template.replace("{command}", command)
            .replace("{exit_code}", str(exit_code))
            .replace("{output}", output)
            .replace("{response_guide}", response_guide)
        )
