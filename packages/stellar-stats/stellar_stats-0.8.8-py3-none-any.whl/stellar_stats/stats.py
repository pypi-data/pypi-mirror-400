from functools import partial

import empyrical as ep
import numpy as np
import pandas as pd


def annual_return(returns):
    """
    Calculate annualized return using actual calendar time from datetime index.

    Unlike empyrical's version which uses data point counts, this uses the actual
    time elapsed between first and last dates in the index.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns with DatetimeIndex

    Returns
    -------
    float
        Annualized return (CAGR) based on actual calendar time
    """
    if len(returns) == 0:
        return np.nan

    if len(returns) == 1:
        return returns.iloc[0]

    # Calculate actual time elapsed in years
    start_date = returns.index[0]
    end_date = returns.index[-1]
    days_elapsed = (end_date - start_date).days

    if days_elapsed == 0:
        return returns.iloc[0]

    years_elapsed = days_elapsed / 365.25  # Account for leap years

    # Calculate total return: (1 + r1) * (1 + r2) * ... - 1
    total_return = (1 + returns).prod() - 1

    # Annualize using CAGR formula
    if 1 + total_return > 0 and years_elapsed > 0:
        return (1 + total_return) ** (1 / years_elapsed) - 1
    else:
        return total_return


def annual_volatility(returns):
    """
    Calculate annualized volatility using actual calendar time from datetime index.

    Unlike empyrical's version which uses data point counts, this uses the actual
    time elapsed and scales volatility appropriately.

    Parameters
    ----------
    returns : pd.Series
        Periodic returns with DatetimeIndex

    Returns
    -------
    float
        Annualized volatility based on actual calendar time
    """
    if len(returns) == 0:
        return np.nan

    if len(returns) == 1:
        return 0.0

    # Calculate sample standard deviation of returns
    vol = returns.std()

    # Calculate actual time elapsed
    start_date = returns.index[0]
    end_date = returns.index[-1]
    days_elapsed = (end_date - start_date).days

    if days_elapsed == 0:
        return 0.0

    # Calculate average time between observations
    avg_days_between_obs = days_elapsed / (len(returns) - 1)

    # Annualize: scale by sqrt of periods per year
    periods_per_year = 365.25 / avg_days_between_obs
    annual_vol = vol * np.sqrt(periods_per_year)

    return annual_vol


def get_max_drawdown_underwater(underwater):
    """
    Determines peak, valley, and recovery dates given an 'underwater'
    DataFrame.
    """

    valley = underwater.idxmin()  # end of the period
    # Find first 0
    peak = underwater[:valley][underwater[:valley] == 0].index[-1]
    # Find last 0
    try:
        recovery = underwater[valley:][underwater[valley:] == 0].index[0]
    except IndexError:
        recovery = np.nan  # drawdown not recovered
    return peak, valley, recovery


def get_top_drawdowns(returns, top=10):
    returns = returns.copy()
    df_cum = ep.cum_returns(returns, 1.0)
    running_max = np.maximum.accumulate(df_cum)
    underwater = df_cum / running_max - 1

    drawdowns = []
    for _ in range(top):
        peak, valley, recovery = get_max_drawdown_underwater(underwater)
        # Slice out draw-down period
        if not pd.isnull(recovery):
            underwater.drop(underwater[peak:recovery].index[1:-1], inplace=True)
        else:
            # drawdown has not ended yet
            underwater = underwater.loc[:peak]

        drawdowns.append((peak, valley, recovery))
        if (len(returns) == 0) or (len(underwater) == 0) or (np.min(underwater) == 0):
            break

    return drawdowns


def gen_drawdown_table(returns, top=10):
    df_cum = ep.cum_returns(returns, 1.0)
    drawdown_periods = get_top_drawdowns(returns, top=top)
    df_drawdowns = pd.DataFrame(
        index=list(range(top)),
        columns=[
            "Drawdown %",
            "Peak date",
            "Valley date",
            "Recovery date",
            "Duration",
        ],
    )

    for i, (peak, valley, recovery) in enumerate(drawdown_periods):
        # Store dates as date objects (without time)
        df_drawdowns.loc[i, "Peak date"] = peak.date()
        df_drawdowns.loc[i, "Valley date"] = valley.date()
        df_drawdowns.loc[i, "Recovery date"] = (
            recovery.date() if not pd.isnull(recovery) else pd.NaT
        )

        # Calculate duration - handle NaN recovery dates by using end of returns series
        if pd.isnull(recovery):
            df_drawdowns.loc[i, "Duration"] = len(
                pd.date_range(peak, returns.index[-1], freq="D")
            )
        else:
            df_drawdowns.loc[i, "Duration"] = len(
                pd.date_range(peak, recovery, freq="D")
            )

        # Calculate drawdown percentage (negative value)
        df_drawdowns.loc[i, "Drawdown %"] = (
            -1 * ((df_cum.loc[peak] - df_cum.loc[valley]) / df_cum.loc[peak]) * 100
        )

    return df_drawdowns.dropna(axis=0, how="all")


