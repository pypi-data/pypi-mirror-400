"""Statistical analysis models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StatisticalSummary(BaseModel):
    """Statistical summary for a set of measurements."""

    metric_name: str
    unit: str  # "ms", "MB", "s"

    # Central tendency
    mean: float
    median: float

    # Dispersion
    std: float
    variance: float
    min: float
    max: float
    range: float

    # Sample info
    n: int

    # Confidence interval (95%)
    ci_lower: float
    ci_upper: float

    # Percentiles
    p25: float
    p50: float  # Same as median
    p75: float
    p90: float
    p95: float
    p99: float

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)


class ComparisonResult(BaseModel):
    """Comparison between TF and CF for a metric."""

    metric_name: str

    tf_stats: StatisticalSummary
    cf_stats: StatisticalSummary

    # Comparison metrics
    speedup_factor: float | None = Field(
        default=None, description="TF/CF ratio for time metrics (>1 means CF is faster)"
    )
    reduction_percent: float | None = Field(
        default=None, description="(TF-CF)/TF * 100 for memory metrics"
    )

    # Statistical significance
    p_value: float | None = Field(
        default=None, description="P-value from Welch's t-test"
    )
    statistically_significant: bool = Field(
        default=False, description="True if p_value < 0.05"
    )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)
