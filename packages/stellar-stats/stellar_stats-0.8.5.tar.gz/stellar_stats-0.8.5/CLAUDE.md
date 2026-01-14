# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- `stellar-stats run` - Run the Streamlit dashboard application
- `stellar-stats gen-investors <account_name> --investor-name <name>` - Generate investors.csv from cashflow data
- `pip install -e .` - Install package in development mode
- `pip install -e .[dev]` - Install with development dependencies
- `pip install -e .[test]` - Install with test dependencies

### Package Management
This project uses pip with pyproject.toml configuration. No package.json or specific test commands are defined.

## Architecture

This is a Streamlit-based trading statistics dashboard that analyzes backtest and live trading performance.

### Core Components
- **app.py** - Main Streamlit application with dashboard UI and data visualization
- **cli.py** - Command-line interface using Click, wraps Streamlit execution
- **data.py** - Data loading functions for returns, trades, round trips, slippage, and benchmarks
- **config.py** - Configuration management via TOML files, API setup (Tushare, yfinance)
- **ui.py** - UI components and plotting functions for performance visualization
- **auth.py** - Authentication setup for the dashboard
- **utils.py** - Utility functions including cache management
- **stats.py** - Statistical analysis functions and performance metrics calculations
- **roundtrip.py** - Round-trip analysis and trade extraction functions

### Data Sources
- Local CSV/HDF/Parquet files containing returns, trades, round trips, slippage data
- Remote data via yfinance for benchmark symbols
- Tushare API for Chinese market indices (requires token in config.toml)
- Optional investors.csv for investor-specific performance tracking

### Key Features
- Multi-account performance analysis and comparison
- Benchmark comparison with leverage options
- Period selection (YTD, inception, custom ranges)
- Performance metrics, drawdown analysis, return distributions
- Trade analysis including underlying breakdowns and slippage tracking
- Round-trip trade analysis and extraction capabilities
- Investor-specific return calculations when investors.csv exists
- Automated investor data generation from cashflow data

### Configuration
- Optional config.toml file defines accounts and data directories
- Falls back to auto-discovery of directories for account data
- Supports custom benchmark symbols and API tokens

### Dependencies
Uses specialized financial libraries: empyrical-reloaded for performance metrics, with local implementations for trade analysis functions. Additional dependencies include streamlit, plotly, click, yfinance, tushare, tomlkit, tabulate, numpy, pandas and extra-streamlit-components for enhanced functionality.

## Coding Standards

### Python Code Style
- **All imports must be at the top of the file** - Never use imports inside functions or methods
- Follow PEP 8 style guidelines
- Use descriptive variable names and add comments for complex logic