"""Statistical analysis functions for benchmark results."""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
from scipy import stats

from cfabric_benchmarks.models.statistics import ComparisonResult, StatisticalSummary


def compute_summary(
    values: list[float],
    metric_name: str,
    unit: str,
) -> StatisticalSummary:
    """Compute comprehensive statistical summary for a set of values.

    Args:
        values: List of measurement values
        metric_name: Name of the metric (e.g., "load_time", "memory")
        unit: Unit of measurement (e.g., "ms", "MB", "s")

    Returns:
        StatisticalSummary with all computed statistics
    """
    arr = np.array(values)
    n = len(arr)

    if n == 0:
        # Return empty summary for no data
        return StatisticalSummary(
            metric_name=metric_name,
            unit=unit,
            mean=0.0,
            median=0.0,
            std=0.0,
            variance=0.0,
            min=0.0,
            max=0.0,
            range=0.0,
            n=0,
            ci_lower=0.0,
            ci_upper=0.0,
            p25=0.0,
            p50=0.0,
            p75=0.0,
            p90=0.0,
            p95=0.0,
            p99=0.0,
        )

    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    variance = std**2

    # Confidence interval (95%)
    ci_lower, ci_upper = compute_confidence_interval(arr, confidence=0.95)

    # Percentiles
    percentiles = compute_percentiles(arr, [25, 50, 75, 90, 95, 99])

    return StatisticalSummary(
        metric_name=metric_name,
        unit=unit,
        mean=mean,
        median=float(np.median(arr)),
        std=std,
        variance=variance,
        min=float(np.min(arr)),
        max=float(np.max(arr)),
        range=float(np.max(arr) - np.min(arr)),
        n=n,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        p25=percentiles[25],
        p50=percentiles[50],
        p75=percentiles[75],
        p90=percentiles[90],
        p95=percentiles[95],
        p99=percentiles[99],
    )


def compute_confidence_interval(
    values: np.ndarray | list[float],
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Compute confidence interval for the mean.

    Args:
        values: Array of values
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    arr = np.array(values)
    n = len(arr)

    if n < 2:
        mean = float(np.mean(arr)) if n > 0 else 0.0
        return mean, mean

    mean = float(np.mean(arr))
    std_err = float(stats.sem(arr))

    # t-value for the given confidence level
    alpha = 1 - confidence
    t_val = stats.t.ppf(1 - alpha / 2, df=n - 1)

    margin = t_val * std_err
    return mean - margin, mean + margin


def compute_percentiles(
    values: np.ndarray | list[float],
    percentiles: list[int],
) -> dict[int, float]:
    """Compute multiple percentiles.

    Args:
        values: Array of values
        percentiles: List of percentiles to compute (e.g., [50, 90, 95, 99])

    Returns:
        Dictionary mapping percentile to value
    """
    arr = np.array(values)
    if len(arr) == 0:
        return {p: 0.0 for p in percentiles}

    result = {}
    for p in percentiles:
        result[p] = float(np.percentile(arr, p))
    return result


def welch_t_test(
    sample_a: list[float],
    sample_b: list[float],
) -> tuple[float, float]:
    """Perform Welch's t-test for independent samples.

    Welch's t-test does not assume equal variances between groups.

    Args:
        sample_a: First sample
        sample_b: Second sample

    Returns:
        Tuple of (t_statistic, p_value)
    """
    if len(sample_a) < 2 or len(sample_b) < 2:
        return 0.0, 1.0

    t_stat, p_value = stats.ttest_ind(sample_a, sample_b, equal_var=False)
    return float(t_stat), float(p_value)


def compare_implementations(
    tf_values: list[float],
    cf_values: list[float],
    metric_name: str,
    unit: str,
    metric_type: Literal["time", "memory", "other"] = "other",
    significance_level: float = 0.05,
) -> ComparisonResult:
    """Compare TF and CF measurements for a metric.

    Args:
        tf_values: Text-Fabric measurements
        cf_values: Context-Fabric measurements
        metric_name: Name of the metric
        unit: Unit of measurement
        metric_type: Type of metric for computing comparison ratios
        significance_level: P-value threshold for statistical significance

    Returns:
        ComparisonResult with statistics, comparison metrics, and effect size
    """
    tf_stats = compute_summary(tf_values, f"{metric_name}_TF", unit)
    cf_stats = compute_summary(cf_values, f"{metric_name}_CF", unit)

    # Statistical test
    t_stat, p_value = welch_t_test(tf_values, cf_values)
    significant = p_value < significance_level

    # Compute comparison metrics based on type
    speedup_factor = None
    reduction_percent = None

    if tf_stats.mean > 0 and cf_stats.mean > 0:
        if metric_type == "time":
            # For time, speedup = TF/CF (>1 means CF is faster)
            speedup_factor = tf_stats.mean / cf_stats.mean
        elif metric_type == "memory":
            # For memory, reduction = (TF-CF)/TF * 100
            reduction_percent = (tf_stats.mean - cf_stats.mean) / tf_stats.mean * 100

    return ComparisonResult(
        metric_name=metric_name,
        tf_stats=tf_stats,
        cf_stats=cf_stats,
        speedup_factor=speedup_factor,
        reduction_percent=reduction_percent,
        p_value=p_value,
        statistically_significant=significant,
    )


def compute_latency_percentiles(
    values: list[float],
) -> dict[str, float]:
    """Compute common latency percentiles.

    Args:
        values: Latency measurements in milliseconds

    Returns:
        Dictionary with p50, p95, p99 values
    """
    percentiles = compute_percentiles(values, [50, 95, 99])
    return {
        "p50_ms": percentiles[50],
        "p95_ms": percentiles[95],
        "p99_ms": percentiles[99],
    }


def linear_regression(
    x: list[float] | np.ndarray,
    y: list[float] | np.ndarray,
) -> tuple[float, float, float]:
    """Perform simple linear regression.

    Args:
        x: Independent variable values
        y: Dependent variable values

    Returns:
        Tuple of (slope, intercept, r_squared)
    """
    x_arr = np.array(x)
    y_arr = np.array(y)

    if len(x_arr) < 2:
        return 0.0, 0.0, 0.0

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_arr, y_arr)
    r_squared = r_value**2

    return float(slope), float(intercept), float(r_squared)


def aggregate_runs(
    measurements: list[list[float]],
) -> tuple[list[float], list[float]]:
    """Aggregate multiple runs into mean and std for each step.

    Args:
        measurements: List of runs, where each run is a list of step values

    Returns:
        Tuple of (means, stds) for each step
    """
    if not measurements:
        return [], []

    # Transpose to get values per step
    num_steps = len(measurements[0])
    step_values = [[] for _ in range(num_steps)]

    for run in measurements:
        for i, val in enumerate(run):
            if i < num_steps:
                step_values[i].append(val)

    means = [float(np.mean(vals)) for vals in step_values]
    stds = [float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0 for vals in step_values]

    return means, stds
