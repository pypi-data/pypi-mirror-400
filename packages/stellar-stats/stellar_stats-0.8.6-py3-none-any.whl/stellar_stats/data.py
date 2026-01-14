import os

import numpy as np
import pandas as pd
import streamlit as st
import tushare as ts
import yfinance as yf

from stellar_stats.stats import return_stats


def load_returns(strategies, datadirs, strategy_info=None):
    return_dfs = []
    for strategy in strategies:
        if strategy in datadirs:
            # Handle both single directories and lists of directories (strategies)
            dirs_to_check = (
                datadirs[strategy]
                if isinstance(datadirs[strategy], list)
                else [datadirs[strategy]]
            )

            # Check if this is a strategy with multiple accounts
            if (
                isinstance(datadirs[strategy], list)
                and strategy_info
                and strategy in strategy_info
            ):
                # Use strategy merging logic for multiple accounts
                strategy_data = strategy_info[strategy]
                account_configs = strategy_data.get("accounts", [])

                if len(account_configs) > 1:
                    # Merge multiple accounts with proper date transitions
                    merged_df = _merge_strategy_accounts(account_configs)
                    if merged_df is not None:
                        return_dfs.append(merged_df)
                else:
                    # Single account in strategy, load with date filtering
                    for config in account_configs:
                        account_dir = config["account_dir"]
                        start_date = (
                            pd.to_datetime(config["start_date"])
                            if config["start_date"]
                            else None
                        )
                        end_date = (
                            pd.to_datetime(config["end_date"])
                            if config["end_date"]
                            else None
                        )

                        df = _load_single_returns_file(account_dir)
                        if df is not None:
                            # Filter by date range
                            if start_date:
                                df = df[df.index >= start_date]
                            if end_date:
                                df = df[df.index <= end_date]

                            if len(df) > 0:
                                return_dfs.append(df)
            else:
                # Regular account loading
                for data_dir in dirs_to_check:
                    df = _load_single_returns_file(data_dir)
                    if df is not None:
                        return_dfs.append(df)

    if len(return_dfs) > 1:
        returns = pd.concat(return_dfs).groupby(level=0).sum()
        returns = return_stats(returns)
    elif len(return_dfs) == 1:
        returns = return_dfs[0]
    else:
        returns = None

    return returns


def _load_single_returns_file(data_dir):
    """Load returns from a single directory."""
    if os.path.exists(f"{data_dir}/returns.csv"):
        return pd.read_csv(f"{data_dir}/returns.csv", index_col=0, parse_dates=True)
    elif os.path.exists(f"{data_dir}/returns.hdf"):
        return pd.read_hdf(f"{data_dir}/returns.hdf")
    elif os.path.exists(f"{data_dir}/returns.parquet"):
        return pd.read_parquet(f"{data_dir}/returns.parquet")
    return None


