from itertools import groupby

import empyrical as ep
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
import streamlit as st
from tabulate import tabulate

from data import calculate_max_principle_series
from stats import (
    annual_return,
    annual_volatility,
    gen_perf,
    get_period_return,
    moving_average,
)
from utils import strfdelta


def show_performance_metrics(returns, bm_returns, drawdowns, bm_drawdowns):
    """Display performance metrics in a table format."""
    summary = [
        [
            "Period",
            "{} days".format((returns.index[-1] - returns.index[0]).days),
            "{} days".format((bm_returns.index[-1] - bm_returns.index[0]).days),
        ],
        [
            "Return",
            "{:.2%}".format(returns["cum_returns"].iloc[-1]),
            "{:.2%}".format(bm_returns["cum_returns"].iloc[-1]),
        ],
        [
            "Annualized",
            "{:.2%}".format(annual_return(returns["returns"])),
            "{:.2%}".format(annual_return(bm_returns["returns"])),
        ],
        [
            "Max Drawdown",
            "{:.2f}%".format(drawdowns.iloc[0, 0]),
            "{:.2f}%".format(bm_drawdowns.iloc[0, 0]),
        ],
        [
            "Sharpe Ratio",
            "{:.3f}".format(ep.sharpe_ratio(returns["returns"])),
            "{:.3f}".format(ep.sharpe_ratio(bm_returns["returns"])),
        ],
        [
            "Sortino Ratio",
            "{:.3f}".format(ep.sortino_ratio(returns["returns"])),
            "{:.3f}".format(ep.sortino_ratio(bm_returns["returns"])),
        ],
        [
            "Volatility",
            "{:.2%}".format(annual_volatility(returns["returns"])),
            "{:.2%}".format(annual_volatility(bm_returns["returns"])),
        ],
        [
            "Calmar Ratio",
            "{:.3f}".format(ep.calmar_ratio(returns["returns"])),
            "{:.3f}".format(ep.calmar_ratio(bm_returns["returns"])),
        ],
        [
            "Tail Ratio",
            "{:.3f}".format(ep.tail_ratio(returns["returns"])),
            "{:.3f}".format(ep.tail_ratio(bm_returns["returns"])),
        ],
        [
            "Gain to Pain Ratio",
            "{:.3f}".format(ep.omega_ratio(get_period_return(returns, freq="ME"))),
            "{:.3f}".format(ep.omega_ratio(get_period_return(bm_returns, freq="ME"))),
        ],
        [
            "Up Days",
            "{:,} ({:.1%})".format(
                sum(returns["returns"] > 0), sum(returns["returns"] > 0) / len(returns)
            ),
            "{:,} ({:.1%})".format(
                sum(bm_returns["returns"] > 0),
                sum(bm_returns["returns"] > 0) / len(bm_returns),
            ),
        ],
        [
            "Down Days",
            "{:,} ({:.1%})".format(
                sum(returns["returns"] < 0), sum(returns["returns"] < 0) / len(returns)
            ),
            "{:,} ({:.1%})".format(
                sum(bm_returns["returns"] < 0),
                sum(bm_returns["returns"] < 0) / len(bm_returns),
            ),
        ],
    ]

    summary_table = tabulate(summary, ["Metric", "Account", "Bench"], tablefmt="github")
    st.markdown(summary_table)


