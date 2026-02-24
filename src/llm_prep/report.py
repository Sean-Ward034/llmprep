"""Validation report and stage timing helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from llm_prep import SCHEMA_VERSION
from llm_prep.models import ValidationReport


@dataclass
class PipelineReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, int | float] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)

    @contextmanager
    def timed(self, stage_name: str) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            self.timings[stage_name] = round((time.perf_counter() - start) * 1000.0, 3)

    def to_model(self) -> ValidationReport:
        merged_metrics = dict(self.metrics)
        merged_metrics["time_ms"] = round(sum(self.timings.values()), 3)
        return ValidationReport(
            schema_version=SCHEMA_VERSION,
            errors=self.errors,
            warnings=self.warnings,
            metrics=merged_metrics,
            timing_breakdown=self.timings,
        )
