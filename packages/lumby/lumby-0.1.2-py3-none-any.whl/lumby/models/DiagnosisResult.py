"""Diagnosis result data model."""

from dataclasses import dataclass


@dataclass
class DiagnosisResult:
    """Result of AI diagnosis."""

    diagnosis: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
