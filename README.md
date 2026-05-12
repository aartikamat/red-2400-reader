# RED-2400 Reader

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](DATA_LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19989075-blue)](https://doi.org/10.5281/zenodo.19989075)

A small, dependency-light Python package for loading and analyzing the
**RED-2400 (Rejection Event Dataset, 2,400+ events)** public benchmark dataset
published by Arati U. Kamat. RED-2400 contains canonical post-rejection
outcome records for tokens that were filtered out by an automated screening
system, with their on-chain market state tracked after the rejection decision.

The dataset is hosted on Zenodo and described in a companion SSRN manuscript.
This repository provides a typed reader, schema validator, common filters,
and a quickstart notebook.

## Citation

If you use this dataset or package in academic work, please cite:

**Plain text**

Kamat, A. U. (2026). *RED-2400: Public Benchmark Dataset (Rejection Event
Dataset, 2,400+ events)* [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.19989075

**BibTeX**

```bibtex
@dataset{kamat_red2400_2026,
  author       = {Kamat, Arati U.},
  title        = {{RED-2400: Public Benchmark Dataset
                  (Rejection Event Dataset, 2,400+ events)}},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19989075},
  url          = {https://doi.org/10.5281/zenodo.19989075}
}

@misc{kamat_red2400_manuscript_2026,
  author       = {Kamat, Arati U.},
  title        = {{RED-2400 Manuscript}},
  year         = {2026},
  doi          = {10.5281/zenodo.20011631},
  howpublished = {SSRN 6702198}
}
```

**APA**

Kamat, A. U. (2026). RED-2400: Public benchmark dataset (Rejection Event
Dataset, 2,400+ events) [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.19989075

## Installation

This package is not yet on PyPI. Install from source:

```bash
git clone https://github.com/<owner>/red-2400-reader.git
cd red-2400-reader
pip install -e .
```

Optional fast reader backend:

```bash
pip install polars
```

## Quickstart

```python
from red2400 import RED2400Reader, by_reason, by_min_liquidity

reader = RED2400Reader("rejection_outcomes.jsonl")
df = reader.load()

print(reader.describe())
# {'n_rows': 2412, 'date_range': (...), 'unique_mints': 2398, ...}

# Filter to a single reject reason
ultra_fast = by_reason(df, "ultra_fast_reject")

# Filter to events that retained at least $5k liquidity
liquid = by_min_liquidity(df, 5_000.0)
```

## Schema

`rejection_outcomes.jsonl` is line-delimited JSON. Each row represents one
rejected token whose post-rejection market state was sampled.

| Column            | Type    | Description                                          |
|-------------------|---------|------------------------------------------------------|
| `sampleTs`        | string  | ISO-8601 timestamp of the post-rejection sample      |
| `mint`            | string  | Solana mint address                                  |
| `symbol`          | string  | Token symbol                                         |
| `rejectReason`    | string  | Categorical rejection reason                         |
| `ageMin`          | number  | Minutes since token launch at rejection              |
| `priceUsd`        | number  | USD price at sample time                             |
| `liquidity`       | number  | USD pool liquidity                                   |
| `volume24h`       | number  | 24-hour USD volume                                   |
| `priceChange5m`   | number  | Percent change over 5 minutes                        |
| `priceChange1h`   | number  | Percent change over 1 hour                           |
| `priceChange24h`  | number  | Percent change over 24 hours                         |
| `dexId`           | string  | DEX identifier (e.g., `raydium`, `orca`)             |

Additional fields may appear in some rows; the reader is tolerant and will
preserve unknown columns.

## License

- **Code** in this repository: [MIT](LICENSE).
- **RED-2400 dataset** itself: [CC-BY-4.0](DATA_LICENSE). See the Zenodo
  record at https://doi.org/10.5281/zenodo.19989075 for canonical terms.

## Author

- Arati U. Kamat
- ORCID: [0009-0000-4781-312X](https://orcid.org/0009-0000-4781-312X)
- IEEE Member #102289285
- GitHub: see repository owner

If you use this dataset, please cite Kamat (2026) as shown above.
