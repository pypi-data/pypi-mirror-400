import datetime

import numpy as np
import pandas as pd
import streamlit as st
from tabulate import tabulate

from stellar_stats.auth import setup_authentication
from stellar_stats.config import load_config, sort_accounts_by_mtime
from stellar_stats.data import (
    adjust_strategy_rebate,
    calculate_max_capital_series,
    calculate_max_invested_series,
    calculate_max_principle_series,
    load_benchmark,
    load_investors,
    load_investor_returns,
    load_rebates,
    load_returns,
    load_round_trips,
    load_trades,
)
from stellar_stats.stats import (
    annual_return,
    gen_drawdown_table,
    gen_perf,
    return_stats,
    style_returns,
    style_drawdowns,
)
from stellar_stats.ui import (
    plot_returns_cumulative,
    plot_returns_periodic,
    plot_monthly_returns_heatmap,
    plot_profit_distribution,
    plot_return_distribution,
    plot_slippage_distribution,
    show_performance_metrics,
    show_trade_metrics,
)
from stellar_stats.utils import refresh_cache, show_col_desc


def app():
    st.set_page_config(
        page_title="Trade Stats Dashboard",
        page_icon="📈",
        layout="wide",
    )

    # Load configuration and setup
    cfg, pro, strategies, datadirs, benchmark_names, strategy_info = load_config()
    using_strategies = bool(
        strategy_info
    )  # True if we have strategy info (JSON config)

    # Setup authentication
    setup_authentication(cfg)

    # Refresh cache
    refresh_cache(datadirs)

    # Sort strategies by modification time
    strategies = sort_accounts_by_mtime(strategies, datadirs)

    # Setup benchmark options
    benchmark_options = benchmark_names + strategies + ["Custom Symbol"]
    benchmark_idx = len(benchmark_names) + 1

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Strategy selection
    def check_strategy_widget(strategies):
        if "account" not in st.session_state:
            return False
        return all(elem in strategies for elem in st.session_state.account)

    def check_benchmark_widget(benchmark_options):
        if "benchmark" not in st.session_state:
            return False
        return st.session_state.benchmark in benchmark_options

    if st.session_state.get("swap_once"):
        account = st.session_state.benchmark
        if len(st.session_state.account) > 0:
            benchmark = st.session_state.account[0]
        else:
            benchmark = strategies[1]
        st.session_state.account = [account]
        st.session_state.benchmark = benchmark
        st.session_state["swap_once"] = False
    else:
        st.session_state.account = st.session_state.get("account", [strategies[0]])
        st.session_state.benchmark = st.session_state.get(
            "benchmark", benchmark_options[benchmark_idx]
        )

    if not check_strategy_widget(strategies):
        st.warning("Strategy not found, reset to default strategy")
        st.session_state.account = [strategies[0]]

    # Update UI labels based on config type
    selection_label = "Select Strategy" if using_strategies else "Select Account"

    # Create display names for selection
    if using_strategies:
        display_options = [
            strategy_info.get(strategy, {}).get("name", strategy)
            for strategy in strategies
        ]
        strategy_mapping = dict(zip(display_options, strategies))
    else:
        display_options = strategies
        strategy_mapping = {strategy: strategy for strategy in strategies}

    selected_display = st.sidebar.multiselect(
        selection_label, display_options, key="account"
    )

    # Map back to strategy IDs, filtering out invalid selections
    selected_strategies = [
        strategy_mapping[disp] for disp in selected_display if disp in strategy_mapping
    ]

    if len(selected_strategies) > 1:
        current_strategy = "Combined"
    elif len(selected_strategies) == 1:
        current_strategy = selected_strategies[0]
    else:
        selected_strategies = [strategies[0]]
        current_strategy = selected_strategies[0]

    def swap_account_benchmark():
        st.session_state["swap_once"] = True

    st.sidebar.button("  ↕  ", on_click=swap_account_benchmark)

    if not check_benchmark_widget(benchmark_options):
        st.warning("Benchmark not found, reset to default benchmark")
        st.session_state.benchmark = benchmark_options[benchmark_idx]

    benchmark = st.sidebar.selectbox(
        "Select Benchmark", benchmark_options, key="benchmark"
    )

    if benchmark == "Custom Symbol":
        benchmark = st.sidebar.text_input("Benchmark Symbol", "MSFT")

    bm_ratio = st.sidebar.selectbox("Set Benchmark Leverage", [1, 2, 3, 4, 5], 0)

    # Load investors and rebates data from account directories
    investors = load_investors(selected_strategies, datadirs, strategy_info)
    rebates = load_rebates(selected_strategies, datadirs, strategy_info)

    # Only show rebate mode radio buttons if rebates data exists
    if rebates is not None:
        rebate_mode = st.sidebar.radio(
            "Rebate Handling",
            ["Rebates as Returns", "Rebates as Investor"],
            index=0,  # Default to "Rebates as Returns"
        )
    else:
        rebate_mode = "Rebates as Investor"  # Default value when no rebates

    if st.session_state.get("swap_once"):
        st.rerun()

    # Determine display title
    if cfg is None:
        title = "Strategy Performance Stats"
    elif using_strategies and len(selected_strategies) == 1:
        strategy_name = strategy_info.get(selected_strategies[0], {}).get(
            "name", selected_strategies[0]
        )
        title = f"{strategy_name} Performance Stats"
    elif len(selected_strategies) > 1:
        title = "Combined Performance Stats"
    else:
        title = f"{current_strategy} Performance Stats"

    st.header(title)
    st.markdown("""---""")

    # Load returns and benchmark data
    raw_returns = load_returns(selected_strategies, datadirs, strategy_info)

    # Apply rebate processing based on selected mode
    include_rebates = rebate_mode == "Rebates as Returns"
    returns = adjust_strategy_rebate(
        raw_returns,
        selected_strategies,
        datadirs,
        strategy_info,
        include_rebates_in_returns=include_rebates,
    )

    # max_principle = calculate_max_principle_series(returns)
    bm_returns = load_benchmark(
        benchmark,
        datadirs,
        strategy_info,
        selected_strategies,
        include_rebates_in_returns=include_rebates,
    )

    if bm_returns is not None:
        bm_returns["returns"] *= bm_ratio

    # Load trade data
    trades = load_trades(selected_strategies, datadirs, strategy_info)
    rts = load_round_trips(selected_strategies, datadirs, strategy_info)

    # Create rebate investor only when in "Rebates as Investor" mode
    if (
        rebate_mode == "Rebates as Investor"
        and rebates is not None
        and len(rebates) > 0
    ):
        # Create rebate investor data
        rebate_investor_data = []
        for date, row in rebates.iterrows():
            rebate_investor_data.append(
                {
                    "name": "Rebate_Fund",
                    "account": selected_strategies[0]
                    if len(selected_strategies) == 1
                    else "Combined",  # Use strategy name or "Combined" for multiple strategies
                    "date": date.strftime("%Y-%m-%d"),
                    "cashflow": row["rebate_amount"],
                }
            )

        rebate_investor_df = pd.DataFrame(rebate_investor_data)
        rebate_investor_df["date"] = pd.to_datetime(rebate_investor_df["date"])

        # Combine with existing investors
        if investors is not None and len(investors) > 0:
            investors = pd.concat(
                [investors, rebate_investor_df], ignore_index=True
            ).sort_values("date")
        else:
            investors = rebate_investor_df

    # Load investor returns using the complete returns series
    investor_returns = load_investor_returns(investors, returns)

    # Period selection
    years = list(returns.index.year.unique())
    years.sort(reverse=True)
    year = years[0]
    current_year = datetime.datetime.now().year

    # Determine if strategy has ended (no data in current year)
    strategy_ended = year < current_year

    periods = [
        "Year To Date" if not strategy_ended else f"{year} (Last Year)",
        "Since Inception",
        "Custom Year Range",
        "Custom Date Range",
    ]
    with st.sidebar:
        period = st.selectbox("Select Period", periods, 1 if cfg is None else 0)

        if period == "Year To Date" or period.endswith("(Last Year)"):
            returns = return_stats(
                returns[returns.index.year == year], preserve_nav=True
            )
        elif period == "Since Inception":
            returns = return_stats(returns, preserve_nav=True)
        elif period == "Custom Year Range":
            start_year = st.text_input("Start Year", returns.index[-1].date().year)
            end_year = st.text_input("End Year", returns.index[-1].date().year)
            if start_year > end_year:
                st.error("Error: end year should not be earlier than start year.")
            else:
                returns = return_stats(returns[start_year:end_year], preserve_nav=True)
        elif period == "Custom Date Range":
            start_date = st.date_input("Start Date", datetime.date(year, 1, 2))
            end_date = st.date_input("End Date", returns.index[-1].date())
            if start_date > end_date:
                st.error("Error: end date should not be earlier than start date.")
            else:
                returns = return_stats(
                    returns[
                        (returns.index.date >= start_date)
                        & (returns.index.date <= end_date)
                    ],
                    preserve_nav=True,
                )
        else:
            returns = return_stats(
                returns[returns.index.year == period], preserve_nav=True
            )

    start_date = returns.index.date[0]
    end_date = returns.index.date[-1]

    # max_principle = max_principle[
    #     (max_principle.index.date >= start_date) & (max_principle.index.date <= end_date)
    # ]

    if bm_returns is not None:
        bm_returns = return_stats(
            bm_returns[
                (bm_returns.index.date >= start_date)
                & (bm_returns.index.date <= end_date)
            ],
            preserve_nav=True,
        )

    # Recalculate investor returns for the selected period (preserving NAV values)
    for investor, ireturns in investor_returns.items():
        if ireturns is not None:
            filtered_returns = ireturns[
                (ireturns.index.date >= start_date) & (ireturns.index.date <= end_date)
            ]
            # Only process if there's actual data in the filtered range
            if not filtered_returns.empty:
                # Use return_stats to recalculate returns for the period while preserving NAV
                recalculated_returns = return_stats(filtered_returns, preserve_nav=True)
                if recalculated_returns is not None:
                    investor_returns[investor] = recalculated_returns
                else:
                    investor_returns[investor] = None
            else:
                # Remove investors with no data in the selected range
                investor_returns[investor] = None

    # Filter trade data by date range
    if trades is not None:
        if "date" in trades.columns:
            trades = trades.set_index("date")
        elif "datetime" in trades.columns:
            trades = trades.set_index("datetime")
        elif "timestamp" in trades.columns:
            trades["timestamp"] = trades["timestamp"].apply(
                lambda x: pd.Timestamp(x).tz_localize(None)
            )
            trades = trades.set_index("timestamp")

    if trades is not None:
        trades = trades[
            (trades.index.date >= start_date) & (trades.index.date <= end_date)
        ]
    if rts is not None:
        rts = rts[(rts.index.date >= start_date) & (rts.index.date <= end_date)]

    if trades is not None and len(trades) == 0:
        trades = None
    if rts is not None and len(rts) == 0:
        rts = None

    if bm_returns is None:
        bm_returns = returns.copy()
        bm_returns.loc[:, :] = 0.0

    returns["benchmark_cum_returns"] = bm_returns["cum_returns"]
    returns["benchmark_underwater"] = bm_returns["underwater"]

    # Generate drawdown tables
    drawdowns = gen_drawdown_table(returns["returns"], 10)
    bm_drawdowns = gen_drawdown_table(bm_returns["returns"], 10)

    # Generate return tables
    yearly_return = (
        returns.groupby(pd.Grouper(freq="YE"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    yearly_return.insert(0, "Year", yearly_return.index.year.astype(str))
    yearly_return = yearly_return.reset_index().drop("date", axis=1).set_index("Year")

    bm_yearly_return = (
        bm_returns.groupby(pd.Grouper(freq="YE"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    bm_yearly_return.insert(0, "Year", bm_yearly_return.index.year.astype(str))
    bm_yearly_return = (
        bm_yearly_return.reset_index().drop("date", axis=1).set_index("Year")
    )

    monthly_return = (
        returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    monthly_return.insert(0, "Date", monthly_return.index)
    monthly_return.insert(
        1,
        "Timespan",
        monthly_return.index.year.astype(str)
        + "-"
        + monthly_return.index.month.map("{:02}".format),
    )
    monthly_return = (
        monthly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )
    monthly_return = monthly_return.sort_index()

    bm_monthly_return = (
        bm_returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    bm_monthly_return.insert(0, "Date", bm_monthly_return.index)
    bm_monthly_return.insert(
        1,
        "Timespan",
        bm_monthly_return.index.year.astype(str)
        + "-"
        + bm_monthly_return.index.month.map("{:02}".format),
    )
    bm_monthly_return = (
        bm_monthly_return.reset_index()
        .drop("date", axis=1)
        .set_index("Timespan")
        .sort_index()
    )

    # Helper function to format week date ranges
    def format_week_range(week_end_date):
        """Format week as date range: YYYY-MM/DD~MM/DD or YYYY-MM/DD~YYYY-MM/DD if crossing years."""
        week_start = week_end_date - pd.Timedelta(days=6)
        if week_start.year == week_end_date.year:
            # Same year: 2024-01/01~01/07
            return (
                f"{week_start.strftime('%Y-%m/%d')}~{week_end_date.strftime('%m/%d')}"
            )
        else:
            # Different years: 2024-12/30~2025-01/05
            return f"{week_start.strftime('%Y-%m/%d')}~{week_end_date.strftime('%Y-%m/%d')}"

    weekly_return = (
        returns.groupby(pd.Grouper(freq="W"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    weekly_return.insert(0, "Date", weekly_return.index)
    weekly_return.insert(
        1,
        "Timespan",
        weekly_return.index.map(format_week_range),
    )
    weekly_return = (
        weekly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )

    bm_weekly_return = (
        bm_returns.groupby(pd.Grouper(freq="W"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    bm_weekly_return.insert(0, "Date", bm_weekly_return.index)
    bm_weekly_return.insert(
        1,
        "Timespan",
        bm_weekly_return.index.map(format_week_range),
    )
    bm_weekly_return = (
        bm_weekly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )

    # Calculate underlying breakdowns
    ul_breakdown = None
    slippage_breakdown = None
    if trades is not None:
        turnover_col_name = "proceeds" if "proceeds" in trades.columns else "value"

        # Optimized vectorized underlying extraction
        trades_copy = trades.copy()
        # Use vectorized string operations instead of apply with lambda
        has_underscore = trades_copy.symbol.str.contains("_", na=False)
        trades_copy["underlying"] = trades_copy.symbol.str.split("_").str[0]
        # For symbols without underscore, remove digits
        mask = ~has_underscore
        trades_copy.loc[mask, "underlying"] = trades_copy.loc[
            mask, "symbol"
        ].str.replace(r"\d+", "", regex=True)

        ul_breakdown = trades_copy.groupby("underlying").agg(
            total_pnl=pd.NamedAgg(column="pnl", aggfunc="sum"),
            total_turnover=pd.NamedAgg(
                column=turnover_col_name, aggfunc=lambda x: x.abs().sum()
            ),
        )

        # Add actual round trips count if rts data exists
        if rts is not None:
            # Extract underlying symbols from round trips data using same logic
            rts_copy = rts.copy()
            has_underscore_rts = rts_copy.symbol.str.contains("_", na=False)
            rts_copy["underlying"] = rts_copy.symbol.str.split("_").str[0]
            # For symbols without underscore, remove digits
            mask_rts = ~has_underscore_rts
            rts_copy.loc[mask_rts, "underlying"] = rts_copy.loc[
                mask_rts, "symbol"
            ].str.replace(r"\d+", "", regex=True)

            # Count actual round trips by underlying
            rts_counts = rts_copy.groupby("underlying").size().to_frame("roundtrips")

            # Merge round trips count into ul_breakdown
            ul_breakdown = ul_breakdown.merge(
                rts_counts, left_index=True, right_index=True, how="left"
            )
            # Fill NaN values with 0 for underlyings that have no round trips
            ul_breakdown["roundtrips"] = (
                ul_breakdown["roundtrips"].fillna(0).astype(int)
            )
        else:
            # If no round trips data, set roundtrips to 0
            ul_breakdown["roundtrips"] = 0

        ul_breakdown["pnl_ratio"] = (
            ul_breakdown["total_pnl"] / ul_breakdown["total_turnover"]
        )

        # Reorder columns to put roundtrips first
        ul_breakdown = ul_breakdown[
            ["roundtrips", "total_pnl", "total_turnover", "pnl_ratio"]
        ]

        ul_breakdown = ul_breakdown.sort_values("total_pnl", ascending=False)

        if "slippage_value" in trades_copy.columns:
            slippage_breakdown = trades_copy.groupby("underlying").agg(
                total_slippage=pd.NamedAgg(column="slippage_value", aggfunc="sum"),
                total_turnover=pd.NamedAgg(
                    column=turnover_col_name, aggfunc=lambda x: x.abs().sum()
                ),
            )
            slippage_breakdown["slippage_ratio"] = (
                slippage_breakdown["total_slippage"]
                / slippage_breakdown["total_turnover"]
            )

    # Display dashboard
    left_col, right_col = st.columns([5, 2])

    with right_col:
        st.markdown("##### Performance Metrics")
        show_performance_metrics(returns, bm_returns, drawdowns, bm_drawdowns)

        if rts is not None and len(rts) > 0:
            st.write("")
            st.markdown("##### Trade Metrics")
            winners, losers = show_trade_metrics(
                rts, trades, returns, turnover_col_name
            )

    with left_col:
        if not cfg:
            with st.expander("Account/Benchmark Full Names"):
                records = []
                for acct in selected_strategies:
                    records.append(["Account", acct])
                records.append(["Benchmark", benchmark])
                full_names = (
                    pd.DataFrame.from_records(records, columns=["Type", "Name"])
                    .set_index("Type")
                    .sort_index()
                )
                st.markdown(tabulate(full_names, headers="keys", tablefmt="github"))

        # Add title first
        st.markdown("### Returns")

        plot_returns_cumulative(returns, bm_returns, bm_ratio)
        plot_returns_periodic(
            yearly_return,
            bm_yearly_return,
            monthly_return,
            bm_monthly_return,
            weekly_return,
            bm_weekly_return,
        )
        plot_monthly_returns_heatmap(returns)

        if trades is not None and len(trades) > 0:
            plot_profit_distribution(ul_breakdown)

        if trades is not None and "slippage_value" in trades.columns:
            plot_slippage_distribution(slippage_breakdown)

    with left_col:
        st.markdown("### Top Drawdowns Table")
        st.dataframe(style_drawdowns(drawdowns))

        st.markdown("### Returns Tables")
        daily_tab, weekly_tab, monthly_tab, yearly_tab = st.tabs(
            ["Daily", "Weekly", "Monthly", "Yearly"]
        )
        with daily_tab:
            st.markdown("##### Daily Returns")
            st.dataframe(
                returns.drop(["benchmark_cum_returns", "benchmark_underwater"], axis=1)
                .sort_index(ascending=False)
                .style.format("{:,.0f}")
                .format("{:.4f}", subset=["net_asset_values"])
                .format("{:.2%}", subset=["returns", "cum_returns", "underwater"])
            )
            show_col_desc(returns, ["returns"])

        with weekly_tab:
            st.markdown("##### Weekly Returns")
            sub_left_col, sub_right_col = weekly_tab.columns([4, 4])
            with sub_left_col:
                st.dataframe(style_returns(weekly_return))
            with sub_right_col:
                show_col_desc(weekly_return, ["Return"])
                plot_return_distribution(weekly_return, "weekly")

        with monthly_tab:
            st.markdown("##### Monthly Returns")
            sub_left_col, sub_right_col = monthly_tab.columns([4, 4])
            with sub_left_col:
                st.dataframe(style_returns(monthly_return))
            with sub_right_col:
                show_col_desc(monthly_return, ["Return"])
                plot_return_distribution(monthly_return, "monthly")

        with yearly_tab:
            st.markdown("### Yearly Returns")
            st.dataframe(style_returns(yearly_return))

        if rts is not None:
            st.markdown("### Roundtrips Tables")

            # Check if close_value column exists in rts dataframe
            format_cols = ["pnl"]
            if "close_value" in rts.columns:
                format_cols.append("close_value")

            winners_tab, losers_tab, rts_tab = st.tabs(["Winners", "Losers", "All"])
            with winners_tab:
                if winners is not None:
                    st.markdown("##### Winners")
                    winners["duration"] = winners["duration"].dt.days
                    st.dataframe(
                        winners.style.format("{:,.0f}", subset=format_cols).format(
                            "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                        )
                    )
                    show_col_desc(winners, ["pnl_pct", "account_pnl_pct"])
                    show_col_desc(winners, ["duration"], dtype="int")

            with losers_tab:
                if losers is not None:
                    st.markdown("##### Losers")
                    losers["duration"] = losers["duration"].dt.days
                    st.dataframe(
                        losers.style.format("{:,.0f}", subset=format_cols).format(
                            "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                        )
                    )
                    show_col_desc(losers, ["pnl_pct", "account_pnl_pct"])
                    show_col_desc(losers, ["duration"], dtype="int")

            with rts_tab:
                st.markdown("##### All")
                rts["duration"] = rts["duration"].dt.days
                st.dataframe(
                    rts.style.format("{:,.0f}", subset=format_cols).format(
                        "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                    )
                )

        if trades is not None:
            st.markdown("### Underlying Breakdown")
            if "slippage_value" in trades.columns:
                ul_breakdown = ul_breakdown.merge(
                    slippage_breakdown.filter(["total_slippage", "slippage_ratio"]),
                    left_index=True,
                    right_index=True,
                )
                st.dataframe(
                    ul_breakdown.style.format(precision=0)
                    .format("{:.6f}", subset=["pnl_ratio", "slippage_ratio"])
                    .format(
                        "{:,.0f}",
                        subset=["total_pnl", "total_turnover", "total_slippage"],
                    )
                )
            else:
                st.dataframe(
                    ul_breakdown.style.format(precision=0)
                    .format("{:.6f}", subset=["pnl_ratio"])
                    .format("{:,.0f}", subset=["total_pnl", "total_turnover"])
                )

        if investors is not None:
            st.markdown("### Investors Tables")
            names = list(investors["name"].unique())
            # Sort names to put Rebate_Fund at the end
            names = sorted(names, key=lambda x: (x == "Rebate_Fund", x))
            # Filter out investors with no data in the selected period
            available_investors = [
                name
                for name in names
                if name in investor_returns and investor_returns[name] is not None
            ]

            if not available_investors:
                st.info("No investor data available for the selected date range.")

            for idx, tab in enumerate(st.tabs(available_investors)):
                investor = available_investors[idx]
                ireturns = investor_returns[investor]
                invested = ireturns.cashflow.sum()

                icashflow = ireturns.filter(["date", "cashflow"])
                icashflow = icashflow.where(icashflow.cashflow != 0).dropna()

                start_value = ireturns.adj_last_eod_value.iloc[0]
                if np.isnan(start_value):
                    st.markdown("No data for the selected period.")
                    continue

                current_value = ireturns.account_value.iloc[-1]

                with tab:
                    # Calculate money-weighted return: PnL divided by max capital ever
                    pnl = ireturns.today_pnl.sum()
                    max_capital_series = calculate_max_capital_series(ireturns)
                    max_capital = max_capital_series.max()
                    if max_capital > 0:
                        mwr = pnl / max_capital
                        # Use same calendar-based annualization as our custom annual_return function
                        start_date = ireturns.index[0]
                        end_date = ireturns.index[-1]
                        days_elapsed = (end_date - start_date).days

                        if days_elapsed > 0:
                            years_elapsed = (
                                days_elapsed / 365.25
                            )  # Account for leap years
                            # Use same CAGR formula as our annual_return function
                            annual_mwr = (
                                (1 + mwr) ** (1 / years_elapsed) - 1
                                if years_elapsed > 0 and (1 + mwr) > 0
                                else mwr
                            )
                        else:
                            annual_mwr = mwr
                    else:
                        mwr = 0.0
                        annual_mwr = 0.0

                    isummary_data = [
                        ("Start Value", start_value),
                        ("Net Invested", invested),
                        ("Max Capital", max_capital),
                        ("Current Value", current_value),
                        ("PnL", pnl),
                        ("Return", ireturns.cum_returns.iloc[-1]),
                        ("Annual Return", annual_return(ireturns["returns"])),
                        ("Money-Weighted Return", mwr),
                        ("Money-Weighted Annual Return", annual_mwr),
                        ("Max Drawdown", ireturns.underwater.min()),
                    ]
                    isummary = pd.DataFrame.from_records(isummary_data).pivot_table(
                        values=1, columns=0, sort=False
                    )
                    isummary.index = [investor]
                    st.markdown("##### Summary")
                    st.dataframe(
                        isummary.style.format(precision=0)
                        .format(
                            "{:.2%}",
                            subset=[
                                "Return",
                                "Annual Return",
                                "Money-Weighted Return",
                                "Money-Weighted Annual Return",
                                "Max Drawdown",
                            ],
                        )
                        .format(
                            "{:,.0f}",
                            subset=[
                                "Start Value",
                                "Net Invested",
                                "Max Capital",
                                "Current Value",
                                "PnL",
                            ],
                        )
                    )

                    st.write("")
                    st.markdown("##### Cashflow")
                    st.dataframe(icashflow.style.format("{:,.0f}"))

                    st.write("")
                    st.markdown("##### Daily Returns")
                    st.dataframe(
                        ireturns.style.format("{:,.0f}")
                        .format("{:,.4f}", subset=["net_asset_values"])
                        .format(
                            "{:.2%}", subset=["returns", "cum_returns", "underwater"]
                        )
                    )


if __name__ == "__main__":
    app()
