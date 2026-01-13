"""Diagnosis service using Claude Agent SDK."""

import time

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from lumby.logging import AppLogger
from lumby.models import CommandResult, Config, DiagnosisResult
from lumby.services.PromptRenderer import PromptRenderer


class DiagnosisService:
    """Provides AI-powered diagnosis of command failures."""

    # Read-only tools for context gathering during diagnosis
    ALLOWED_TOOLS = ["Read", "Glob", "Grep"]

    def __init__(
        self,
        prompt_renderer: PromptRenderer,
        logger: AppLogger,
    ) -> None:
        """
        Initialize the diagnosis service.

        Args:
            prompt_renderer: Renders prompt templates
            logger: Logger for debug output
        """
        self._prompt_renderer = prompt_renderer
        self._logger = logger

    async def diagnose(self, result: CommandResult, config: Config) -> DiagnosisResult:
        """
        Analyze a failed command and return diagnosis.

        Uses Claude Agent SDK to analyze the failure and provide
        actionable diagnosis.

        Args:
            result: The failed command result
            config: Configuration with response guidelines

        Returns:
            DiagnosisResult with diagnosis text and token usage
        """
        self._logger.debug(
            "Starting diagnosis",
            command=result.command_string,
            exit_code=result.exit_code,
        )

        start_time = time.monotonic()

        # Render the prompt
        prompt = self._prompt_renderer.render(
            command=result.command_string,
            exit_code=result.exit_code,
            output=result.output,
            response_guide=config.response_guide,
            config=config,
        )

        # Configure the Claude agent
        agent_options = ClaudeAgentOptions(
            max_turns=3,  # Limited turns for diagnosis
            allowed_tools=self.ALLOWED_TOOLS,
        )

        # Run diagnosis
        diagnosis_texts: list[str] = []
        input_tokens = 0
        output_tokens = 0

        try:
            async for message in query(prompt=prompt, options=agent_options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            diagnosis_texts.append(block.text)

                    # Track usage
                    usage = getattr(message, "usage", None)
                    if usage:
                        input_tokens += usage.get("input_tokens", 0)
                        input_tokens += usage.get("cache_creation_input_tokens", 0)
                        input_tokens += usage.get("cache_read_input_tokens", 0)
                        output_tokens += usage.get("output_tokens", 0)

                elif isinstance(message, ResultMessage):
                    # Final message - we can extract final cost here if needed
                    pass

        except Exception as e:
            self._logger.error(f"Diagnosis failed: {e}")
            diagnosis_texts = [f"Diagnosis failed: {e}"]

        duration_ms = int((time.monotonic() - start_time) * 1000)
        diagnosis = "\n\n".join(diagnosis_texts) if diagnosis_texts else "No diagnosis available."

        self._logger.debug(
            "Diagnosis complete",
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        return DiagnosisResult(
            diagnosis=diagnosis,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
        )