def _merge_strategy_accounts(account_configs):
    """Merge multiple accounts for a strategy based on date ranges."""
    dfs = []

    # Load and filter each account by its date range
    for config in account_configs:
        account_dir = config["account_dir"]
        start_date = (
            pd.to_datetime(config["start_date"]) if config["start_date"] else None
        )
        end_date = pd.to_datetime(config["end_date"]) if config["end_date"] else None

        df = _load_single_returns_file(account_dir)
        if df is None:
            continue

        # Filter by date range
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        if len(df) > 0:
            dfs.append(df)

    if len(dfs) == 0:
        return None
    elif len(dfs) == 1:
        return dfs[0]

    # Merge accounts with proper transitions
    result = dfs[0].copy()

    for i in range(1, len(dfs)):
        next_df = dfs[i].copy()

        # Check for overlap or gap
        last_date = result.index[-1]
        first_date = next_df.index[0]

        if last_date == first_date:
            # Same date overlap - combine the accounts intelligently
            last_eod_value = result["last_eod_value"].iloc[-1]
            current_cashflow = result["cashflow"].iloc[-1]
            next_account_value = next_df["account_value"].iloc[0]
            next_cashflow = next_df["cashflow"].iloc[0]

            # Combine cashflows to preserve transfer information
            combined_cashflow = current_cashflow + next_cashflow

            # Use the next account's value as the final account value
            # This assumes the fund transfer is captured in the cashflows
            result.loc[last_date, "account_value"] = next_account_value
            result.loc[last_date, "cashflow"] = combined_cashflow

            # Recalculate P&L considering the combined cashflow
            today_pnl = next_account_value - last_eod_value - combined_cashflow
            result.loc[last_date, "today_pnl"] = today_pnl

            # Calculate returns based on adjusted last EOD value
            adjusted_last_eod = last_eod_value + max(0, combined_cashflow)
            result.loc[last_date, "returns"] = (
                today_pnl / adjusted_last_eod if adjusted_last_eod != 0 else 0
            )

            # Print transition info for transparency
            print(
                f"Account transition on {last_date}: combined cashflow={combined_cashflow}, account_value={next_account_value}"
            )

            # Skip the first row of next_df
            next_df = next_df.iloc[1:]
        else:
            # Gap between accounts - maintain continuity
            prev_account_value = result["account_value"].iloc[-1]
            prev_cashflow = result["cashflow"].iloc[-1]

            # Adjust the previous account's final value to exclude outgoing transfer
            # This assumes the transfer appears as negative cashflow
            adjusted_prev_value = prev_account_value - prev_cashflow

            # Set the next account's starting point to maintain continuity
            next_df["last_eod_value"].iat[0] = adjusted_prev_value

            # Recalculate the first day's returns in the next account
            next_first_pnl = next_df["today_pnl"].iloc[0]
            next_first_cashflow = next_df["cashflow"].iloc[0]

            # Adjust for any remaining transfer amount
            adjusted_last_eod = adjusted_prev_value + max(0, next_first_cashflow)
            if adjusted_last_eod != 0:
                next_df["returns"].iat[0] = next_first_pnl / adjusted_last_eod
            else:
                next_df["returns"].iat[0] = 0

            # Print gap handling info for transparency
            print(
                f"Account gap from {last_date} to {first_date}: prev_value={prev_account_value}, adjusted={adjusted_prev_value}"
            )

        # Concatenate
        result = pd.concat([result, next_df])

    return result


# @st.cache_data
def load_remote(symbol, start="2000-01-01"):
    data_df = yf.download(symbol, start=start, auto_adjust=True)
    data_df.columns = data_df.columns.droplevel("Ticker")
    data_df = data_df.sort_index()
    data_df.index.name = "date"
    returns = pd.DataFrame(
        {
            "last_eod_value": data_df["Close"].shift(1).dropna(),
            "account_value": data_df["Close"][1:],
            "cashflow": 0,
            "returns": data_df["Close"].pct_change().dropna(),
        }
    )
    return returns


def _smart_load_remote(symbol, datadirs=None, strategy_info=None):
    """Wrapper for load_remote that uses smart start date based on account data."""
    if datadirs is None:
        # Fallback to default if no datadirs provided
        return load_remote(symbol)

    smart_start = _get_smart_start_date(datadirs, strategy_info)
    return load_remote(symbol, start=smart_start)


def _smart_tushare_index(pro, ts_code, datadirs=None, strategy_info=None):
    """Wrapper for Tushare index_daily that uses smart date range based on account data."""
    if datadirs is None:
        # Fallback to default if no datadirs provided
        today = pd.Timestamp.now().strftime("%Y%m%d")
        return pro.index_daily(ts_code=ts_code, start_date="20000101", end_date=today)

    smart_start = _get_smart_start_date(datadirs, strategy_info)
    today = pd.Timestamp.now().strftime("%Y%m%d")
    # Convert smart_start to YYYYMMDD format for Tushare
    start_date = pd.to_datetime(smart_start).strftime("%Y%m%d")

    return pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=today)


