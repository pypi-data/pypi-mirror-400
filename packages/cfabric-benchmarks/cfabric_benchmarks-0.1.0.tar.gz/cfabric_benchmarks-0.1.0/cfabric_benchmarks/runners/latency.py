"""Latency benchmark runner.

Measures search query latency for Text-Fabric and Context-Fabric.
"""

from __future__ import annotations

import random
import time
from typing import Any, Literal

from cfabric_benchmarks.analysis.comparison import (
    compute_latency_stats_by_category,
    compute_latency_stats_by_query,
)
from cfabric_benchmarks.analysis.statistics import compute_summary
from cfabric_benchmarks.generators.validator import validate_queries_on_corpus
from cfabric_benchmarks.models.config import BenchmarkConfig, CorpusConfig
from cfabric_benchmarks.models.latency import (
    LatencyBenchmarkResult,
    LatencyStatistics,
    QueryMeasurement,
    SearchQuery,
)
from cfabric_benchmarks.queries import get_queries_for_corpus
from cfabric_benchmarks.runners.base import BaseBenchmarkRunner, load_cf_api, load_tf_api


class LatencyBenchmarkRunner(BaseBenchmarkRunner[LatencyBenchmarkResult]):
    """Runner for latency benchmarks.

    Validates and measures execution time for curated search queries
    on both Text-Fabric and Context-Fabric.
    """

    def name(self) -> str:
        return "LatencyBenchmark"

    def run(
        self,
        corpus: CorpusConfig,
        validation_corpus: CorpusConfig | None = None,
        queries: list[SearchQuery] | None = None,
    ) -> LatencyBenchmarkResult:
        """Run latency benchmark for a corpus.

        Args:
            corpus: Corpus to benchmark
            validation_corpus: Optional corpus for query validation
            queries: Optional pre-defined queries (if None, uses curated queries for corpus)

        Returns:
            LatencyBenchmarkResult with all measurements
        """
        source = str(corpus.tf_path)

        # Load APIs
        self.log(f"Loading APIs for {corpus.name}...")
        tf_api = load_tf_api(source)
        cf_api = load_cf_api(source)

        # Get queries
        if queries is None:
            queries = get_queries_for_corpus(corpus.name)
            self.log(f"Using {len(queries)} curated queries for {corpus.name}")

        # Validate queries
        if validation_corpus:
            self.log(f"Validating queries on {validation_corpus.name}...")
            val_api = load_tf_api(str(validation_corpus.tf_path))
            report = validate_queries_on_corpus(
                queries,
                val_api,
                corpus_name=validation_corpus.name,
            )
            queries = [q for q in report.queries if q.validated]
            self.log(f"  {len(queries)}/{report.total_queries} queries validated")
        else:
            # Validate on target corpus
            self.log(f"Validating queries on {corpus.name}...")
            report = validate_queries_on_corpus(
                queries,
                tf_api,
                corpus_name=corpus.name,
            )
            queries = [q for q in report.queries if q.validated]
            self.log(f"  {len(queries)}/{report.total_queries} queries validated")

        if not queries:
            self.log("No valid queries to benchmark!")
            return LatencyBenchmarkResult(
                corpus=corpus.name,
                queries=[],
                measurements=[],
                statistics=[],
            )

        # Run benchmarks
        measurements: list[QueryMeasurement] = []
        total_runs = self.config.warmup_runs + self.config.latency_runs

        for run_id in range(1, total_runs + 1):
            is_warmup = run_id <= self.config.warmup_runs
            actual_run_id = run_id - self.config.warmup_runs if not is_warmup else 0

            if is_warmup:
                self.log(f"  Warmup run {run_id}/{self.config.warmup_runs}")
            else:
                self.log(f"  Run {actual_run_id}/{self.config.latency_runs}")

            # Randomize query order to avoid cache effects
            query_order = list(queries)
            random.shuffle(query_order)

            for query_idx, query in enumerate(query_order, 1):
                if query_idx % 10 == 0 or query_idx == 1:
                    self.log(f"    Query {query_idx}/{len(query_order)}")
                for impl, api in [("TF", tf_api), ("CF", cf_api)]:
                    for iteration in range(1, self.config.latency_iterations + 1):
                        measurement = self._measure_query(
                            query, api, impl, actual_run_id, iteration
                        )
                        if not is_warmup:
                            measurements.append(measurement)

        # Compute statistics
        self.log("Computing statistics...")
        statistics = self._compute_query_statistics(measurements, queries)
        category_stats = self._compute_category_statistics(measurements, queries)

        # Overall statistics
        tf_overall = compute_summary(
            [m.execution_time_ms for m in measurements if m.implementation == "TF" and m.success],
            "tf_latency",
            "ms",
        )
        cf_overall = compute_summary(
            [m.execution_time_ms for m in measurements if m.implementation == "CF" and m.success],
            "cf_latency",
            "ms",
        )

        return LatencyBenchmarkResult(
            corpus=corpus.name,
            queries=queries,
            measurements=measurements,
            statistics=statistics,
            category_statistics=category_stats,
            tf_overall_stats=tf_overall,
            cf_overall_stats=cf_overall,
        )

    def _measure_query(
        self,
        query: SearchQuery,
        api: Any,
        impl: Literal["TF", "CF"],
        run_id: int,
        iteration: int,
    ) -> QueryMeasurement:
        """Measure execution time for a single query.

        Args:
            query: Query to execute
            api: API object to use
            impl: Implementation identifier
            run_id: Run identifier
            iteration: Iteration number

        Returns:
            QueryMeasurement with timing data
        """
        start = time.perf_counter()
        success = True
        error = None
        result_count = 0

        try:
            results = api.S.search(query.template)
            # Consume results to get actual count
            for _ in results:
                result_count += 1
                # Limit to prevent very long runs
                if result_count >= 100000:
                    break
        except Exception as e:
            success = False
            error = str(e)

        execution_time_ms = (time.perf_counter() - start) * 1000

        return QueryMeasurement(
            query_id=query.id,
            implementation=impl,
            run_id=run_id,
            iteration=iteration,
            execution_time_ms=execution_time_ms,
            result_count=result_count,
            success=success,
            error=error,
        )

    def _compute_query_statistics(
        self,
        measurements: list[QueryMeasurement],
        queries: list[SearchQuery],
    ) -> list[LatencyStatistics]:
        """Compute statistics for each query.

        Args:
            measurements: All query measurements
            queries: All queries

        Returns:
            List of LatencyStatistics per query/implementation
        """
        statistics = []
        for query in queries:
            for impl in ["TF", "CF"]:
                stats = compute_latency_stats_by_query(measurements, query.id, impl)
                statistics.append(stats)
        return statistics

    def _compute_category_statistics(
        self,
        measurements: list[QueryMeasurement],
        queries: list[SearchQuery],
    ) -> list[LatencyStatistics]:
        """Compute statistics for each category.

        Args:
            measurements: All query measurements
            queries: All queries

        Returns:
            List of LatencyStatistics per category/implementation
        """
        statistics = []
        categories = ["lexical", "structural", "quantified", "complex"]
        for category in categories:
            for impl in ["TF", "CF"]:
                stats = compute_latency_stats_by_category(
                    measurements, queries, category, impl
                )
                statistics.append(stats)
        return statistics
