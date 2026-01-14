"""Progressive corpus loading models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProgressiveLoadStep(BaseModel):
    """Single step in progressive loading test."""

    step: int  # 1, 2, 3, ... N
    corpus_added: str  # Name of corpus added in this step
    corpora_loaded: list[str]  # All corpora loaded so far
    implementation: Literal["TF", "CF"]
    run_id: int

    # Memory at this step
    total_rss_mb: float
    incremental_rss_mb: float  # Delta from previous step

    # Timing
    cumulative_load_time_s: float
    step_load_time_s: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class ScalingAnalysis(BaseModel):
    """Linear scaling analysis results."""

    implementation: Literal["TF", "CF"]

    # Linear fit: memory = slope * num_corpora + intercept
    slope_mb_per_corpus: float
    intercept_mb: float
    r_squared: float  # Coefficient of determination

    # Predictions
    predicted_10_corpora_mb: float
    predicted_50_corpora_mb: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class ProgressiveLoadResult(BaseModel):
    """Complete progressive loading results."""

    max_corpora: int
    corpora_order: list[str]  # Order corpora were loaded
    num_runs: int
    steps: list[ProgressiveLoadStep]

    # Scaling analysis
    tf_scaling: ScalingAnalysis | None = None
    cf_scaling: ScalingAnalysis | None = None

    # Summary stats (average across runs)
    tf_memory_by_step: list[float] | None = Field(
        default=None, description="Average TF memory at each step"
    )
    cf_memory_by_step: list[float] | None = Field(
        default=None, description="Average CF memory at each step"
    )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)

    def get_steps_by_impl(
        self, implementation: Literal["TF", "CF"]
    ) -> list[ProgressiveLoadStep]:
        """Get steps for a specific implementation."""
        return [s for s in self.steps if s.implementation == implementation]

    def get_steps_by_run(self, run_id: int) -> list[ProgressiveLoadStep]:
        """Get steps for a specific run."""
        return [s for s in self.steps if s.run_id == run_id]
