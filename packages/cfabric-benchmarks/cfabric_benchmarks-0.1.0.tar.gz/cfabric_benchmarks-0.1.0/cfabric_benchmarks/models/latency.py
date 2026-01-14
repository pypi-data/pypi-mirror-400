"""API latency benchmark models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from cfabric_benchmarks.models.statistics import StatisticalSummary


class SearchQuery(BaseModel):
    """Search query for latency testing."""

    id: str
    category: Literal["lexical", "structural", "quantified", "complex"]
    template: str
    description: str
    expected_complexity: Literal["low", "medium", "high"]
    validated: bool = Field(
        default=False, description="True if query executed successfully on validation corpus"
    )
    validation_error: str | None = Field(
        default=None, description="Error message if validation failed"
    )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class QueryMeasurement(BaseModel):
    """Single query timing measurement."""

    query_id: str
    implementation: Literal["TF", "CF"]
    run_id: int
    iteration: int

    # Timing
    execution_time_ms: float
    result_count: int

    # Status
    success: bool
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class LatencyStatistics(BaseModel):
    """Latency statistics for a query or category."""

    query_id: str | None = Field(
        default=None, description="Query ID (None for category-level stats)"
    )
    category: str | None = Field(
        default=None, description="Query category (for category-level stats)"
    )
    implementation: Literal["TF", "CF"]

    # Basic stats
    mean_ms: float
    std_ms: float
    min_ms: float
    max_ms: float

    # Percentiles
    p50_ms: float
    p95_ms: float
    p99_ms: float

    # Sample info
    sample_count: int
    error_count: int

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class LatencyBenchmarkResult(BaseModel):
    """Complete latency benchmark results."""

    corpus: str
    queries: list[SearchQuery]
    measurements: list[QueryMeasurement]
    statistics: list[LatencyStatistics]

    # Category-level statistics
    category_statistics: list[LatencyStatistics] | None = None

    # Overall statistics
    tf_overall_stats: StatisticalSummary | None = None
    cf_overall_stats: StatisticalSummary | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)

    def get_validated_queries(self) -> list[SearchQuery]:
        """Get only validated queries."""
        return [q for q in self.queries if q.validated]

    def get_queries_by_category(
        self, category: Literal["lexical", "structural", "quantified", "complex"]
    ) -> list[SearchQuery]:
        """Get queries for a specific category."""
        return [q for q in self.queries if q.category == category]


class ValidationReport(BaseModel):
    """Report of query validation results."""

    validation_corpus: str
    total_queries: int
    validated_count: int
    failed_count: int
    queries: list[SearchQuery]

    @property
    def success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.total_queries == 0:
            return 0.0
        return self.validated_count / self.total_queries

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)