def show_trade_metrics(rts, trades, returns, turnover_col_name):
    """Display trade metrics in a table format."""
    if rts is None or len(rts) == 0:
        return None, None

    max_principle = calculate_max_principle_series(returns)

    winners = rts[rts.pnl > 0]
    losers = rts[rts.pnl <= 0]

    trade_count = len(rts)
    profit_factor = (
        winners.pnl.sum() / abs(losers.pnl.sum())
        if losers.pnl.sum() != 0
        else float("inf")
    )
    pnl_ratio = (
        (winners.pnl.sum() / len(winners)) / abs(losers.pnl.sum() / len(losers))
        if len(losers) > 0 and losers.pnl.sum() != 0
        else float("inf")
    )
    win_rate = len(winners) / trade_count
    lose_rate = 1 - win_rate
    expected_return_rate = (
        win_rate * winners.account_pnl_pct.mean()
        + (1 - win_rate) * losers.account_pnl_pct.mean()
    )
    kelly = (pnl_ratio * win_rate - lose_rate) / pnl_ratio

    streaks = rts["account_pnl_pct"] > 0
    max_winning_streak = 0
    max_losing_streak = 0
    for key, group in groupby(streaks.values.tolist()):
        group = list(group)
        if sum(group) > 0:
            if len(group) > max_winning_streak:
                max_winning_streak = len(group)
        else:
            if len(group) > max_losing_streak:
                max_losing_streak = len(group)

    turnover = trades[turnover_col_name].abs().sum()
    commission = int(trades.commission.sum())
    rebate = returns["cash_rebate"].sum()
    total_pnl = returns["today_pnl"].sum() + rebate
    # total_pnl = returns["adj_today_pnl"].sum()

    trade_summary = [
        ["Max Principle", "{:,.0f}".format(max_principle.iloc[-1])],
        ["Net Profit", "{:,.0f}".format(total_pnl)],  # with rebate
        ["Cash Rebate", "{:,.0f}".format(rebate)],
        ["No. Trades", trade_count],
        ["Turnover", "{:,.0f}".format(turnover)],
        ["PnL/Turnover", "{:,.2f}‱".format(total_pnl / turnover * 10000)],
        ["Commission", "{:,.0f}".format(commission)],
        ["Commission/Turnover", "{:,.2f}‱".format(commission / turnover * 10000)],
    ]

    if "slippage_value" in trades.columns:
        total_slippage = trades["slippage_value"].sum()

        trades_copy = trades.copy()
        trades_copy["underlying"] = trades_copy.symbol.apply(
            lambda x: x.split("_")[0]
            if "_" in x
            else "".join([i for i in x if not i.isdigit()])
        )
        slippage_breakdown = trades_copy.groupby("underlying").agg(
            total_slippage=pd.NamedAgg(column="slippage_value", aggfunc="sum"),
            total_turnover=pd.NamedAgg(
                column=turnover_col_name, aggfunc=lambda x: x.abs().sum()
            ),
        )
        slippage_breakdown["slippage_ratio"] = (
            slippage_breakdown["total_slippage"] / slippage_breakdown["total_turnover"]
        )
        slippage_breakdown = slippage_breakdown.sort_values("total_slippage")

        trade_summary += [
            ["Slippage", "{:,.0f}".format(total_slippage)],
            ["Slippage/Turnover", "{:,.2f}‱".format(total_slippage / turnover * 10000)],
        ]

    trade_summary += [
        [
            "Avg Holding Period",
            strfdelta(pd.to_timedelta(rts.duration).mean(), "%D days %H hrs"),
        ],
        ["Profit Factor", "{:.3f}".format(profit_factor)],
        ["Win Rate", "{:.2%}".format(win_rate)],
        ["Reward/Risk Ratio", "{:.3f}".format(pnl_ratio)],
        ["Expected Return Rate", "{:,.2f}‱".format(expected_return_rate * 10000)],
        ["Kelly Criterion", "{:.2%}".format(kelly)],
        ["Max Winning Streak", max_winning_streak],
        ["Max Losing Streak", max_losing_streak],
        ["Biggest Winner", "{:.2%}".format(winners.account_pnl_pct.max())],
        ["Biggest Loser", "{:.2%}".format(losers.account_pnl_pct.min())],
        ["Winner Median", "{:.2%}".format(winners.account_pnl_pct.median())],
        ["Loser Median", "{:.2%}".format(losers.account_pnl_pct.median())],
    ]

    trade_summary_table = tabulate(
        trade_summary, ["Metric", "Account"], tablefmt="github"
    )
    st.markdown(trade_summary_table)

    return winners, losers


