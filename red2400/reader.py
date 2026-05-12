"""Streaming reader for the RED-2400 ``rejection_outcomes.jsonl`` file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from red2400.schema import SCHEMA, coerce_types

if TYPE_CHECKING:
    import polars as pl


class RED2400Reader:
    """Load and summarize the RED-2400 rejection-outcomes JSONL file.

    The reader is tolerant of malformed lines (they are skipped and reported
    by :meth:`validate`) and preserves any unknown columns it encounters.

    Attributes:
        path: Path to the source ``.jsonl`` file.

    Example:
        >>> reader = RED2400Reader("rejection_outcomes.jsonl")
        >>> df = reader.load()
        >>> stats = reader.describe()
        >>> stats["n_rows"]  # doctest: +SKIP
        2412
    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader.

        Args:
            path: Filesystem path to ``rejection_outcomes.jsonl``.

        Raises:
            FileNotFoundError: If ``path`` does not exist.
        """
        self.path: Path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"RED-2400 file not found: {self.path}")

        self._cached_df: pd.DataFrame | None = None
        self._malformed_lines: list[int] = []

    def load(self) -> pd.DataFrame:
        """Stream the JSONL file into a pandas DataFrame.

        Malformed lines are skipped silently and recorded for later
        retrieval via :meth:`validate`. Unknown columns are preserved.

        Returns:
            A DataFrame with canonical dtypes applied via
            :func:`red2400.schema.coerce_types`.
        """
        records: list[dict[str, Any]] = []
        malformed: list[int] = []

        with self.path.open("r", encoding="utf-8") as handle:
            for lineno, raw in enumerate(handle, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    malformed.append(lineno)
                    continue
                if isinstance(obj, dict):
                    records.append(obj)
                else:
                    malformed.append(lineno)

        df = pd.DataFrame.from_records(records)
        df = coerce_types(df)

        self._cached_df = df
        self._malformed_lines = malformed
        return df

    def load_polars(self) -> "pl.DataFrame":
        """Stream the JSONL file into a polars DataFrame.

        This is an optional fast path. If polars is not installed, an
        :class:`ImportError` is raised with installation instructions.

        Returns:
            A polars DataFrame. Type coercion is left to polars' own
            inference; downstream code should validate.

        Raises:
            ImportError: If polars is not installed.
        """
        try:
            import polars as pl
        except ImportError as exc:  # pragma: no cover - depends on env
            raise ImportError(
                "polars is not installed. Install with `pip install polars` "
                "to use RED2400Reader.load_polars()."
            ) from exc

        return pl.read_ndjson(self.path)

    def describe(self) -> dict[str, Any]:
        """Compute summary statistics for the dataset.

        Returns:
            A dictionary with keys:

            - ``n_rows``: total parsed rows
            - ``n_columns``: column count
            - ``date_range``: ``(min_ts, max_ts)`` tuple or ``(None, None)``
            - ``unique_mints``: distinct mint count
            - ``unique_reject_reasons``: distinct rejection reason count
            - ``reject_reason_counts``: per-reason row counts (dict)
            - ``missing_value_rates``: per-canonical-column NaN/NaT rate
            - ``malformed_lines``: count of skipped malformed lines
        """
        df = self._cached_df if self._cached_df is not None else self.load()

        if "sampleTs" in df.columns and len(df) > 0:
            ts = df["sampleTs"]
            date_range = (ts.min(), ts.max())
        else:
            date_range = (None, None)

        unique_mints = (
            int(df["mint"].nunique()) if "mint" in df.columns else 0
        )
        if "rejectReason" in df.columns:
            unique_reasons = int(df["rejectReason"].nunique())
            reason_counts = (
                df["rejectReason"].value_counts(dropna=False).to_dict()
            )
            reason_counts = {str(k): int(v) for k, v in reason_counts.items()}
        else:
            unique_reasons = 0
            reason_counts = {}

        missing_rates: dict[str, float] = {}
        for col in SCHEMA:
            if col in df.columns and len(df) > 0:
                missing_rates[col] = float(df[col].isna().mean())
            else:
                missing_rates[col] = 1.0 if len(df) > 0 else 0.0

        return {
            "n_rows": int(len(df)),
            "n_columns": int(len(df.columns)),
            "date_range": date_range,
            "unique_mints": unique_mints,
            "unique_reject_reasons": unique_reasons,
            "reject_reason_counts": reason_counts,
            "missing_value_rates": missing_rates,
            "malformed_lines": len(self._malformed_lines),
        }

    def validate(self) -> list[str]:
        """Return human-readable schema warnings (not exceptions).

        Performs the following non-fatal checks:

        - Reports any canonical columns that are missing from the loaded
          file.
        - Reports any malformed lines encountered during :meth:`load`.
        - Reports any extra (non-canonical) columns as informational notes.

        Returns:
            A list of warning strings. Empty list means no deviations.
        """
        df = self._cached_df if self._cached_df is not None else self.load()
        warnings: list[str] = []

        missing_cols = [c for c in SCHEMA if c not in df.columns]
        for col in missing_cols:
            warnings.append(f"missing canonical column: {col!r}")

        extra_cols = [c for c in df.columns if c not in SCHEMA]
        for col in extra_cols:
            warnings.append(f"extra (non-canonical) column present: {col!r}")

        if self._malformed_lines:
            preview = self._malformed_lines[:5]
            warnings.append(
                f"skipped {len(self._malformed_lines)} malformed line(s); "
                f"first offsets: {preview}"
            )

        return warnings