def _get_smart_start_date(datadirs, strategy_info=None):
    """Determine the earliest date from account data to use as benchmark start date."""
    earliest_date = None

    # Check strategy date ranges first
    if strategy_info:
        for strategy_data in strategy_info.values():
            for account_config in strategy_data.get("accounts", []):
                if "start_date" in account_config:
                    start_date = pd.to_datetime(account_config["start_date"])
                    if earliest_date is None or start_date < earliest_date:
                        earliest_date = start_date

    # If no strategy dates found, check actual data files
    if earliest_date is None:
        for dirs in datadirs.values():
            dir_list = dirs if isinstance(dirs, list) else [dirs]
            for data_dir in dir_list:
                try:
                    returns = _load_single_returns_file(data_dir)
                    if returns is not None and not returns.empty:
                        data_start = returns.index.min()
                        if earliest_date is None or data_start < earliest_date:
                            earliest_date = data_start
                except:
                    continue

    # Default to 2000-01-01 if no data found, but subtract some buffer
    if earliest_date is None:
        return "2000-01-01"

    # Go back 1 year to ensure we have enough benchmark data
    buffer_start = earliest_date - pd.DateOffset(years=1)
    return buffer_start.strftime("%Y-%m-%d")


def _get_benchmark_config():
    """Get centralized benchmark configuration."""
    return {
        "南华商品指数": {"source": "tushare", "symbol": "NHCI.NH"},
        "沪深300指数": {"source": "tushare", "symbol": "000300.SH"},
        "标普500指数": {"source": "yfinance", "symbol": "^GSPC"},
        "纳斯达克综指": {"source": "yfinance", "symbol": "^IXIC"},
    }


def _filter_datadirs(datadirs, selected_strategies):
    """Filter datadirs based on selected strategies."""
    if selected_strategies is None:
        return datadirs
    return {k: v for k, v in datadirs.items() if k in selected_strategies}


def _filter_strategy_info(strategy_info, selected_strategies):
    """Filter strategy_info based on selected strategies."""
    if strategy_info is None or selected_strategies is None:
        return strategy_info
    return {k: v for k, v in strategy_info.items() if k in selected_strategies}


def _load_external_benchmark(benchmark, datadirs, strategy_info):
    """Load external benchmark data from tushare or yfinance."""
    benchmark_config = _get_benchmark_config()
    config = benchmark_config.get(benchmark)

    if not config:
        raise ValueError(f"Unknown benchmark: {benchmark}")

    if config["source"] == "tushare":
        return _load_tushare_benchmark(config["symbol"], datadirs, strategy_info)
    else:
        return _load_yfinance_benchmark(config["symbol"], datadirs, strategy_info)


def _load_tushare_benchmark(symbol, datadirs, strategy_info):
    """Load benchmark data from Tushare."""
    tushare_token = os.getenv("TUSHARE_TOKEN")
    pro = ts.pro_api(tushare_token) if tushare_token else None

    if pro is not None:
        index_df = _smart_tushare_index(pro, symbol, datadirs, strategy_info)
    else:
        # Fallback to yfinance
        index_df = _smart_load_remote(symbol, datadirs, strategy_info)

    # Process tushare format
    if "trade_date" in index_df.columns:
        index_df["date"] = pd.to_datetime(index_df["trade_date"])
        index_df = index_df.set_index("date")
        index_df = index_df.sort_index()
        return pd.DataFrame(
            {
                "last_eod_value": index_df["close"].shift(1).dropna(),
                "account_value": index_df["close"][1:],
                "cashflow": 0,
                "returns": index_df["close"].pct_change().dropna(),
            }
        )
    else:
        return index_df


def _load_yfinance_benchmark(symbol, datadirs, strategy_info):
    """Load benchmark data from yfinance."""
    return _smart_load_remote(symbol, datadirs, strategy_info)


