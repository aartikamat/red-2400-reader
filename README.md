# RED-2400 Reader

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](DATA_LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19989074-blue)](https://doi.org/10.5281/zenodo.19989074)
[![arXiv](https://img.shields.io/badge/arXiv-2605.12151-b31b1b.svg)](https://arxiv.org/abs/2605.12151)

> **Legacy reader:** this reader (v0.1.0, May 2026) reads the May 2026 JSON-lines outcomes file
> `rejection_outcomes.jsonl`. It does not read the CSV files of the current
> RED-2400 deposit (version 4.0: `rejections.csv`, `rejection_outcomes.csv`,
> `graveyard_lifecycle.csv`); load those directly with `pandas.read_csv`.

A small, dependency-light Python package for loading and analyzing the
**RED-2400** public benchmark dataset published by Arati Uday Kamat
("2400" is the dataset name, not a count). RED-2400 contains canonical post-rejection
outcome records for tokens that were filtered out by an automated screening
system, with their on-chain market state tracked after the rejection decision.

The dataset is hosted on Zenodo and described in a companion SSRN manuscript.
This repository provides a typed reader, schema validator, common filters,
and a quickstart notebook.

## Citation

If you use this dataset or package in academic work, please cite:

**Plain text**

Kamat, A. U. (2026). *RED-2400: A Public Benchmark of Algorithmically-Rejected
Trading Events with Outcome Labels* [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.19989074

**BibTeX**

```bibtex
@dataset{kamat_red2400_2026,
  author       = {Kamat, Arati Uday},
  title        = {{RED-2400: A Public Benchmark of Algorithmically-Rejected
                  Trading Events with Outcome Labels}},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19989074},
  url          = {https://doi.org/10.5281/zenodo.19989074}
}

@misc{kamat_red2400_manuscript_2026,
  author       = {Kamat, Arati Uday},
  title        = {{RED-2400: A Public Benchmark of Algorithmically-Rejected Trading Events with Outcome Labels}},
  year         = {2026},
  eprint       = {2605.12151},
  archivePrefix= {arXiv},
  primaryClass = {q-fin.TR},
  doi          = {10.5281/zenodo.20011630},
  howpublished = {arXiv:2605.12151, SSRN 6702198, Zenodo 10.5281/zenodo.20011630}
}
```

**APA**

Kamat, A. U. (2026). RED-2400: A public benchmark of algorithmically-rejected
trading events with outcome labels [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.19989074

## Installation

This package is not published on PyPI. Install from source:

```bash
git clone https://github.com/aartikamat/red-2400-reader.git
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
  record at https://doi.org/10.5281/zenodo.19989074 for canonical terms.

## Author

- Arati Uday Kamat
- ORCID: [0009-0000-4781-312X](https://orcid.org/0009-0000-4781-312X)
- GitHub: [@aartikamat](https://github.com/aartikamat)

If you use this dataset, please cite Kamat (2026) as shown above.
