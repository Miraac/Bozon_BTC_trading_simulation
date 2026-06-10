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


## Pytest practice in this project

You can practice `pytest` here by testing strategy logic in small, deterministic units before testing full backtests.

### Suggested learning path

1. **Start from pure decision functions** in `Simulation`:
   - `_rsi_long_signal` / `_rsi_short_signal`
   - `_macd_long_signal` / `_macd_short_signal`
   - `_level_signal`
2. **Then test integration behavior** of `launch_simulation()` with controlled/mocked signals.
3. **Finally add data-oriented tests** for indicator and level generation in `scripts/tools.py`.

### Ready example tests

A starter pytest suite is included in `tests/test_simulation.py` and can be run with:

```bash
pytest -q
```

### Practical exercises

- Add parametrized tests for RSI thresholds (`pytest.mark.parametrize`).
- Add edge-case tests for very short history windows (e.g. less than observation period).
- Add regression tests that lock expected behavior for a known historical slice from `data/`.
- Add fixtures for reusable mock/fake market data.

### Notes

Because this repo currently has no dependency lock file, ensure runtime packages are installed in your environment before running tests (`numpy`, `pandas`, `ta`, etc.).

## Suggested next steps

- Add `requirements.txt` and/or `pyproject.toml`.
- Add unit tests for indicator computations and simulation logic.
- Extend reporting (e.g., equity curve, Sharpe ratio).
- Add configuration via `.yaml` or `.env`.

## Disclaimer

This repository is for educational and research purposes only. The author is not responsible for investment decisions made based on this code.
