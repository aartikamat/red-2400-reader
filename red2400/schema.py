"""Schema definition and type coercion for the RED-2400 dataset.

The canonical column set documented for ``rejection_outcomes.jsonl`` is
listed in :data:`SCHEMA`. The dataset is permissive — additional fields may
appear in some rows — so the loader preserves unknown columns and the
coercion helper only touches known columns.
"""

from __future__ import annotations

import pandas as pd

#: Canonical column name -> pandas/numpy dtype string.
#:
#: ``sampleTs`` is stored as a string in the JSONL file but is coerced to a
#: timezone-aware ``datetime64[ns, UTC]`` by :func:`coerce_types`.
SCHEMA: dict[str, str] = {
    "sampleTs": "datetime64[ns, UTC]",
    "mint": "string",
    "symbol": "string",
    "rejectReason": "string",
    "ageMin": "float64",
    "priceUsd": "float64",
    "liquidity": "float64",
    "volume24h": "float64",
    "priceChange5m": "float64",
    "priceChange1h": "float64",
    "priceChange24h": "float64",
    "dexId": "string",
}

#: Subset of :data:`SCHEMA` columns expected to be numeric.
NUMERIC_COLUMNS: tuple[str, ...] = (
    "ageMin",
    "priceUsd",
    "liquidity",
    "volume24h",
    "priceChange5m",
    "priceChange1h",
    "priceChange24h",
)

#: Subset of :data:`SCHEMA` columns expected to be strings.
STRING_COLUMNS: tuple[str, ...] = (
    "mint",
    "symbol",
    "rejectReason",
    "dexId",
)


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce known columns to their canonical dtypes.

    Coercion is best-effort: invalid values become ``NaN`` (numeric) or
    ``NaT`` (datetime). Unknown columns are passed through untouched.

    Args:
        df: A loaded RED-2400 DataFrame. Must not be ``None``.

    Returns:
        A new DataFrame with canonical dtypes applied to known columns.
        The input is not mutated.
    """
    out = df.copy()

    if "sampleTs" in out.columns:
        out["sampleTs"] = pd.to_datetime(
            out["sampleTs"], errors="coerce", utc=True
        )

    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    for col in STRING_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype("string")

    return out
