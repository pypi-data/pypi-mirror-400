"""Statistical analysis module for benchmark results."""

from cfabric_benchmarks.analysis.comparison import (
    compare_latency_results,
    compare_load_times,
    compare_memory_results,
    compute_latency_stats_by_category,
    compute_latency_stats_by_query,
    format_comparison_summary,
)
from cfabric_benchmarks.analysis.statistics import (
    aggregate_runs,
    compare_implementations,
    compute_confidence_interval,
    compute_latency_percentiles,
    compute_percentiles,
    compute_summary,
    linear_regression,
    welch_t_test,
)

__all__ = [
    # Statistics
    "aggregate_runs",
    "compare_implementations",
    "compute_confidence_interval",
    "compute_latency_percentiles",
    "compute_percentiles",
    "compute_summary",
    "linear_regression",
    "welch_t_test",
    # Comparison
    "compare_latency_results",
    "compare_load_times",
    "compare_memory_results",
    "compute_latency_stats_by_category",
    "compute_latency_stats_by_query",
    "format_comparison_summary",
]
