"""Corpora management utilities for downloading and validating test corpora."""

from cfabric_benchmarks.corpora.download import CORPORA, main as download_corpora
from cfabric_benchmarks.corpora.validate import main as validate_corpora

__all__ = [
    "CORPORA",
    "download_corpora",
    "validate_corpora",
]
