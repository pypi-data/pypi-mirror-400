# Stellar Stats

A Streamlit-based trading statistics dashboard that analyzes backtest and live trading performance with comprehensive metrics and visualizations.

## Features

- **Multi-account performance analysis** - Compare performance across different trading accounts
- **Benchmark comparison** - Compare against market indices with leverage options
- **Flexible time periods** - YTD, inception-to-date, or custom date ranges
- **Comprehensive metrics** - Performance metrics, drawdown analysis, return distributions
- **Trade analysis** - Detailed breakdowns by underlying assets and slippage tracking
- **Round-trip analysis** - Extract and analyze complete trading round-trips
- **Investor tracking** - Calculate investor-specific returns

## Installation

```bash
pip install stellar-stats
```


## Usage

### Run the Dashboard

```bash
stellar-stats run
```

This launches the Streamlit web interface for interactive analysis.


## Configuration

Create an optional `config.toml` file to define:

- Account configurations and data directories
- Custom benchmark symbols
- API tokens (Tushare for Chinese market data)

The system will auto-discover account directories if no configuration is provided, which is useful for viewing backtesting results.

## Data Sources

- **Local files**: CSV/HDF/Parquet files containing returns, trades, round trips, and slippage data
- **Market data**: yfinance for global benchmark symbols
- **Chinese markets**: Tushare API (requires token configuration)
- **Investor data**: Optional investors.csv for investor-specific analysis


## License

MIT