def load_benchmark(benchmark, datadirs, strategy_info=None, selected_strategies=None, include_rebates_in_returns=False):
    # Check if benchmark matches any account directory directly (needed for rebate processing logic)
    all_account_dirs = []
    for strategy_dirs in datadirs.values():
        if isinstance(strategy_dirs, list):
            all_account_dirs.extend(strategy_dirs)
        else:
            all_account_dirs.append(strategy_dirs)
    
    is_local_strategy = benchmark in datadirs or benchmark in all_account_dirs
    
    # First check if benchmark is a local strategy in datadirs
    if benchmark in datadirs:
        # Check if this is a strategy with multiple accounts
        if (
            isinstance(datadirs[benchmark], list)
            and strategy_info
            and benchmark in strategy_info
        ):
            # Use strategy merging logic for multiple accounts
            strategy_data = strategy_info[benchmark]
            account_configs = strategy_data.get("accounts", [])

            if len(account_configs) > 1:
                # Merge multiple accounts with proper date transitions
                bm_returns = _merge_strategy_accounts(account_configs)
            else:
                # Single account in strategy, load with date filtering
                config = account_configs[0]
                account_dir = config["account_dir"]
                start_date = (
                    pd.to_datetime(config["start_date"])
                    if config["start_date"]
                    else None
                )
                end_date = (
                    pd.to_datetime(config["end_date"]) if config["end_date"] else None
                )

                bm_returns = _load_single_returns_file(account_dir)
                if bm_returns is not None:
                    # Filter by date range
                    if start_date:
                        bm_returns = bm_returns[bm_returns.index >= start_date]
                    if end_date:
                        bm_returns = bm_returns[bm_returns.index <= end_date]
        else:
            # Handle single directory
            data_dir = (
                datadirs[benchmark]
                if not isinstance(datadirs[benchmark], list)
                else datadirs[benchmark][0]
            )
            bm_returns = _load_single_returns_file(data_dir)
    elif benchmark in all_account_dirs:
        bm_returns = _load_single_returns_file(benchmark)
    else:
        # External benchmark - filter data and load dynamically
        filtered_datadirs = _filter_datadirs(datadirs, selected_strategies)
        filtered_strategy_info = _filter_strategy_info(
            strategy_info, selected_strategies
        )
        bm_returns = _load_external_benchmark(
            benchmark, filtered_datadirs, filtered_strategy_info
        )

    # Apply rebate processing if this is a local strategy
    if bm_returns is not None and is_local_strategy:
        # This is a local strategy, apply rebate processing
        bm_returns = adjust_strategy_rebate(
            bm_returns, [benchmark], datadirs, strategy_info, 
            include_rebates_in_returns=include_rebates_in_returns
        )
    
    return bm_returns


# @st.cache_data
def load_trades(strategies, datadirs, strategy_info=None):
    trade_dfs = []

    for strategy in strategies:
        if strategy in datadirs:
            # Handle both single directories and lists of directories (strategies)
            dirs_to_check = (
                datadirs[strategy]
                if isinstance(datadirs[strategy], list)
                else [datadirs[strategy]]
            )

            # Check if this is a strategy with date-filtered accounts
            if (
                isinstance(datadirs[strategy], list)
                and strategy_info
                and strategy in strategy_info
            ):
                strategy_data = strategy_info[strategy]
                account_configs = strategy_data.get("accounts", [])

                # Load trades with date filtering for each account
                for config in account_configs:
                    account_dir = config["account_dir"]
                    start_date = (
                        pd.to_datetime(config["start_date"])
                        if config["start_date"]
                        else None
                    )
                    end_date = (
                        pd.to_datetime(config["end_date"])
                        if config["end_date"]
                        else None
                    )

                    df = _load_single_trades_file(account_dir)
                    if df is not None:
                        # Filter by date range using trading_day column
                        if start_date and "trading_day" in df.columns:
                            df = df[pd.to_datetime(df["trading_day"]) >= start_date]
                        if end_date and "trading_day" in df.columns:
                            df = df[pd.to_datetime(df["trading_day"]) <= end_date]

                        if len(df) > 0:
                            trade_dfs.append(df)
            else:
                # Regular account loading
                for data_dir in dirs_to_check:
                    df = _load_single_trades_file(data_dir)
                    if df is not None:
                        trade_dfs.append(df)

    if len(trade_dfs) == 0:
        trades = None
    else:
        trades = pd.concat(trade_dfs).sort_index()
        
        # Calculate slippage_value if slippage column exists
        if trades is not None and "slippage" in trades.columns:
            # Determine turnover column name
            turnover_col_name = "proceeds" if "proceeds" in trades.columns else "value"
            
            # Calculate actual slippage values
            multiplier = trades[turnover_col_name] / trades.price
            trades["slippage_value"] = trades.slippage * multiplier.abs()

    return trades


