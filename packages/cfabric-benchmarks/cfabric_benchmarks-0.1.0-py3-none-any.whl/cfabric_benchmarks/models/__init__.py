"""Pydantic models for benchmark configuration and results."""

from cfabric_benchmarks.models.config import (
    BenchmarkConfig,
    CorpusConfig,
    CORPUS_SIZE_ORDER,
    discover_corpora,
    get_corpora_by_size,
)
from cfabric_benchmarks.models.environment import (
    HardwareInfo,
    SoftwareInfo,
    TestEnvironment,
)
from cfabric_benchmarks.models.latency import (
    LatencyBenchmarkResult,
    LatencyStatistics,
    QueryMeasurement,
    SearchQuery,
    ValidationReport,
)
from cfabric_benchmarks.models.memory import (
    CorpusStats,
    MemoryBenchmarkResult,
    MemoryMeasurement,
)
from cfabric_benchmarks.models.progressive import (
    ProgressiveLoadResult,
    ProgressiveLoadStep,
    ScalingAnalysis,
)
from cfabric_benchmarks.models.statistics import (
    ComparisonResult,
    StatisticalSummary,
)

__all__ = [
    # Config
    "BenchmarkConfig",
    "CorpusConfig",
    "CORPUS_SIZE_ORDER",
    "discover_corpora",
    "get_corpora_by_size",
    # Environment
    "HardwareInfo",
    "SoftwareInfo",
    "TestEnvironment",
    # Memory
    "CorpusStats",
    "MemoryBenchmarkResult",
    "MemoryMeasurement",
    # Latency
    "LatencyBenchmarkResult",
    "LatencyStatistics",
    "QueryMeasurement",
    "SearchQuery",
    "ValidationReport",
    # Progressive
    "ProgressiveLoadResult",
    "ProgressiveLoadStep",
    "ScalingAnalysis",
    # Statistics
    "ComparisonResult",
    "StatisticalSummary",
]
