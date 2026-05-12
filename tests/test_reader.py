"""Unit tests for the red2400 package, exercised against a synthetic fixture."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from red2400 import (
    RED2400Reader,
    SCHEMA,
    by_date_range,
    by_dex,
    by_min_liquidity,
    by_reason,
    coerce_types,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample.jsonl"


@pytest.fixture(scope="module")
def reader() -> RED2400Reader:
    """A reader bound to the bundled synthetic fixture."""
    return RED2400Reader(FIXTURE_PATH)


@pytest.fixture(scope="module")
def df(reader: RED2400Reader) -> pd.DataFrame:
    """Loaded DataFrame from the synthetic fixture."""
    return reader.load()


def test_fixture_exists() -> None:
    assert FIXTURE_PATH.exists(), "synthetic fixture is missing"


def test_load_returns_dataframe(df: pd.DataFrame) -> None:
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10


def test_schema_columns_present(df: pd.DataFrame) -> None:
    for col in SCHEMA:
        assert col in df.columns, f"missing canonical column {col!r}"


def test_coerce_types_idempotent(df: pd.DataFrame) -> None:
    out = coerce_types(df)
    # Re-applying coercion should not change dtypes.
    out2 = coerce_types(out)
    assert (out.dtypes == out2.dtypes).all()


def test_describe_returns_expected_keys(reader: RED2400Reader) -> None:
    stats = reader.describe()
    expected_keys = {
        "n_rows",
        "n_columns",
        "date_range",
        "unique_mints",
        "unique_reject_reasons",
        "reject_reason_counts",
        "missing_value_rates",
        "malformed_lines",
    }
    assert expected_keys.issubset(stats.keys())
    assert stats["n_rows"] == 10
    assert stats["unique_mints"] == 10
    assert stats["unique_reject_reasons"] == 4


def test_validate_clean_fixture(reader: RED2400Reader) -> None:
    reader.load()
    warnings = reader.validate()
    # Synthetic fixture is canonical; no warnings expected.
    assert warnings == []


def test_filter_by_reason(df: pd.DataFrame) -> None:
    sub = by_reason(df, "ultra_fast_reject")
    assert len(sub) == 4
    assert (sub["rejectReason"] == "ultra_fast_reject").all()


def test_filter_by_dex(df: pd.DataFrame) -> None:
    sub = by_dex(df, "orca")
    assert len(sub) == 3
    assert (sub["dexId"] == "orca").all()


def test_filter_by_date_range(df: pd.DataFrame) -> None:
    sub = by_date_range(
        df,
        start="2026-04-01T12:15:00Z",
        end="2026-04-01T12:30:00Z",
    )
    # 12:15, 12:20, 12:25, 12:30 -> 4 rows
    assert len(sub) == 4


def test_filter_by_min_liquidity(df: pd.DataFrame) -> None:
    sub = by_min_liquidity(df, 5_000.0)
    assert len(sub) == 3
    assert (sub["liquidity"] >= 5_000.0).all()


def test_malformed_line_tolerated(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    good_line = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()[0]
    bad.write_text(
        good_line + "\n" + "this is not json\n" + good_line + "\n",
        encoding="utf-8",
    )
    reader = RED2400Reader(bad)
    out = reader.load()
    assert len(out) == 2
    warnings = reader.validate()
    assert any("malformed" in w for w in warnings)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        RED2400Reader(tmp_path / "does_not_exist.jsonl")