def _load_single_trades_file(data_dir):
    """Load trades from a single directory."""
    if os.path.exists(f"{data_dir}/trades.csv"):
        return pd.read_csv(
            f"{data_dir}/trades.csv",
            index_col=0,
            parse_dates=True,
            date_format="%Y-%m-%d %H:%M:%S",
        )
    elif os.path.exists(f"{data_dir}/trades.hdf"):
        return pd.read_hdf(f"{data_dir}/trades.hdf")
    elif os.path.exists(f"{data_dir}/trades.parquet"):
        return pd.read_parquet(f"{data_dir}/trades.parquet")
    return None


# @st.cache_data
def load_round_trips(strategies, datadirs, strategy_info=None):
    rt_dfs = []
    for strategy in strategies:
        if strategy in datadirs:
            # Handle both single directories and lists of directories (strategies)
            dirs_to_check = (
                datadirs[strategy]
                if isinstance(datadirs[strategy], list)
                else [datadirs[strategy]]
            )

            # Check if this is a strategy with date-filtered accounts
            if (
                isinstance(datadirs[strategy], list)
                and strategy_info
                and strategy in strategy_info
            ):
                strategy_data = strategy_info[strategy]
                account_configs = strategy_data.get("accounts", [])

                # Load round trips with date filtering for each account
                for config in account_configs:
                    account_dir = config["account_dir"]
                    start_date = (
                        pd.to_datetime(config["start_date"])
                        if config["start_date"]
                        else None
                    )
                    end_date = (
                        pd.to_datetime(config["end_date"])
                        if config["end_date"]
                        else None
                    )

                    rt_df = _load_single_round_trips_file(account_dir)
                    if rt_df is not None:
                        # Filter by date range using close_dt column
                        if start_date and "close_dt" in rt_df.columns:
                            rt_df = rt_df[
                                pd.to_datetime(rt_df["close_dt"]) >= start_date
                            ]
                        if end_date and "close_dt" in rt_df.columns:
                            rt_df = rt_df[pd.to_datetime(rt_df["close_dt"]) <= end_date]

                        if len(rt_df) > 0:
                            rt_dfs.append(rt_df)
            else:
                # Regular account loading
                for data_dir in dirs_to_check:
                    rt_df = _load_single_round_trips_file(data_dir)
                    if rt_df is not None:
                        rt_dfs.append(rt_df)

    if len(rt_dfs) == 0:
        rts = None
    else:
        rts = pd.concat(rt_dfs).sort_index()

    return rts


def _load_single_round_trips_file(data_dir):
    """Load round trips from a single directory."""
    if os.path.exists(f"{data_dir}/round_trips.csv"):
        rt_df = pd.read_csv(
            f"{data_dir}/round_trips.csv", index_col=0, parse_dates=True
        )
        rt_df["duration"] = pd.to_timedelta(rt_df.duration)
        return rt_df
    elif os.path.exists(f"{data_dir}/round_trips.hdf"):
        return pd.read_hdf(f"{data_dir}/round_trips.hdf")
    elif os.path.exists(f"{data_dir}/round_trips.parquet"):
        return pd.read_parquet(f"{data_dir}/round_trips.parquet")
    return None




