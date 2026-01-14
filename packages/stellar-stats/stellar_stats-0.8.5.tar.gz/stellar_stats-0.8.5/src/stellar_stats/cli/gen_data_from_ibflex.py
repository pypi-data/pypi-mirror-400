import os
from collections import defaultdict

import click
import pandas as pd

try:
    import ibflex
except ImportError as e:
    raise ImportError("ibflex is required for this command. Install with: pip install ibflex") from e

from stellar_stats.roundtrip import extract_roundtrips
from stellar_stats.stats import return_stats


# If there are position transfers and cash transfers in the same day
# take them as mistrades and don't include them in trades or cashflow
def invalid_cashflow(record, mistrades):
    if record[0] in mistrades:
        print("Removing cashflow record for", *record)
        return False
    else:
        return True


@click.command("gen-data-from-ibflex")
@click.option("--data-dir", default="ibflex", help="Directory containing XML files")
@click.option("--output-dir", default="stats", help="Output directory for results")
def gen_data_from_ibflex(output_dir, data_dir):
    """Generate trading data from Interactive Brokers Flex XML files"""
    accounts = set()

    # First pass: discover all account IDs from XML files
    fnames = os.listdir(data_dir)
    fnames.sort()

    for fname in fnames:
        if fname[-4:] != ".xml":
            continue

        try:
            int(fname[:-4])
        except ValueError:
            print("Filename is not a year, ignored", fname)
            continue

        path = os.path.join(data_dir, fname)
        ibxml = ibflex.parse(path)

        for stmt in ibxml.FlexStatements:
            accounts.add(stmt.accountId)

    print(f"Found {len(accounts)} accounts: {sorted(accounts)}")

    returns = defaultdict(list)
    trades = defaultdict(list)
    cf_records = defaultdict(list)
    acct_mistrades = {}

    # Second pass: process data for all discovered accounts

    for fname in fnames:
        if fname[-4:] != ".xml":
            continue

        try:
            int(fname[:-4])
        except ValueError:
            print("Filename is not a year, ignored", fname)
            continue

        path = os.path.join(data_dir, fname)
        ibxml = ibflex.parse(path)

        for stmt in ibxml.FlexStatements:
            if stmt.accountId in accounts:
                records = cf_records[stmt.accountId]
                if stmt.accountId not in acct_mistrades:
                    acct_mistrades[stmt.accountId] = defaultdict(list)

                # mistrades = acct_mistrades[stmt.accountId]

                # Group position transfers by date and symbol to handle net transfers
                position_transfers = defaultdict(float)
                
                for trans in stmt.Transfers:
                    if trans.symbol is not None:
                        print(
                            "Found position transfer",
                            trans.date,
                            trans.symbol,
                            trans.quantity,
                        )
                        # Accumulate transfers by date and symbol
                        key = (trans.reportDate, trans.symbol)
                        position_transfers[key] += float(trans.positionAmount) * float(trans.fxRateToBase)
                    elif trans.cashTransfer != 0:
                        records.append(
                            (
                                trans.reportDate,
                                float(trans.cashTransfer) * float(trans.fxRateToBase),
                            )
                        )
                
                # Only add net position transfers that are non-zero
                for (report_date, symbol), net_amount in position_transfers.items():
                    if abs(net_amount) > 1e-6:  # Use small threshold to handle floating point precision
                        print(f"Net position transfer for {symbol} on {report_date}: {net_amount}")
                        records.append((report_date, net_amount))
                    else:
                        print(f"Ignoring zero net position transfer for {symbol} on {report_date}")

                for trans in stmt.CashTransactions:
                    if (
                        trans.symbol is None
                        and trans.type.value == "Deposits & Withdrawals"
                    ):
                        records.append((trans.reportDate, float(trans.amount)))

                records = []
                for equity in stmt.EquitySummaryInBase:
                    records.append((equity.reportDate, float(equity.total)))
                nav = pd.DataFrame.from_records(
                    records, columns=["date", "account_value"]
                )
                nav["date"] = pd.to_datetime(nav.date)
                nav = nav.set_index("date").sort_index()
                returns[stmt.accountId].append(nav)

                records = []
                for trade in stmt.Trades:
                    # date = trade.dateTime.date()
                    # if date in mistrades and trade.symbol in mistrades[date]:
                    #     print(
                    #         'Removing trade record for', trade.dateTime, trade.symbol,
                    #         trade.buySell.value, trade.quantity
                    #     )
                    # else:
                    records.append(
                        (
                            trade.dateTime,
                            trade.ibOrderID,
                            trade.symbol,
                            trade.multiplier,
                            trade.buySell.value,
                            float(trade.tradePrice),
                            float(trade.quantity),
                            abs(float(trade.proceeds)) * float(trade.fxRateToBase),
                            float(trade.cost),
                            float(trade.ibCommission) * float(trade.fxRateToBase),
                            float(trade.taxes) * float(trade.fxRateToBase),
                            float(trade.fifoPnlRealized),
                        )
                    )

                tdf = pd.DataFrame.from_records(
                    records,
                    columns=[
                        "timestamp",
                        "order_id",
                        "symbol",
                        "multiplier",
                        "side",
                        "price",
                        "volume",
                        "value",
                        "cost",
                        "commission",
                        "taxes",
                        "pnl",
                    ],
                )
                tdf["timestamp"] = pd.to_datetime(tdf["timestamp"])
                # tdf = tdf.set_index(['datetime', 'symbol']).sort_index()
                tdf = tdf.set_index("timestamp").sort_index()
                trades[stmt.accountId].append(tdf)

    for aid in accounts:
        print(f"Generating data for IBKR_{aid}")
        returns_df = pd.concat(returns[aid])
        returns_df = returns_df[~returns_df.index.duplicated(keep="first")]

        if trades[aid]:
            # Filter out empty DataFrames before concatenation
            non_empty_trades = [df for df in trades[aid] if not df.empty]
            trades_df = (
                pd.concat(non_empty_trades) if non_empty_trades else pd.DataFrame()
            )
        else:
            trades_df = pd.DataFrame()

        records = cf_records[aid]
        # mistrades = acct_mistrades[aid]
        # records = [record for record in records if invalid_cashflow(record, mistrades)]
        cashflow = pd.DataFrame.from_records(records, columns=["date", "cashflow"])
        cashflow["date"] = pd.to_datetime(cashflow["date"])
        cashflow = cashflow.set_index("date").sort_index()
        print(cashflow)
        cashflow = cashflow.groupby(cashflow.index).agg("sum")

        # Move cashflows from non-trading days to next trading day
        moved_cashflows = []
        trading_days = set(returns_df.index)

        for cf_date, cf_row in cashflow.iterrows():
            if cf_date not in trading_days:
                # Find next trading day
                next_trading_days = [td for td in trading_days if td > cf_date]
                if next_trading_days:
                    next_trading_day = min(next_trading_days)
                    # Move cashflow to next trading day
                    if next_trading_day in cashflow.index:
                        cashflow.loc[next_trading_day, "cashflow"] += cf_row["cashflow"]
                    else:
                        # Add new row for next trading day
                        cashflow.loc[next_trading_day] = cf_row["cashflow"]
                    # Log the move
                    moved_cashflows.append(
                        (cf_date, next_trading_day, cf_row["cashflow"])
                    )
                    # Remove from original date
                    cashflow = cashflow.drop(cf_date)

        # Log moved cashflows
        if moved_cashflows:
            print(f"Moved cashflows for account {aid}:")
            for from_date, to_date, amount in moved_cashflows:
                print(f"  {from_date.date()} -> {to_date.date()}: {amount:.2f}")

        # Only keep cashflows on trading days
        cashflow = cashflow[cashflow.index.isin(trading_days)]

        rdf = pd.concat([returns_df, cashflow], axis=1).sort_index()

        if "cashflow" not in rdf.columns:
            rdf["cashflow"] = 0

        rdf = rdf.fillna(0)

        rdf["last_eod_value"] = rdf["account_value"].shift(1)
        rdf = rdf.dropna()

        # Add adjusted last EOD value (last_eod_value + cashflow)
        rdf["adj_last_eod_value"] = rdf["last_eod_value"] + rdf["cashflow"]

        rdf.index.name = "date"
        rdf["today_pnl"] = (
            rdf["account_value"] - rdf["last_eod_value"] - rdf["cashflow"]
        )
        rdf["returns"] = rdf["today_pnl"] / rdf["adj_last_eod_value"]
        # rdf['returns'] = rdf['returns'].replace([np.inf, -np.inf], np.nan)
        # rdf['returns'] = rdf['returns'].fillna(0)

        os.makedirs(f"{output_dir}/IBKR_{aid}/", exist_ok=True)
        ret_df = return_stats(rdf)
        ret_df.to_csv(f"{output_dir}/IBKR_{aid}/returns.csv")

        trades_df.to_csv(f"{output_dir}/IBKR_{aid}/trades.csv")

        tdf = trades_df.copy()
        tdf["amount"] = (
            tdf["side"].map(lambda x: 1 if x == "BUY" else -1) * tdf["volume"].abs()
        )
        tdf["trading_day"] = pd.to_datetime([d.date() for d in tdf.index])
        # tdf["value"] = tdf["proceeds"].abs()  # value should always be positive
        tdf = tdf.reset_index()
        rts = extract_roundtrips(tdf)

        rts = rts.merge(
            ret_df.filter(["adj_last_eod_value"]),
            left_on="close_dt",
            right_index=True,
        )

        rts["account_pnl_pct"] = rts.pnl / rts.adj_last_eod_value
        rts = (
            rts.drop(["adj_last_eod_value"], axis=1).set_index("close_dt").sort_index()
        )
        rts.to_csv(f"{output_dir}/IBKR_{aid}/round_trips.csv")
