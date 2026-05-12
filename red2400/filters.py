"""Common row filters for RED-2400 DataFrames.

Each filter returns a new DataFrame view and does not mutate its input.
Filters return an empty DataFrame (with original columns preserved) when
the relevant column is missing, rather than raising, so they can be
composed safely on heterogeneous inputs.
"""

from __future__ import annotations

from typing import Union

import pandas as pd

DateLike = Union[str, pd.Timestamp]


def by_reason(df: pd.DataFrame, reason: str) -> pd.DataFrame:
    """Filter rows whose ``rejectReason`` equals ``reason``.

    Args:
        df: A loaded RED-2400 DataFrame.
        reason: Exact reject-reason string to match (case-sensitive).

    Returns:
        Subset DataFrame. Empty if the column is missing or no row matches.
    """
    if "rejectReason" not in df.columns:
        return df.iloc[0:0].copy()
    mask = df["rejectReason"] == reason
    return df.loc[mask].copy()


def by_date_range(
    df: pd.DataFrame,
    start: DateLike | None = None,
    end: DateLike | None = None,
) -> pd.DataFrame:
    """Filter rows whose ``sampleTs`` falls in the inclusive ``[start, end]``.

    Either bound may be ``None`` to leave that side open.

    Args:
        df: A loaded RED-2400 DataFrame.
        start: Inclusive lower bound (timezone-aware or naive). May be
            ``None``.
        end: Inclusive upper bound. May be ``None``.

    Returns:
        Subset DataFrame. Empty if the timestamp column is missing.
    """
    if "sampleTs" not in df.columns:
        return df.iloc[0:0].copy()

    ts = df["sampleTs"]
    mask = pd.Series(True, index=df.index)

    if start is not None:
        start_ts = pd.to_datetime(start, utc=True)
        mask &= ts >= start_ts
    if end is not None:
        end_ts = pd.to_datetime(end, utc=True)
        mask &= ts <= end_ts

    return df.loc[mask].copy()


def by_dex(df: pd.DataFrame, dex_id: str) -> pd.DataFrame:
    """Filter rows whose ``dexId`` equals ``dex_id``.

    Args:
        df: A loaded RED-2400 DataFrame.
        dex_id: Exact DEX identifier string to match.

    Returns:
        Subset DataFrame. Empty if the column is missing or no row matches.
    """
    if "dexId" not in df.columns:
        return df.iloc[0:0].copy()
    mask = df["dexId"] == dex_id
    return df.loc[mask].copy()


def by_min_liquidity(df: pd.DataFrame, min_usd: float) -> pd.DataFrame:
    """Filter rows whose ``liquidity`` is at least ``min_usd``.

    Rows with missing liquidity are excluded.

    Args:
        df: A loaded RED-2400 DataFrame.
        min_usd: Minimum USD liquidity threshold (inclusive).

    Returns:
        Subset DataFrame. Empty if the column is missing.
    """
    if "liquidity" not in df.columns:
        return df.iloc[0:0].copy()
    mask = df["liquidity"].fillna(-1) >= min_usd
    return df.loc[mask].copy()
