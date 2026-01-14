"""Memory benchmark result models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, computed_field

from cfabric_benchmarks.models.statistics import StatisticalSummary


class CorpusStats(BaseModel):
    """Corpus statistics."""

    name: str
    max_slot: int
    max_node: int
    node_types: int
    node_features: int
    edge_features: int

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class MemoryMeasurement(BaseModel):
    """Single memory measurement."""

    run_id: int
    corpus: str
    implementation: Literal["TF", "CF"]
    mode: Literal["single", "spawn", "fork"]

    # Timing
    compile_time_s: float | None = None
    load_time_s: float

    # Memory (MB)
    rss_before_mb: float
    rss_after_mb: float

    # For parallel modes
    num_workers: int | None = None
    total_rss_mb: float | None = None
    per_worker_rss_mb: float | None = None

    # Cache info
    cache_size_mb: float | None = None

    @computed_field
    @property
    def memory_used_mb(self) -> float:
        """Calculate memory used (after - before)."""
        return self.rss_after_mb - self.rss_before_mb

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class MemoryBenchmarkResult(BaseModel):
    """Aggregated memory benchmark results for one corpus."""

    corpus: str
    corpus_stats: CorpusStats
    measurements: list[MemoryMeasurement]

    # Statistical summaries (computed after multiple runs)
    tf_load_time_stats: StatisticalSummary | None = None
    cf_load_time_stats: StatisticalSummary | None = None
    tf_memory_stats: StatisticalSummary | None = None
    cf_memory_stats: StatisticalSummary | None = None

    # Parallel mode stats
    tf_spawn_stats: StatisticalSummary | None = None
    cf_spawn_stats: StatisticalSummary | None = None
    tf_fork_stats: StatisticalSummary | None = None
    cf_fork_stats: StatisticalSummary | None = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)

    def get_measurements_by_impl(
        self, implementation: Literal["TF", "CF"]
    ) -> list[MemoryMeasurement]:
        """Get measurements for a specific implementation."""
        return [m for m in self.measurements if m.implementation == implementation]

    def get_measurements_by_mode(
        self, mode: Literal["single", "spawn", "fork"]
    ) -> list[MemoryMeasurement]:
        """Get measurements for a specific mode."""
        return [m for m in self.measurements if m.mode == mode]