def load_rebates(strategies, datadirs, strategy_info=None):
    """
    Load rebates data from rebates.csv files for specified strategies.

    Args:
        strategies: List of strategy names
        datadirs: Dictionary mapping strategy names to data directories
        strategy_info: Optional strategy configuration

    Returns:
        DataFrame with date index and rebate_amount column, or None if no rebates data found
    """
    rebate_dfs = []
    for strategy in strategies:
        if strategy in datadirs:
            # Handle both single directories and lists of directories (strategies)
            dirs_to_check = (
                datadirs[strategy]
                if isinstance(datadirs[strategy], list)
                else [datadirs[strategy]]
            )

            for data_dir in dirs_to_check:
                if os.path.exists(f"{data_dir}/rebates.csv"):
                    df = pd.read_csv(f"{data_dir}/rebates.csv")
                    if "date" in df.columns and "rebate_amount" in df.columns:
                        # Convert date column to datetime and set as index
                        df["date"] = pd.to_datetime(df["date"])
                        df = df.set_index("date")
                        # Keep all rebates from this directory, no need to filter by account
                        # since we're already iterating through the correct strategy's directories
                        rebate_dfs.append(df[["rebate_amount"]])

    if len(rebate_dfs) == 0:
        return None
    else:
        rebates = pd.concat(rebate_dfs).sort_index()
        # Sum rebates if there are duplicates on the same date
        rebates = rebates.groupby(rebates.index).sum()
        return rebates


def load_investors(strategies, datadirs, strategy_info=None):
    """
    Load investors data from investors.csv files for specified strategies.
    Args:
        strategies: List of strategy names/IDs
        datadirs: Dictionary mapping strategy names to data directories
        strategy_info: Optional strategy configuration
    Returns:
        DataFrame with [name,account,date,cashflow] columns, or None if no investors data found
    """
    investor_dfs = []
    for strategy in strategies:
        if strategy in datadirs:
            # Handle both single directories and lists of directories (strategies)
            dirs_to_check = (
                datadirs[strategy]
                if isinstance(datadirs[strategy], list)
                else [datadirs[strategy]]
            )
            for data_dir in dirs_to_check:
                if os.path.exists(f"{data_dir}/investors.csv"):
                    df = pd.read_csv(f"{data_dir}/investors.csv")
                    if (
                        "name" in df.columns
                        and "date" in df.columns
                        and "cashflow" in df.columns
                    ):
                        # Convert date column to datetime
                        df["date"] = pd.to_datetime(df["date"])
                        # Ensure account column exists, use strategy name if not present
                        if "account" not in df.columns:
                            df["account"] = strategy
                        investor_dfs.append(df)

    if len(investor_dfs) == 0:
        return None
    else:
        investors = pd.concat(investor_dfs, ignore_index=True).sort_values("date")
        return investors


