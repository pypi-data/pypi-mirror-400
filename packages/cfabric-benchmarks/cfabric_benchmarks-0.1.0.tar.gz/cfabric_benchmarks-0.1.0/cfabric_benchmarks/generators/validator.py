"""Query validation utilities.

Validates generated search queries by executing them on a lightweight
corpus before using them for full benchmarking.
"""

from __future__ import annotations

import time
from typing import Any

from cfabric_benchmarks.models.latency import SearchQuery, ValidationReport


class QueryValidator:
    """Validates search queries by executing them on a corpus.

    Ensures queries are syntactically correct and execute without errors
    before using them for latency benchmarking.
    """

    def __init__(
        self,
        api: Any,
        timeout_ms: float = 5000.0,
        max_results: int = 1000,
    ):
        """Initialize query validator.

        Args:
            api: Text-Fabric or Context-Fabric API object
            timeout_ms: Maximum execution time per query in milliseconds
            max_results: Maximum results to collect (for safety)
        """
        self.api = api
        self.S = api.S
        self.timeout_ms = timeout_ms
        self.max_results = max_results

    def validate_query(self, query: SearchQuery) -> SearchQuery:
        """Validate a single query by executing it.

        Args:
            query: Query to validate

        Returns:
            Updated query with validation status
        """
        start = time.perf_counter()

        try:
            # Execute the search
            results = self.S.search(query.template)

            # Collect some results to verify it works
            count = 0
            for _ in results:
                count += 1
                if count >= self.max_results:
                    break

                # Check timeout
                elapsed_ms = (time.perf_counter() - start) * 1000
                if elapsed_ms > self.timeout_ms:
                    break

            # Query validated successfully
            return SearchQuery(
                id=query.id,
                category=query.category,
                template=query.template,
                description=query.description,
                expected_complexity=query.expected_complexity,
                validated=True,
                validation_error=None,
            )

        except Exception as e:
            # Query failed validation
            return SearchQuery(
                id=query.id,
                category=query.category,
                template=query.template,
                description=query.description,
                expected_complexity=query.expected_complexity,
                validated=False,
                validation_error=str(e),
            )

    def validate_queries(
        self,
        queries: list[SearchQuery],
        corpus_name: str = "unknown",
    ) -> ValidationReport:
        """Validate a list of queries.

        Args:
            queries: List of queries to validate
            corpus_name: Name of the corpus being used for validation

        Returns:
            ValidationReport with results
        """
        validated_queries: list[SearchQuery] = []
        validated_count = 0
        failed_count = 0

        for query in queries:
            result = self.validate_query(query)
            validated_queries.append(result)

            if result.validated:
                validated_count += 1
            else:
                failed_count += 1

        return ValidationReport(
            validation_corpus=corpus_name,
            total_queries=len(queries),
            validated_count=validated_count,
            failed_count=failed_count,
            queries=validated_queries,
        )

    def filter_valid_queries(
        self,
        report: ValidationReport,
    ) -> list[SearchQuery]:
        """Extract only validated queries from a report.

        Args:
            report: ValidationReport to filter

        Returns:
            List of validated queries
        """
        return [p for p in report.queries if p.validated]


def validate_queries_on_corpus(
    queries: list[SearchQuery],
    api: Any,
    corpus_name: str = "unknown",
    timeout_ms: float = 5000.0,
) -> ValidationReport:
    """Convenience function to validate queries on a corpus.

    Args:
        queries: Queries to validate
        api: Text-Fabric or Context-Fabric API object
        corpus_name: Name of the validation corpus
        timeout_ms: Maximum execution time per query

    Returns:
        ValidationReport with results
    """
    validator = QueryValidator(api, timeout_ms=timeout_ms)
    return validator.validate_queries(queries, corpus_name)


def format_validation_report(report: ValidationReport) -> str:
    """Format validation report as human-readable text.

    Args:
        report: ValidationReport to format

    Returns:
        Formatted string
    """
    lines = [
        f"Query Validation Report",
        f"=" * 50,
        f"Corpus: {report.validation_corpus}",
        f"Total queries: {report.total_queries}",
        f"Validated: {report.validated_count} ({report.success_rate:.1%})",
        f"Failed: {report.failed_count}",
        "",
    ]

    if report.failed_count > 0:
        lines.append("Failed queries:")
        lines.append("-" * 50)
        for p in report.queries:
            if not p.validated:
                lines.append(f"  [{p.id}] {p.category}")
                lines.append(f"    Error: {p.validation_error}")
                lines.append(f"    Template: {p.template[:50]}...")
                lines.append("")

    return "\n".join(lines)
