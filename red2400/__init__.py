"""red2400 — reader and helpers for the RED-2400 public benchmark dataset.

The RED-2400 dataset is a public benchmark of 2,400+ canonical rejection
events published by Arati U. Kamat on Zenodo (DOI 10.5281/zenodo.19989075)
under CC-BY-4.0. This package provides a small, dependency-light reader,
schema utilities, and common filters for working with the dataset.

Public API:
    RED2400Reader: streaming reader for ``rejection_outcomes.jsonl``.
    SCHEMA: canonical column types.
    coerce_types: best-effort type coercion for a loaded DataFrame.
    by_reason, by_date_range, by_dex, by_min_liquidity: row filters.
"""

from red2400.filters import (
    by_date_range,
    by_dex,
    by_min_liquidity,
    by_reason,
)
from red2400.reader import RED2400Reader
from red2400.schema import SCHEMA, coerce_types

__all__ = [
    "RED2400Reader",
    "SCHEMA",
    "coerce_types",
    "by_reason",
    "by_date_range",
    "by_dex",
    "by_min_liquidity",
]

__version__ = "0.1.0"