# @st.cache_data
def load_investor_returns(investors, returns):
    """
    Must be run with full returns history

    investors: Dataframe with [name,account,date,cashflow] columns sorted by date (including rebate investors if any)
    returns: Dataframe with date as index, [last_eod_value,account_value,cashflow,today_pnl,returns,cum_returns,net_asset_values,underwater] as columns
    """
    investor_returns = {}

    if investors is None or len(investors) == 0:
        return investor_returns

    # Calculate total fund shares based on all investors' cashflows
    all_cashflows = (
        investors.groupby("date")["cashflow"].sum().reindex(returns.index, fill_value=0)
    )

    # Initialize fund share tracking
    total_shares = 0
    fund_nav_series = returns["net_asset_values"]

    # Calculate total fund shares for each date
    total_shares_series = []
    for date in returns.index:
        if date in all_cashflows.index and all_cashflows[date] != 0:
            nav = fund_nav_series[date]
            if nav > 0:
                total_shares += all_cashflows[date] / nav
        total_shares_series.append(total_shares)

    for investor in investors["name"].unique():
        idf = investors[investors["name"] == investor]
        investor_start_date = idf["date"].iloc[0]
        idf = idf.set_index("date")
        ireturns = returns[returns.index >= investor_start_date]
        ireturns = ireturns.filter(["returns", "net_asset_values"])

        # Merge investor's cashflows
        investor_cashflows = idf.filter(["cashflow"]).reindex(
            ireturns.index, fill_value=0
        )
        ireturns["cashflow"] = investor_cashflows["cashflow"]

        # Calculate investor's shares based on fund-style calculation
        investor_shares = 0
        shares_series = []
        account_values = []

        # Get the initial prev_nav from the day before investor's first date
        first_date = ireturns.index[0]
        prev_date_idx = returns.index.get_loc(first_date) - 1
        if prev_date_idx >= 0:
            prev_nav = returns.iloc[prev_date_idx]["net_asset_values"]
        else:
            prev_nav = 1.0  # Fallback to 1.0 if no previous data exists

        for date, row in ireturns.iterrows():
            cashflow = row["cashflow"]
            today_nav = row["net_asset_values"]

            # Calculate share changes based on cashflow
            if cashflow > 0:
                # Positive cashflow: add shares based on previous day's NAV
                investor_shares += cashflow / prev_nav
            elif cashflow < 0:
                # Negative cashflow: reduce shares based on today's NAV
                investor_shares += cashflow / today_nav  # cashflow is negative

            shares_series.append(investor_shares)

            # Calculate account value using today's NAV
            account_value = investor_shares * today_nav
            account_values.append(round(account_value, 2))

            # Update prev_nav for next iteration
            prev_nav = today_nav

        # Build the investor returns dataframe
        ireturns.insert(0, "shares", shares_series)
        ireturns.insert(1, "account_value", account_values)
        last_eod_values = ireturns["account_value"].shift(1)
        last_eod_values.iloc[0] = 0
        ireturns.insert(1, "last_eod_value", last_eod_values)

        # Calculate today's P&L
        today_pnl = (
            ireturns["account_value"]
            - ireturns["last_eod_value"]
            - ireturns["cashflow"]
        )
        ireturns.insert(3, "today_pnl", today_pnl.round(2))

        # Calculate adjusted last EOD value for return calculation
        ireturns.insert(3, "adj_last_eod_value", ireturns["last_eod_value"])
        ireturns.loc[ireturns["cashflow"] > 0, "adj_last_eod_value"] = (
            ireturns["last_eod_value"] + ireturns["cashflow"]
        )

        # # Calculate returns
        # ireturns["returns"] = ireturns["today_pnl"] / ireturns["adj_last_eod_value"]
        # ireturns["returns"] = ireturns["returns"].fillna(0)

        # Apply return_stats to get cumulative returns and other metrics while preserving NAV
        ireturns = return_stats(ireturns, preserve_nav=True)
        investor_returns[investor] = ireturns

    return investor_returns


def calculate_max_principle_series(df):
    initial_capital = df["last_eod_value"].iloc[0]
    accumulated_pnl = 0
    net_cashflow = 0
    current_max_principle = initial_capital
    max_principle_values = []

    for _, row in df.iterrows():
        accumulated_pnl += row["today_pnl"]
        net_cashflow += row["cashflow"]

        if net_cashflow > accumulated_pnl:
            new_max = initial_capital + (net_cashflow - accumulated_pnl)
            current_max_principle = max(current_max_principle, new_max)

        max_principle_values.append(current_max_principle)

    return pd.Series(max_principle_values, index=df.index, name="max_principle")


