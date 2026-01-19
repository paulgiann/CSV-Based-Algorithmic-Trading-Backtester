CSV-Based Algorithmic Trading Backtester

This repository contains a small, modular Python backtester that:

Loads market data from a CSV file (timestamp, symbol, price).

Runs one or more strategies to generate trade signals.

Converts signals into orders and simulates execution.

Tracks cash, positions, and equity over time.

Writes a performance report to performance.md.

Contents

data\_generator.py
Provided market data generator. Creates market\_data.csv.

data\_loader.py
Reads market\_data.csv using the Python standard library csv module.

models.py
MarketDataPoint (immutable/frozen dataclass), Order (mutable), and custom exceptions.

strategies.py
Strategy interface plus two example strategies.

engine.py
Execution engine (order validation, simulated execution, portfolio updates, error handling).

reporting.py
Performance metrics and Markdown report writer.

main.py
Runs the full pipeline: load data → run backtest → write report.

tests/
Unit tests.

performance.ipynb
Notebook version that runs a backtest and shows metrics/plots.

Requirements

Python 3.10 or newer.

The backtest itself does not require any external packages.

If you want to run the notebook with plots, install:
python -m pip install matplotlib notebook

How to Run

Generate the CSV data:
python data\_generator.py

This writes market\_data.csv to the repo root.

Run the backtest (writes performance.md):
python main.py --csv market\_data.csv --report performance.md

Optional: disable simulated execution failures (deterministic run):
python main.py --csv market\_data.csv --report performance.md --fail-rate 0

Run unit tests:
python -m unittest discover -s tests -p "test\_\*.py" -v

Simulation Notes

The portfolio is long-only (no shorting).

Orders with invalid quantity are rejected (OrderError).

The engine can simulate occasional execution failures (ExecutionError) and continues processing.

Submission

This repository is intended to be pushed to GitHub and shared via the repository link.

From the repo root:

```powershell
# Go to repo root
cd "C:\Users\Pavlos\Desktop\CSV-Based-Algorithmic-Trading-Backtester"

# (Re)generate market data (instructor generator)
py "C:\Users\Pavlos\Desktop\(325) Assignment 1\data_generator.py" --out ".\market_data.csv"

# Remove prior outputs
Remove-Item -Force .\performance.md -ErrorAction SilentlyContinue
Remove-Item -Force .\periodic_returns.csv -ErrorAction SilentlyContinue

# Run backtester
py .\main.py --csv .\market_data.csv

# Run unit tests
py -m pytest -q




