# Bozon BTC Trading Simulation

A research-oriented project for analyzing historical BTC/USDT data and simulating a strategy based on technical indicators (EMA, RSI, MACD, Bollinger Bands) and support/resistance levels. It includes scripts for data acquisition, indicator calculation, and backtest-style trade simulation.

> **Note:** This repository is for experimentation and backtesting. It is not a production-ready live trading bot.

## Features

- Fetch OHLCV data from Bybit via `ccxt`.
- Load data from CSV and cache downloaded candles.
- Compute technical indicators (EMA, RSI, MACD, Bollinger Bands).
- Generate support/resistance levels from peaks/troughs and clustering.
- Simulate a strategy with entries/exits, TP/SL, and summary statistics.

## Project structure

```
.
├── main.py                # runs the local data pipeline
├── data/                  # historical CSV files
└── scripts/
    ├── bb_data_load.py    # data fetching/loading helpers
    ├── tools.py           # indicators and level generation
    └── simulation.py      # strategy simulation logic
```

## Requirements

- Python 3.10+
- Libraries (example): `pandas`, `numpy`, `ccxt`, `ta`, `scipy`, `sklearn`, `mplfinance`, `yahooquery`

> There is no `requirements.txt` yet, so dependencies should be installed based on the imported modules.

## Quick start

1. Prepare CSV data in `data/` or download it via `ccxt`.
2. Ensure the dataset contains OHLCV columns.
3. Run the main script:

```bash
python main.py
```

## Data flow

1. **Fetch/load data** – `scripts/bb_data_load.py`.
2. **Compute indicators** – `scripts/tools.py` (`TechnicalIndicators`).
3. **Generate levels** – `scripts/tools.py` (`GenerateLevels`).
4. **Run simulation** – `scripts/simulation.py` (`Simulation`).

## Strategy configuration

Strategy parameters (RSI, MACD, TP/SL, level buffer) live in the `Simulation` class in `scripts/simulation.py`. Level parameters are defined in `GenerateLevels` in `scripts/tools.py`.

## Data

The project assumes hourly BTC/USDT data, e.g. `data/BTC_USDT_1h_t_full.csv`. You can extend or rebuild history using `fetch_full_history` in `scripts/bb_data_load.py`.

## Limitations

- The strategy is illustrative and not validated across multiple markets.
- No unit tests or experiment standardization yet.
- No live trading or portfolio risk management.

## Suggested next steps

- Add `requirements.txt` and/or `pyproject.toml`.
- Add unit tests for indicator computations and simulation logic.
- Extend reporting (e.g., equity curve, Sharpe ratio).
- Add configuration via `.yaml` or `.env`.

## Disclaimer

This repository is for educational and research purposes only. The author is not responsible for investment decisions made based on this code.
