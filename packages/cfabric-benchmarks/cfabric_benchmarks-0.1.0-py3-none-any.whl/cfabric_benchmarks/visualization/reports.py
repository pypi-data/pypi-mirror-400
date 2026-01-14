"""PDF report generation for benchmark results."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages

from cfabric_benchmarks.models.latency import LatencyBenchmarkResult
from cfabric_benchmarks.models.memory import MemoryBenchmarkResult
from cfabric_benchmarks.models.progressive import ProgressiveLoadResult
from cfabric_benchmarks.visualization.charts import (
    create_latency_distribution_chart,
    create_latency_percentiles_chart,
    create_memory_comparison_chart,
    create_multi_corpus_memory_chart,
    create_progressive_scaling_chart,
)


def generate_full_report(
    output_path: Path,
    memory_results: list[MemoryBenchmarkResult] | None = None,
    latency_result: LatencyBenchmarkResult | None = None,
    progressive_result: ProgressiveLoadResult | None = None,
) -> None:
    """Generate a complete PDF report with all charts.

    Args:
        output_path: Path to save PDF report
        memory_results: Memory benchmark results
        latency_result: Latency benchmark result
        progressive_result: Progressive load result
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_path.parent / ".temp_charts"
    temp_dir.mkdir(exist_ok=True)

    charts = []

    # Memory comparison for each corpus
    if memory_results:
        for result in memory_results:
            chart_path = temp_dir / f"memory_{result.corpus}.pdf"
            create_memory_comparison_chart(result, chart_path)
            charts.append(chart_path)

        # Multi-corpus comparison
        if len(memory_results) > 1:
            chart_path = temp_dir / "memory_multicorpus.pdf"
            create_multi_corpus_memory_chart(memory_results, chart_path)
            charts.append(chart_path)

    # Progressive scaling
    if progressive_result:
        chart_path = temp_dir / "progressive_scaling.pdf"
        create_progressive_scaling_chart(progressive_result, chart_path)
        charts.append(chart_path)

    # Latency charts
    if latency_result:
        chart_path = temp_dir / "latency_distribution.pdf"
        create_latency_distribution_chart(latency_result, chart_path)
        charts.append(chart_path)

        chart_path = temp_dir / "latency_percentiles.pdf"
        create_latency_percentiles_chart(latency_result, chart_path)
        charts.append(chart_path)

    # Combine into single PDF
    if charts:
        _combine_pdfs(charts, output_path)

    # Cleanup temp files
    for chart in charts:
        if chart.exists():
            chart.unlink()
    if temp_dir.exists():
        temp_dir.rmdir()


def _combine_pdfs(input_paths: list[Path], output_path: Path) -> None:
    """Combine multiple PDF files into one.

    Args:
        input_paths: List of input PDF paths
        output_path: Output PDF path
    """
    from PyPDF2 import PdfMerger

    merger = PdfMerger()
    for path in input_paths:
        if path.exists():
            merger.append(str(path))

    merger.write(str(output_path))
    merger.close()


def save_individual_charts(
    output_dir: Path,
    memory_results: list[MemoryBenchmarkResult] | None = None,
    latency_result: LatencyBenchmarkResult | None = None,
    progressive_result: ProgressiveLoadResult | None = None,
) -> list[Path]:
    """Save individual chart files.

    Args:
        output_dir: Directory to save charts
        memory_results: Memory benchmark results
        latency_result: Latency benchmark result
        progressive_result: Progressive load result

    Returns:
        List of created file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []

    # Memory charts
    if memory_results:
        for result in memory_results:
            pdf_path = output_dir / f"fig_memory_{result.corpus}.pdf"
            png_path = output_dir / f"fig_memory_{result.corpus}.png"
            create_memory_comparison_chart(result, pdf_path)
            create_memory_comparison_chart(result, png_path)
            created.extend([pdf_path, png_path])

        if len(memory_results) > 1:
            pdf_path = output_dir / "fig_memory_multicorpus.pdf"
            png_path = output_dir / "fig_memory_multicorpus.png"
            create_multi_corpus_memory_chart(memory_results, pdf_path)
            create_multi_corpus_memory_chart(memory_results, png_path)
            created.extend([pdf_path, png_path])

    # Progressive chart
    if progressive_result:
        pdf_path = output_dir / "fig_scaling_progressive.pdf"
        png_path = output_dir / "fig_scaling_progressive.png"
        create_progressive_scaling_chart(progressive_result, pdf_path)
        create_progressive_scaling_chart(progressive_result, png_path)
        created.extend([pdf_path, png_path])

    # Latency charts
    if latency_result:
        pdf_path = output_dir / "fig_latency_distribution.pdf"
        png_path = output_dir / "fig_latency_distribution.png"
        create_latency_distribution_chart(latency_result, pdf_path)
        create_latency_distribution_chart(latency_result, png_path)
        created.extend([pdf_path, png_path])

        pdf_path = output_dir / "fig_latency_percentiles.pdf"
        png_path = output_dir / "fig_latency_percentiles.png"
        create_latency_percentiles_chart(latency_result, pdf_path)
        create_latency_percentiles_chart(latency_result, png_path)
        created.extend([pdf_path, png_path])

    return created