def calculate_max_capital_series(df):
    initial_capital = df["last_eod_value"].iloc[0]
    net_cashflow = 0
    current_max_capital = initial_capital
    max_capital_values = []

    for _, row in df.iterrows():
        net_cashflow += row["cashflow"]
        
        # Max capital is simply initial capital plus cumulative positive cashflows
        total_capital = initial_capital + max(0, net_cashflow)
        current_max_capital = max(current_max_capital, total_capital)
        
        max_capital_values.append(current_max_capital)

    return pd.Series(max_capital_values, index=df.index, name="max_capital")


def calculate_max_invested_series(df):
    initial_capital = df["last_eod_value"].iloc[0]
    cumulative_deposits = 0  # Track only deposits (positive cashflows)
    current_max_invested = initial_capital
    max_invested_values = []

    for _, row in df.iterrows():
        cashflow = row["cashflow"]
        
        # Only add positive cashflows (deposits) to cumulative deposits
        if cashflow > 0:
            cumulative_deposits += cashflow
        
        # Max invested is initial capital plus max cumulative deposits ever made
        total_invested = initial_capital + cumulative_deposits
        current_max_invested = max(current_max_invested, total_invested)
        
        max_invested_values.append(current_max_invested)

    return pd.Series(max_invested_values, index=df.index, name="max_invested")


def adjust_strategy_rebate(
    returns, strategies, datadirs, strategy_info=None, preserve_nav=False, include_rebates_in_returns=False
):
    """
    Adjust returns based on rebate handling mode using explicit rebates.csv.

    Args:
        returns: DataFrame with return data
        strategies: List of strategy names for loading rebates.csv
        datadirs: Data directories mapping
        strategy_info: Strategy configuration
        preserve_nav: Whether to preserve NAV calculation (for period filtering)
        include_rebates_in_returns: If True, add rebates to returns; if False, remove rebates from returns

    Returns:
        Returns DataFrame with rebates either included or excluded from calculations
    """
    if "cashflow" not in returns or "today_pnl" not in returns:
        return return_stats(returns, preserve_nav=preserve_nav)

    # Try to load explicit rebates data
    rebates_data = load_rebates(strategies, datadirs, strategy_info)

    # Create a copy to avoid modifying the original
    returns = returns.copy()

    if rebates_data is not None and len(rebates_data) > 0:
        # Use explicit rebates.csv data
        # Align rebates data with returns index
        aligned_rebates = rebates_data.reindex(returns.index, fill_value=0)
        rebate_amounts = aligned_rebates["rebate_amount"]

        # Store rebates for reference
        returns["cash_rebate"] = rebate_amounts

        # Calculate the current adjustment (positive cashflows)
        current_adjustment = np.where(returns["cashflow"] > 0, returns["cashflow"], 0)

        if include_rebates_in_returns:
            # Include rebates as part of trading returns
            returns["adj_last_eod_value"] = returns["last_eod_value"] + current_adjustment
            returns["adj_today_pnl"] = returns["today_pnl"] + rebate_amounts
        else:
            # Remove rebates from trading returns (default behavior)
            clean_adjustment = current_adjustment - rebate_amounts
            returns["adj_last_eod_value"] = returns["last_eod_value"] + clean_adjustment
            returns["adj_today_pnl"] = returns["today_pnl"]

        # Recalculate returns - handle zero division
        returns["returns"] = np.where(
            returns["adj_last_eod_value"] != 0,
            returns["adj_today_pnl"] / returns["adj_last_eod_value"],
            0.0,
        )

    else:
        # No explicit rebates data available - treat all positive cashflows as capital additions
        positive_cashflows = np.where(returns["cashflow"] > 0, returns["cashflow"], 0)
        returns["adj_last_eod_value"] = returns["last_eod_value"] + positive_cashflows
        returns["adj_today_pnl"] = returns["today_pnl"]
        returns["cash_rebate"] = 0.0
        returns["returns"] = np.where(
            returns["adj_last_eod_value"] != 0,
            returns["adj_today_pnl"] / returns["adj_last_eod_value"],
            0.0,
        )

    return return_stats(returns, preserve_nav=preserve_nav)
