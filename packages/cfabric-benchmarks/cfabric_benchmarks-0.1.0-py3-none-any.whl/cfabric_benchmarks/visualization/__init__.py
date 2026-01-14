"""Visualization tools for benchmark results."""

from cfabric_benchmarks.visualization.charts import (
    COLORS,
    create_latency_distribution_chart,
    create_latency_percentiles_chart,
    create_memory_comparison_chart,
    create_multi_corpus_memory_chart,
    create_progressive_scaling_chart,
    setup_dark_style,
)
from cfabric_benchmarks.visualization.reports import (
    generate_full_report,
    save_individual_charts,
)

__all__ = [
    # Style
    "COLORS",
    "setup_dark_style",
    # Charts
    "create_memory_comparison_chart",
    "create_multi_corpus_memory_chart",
    "create_progressive_scaling_chart",
    "create_latency_distribution_chart",
    "create_latency_percentiles_chart",
    # Reports
    "generate_full_report",
    "save_individual_charts",
]