def plot_returns_cumulative(returns, bm_returns, bm_ratio=1):
    """Plot cumulative returns chart with underwater and time scale selection."""

    # Prepare data for all three time scales
    # We'll create all datasets upfront, then use Plotly buttons to switch between them

    # === DAILY DATA ===
    date0 = returns.index[0] - pd.Timedelta(days=1)
    new_row = pd.DataFrame(
        np.zeros((1, len(returns.columns))), columns=returns.columns, index=[date0]
    )
    preturns = pd.concat([new_row, returns], axis=0)

    daily_account_cum = preturns["cum_returns"]
    daily_bench_cum = preturns["benchmark_cum_returns"]
    daily_account_underwater = preturns["underwater"]
    daily_bench_underwater = preturns["benchmark_underwater"]
    daily_x_data = preturns.index
    daily_cashflows = returns.loc[returns["cashflow"] != 0, "cashflow"]

    # Calculate moving averages for daily view
    daily_ma_5 = moving_average(daily_account_cum, 5)
    daily_ma_50 = moving_average(daily_account_cum, 50)
    daily_ma_100 = moving_average(daily_account_cum, 100)

    # === WEEKLY DATA ===
    weekly_returns_resampled = returns.resample("W").apply(gen_perf).dropna()
    bm_weekly_returns_resampled = bm_returns.resample("W").apply(gen_perf).dropna()

    weekly_account_cum = (1 + weekly_returns_resampled["Return"]).cumprod() - 1
    weekly_bench_cum = (1 + bm_weekly_returns_resampled["Return"]).cumprod() - 1

    weekly_account_first_date = weekly_account_cum.index[0]
    weekly_account_date0 = weekly_account_first_date - pd.Timedelta(days=7)
    weekly_account_cum = pd.concat(
        [pd.Series([0], index=[weekly_account_date0]), weekly_account_cum]
    )

    weekly_bench_first_date = weekly_bench_cum.index[0]
    weekly_bench_date0 = weekly_bench_first_date - pd.Timedelta(days=7)
    weekly_bench_cum = pd.concat(
        [pd.Series([0], index=[weekly_bench_date0]), weekly_bench_cum]
    )

    weekly_account_nav = 1 + weekly_account_cum
    weekly_account_running_max = weekly_account_nav.cummax()
    weekly_account_underwater = weekly_account_nav / weekly_account_running_max - 1

    weekly_bench_nav = 1 + weekly_bench_cum
    weekly_bench_running_max = weekly_bench_nav.cummax()
    weekly_bench_underwater = weekly_bench_nav / weekly_bench_running_max - 1

    weekly_all_dates = weekly_account_cum.index.union(weekly_bench_cum.index)
    weekly_account_cum = weekly_account_cum.reindex(weekly_all_dates)
    weekly_bench_cum_aligned = weekly_bench_cum.reindex(weekly_all_dates)
    weekly_bench_cum = weekly_bench_cum_aligned.copy()
    weekly_bench_cum.loc[weekly_bench_cum.index < weekly_bench_date0] = 0

    weekly_account_underwater = weekly_account_underwater.reindex(weekly_all_dates)
    weekly_bench_underwater_aligned = weekly_bench_underwater.reindex(weekly_all_dates)
    weekly_bench_underwater = weekly_bench_underwater_aligned.copy()
    weekly_bench_underwater.loc[weekly_bench_underwater.index < weekly_bench_date0] = 0

    weekly_x_data = weekly_all_dates

    # === MONTHLY DATA ===
    monthly_returns_resampled = returns.resample("ME").apply(gen_perf).dropna()
    bm_monthly_returns_resampled = bm_returns.resample("ME").apply(gen_perf).dropna()

    monthly_account_cum = (1 + monthly_returns_resampled["Return"]).cumprod() - 1
    monthly_bench_cum = (1 + bm_monthly_returns_resampled["Return"]).cumprod() - 1

    monthly_account_first_date = monthly_account_cum.index[0]
    monthly_account_date0 = monthly_account_first_date - pd.Timedelta(days=31)
    monthly_account_cum = pd.concat(
        [pd.Series([0], index=[monthly_account_date0]), monthly_account_cum]
    )

    monthly_bench_first_date = monthly_bench_cum.index[0]
    monthly_bench_date0 = monthly_bench_first_date - pd.Timedelta(days=31)
    monthly_bench_cum = pd.concat(
        [pd.Series([0], index=[monthly_bench_date0]), monthly_bench_cum]
    )

    monthly_account_nav = 1 + monthly_account_cum
    monthly_account_running_max = monthly_account_nav.cummax()
    monthly_account_underwater = monthly_account_nav / monthly_account_running_max - 1

    monthly_bench_nav = 1 + monthly_bench_cum
    monthly_bench_running_max = monthly_bench_nav.cummax()
    monthly_bench_underwater = monthly_bench_nav / monthly_bench_running_max - 1

    monthly_all_dates = monthly_account_cum.index.union(monthly_bench_cum.index)
    monthly_account_cum = monthly_account_cum.reindex(monthly_all_dates)
    monthly_bench_cum_aligned = monthly_bench_cum.reindex(monthly_all_dates)
    monthly_bench_cum = monthly_bench_cum_aligned.copy()
    monthly_bench_cum.loc[monthly_bench_cum.index < monthly_bench_date0] = 0

    monthly_account_underwater = monthly_account_underwater.reindex(monthly_all_dates)
    monthly_bench_underwater_aligned = monthly_bench_underwater.reindex(
        monthly_all_dates
    )
    monthly_bench_underwater = monthly_bench_underwater_aligned.copy()
    monthly_bench_underwater.loc[
        monthly_bench_underwater.index < monthly_bench_date0
    ] = 0

    monthly_x_data = monthly_all_dates

    # Create figure manually instead of using make_subplots
    # This is necessary because hoversubplots="axis" doesn't work with make_subplots
    # See: https://github.com/plotly/plotly.py/issues/4603
    fig = go.Figure()

    # Helper function for cashflows
    def simplify_amount(amount):
        if abs(amount) >= 1e6:
            return f"${amount / 1e6:.1f}M"
        elif abs(amount) >= 1e3:
            return f"${amount / 1e3:.1f}K"
        else:
            return f"${amount:.2f}"

    # Prepare cashflow data for daily view
    cashflow_x = daily_cashflows.index.tolist() if len(daily_cashflows) > 0 else []
    cashflow_y = (
        [
            daily_account_cum.loc[date] if date in daily_account_cum.index else 0
            for date in cashflow_x
        ]
        if len(cashflow_x) > 0
        else []
    )
    cashflow_hover_text = (
        [simplify_amount(amount) for amount in daily_cashflows]
        if len(daily_cashflows) > 0
        else []
    )
    cashflow_colors = (
        ["green" if amount >= 0 else "red" for amount in daily_cashflows]
        if len(daily_cashflows) > 0
        else []
    )

    # Add all traces (Daily, Weekly, Monthly)
    # Manually specify yaxis for each trace instead of using row/col
    # yaxis="y" for top subplot (cumulative returns)
    # yaxis="y2" for bottom subplot (underwater)

    # DAILY traces (indices 0-8) - visible by default
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_account_cum,
            name="Account",
            connectgaps=True,
            visible=True,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_bench_cum,
            name=f"Benchmark x {bm_ratio}" if bm_ratio > 1 else "Benchmark",
            connectgaps=True,
            visible=True,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_account_underwater,
            name="Account UW",
            connectgaps=True,
            fill="tozeroy",
            line=dict(color="red", width=1),
            fillcolor="rgba(255, 0, 0, 0.2)",
            visible=True,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_bench_underwater,
            name="Benchmark UW",
            connectgaps=True,
            fill="tozeroy",
            fillcolor="rgba(100, 100, 255, 0.2)",
            line=dict(width=1),
            visible=True,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )

    # Daily: Cashflows (visible="legendonly")
    if len(cashflow_x) > 0:
        fig.add_trace(
            go.Scatter(
                x=cashflow_x,
                y=cashflow_y,
                name="Cashflows",
                mode="markers",
                hovertext=cashflow_hover_text,
                hoverinfo="text+x+y",
                marker=dict(size=10, color=cashflow_colors),
                visible="legendonly",
                yaxis="y",
            )
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=[], y=[], name="Cashflows", mode="markers", visible="legendonly",
                yaxis="y",
            )
        )

    # Daily: Moving averages (visible="legendonly" or True)
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_ma_5,
            connectgaps=True,
            name="5 days SMA",
            line=dict(dash="dot"),
            visible="legendonly",
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_ma_50,
            connectgaps=True,
            name="50 days SMA",
            line=dict(dash="dot"),
            visible=True,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=daily_x_data,
            y=daily_ma_100,
            connectgaps=True,
            name="100 days SMA",
            line=dict(dash="dot"),
            visible=True,
            yaxis="y",
        )
    )

    # WEEKLY dummy placeholder (index 8) - to keep trace count consistent
    fig.add_trace(go.Scatter(x=[], y=[], showlegend=False, visible=False, yaxis="y"))

    # WEEKLY traces (indices 9-12)
    fig.add_trace(
        go.Scatter(
            x=weekly_x_data,
            y=weekly_account_cum,
            name="Account",
            connectgaps=True,
            visible=False,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weekly_x_data,
            y=weekly_bench_cum,
            name=f"Benchmark x {bm_ratio}" if bm_ratio > 1 else "Benchmark",
            connectgaps=True,
            visible=False,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weekly_x_data,
            y=weekly_account_underwater,
            name="Account UW",
            connectgaps=True,
            fill="tozeroy",
            line=dict(color="red", width=1),
            fillcolor="rgba(255, 0, 0, 0.2)",
            visible=False,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weekly_x_data,
            y=weekly_bench_underwater,
            name="Benchmark UW",
            connectgaps=True,
            fill="tozeroy",
            fillcolor="rgba(100, 100, 255, 0.2)",
            line=dict(width=1),
            visible=False,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )

    # MONTHLY traces (indices 13-16)
    fig.add_trace(
        go.Scatter(
            x=monthly_x_data,
            y=monthly_account_cum,
            name="Account",
            connectgaps=True,
            visible=False,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_x_data,
            y=monthly_bench_cum,
            name=f"Benchmark x {bm_ratio}" if bm_ratio > 1 else "Benchmark",
            connectgaps=True,
            visible=False,
            yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_x_data,
            y=monthly_account_underwater,
            name="Account UW",
            connectgaps=True,
            fill="tozeroy",
            line=dict(color="red", width=1),
            fillcolor="rgba(255, 0, 0, 0.2)",
            visible=False,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_x_data,
            y=monthly_bench_underwater,
            name="Benchmark UW",
            connectgaps=True,
            fill="tozeroy",
            fillcolor="rgba(100, 100, 255, 0.2)",
            line=dict(width=1),
            visible=False,
            xaxis="x",  # Use same xaxis name for unified hover
            yaxis="y2",
        )
    )

    # Calculate Y axis ranges for all time scales
    all_account_cum = [daily_account_cum, weekly_account_cum, monthly_account_cum]
    all_bench_cum = [daily_bench_cum, weekly_bench_cum, monthly_bench_cum]
    all_account_uw = [
        daily_account_underwater,
        weekly_account_underwater,
        monthly_account_underwater,
    ]
    all_bench_uw = [
        daily_bench_underwater,
        weekly_bench_underwater,
        monthly_bench_underwater,
    ]

    max_return = max(
        [
            0 if pd.isna(data).all() else data.max(skipna=True)
            for data in all_account_cum + all_bench_cum
        ]
    )
    min_return = min(
        [
            0 if pd.isna(data).all() else data.min(skipna=True)
            for data in all_account_cum + all_bench_cum
        ]
    )
    min_underwater = min(
        [
            0 if pd.isna(data).all() else data.min(skipna=True)
            for data in all_account_uw + all_bench_uw
        ]
    )

    # Top subplot: cumulative returns (can be negative when losing money)
    # Add some padding above and below
    if max_return > 0:
        upper_range = max_return * 1.05
    else:
        upper_range = 0.1  # If max is 0 or negative, show at least to +10%

    if min_return < 0:
        lower_range = min_return * 1.05  # Expand downward for negative returns
    else:
        lower_range = 0  # Start from 0 if no negative returns

    # Bottom subplot: underwater (from min to 0)
    # Cap at -100% (physical limit), ensure at least -10% for visibility
    underwater_range = max(min(min_underwater * 1.05, -0.1), -1.0)

    # Create buttons for time scale selection
    # Visibility pattern: [Daily(0-8), Weekly(9-12), Monthly(13-16)]
    # Daily: Account, Bench, Account UW, Bench UW, Cashflows, MA5, MA50, MA100, dummy
    # Weekly: Account, Bench, Account UW, Bench UW
    # Monthly: Account, Bench, Account UW, Bench UW
    updatemenus = [
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(
                    label="Daily",
                    method="update",
                    args=[
                        {
                            "visible": [
                                True,
                                True,
                                True,
                                True,
                                "legendonly",
                                "legendonly",
                                True,
                                True,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                            ]
                        },
                    ],
                ),
                dict(
                    label="Weekly",
                    method="update",
                    args=[
                        {
                            "visible": [
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                True,
                                True,
                                True,
                                True,
                                False,
                                False,
                                False,
                                False,
                            ]
                        },
                    ],
                ),
                dict(
                    label="Monthly",
                    method="update",
                    args=[
                        {
                            "visible": [
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                True,
                                True,
                                True,
                                True,
                            ]
                        },
                    ],
                ),
            ],
            active=0,  # Daily is default
            x=0.5,
            xanchor="center",
            y=-0.15,  # Position below the chart
            yanchor="top",
        ),
    ]

    # Update layout with manually configured axes for hoversubplots support
    # This replaces make_subplots to enable hoversubplots="axis"
    # Key: All traces must use the SAME xaxis name ("x") for unified hover to work
    fig.update_layout(
        title="Cumulative Returns",
        template="seaborn",
        height=700,
        legend=dict(title=""),
        hovermode="x unified",
        hoversubplots="axis",  # Enable hover across subplots sharing the same x-axis
        showlegend=True,
        updatemenus=updatemenus,
        # Define grid structure for subplots
        grid=dict(
            rows=2,
            columns=1,
            subplots=[["xy"], ["xy2"]],  # Map subplot positions
            roworder="top to bottom",
        ),
        # Define y-axis (top subplot - cumulative returns)
        yaxis=dict(
            title="Cumulative Returns",
            tickformat=".2%",
            range=[lower_range, upper_range],
            domain=[0.35, 1.0],  # Top 70% of the figure (with 5% spacing)
        ),
        # Define y2-axis (bottom subplot - underwater)
        yaxis2=dict(
            title="Underwater",
            tickformat=".2%",
            range=[underwater_range, 0],
            domain=[0.0, 0.30],  # Bottom 30% of the figure
        ),
        # X-axis configuration - single xaxis shared by both subplots
        xaxis=dict(
            title="",
            hoverformat="%Y-%m-%d",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_underwater(returns, bm_returns):
    """Plot underwater chart."""
    fig = go.Figure()
    trace = go.Scatter(
        x=returns.index,
        y=returns["underwater"],
        connectgaps=True,
        line_color="red",
        fill="tozeroy",
    )
    bm_trace = go.Scatter(
        x=bm_returns.index,
        y=bm_returns["underwater"],
        connectgaps=True,
        fill="tozeroy",
    )
    fig.add_trace(trace)
    fig.add_trace(bm_trace)
    fig["layout"]["title"] = "Underwater"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Underwater"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["layout"]["template"] = "seaborn"
    fig["data"][0]["name"] = "Account"
    fig["data"][1]["name"] = "Benchmark"

    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_returns_heatmap(returns):
    """Plot monthly returns heatmap."""
    mreturns = (
        returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    mreturns["Return"] *= 100
    mreturns["Year"] = mreturns.index.year
    mreturns["Month"] = mreturns.index.month_name().str[:3]

    mreturns_matrix = mreturns.pivot(
        index="Year", columns="Month", values="Return"
    ).fillna(0)
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    # Handle missing months
    for month in months:
        if month not in mreturns_matrix.columns:
            mreturns_matrix.loc[:, month] = 0
    # Order columns by month
    mreturns_matrix = mreturns_matrix[months]

    fig = px.imshow(
        mreturns_matrix,
        title="Monthly Returns Heatmap",
        labels=dict(x="Month", y="Year", color="Return"),
        x=mreturns_matrix.columns.tolist(),
        y=mreturns_matrix.index.map(str).tolist(),
        color_continuous_scale="rdylgn",
        color_continuous_midpoint=0,
        aspect="auto",
        text_auto=".2f",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig["layout"]["template"] = "seaborn"

    st.plotly_chart(fig, use_container_width=True)


def plot_return_distribution(returns, period="weekly"):
    """Plot return distribution for a given period."""
    if period == "weekly":
        bins = [-np.inf, -0.05, -0.025, 0, 0.025, 0.05, np.inf]
        labels = ["<-5%", "-5%~-2.5%", "-2.5%~0%", "0%~2.5%", "2.5%~5%", ">5%"]
    elif period == "monthly":
        bins = [-np.inf, -0.1, -0.05, 0, 0.05, 0.1, np.inf]
        labels = ["<-10%", "-10%~-5%", "-5%~0%", "0%~5%", "5%~10%", ">10%"]

    category = pd.cut(returns["Return"], bins=bins, labels=labels)
    counts = category.value_counts()
    fig = px.pie(values=counts, names=counts.index.astype(str))
    st.plotly_chart(fig, use_container_width=True)


def plot_returns_periodic(
    yearly_return,
    bm_yearly_return,
    monthly_return,
    bm_monthly_return,
    weekly_return,
    bm_weekly_return,
):
    """Plot periodic returns bar chart with time scale selection (Yearly/Monthly/Weekly)."""

    # Create figure
    fig = go.Figure()

    # Add YEARLY traces (indices 0-1) - hidden by default
    fig.add_trace(
        go.Bar(
            name="Account",
            x=yearly_return.index,
            y=yearly_return.Return,
            visible=False,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Benchmark",
            x=bm_yearly_return.index,
            y=bm_yearly_return.Return,
            visible=False,
        )
    )

    # Add MONTHLY traces (indices 2-3) - hidden by default
    fig.add_trace(
        go.Bar(
            name="Account",
            x=monthly_return.index,
            y=monthly_return.Return,
            visible=False,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Benchmark",
            x=bm_monthly_return.index,
            y=bm_monthly_return.Return,
            visible=False,
        )
    )

    # Add WEEKLY traces (indices 4-5) - visible by default
    # Use the Date column which contains the actual datetime objects
    weekly_dates = weekly_return["Date"].tolist()
    bm_weekly_dates = bm_weekly_return["Date"].tolist()

    fig.add_trace(
        go.Bar(
            name="Account",
            x=weekly_dates,
            y=weekly_return.Return,
            visible=True,
            customdata=weekly_return.index,
            hovertemplate="<b>%{customdata}</b><br>Account: %{y:.2%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Benchmark",
            x=bm_weekly_dates,
            y=bm_weekly_return.Return,
            visible=True,
            customdata=bm_weekly_return.index,
            hovertemplate="<b>%{customdata}</b><br>Benchmark: %{y:.2%}<extra></extra>",
        )
    )

    # Create buttons for time scale selection
    updatemenus = [
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(
                    label="Weekly",
                    method="update",
                    args=[
                        {"visible": [False, False, False, False, True, True]},
                        {
                            "xaxis": {
                                "title": {"text": ""},
                                "autorange": True,
                                "tickformat": "%Y-%m-%d",
                            }
                        },
                    ],
                ),
                dict(
                    label="Monthly",
                    method="update",
                    args=[
                        {"visible": [False, False, True, True, False, False]},
                        {"xaxis": {"title": {"text": ""}, "autorange": True}},
                    ],
                ),
                dict(
                    label="Yearly",
                    method="update",
                    args=[
                        {"visible": [True, True, False, False, False, False]},
                        {
                            "xaxis": {
                                "title": {"text": ""},
                                "tickformat": "%Y %b",
                                "autorange": True,
                            }
                        },
                    ],
                ),
            ],
            active=0,  # Weekly is default (now index 0)
            x=0.5,
            xanchor="center",
            y=-0.15,
            yanchor="top",
        ),
    ]

    # Update layout
    fig.update_layout(
        title="Periodic Returns",
        xaxis=dict(
            title="",
            autorange=True,  # Default for Weekly
            tickformat="%Y-%m-%d",  # Default for Weekly - format dates
        ),
        yaxis=dict(
            title="Returns",
            tickformat=",.2%",
        ),
        template="seaborn",
        updatemenus=updatemenus,
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_profit_distribution(ul_breakdown):
    """Plot profit distribution by underlying."""
    fig = px.bar(
        ul_breakdown,
        x=ul_breakdown.index,
        y="total_pnl",
        title="Profit Distribution by UL",
        template="seaborn",
    )
    fig["layout"]["xaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "PnL"
    fig["layout"]["yaxis"]["tickformat"] = ",.0f"
    st.plotly_chart(fig, use_container_width=True)


def plot_slippage_distribution(slippage_breakdown):
    """Plot slippage distribution by underlying."""
    fig = px.bar(
        slippage_breakdown,
        x=slippage_breakdown.index,
        y="total_slippage",
        title="Slippage Distribution by UL",
        template="seaborn",
    )
    fig["layout"]["xaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Slippage"
    fig["layout"]["yaxis"]["tickformat"] = ",.0f"
    st.plotly_chart(fig, use_container_width=True)