def get_period_return(df, freq):
    def _calc_return(x):
        try:
            initial_value = x["last_eod_value"].iloc[0] + x["cashflow"].sum()
            if initial_value == 0:
                return np.nan
            return (x["account_value"].iloc[-1] - initial_value) / initial_value
        except:
            return np.nan

    return df.groupby(pd.Grouper(freq=freq)).apply(_calc_return).dropna()


def get_underwater(navs):
    running_max = np.maximum.accumulate(navs)
    underwater = -1 * ((running_max - navs) / running_max)
    return underwater


def moving_average(navs, days):
    return navs.rolling(window=days, center=False).mean()


def return_stats(returns, preserve_nav=False):
    if len(returns) == 0:
        return None
    returns_dict = {}

    # Preserve original net_asset_values if requested and it exists
    original_nav = None
    if preserve_nav and "net_asset_values" in returns.columns:
        original_nav = returns["net_asset_values"].copy()

    returns = returns.drop(
        ["cum_returns", "net_asset_values", "underwater"], axis=1, errors="ignore"
    )
    returns_dict["cum_returns"] = ep.cum_returns(returns["returns"])
    new_nav = returns_dict["cum_returns"] + 1.0

    if preserve_nav and original_nav is not None:
        # Use preserved NAV instead of recalculating
        returns_dict["net_asset_values"] = original_nav
        nav = original_nav
    else:
        # Calculate NAV from returns as before
        nav = new_nav
        returns_dict["net_asset_values"] = nav

    running_max = np.maximum.accumulate(new_nav)
    returns_dict["underwater"] = -1 * ((running_max - new_nav) / running_max)
    rdf = pd.concat(returns_dict, axis=1)
    return pd.concat([returns, rdf], axis=1)


def adjust_rebate(returns, rebate_threshold=0.01, preserve_nav=False):
    if "cashflow" not in returns or "today_pnl" not in returns:
        return return_stats(returns, preserve_nav=preserve_nav)

    rebate_mask = (returns.cashflow > 0) & (
        returns.cashflow / returns.account_value < rebate_threshold
    )
    adjustment = np.where(returns["cashflow"] > 0, returns["cashflow"], 0)
    returns["adj_last_eod_value"] = returns["last_eod_value"] + adjustment
    returns["cash_rebate"] = returns["cashflow"] * rebate_mask
    # Adjust today's pnl as cash rebate is profit
    # This way it will also be considered in the return calculation
    returns["adj_today_pnl"] = returns["today_pnl"] + returns["cash_rebate"]
    returns["returns"] = returns["adj_today_pnl"] / returns["adj_last_eod_value"]
    return return_stats(returns, preserve_nav=preserve_nav)


def gen_perf(df):
    if len(df) == 0:
        return None
    cashflow = df["cashflow"].sum()
    begin = (
        df["adj_last_eod_value"].iloc[0]
        if "adj_last_eod_value" in df
        else df["account_value"].iloc[0]
    )
    end = df["account_value"].dropna().iloc[-1]
    change = end - begin - cashflow
    ret = df["returns"] + 1

    return pd.Series(
        [
            begin,
            cashflow,
            end,
            change,
            ret.prod() - 1,
        ],
        index=["Beginning", "Total D/W", "Ending", "Change", "Return"],
    )


def style_returns(df, caption="", sign="", color=None):
    format_dict = {
        "Beginning": "%s{0:,.0f}" % sign,
        "Total D/W": "%s{0:,.0f}" % sign,
        "Ending": "%s{0:,.0f}" % sign,
        "Change": "%s{0:,.0f}" % sign,
        "Return": "{:.2%}",
    }
    if not color:
        color = ["#d65f5f", "#5fba7d"]
    sdf = (
        df.style.format(format_dict)
        .hide(axis="index")
        .set_table_attributes('class="rendered_html"')
        .bar(color=color, subset=["Change", "Return"], align="zero")
    )

    if caption:
        return sdf.set_caption(caption)
    else:
        return sdf


def style_drawdowns(df, caption="", color=None):
    format_dict = {
        "Drawdown %": "{:.2f}%",
    }
    if not color:
        color = ["#d65f5f", "#5fba7d"]
    sdf = (
        df.style.format(format_dict)
        .hide(axis="index")
        .set_caption(caption)
        .bar(color=color, subset=["Drawdown %"], align="right")
    )
    return sdf


def adjust_last_eod_value(df):
    return df.last_eod_value + np.where(df.cashflow > 0, df.cashflow, 0)
