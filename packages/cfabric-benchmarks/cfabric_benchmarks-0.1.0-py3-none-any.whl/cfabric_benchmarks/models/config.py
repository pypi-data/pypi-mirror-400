"""Benchmark configuration models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class CorpusConfig(BaseModel):
    """Configuration for a single corpus."""

    name: str
    path: Path
    tf_path: Path  # Path to TF source files

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "tf_path": str(self.tf_path),
        }


class BenchmarkConfig(BaseModel):
    """Main benchmark configuration."""

    # Run parameters (per-benchmark)
    memory_runs: int = Field(
        default=5, ge=1, le=100, description="Runs for memory benchmark"
    )
    latency_runs: int = Field(
        default=5, ge=1, le=100, description="Runs for latency benchmark"
    )
    progressive_runs: int = Field(
        default=5, ge=1, le=100, description="Runs for progressive benchmark"
    )
    warmup_runs: int = Field(
        default=1, ge=0, description="Warmup runs (excluded from stats)"
    )

    # Corpus selection
    corpora_dir: Path = Field(default=Path(".corpora"))
    selected_corpora: list[str] | None = Field(
        default=None, description="Subset of corpora to test (None = all)"
    )

    # Memory benchmark settings
    num_workers: int = Field(default=4, ge=1, description="Workers for parallel tests")
    measure_fork: bool = Field(default=True, description="Include fork-mode tests")
    measure_spawn: bool = Field(default=True, description="Include spawn-mode tests")

    # Latency benchmark settings
    num_queries: int = Field(
        default=50, ge=10, description="Search queries to generate"
    )
    latency_iterations: int = Field(
        default=10, description="Iterations per pattern for latency testing"
    )
    validation_corpus: str = Field(
        default="cuc", description="Lightweight corpus for query validation"
    )

    # Progressive load settings
    max_corpora: int = Field(
        default=10, ge=2, description="Max corpora for progressive test"
    )

    # Output settings
    output_dir: Path = Field(default=Path("results"))
    generate_pdf: bool = Field(default=True, description="Generate PDF charts")
    generate_csv: bool = Field(default=True, description="Generate CSV data files")

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)


# Corpus size order for progressive loading (smallest to largest)
CORPUS_SIZE_ORDER: list[str] = [
    "cuc",  # 1.6 MB - Ugaritic cuneiform
    "tischendorf",  # 34 MB
    "syrnt",  # 52 MB
    "peshitta",  # 55 MB
    "quran",  # 73 MB
    "sp",  # 147 MB - Samaritan Pentateuch
    "lxx",  # 268 MB
    "n1904",  # 319 MB
    "dss",  # 936 MB - Dead Sea Scrolls
    "bhsa",  # 1.1 GB - BHSA
]


def discover_corpora(corpora_dir: Path) -> list[CorpusConfig]:
    """Discover all corpora in the benchmark directory.

    Args:
        corpora_dir: Path to directory containing corpus subdirectories

    Returns:
        List of CorpusConfig objects for discovered corpora
    """
    # Resolve to absolute path to avoid issues with relative paths in subprocesses
    corpora_dir = corpora_dir.resolve()
    corpora = []
    for corpus_dir in corpora_dir.iterdir():
        if not corpus_dir.is_dir() or corpus_dir.name.startswith("."):
            continue
        tf_path = corpus_dir / "tf"
        if tf_path.exists():
            corpora.append(
                CorpusConfig(
                    name=corpus_dir.name,
                    path=corpus_dir,
                    tf_path=tf_path,
                )
            )
    return sorted(corpora, key=lambda c: c.name)


def get_corpora_by_size(corpora: list[CorpusConfig]) -> list[CorpusConfig]:
    """Sort corpora by size for progressive loading tests.

    Args:
        corpora: List of corpus configs

    Returns:
        Corpora sorted by size (smallest first)
    """
    # Create a map for O(1) lookup
    corpus_map = {c.name: c for c in corpora}

    # Return in size order, filtering to only those that exist
    result = []
    for name in CORPUS_SIZE_ORDER:
        if name in corpus_map:
            result.append(corpus_map[name])

    # Add any corpora not in the predefined order at the end
    known_names = set(CORPUS_SIZE_ORDER)
    for corpus in corpora:
        if corpus.name not in known_names:
            result.append(corpus)

    return result
