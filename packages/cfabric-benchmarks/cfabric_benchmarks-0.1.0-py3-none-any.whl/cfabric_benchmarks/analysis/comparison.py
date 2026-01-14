"""Comparison utilities for TF vs CF benchmark results."""

from __future__ import annotations

from typing import Literal

from cfabric_benchmarks.analysis.statistics import (
    compare_implementations,
    compute_summary,
)
from cfabric_benchmarks.models.memory import MemoryBenchmarkResult, MemoryMeasurement
from cfabric_benchmarks.models.latency import (
    LatencyBenchmarkResult,
    LatencyStatistics,
    QueryMeasurement,
)
from cfabric_benchmarks.models.statistics import ComparisonResult, StatisticalSummary


def compare_memory_results(
    result: MemoryBenchmarkResult,
    mode: Literal["single", "spawn", "fork"] = "single",
) -> ComparisonResult:
    """Compare TF vs CF memory usage for a specific mode.

    Args:
        result: Memory benchmark result containing measurements
        mode: Benchmark mode to compare

    Returns:
        ComparisonResult with memory comparison statistics
    """
    tf_measurements = [
        m.memory_used_mb
        for m in result.measurements
        if m.implementation == "TF" and m.mode == mode
    ]
    cf_measurements = [
        m.memory_used_mb
        for m in result.measurements
        if m.implementation == "CF" and m.mode == mode
    ]

    return compare_implementations(
        tf_measurements,
        cf_measurements,
        metric_name=f"memory_{mode}",
        unit="MB",
        metric_type="memory",
    )


def compare_load_times(result: MemoryBenchmarkResult) -> ComparisonResult:
    """Compare TF vs CF load times.

    Args:
        result: Memory benchmark result containing measurements

    Returns:
        ComparisonResult with load time comparison statistics
    """
    tf_times = [
        m.load_time_s
        for m in result.measurements
        if m.implementation == "TF" and m.mode == "single"
    ]
    cf_times = [
        m.load_time_s
        for m in result.measurements
        if m.implementation == "CF" and m.mode == "single"
    ]

    return compare_implementations(
        tf_times,
        cf_times,
        metric_name="load_time",
        unit="s",
        metric_type="time",
    )


def compare_latency_results(
    result: LatencyBenchmarkResult,
    category: str | None = None,
) -> ComparisonResult:
    """Compare TF vs CF query latency.

    Args:
        result: Latency benchmark result containing measurements
        category: Optional category to filter by

    Returns:
        ComparisonResult with latency comparison statistics
    """
    tf_measurements = [
        m.execution_time_ms
        for m in result.measurements
        if m.implementation == "TF" and m.success
    ]
    cf_measurements = [
        m.execution_time_ms
        for m in result.measurements
        if m.implementation == "CF" and m.success
    ]

    if category:
        # Filter by category using pattern mapping
        query_ids_in_category = {
            p.id for p in result.queries if p.category == category
        }
        tf_measurements = [
            m.execution_time_ms
            for m in result.measurements
            if m.implementation == "TF"
            and m.success
            and m.query_id in query_ids_in_category
        ]
        cf_measurements = [
            m.execution_time_ms
            for m in result.measurements
            if m.implementation == "CF"
            and m.success
            and m.query_id in query_ids_in_category
        ]

    metric_name = f"latency_{category}" if category else "latency_overall"

    return compare_implementations(
        tf_measurements,
        cf_measurements,
        metric_name=metric_name,
        unit="ms",
        metric_type="time",
    )


def compute_latency_stats_by_query(
    measurements: list[QueryMeasurement],
    query_id: str,
    implementation: Literal["TF", "CF"],
) -> LatencyStatistics:
    """Compute latency statistics for a specific pattern and implementation.

    Args:
        measurements: All query measurements
        query_id: Pattern ID to filter by
        implementation: Implementation to filter by

    Returns:
        LatencyStatistics for the pattern
    """
    filtered = [
        m
        for m in measurements
        if m.query_id == query_id and m.implementation == implementation
    ]

    successful = [m for m in filtered if m.success]
    times = [m.execution_time_ms for m in successful]

    if not times:
        return LatencyStatistics(
            query_id=query_id,
            implementation=implementation,
            mean_ms=0.0,
            std_ms=0.0,
            min_ms=0.0,
            max_ms=0.0,
            p50_ms=0.0,
            p95_ms=0.0,
            p99_ms=0.0,
            sample_count=0,
            error_count=len(filtered) - len(successful),
        )

    summary = compute_summary(times, f"latency_{query_id}", "ms")

    return LatencyStatistics(
        query_id=query_id,
        implementation=implementation,
        mean_ms=summary.mean,
        std_ms=summary.std,
        min_ms=summary.min,
        max_ms=summary.max,
        p50_ms=summary.p50,
        p95_ms=summary.p95,
        p99_ms=summary.p99,
        sample_count=len(successful),
        error_count=len(filtered) - len(successful),
    )


def compute_latency_stats_by_category(
    measurements: list[QueryMeasurement],
    queries: list,  # list[SearchPattern]
    category: str,
    implementation: Literal["TF", "CF"],
) -> LatencyStatistics:
    """Compute latency statistics for a category of patterns.

    Args:
        measurements: All query measurements
        patterns: All search queries
        category: Category to filter by
        implementation: Implementation to filter by

    Returns:
        LatencyStatistics for the category
    """
    query_ids = {p.id for p in queries if p.category == category}

    filtered = [
        m
        for m in measurements
        if m.query_id in query_ids and m.implementation == implementation
    ]

    successful = [m for m in filtered if m.success]
    times = [m.execution_time_ms for m in successful]

    if not times:
        return LatencyStatistics(
            category=category,
            implementation=implementation,
            mean_ms=0.0,
            std_ms=0.0,
            min_ms=0.0,
            max_ms=0.0,
            p50_ms=0.0,
            p95_ms=0.0,
            p99_ms=0.0,
            sample_count=0,
            error_count=len(filtered) - len(successful),
        )

    summary = compute_summary(times, f"latency_{category}", "ms")

    return LatencyStatistics(
        category=category,
        implementation=implementation,
        mean_ms=summary.mean,
        std_ms=summary.std,
        min_ms=summary.min,
        max_ms=summary.max,
        p50_ms=summary.p50,
        p95_ms=summary.p95,
        p99_ms=summary.p99,
        sample_count=len(successful),
        error_count=len(filtered) - len(successful),
    )


def format_comparison_summary(comparison: ComparisonResult) -> str:
    """Format a comparison result as a human-readable summary.

    Args:
        comparison: ComparisonResult to format

    Returns:
        Formatted string summary
    """
    lines = [f"Comparison: {comparison.metric_name}"]
    lines.append("-" * 40)
    lines.append(
        f"TF: mean={comparison.tf_stats.mean:.2f} {comparison.tf_stats.unit} "
        f"(std={comparison.tf_stats.std:.2f}, n={comparison.tf_stats.n})"
    )
    lines.append(
        f"CF: mean={comparison.cf_stats.mean:.2f} {comparison.cf_stats.unit} "
        f"(std={comparison.cf_stats.std:.2f}, n={comparison.cf_stats.n})"
    )

    if comparison.speedup_factor is not None:
        lines.append(f"Speedup: {comparison.speedup_factor:.2f}x")
    if comparison.reduction_percent is not None:
        lines.append(f"Reduction: {comparison.reduction_percent:.1f}%")

    if comparison.p_value is not None:
        sig = "significant" if comparison.statistically_significant else "not significant"
        lines.append(f"P-value: {comparison.p_value:.4f} ({sig})")

    return "\n".join(lines)
