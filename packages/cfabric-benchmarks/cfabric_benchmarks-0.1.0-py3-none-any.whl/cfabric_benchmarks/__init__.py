"""Context-Fabric Benchmarking Suite.

A comprehensive benchmarking package for comparing Context-Fabric and Text-Fabric
performance across memory usage, query latency, and scaling characteristics.
"""

__version__ = "0.1.0"

from cfabric_benchmarks.models import (
    BenchmarkConfig,
    CorpusConfig,
    TestEnvironment,
    MemoryMeasurement,
    MemoryBenchmarkResult,
    SearchQuery,
    QueryMeasurement,
    LatencyStatistics,
    ProgressiveLoadStep,
    ProgressiveLoadResult,
    StatisticalSummary,
    ComparisonResult,
)

__all__ = [
    "__version__",
    # Config
    "BenchmarkConfig",
    "CorpusConfig",
    # Environment
    "TestEnvironment",
    # Memory
    "MemoryMeasurement",
    "MemoryBenchmarkResult",
    # Latency
    "SearchQuery",
    "QueryMeasurement",
    "LatencyStatistics",
    # Progressive
    "ProgressiveLoadStep",
    "ProgressiveLoadResult",
    # Statistics
    "StatisticalSummary",
    "ComparisonResult",
]
