# CSV-Based Algorithmic Trading Backtester

This repo contains a small, modular backtester that:

1. Loads market data from a CSV file (`timestamp,symbol,price`).
2. Runs one or more strategies to generate trade signals.
3. Converts signals into orders and simulates execution.
4. Tracks positions and equity through time.
5. Writes a `performance.md` report.

## Files

- `data_generator.py` - provided market data generator to create `market_data.csv`
- `data_loader.py` - reads `market_data.csv` using the standard library `csv` module
- `models.py` - immutable `MarketDataPoint` dataclass, mutable `Order`, custom exceptions
- `strategies.py` - `Strategy` interface + two concrete strategies
- `engine.py` - execution engine (portfolio, order simulation, resiliency)
- `reporting.py` - return metrics + Markdown report writer
- `main.py` - entrypoint
- `tests/` - unit tests
- `performance.ipynb` - notebook that runs a full backtest and shows plots/metrics

## Setup

Python 3.10+ is recommended.

No external packages are required to run the backtest.

(Optional) For notebook plotting:

```bash
python -m pip install matplotlib notebook
```

## Quick Start

From the repo root:

1) Generate data:

```bash
python data_generator.py
```

This creates `market_data.csv`.

2) Run the backtest:

```bash
python main.py --csv market_data.csv --report performance.md
```

3) Run unit tests:

```bash
python -m unittest -v
```

## Notes on the Simulation

- The engine uses a simple cash account + long-only positions (no shorting).
- Some executions are intentionally failed to demonstrate `ExecutionError` handling (controlled by `--fail-rate`).

## Delivering (GitHub)

1) Create a new GitHub repo under your account.
2) From this folder:

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
git push -u origin main
```
