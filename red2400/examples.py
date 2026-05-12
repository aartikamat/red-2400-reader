"""Runnable demonstration script for the red2400 package.

Usage:
    python -m red2400.examples path/to/rejection_outcomes.jsonl

The script loads the dataset, prints a short summary, runs a couple of
filters, and exits with status 0 on success.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from red2400 import (
    RED2400Reader,
    by_min_liquidity,
    by_reason,
)


def main(argv: list[str] | None = None) -> int:
    """Run the demonstration.

    Args:
        argv: Optional argv override (useful for tests).

    Returns:
        Process exit code. ``0`` on success.
    """
    parser = argparse.ArgumentParser(
        description="Demonstrate the red2400 reader."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to rejection_outcomes.jsonl",
    )
    parser.add_argument(
        "--reason",
        default=None,
        help="Optional reject reason to filter on.",
    )
    parser.add_argument(
        "--min-liquidity",
        type=float,
        default=None,
        help="Optional minimum USD liquidity threshold.",
    )
    args = parser.parse_args(argv)

    reader = RED2400Reader(args.path)
    df = reader.load()
    stats = reader.describe()
    warnings = reader.validate()

    print(f"Loaded {stats['n_rows']} rows, {stats['n_columns']} columns")
    print(f"Date range: {stats['date_range']}")
    print(f"Unique mints: {stats['unique_mints']}")
    print(f"Unique reject reasons: {stats['unique_reject_reasons']}")
    print("Top reject reasons:")
    top = sorted(
        stats["reject_reason_counts"].items(),
        key=lambda kv: kv[1],
        reverse=True,
    )[:5]
    for reason, count in top:
        print(f"  {reason}: {count}")

    if warnings:
        print("\nSchema warnings:")
        for w in warnings:
            print(f"  - {w}")

    if args.reason is not None:
        subset = by_reason(df, args.reason)
        print(f"\nRows with reason={args.reason!r}: {len(subset)}")

    if args.min_liquidity is not None:
        subset = by_min_liquidity(df, args.min_liquidity)
        print(
            f"\nRows with liquidity >= ${args.min_liquidity:.2f}: "
            f"{len(subset)}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
