import glob
import os

import click
import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import s3fs
from tqdm import tqdm

try:
    from cfmmc_utils.reports import parse_excel, read_trades_by_broker
except ImportError as e:
    raise ImportError(
        "cfmmc_utils is required for this command. Install with: pip install cfmmc_utils"
    ) from e

from stellar_stats.roundtrip import extract_roundtrips
from stellar_stats.stats import return_stats
from stellar_stats.utils import normalize_futures_symbol

# 统计关键字段
keys = [
    "交易日期",
    "上日结存",
    "客户权益",
    "当日存取合计",
    "当日手续费",
    "保证金占用",
    "可用资金",
    "当日盈亏",
    "最大入金",
    "期权价值",
]


def add_slippage_data(trades_df, dataset_path, s3_endpoint_url=None):
    """Add ref_price and slippage columns to trades DataFrame"""
    if trades_df.empty:
        return trades_df

    # Prepare trades data
    trades = trades_df.reset_index()

    # Create a floored timestamp column for matching with price data (but keep original timestamp)
    trades["timestamp_floored"] = trades["timestamp"].dt.floor(freq="min")

    # Get date range from trades data
    start_date = trades["timestamp_floored"].min()
    end_date = trades["timestamp_floored"].max()

    click.echo(f"Processing slippage data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

    # Setup dataset connection
    if s3_endpoint_url:
        s3_options = {
            "anon": True,
            "client_kwargs": {
                "endpoint_url": s3_endpoint_url,
            },
        }
        s3 = s3fs.S3FileSystem(**s3_options)
        dataset = ds.dataset(dataset_path, filesystem=s3, format="parquet")
    else:
        # Check if local path exists
        if not os.path.exists(dataset_path):
            click.echo(f"Error: Dataset path does not exist: {dataset_path}")
            return trades_df
        dataset = ds.dataset(dataset_path, format="parquet")

    # Generate day range
    current_date = start_date.normalize()
    results = []

    while current_date <= end_date:
        # Get trades for this day
        day_start = current_date
        day_end = current_date + pd.Timedelta(days=1)

        day_trades = trades[
            (trades["timestamp_floored"] >= day_start) & (trades["timestamp_floored"] < day_end)
        ]

        if day_trades.empty:
            # Skip days without trades silently
            pass
        else:
            # Load only this day's data
            click.echo(f"Loading {current_date.strftime('%Y-%m-%d')} price data...")
            expr = (ds.field("timestamp") >= day_start) & (
                ds.field("timestamp") < day_end
            )

            try:
                df = dataset.to_table(filter=expr).to_pandas().reset_index()
                df.timestamp -= pd.Timedelta(minutes=1)
                click.echo(f"{current_date.strftime('%Y-%m-%d')} price data loaded")

                # Filter price data for trade time range
                prices = df[
                    (df.timestamp >= day_trades["timestamp_floored"].min())
                    & (df.timestamp <= day_trades["timestamp_floored"].max())
                ]

                # Merge trades with price data using floored timestamp
                result = day_trades.merge(
                    prices.filter(["timestamp", "symbol", "open"]),
                    left_on=["timestamp_floored", "symbol"],
                    right_on=["timestamp", "symbol"],
                    how="left"
                )

                # Drop the floored timestamp column and the duplicate timestamp from prices
                result = result.drop(columns=["timestamp_floored", "timestamp_y"]).rename(columns={"timestamp_x": "timestamp"})

                result = result.rename(columns={"open": "ref_price"})

                # Calculate slippage
                result["slippage"] = 0.0
                result.loc[result.side.isin(["BUY_OPEN", "BUY_CLOSE"]), "slippage"] = (
                    result["ref_price"] - result["price"]
                )
                result.loc[result.side.isin(["SELL_OPEN", "SELL_CLOSE"]), "slippage"] = (
                    result["price"] - result["ref_price"]
                )

                results.append(result)
                click.echo(f"{current_date.strftime('%Y-%m-%d')} slippage calculation finished")

            except Exception as e:
                click.echo(f"Warning: Cannot load {current_date.strftime('%Y-%m-%d')} data: {e}")
                # Add trades without slippage data for this day
                day_trades_clean = day_trades.drop(columns=["timestamp_floored"])
                day_trades_clean["ref_price"] = None
                day_trades_clean["slippage"] = None
                results.append(day_trades_clean)

        # Move to next day
        current_date += pd.Timedelta(days=1)

    if not results:
        click.echo("No slippage data calculated")
        return trades_df

    # Combine results
    result_df = pd.concat(results, ignore_index=True)

    # Set index back to match original trades_df format
    if "timestamp" in result_df.columns and "symbol" in result_df.columns:
        result_df = result_df.set_index(["timestamp", "symbol"])

    return result_df


@click.command("gen-data-from-cfmmc")
@click.option("--data-dir", "-d", required=True, help="要处理的具体数据目录路径")
@click.option("--output-dir", "-o", required=True, help="输出目录路径")
@click.option(
    "--use-max-cashflow",
    is_flag=True,
    help="使用当日最大入金（而不是总入金）调整账户价值",
)
@click.option(
    "--dataset-path",
    "-p",
    default=None,
    help="分钟数据集路径，用于计算滑点数据",
)
@click.option(
    "--s3-endpoint-url",
    default=None,
    help="S3端点URL，用于从S3加载数据集",
)
@click.option(
    "--regenerate-trades",
    is_flag=True,
    default=False,
    help="重新生成所有trades数据；默认为false，仅增量添加新trades",
)
def gen_data_from_cfmmc(data_dir, output_dir, use_max_cashflow=False, dataset_path=None, s3_endpoint_url=None, regenerate_trades=False):
    """生成期货交易数据统计报告"""

    if not os.path.isdir(data_dir):
        click.echo(f"错误: 数据目录不存在: {data_dir}")
        return

    click.echo(f"正在处理 {data_dir}...")

    # 使用glob模式匹配两种目录结构
    # 新结构: daily/*/*.xls, trades/*/*.xls
    # 旧结构: 日报/逐日/*.xls, 日报/逐笔/*.xls
    daily_paths = (
        glob.glob(f"{data_dir}/daily/*/*.xls")  # 新结构
        + glob.glob(f"{data_dir}/日报/逐日/*.xls")  # 旧结构
    )

    trade_paths = (
        glob.glob(f"{data_dir}/trades/*/*.xls")  # 新结构
        + glob.glob(f"{data_dir}/日报/逐笔/*.xls")  # 旧结构
    )

    if not daily_paths:
        click.echo(f"错误: 找不到逐日报告文件: {data_dir}")
        return

    returns = []

    for file_path in tqdm(sorted(daily_paths), desc="解析xls文件"):
        try:
            info = parse_excel(file_path)
            info = info.filter(keys)
        except Exception as e:
            click.echo(f"读取文件出错 {file_path}: {e}")
            continue

        date = info.loc["交易日期"]
        reported_value = info.loc["客户权益"]
        cashflow = info.loc["当日存取合计"]
        commission = info.loc["当日手续费"]
        max_cashflow = info.loc["最大入金"]
        options_value = info.loc["期权价值"]

        # 计算调整后的账户价值
        account_value = reported_value + options_value

        returns.append(
            (
                date,
                reported_value,
                cashflow,
                commission,
                max_cashflow,
                options_value,
                account_value,
            )
        )

    if not returns:
        click.echo(f"没有找到有效数据: {data_dir}")
        return

    click.echo("生成统计报告...")
    rdf = pd.DataFrame.from_records(
        returns,
        columns=[
            "date",
            "reported_value",
            "cashflow",
            "commission",
            "max_cashflow",
            "options_value",
            "account_value",
        ],
    ).set_index("date")
    rdf.index = pd.to_datetime(rdf.index)
    rdf["last_eod_value"] = rdf["account_value"].shift(1)
    rdf = rdf.dropna()

    rdf["today_pnl"] = rdf["account_value"] - rdf["last_eod_value"] - rdf["cashflow"]
    if not use_max_cashflow:
        adjustment = np.where(rdf["cashflow"] > 0, rdf["cashflow"], 0)
    else:
        adjustment = np.where(
            rdf["max_cashflow"] > rdf["cashflow"], rdf["max_cashflow"], rdf["cashflow"]
        )

    rdf["adj_last_eod_value"] = rdf["last_eod_value"] + adjustment
    rdf["returns"] = rdf["today_pnl"] / rdf["adj_last_eod_value"]

    os.makedirs(f"{output_dir}/", exist_ok=True)
    rdf = return_stats(rdf)

    # 处理交易数据
    if trade_paths:
        # 获取所有交易数据目录
        trade_dirs = list(set(os.path.dirname(path) for path in trade_paths))
        trade_dirs.sort()

        all_trades = []
        for trade_dir in trade_dirs:
            tdf = read_trades_by_broker(trade_dir.rstrip("/") + "/")
            if not tdf.empty:
                all_trades.append(tdf)

        if all_trades:
            new_trades = pd.concat(all_trades).sort_index()

            # Normalize futures symbols
            if "symbol" in new_trades.columns:
                new_trades["symbol"] = new_trades.apply(
                    lambda row: normalize_futures_symbol(row["symbol"], row.name.year),
                    axis=1,
                )

            # Set multi-level index (timestamp, symbol) to match the format in trades.csv
            new_trades = new_trades.reset_index().set_index(["timestamp", "symbol"]).sort_index()

            # 处理增量更新逻辑
            if not regenerate_trades and os.path.exists(f"{output_dir}/trades.csv"):
                click.echo("Found existing trades.csv, loading for incremental update...")
                try:
                    existing_trades = pd.read_csv(
                        f"{output_dir}/trades.csv",
                        index_col=["timestamp", "symbol"],
                        parse_dates=["timestamp"]
                    )

                    # Convert trading_day to datetime (parse_dates doesn't always work for columns with mixed formats)
                    if "trading_day" in existing_trades.columns:
                        existing_trades["trading_day"] = pd.to_datetime(existing_trades["trading_day"], format='mixed')

                    # 找出新的 trades（不在现有数据中的）
                    # 使用索引来识别新trades
                    new_indices = new_trades.index.difference(existing_trades.index)

                    if len(new_indices) > 0:
                        click.echo(f"Found {len(new_indices)} new trades to add")
                        trades_to_add = new_trades.loc[new_indices]

                        # Ensure index names are preserved (index.difference() loses names)
                        trades_to_add.index.names = new_trades.index.names

                        # 只为新的 trades 添加 slippage 数据
                        if dataset_path:
                            click.echo("Adding slippage data to new trades...")
                            trades_to_add = add_slippage_data(trades_to_add, dataset_path, s3_endpoint_url)

                        # 确保 trades_to_add 与 existing_trades 有相同的列
                        # 如果 existing_trades 有 ref_price 和 slippage，但 trades_to_add 没有（因为没有 dataset_path）
                        if "ref_price" in existing_trades.columns and "ref_price" not in trades_to_add.columns:
                            trades_to_add["ref_price"] = None
                        if "slippage" in existing_trades.columns and "slippage" not in trades_to_add.columns:
                            trades_to_add["slippage"] = None

                        # 合并现有和新的 trades
                        tdf = pd.concat([existing_trades, trades_to_add]).sort_index()
                        click.echo(f"Updated trades: {len(existing_trades)} existing + {len(trades_to_add)} new = {len(tdf)} total")
                    else:
                        click.echo("No new trades found, using existing trades.csv")
                        tdf = existing_trades

                except Exception as e:
                    click.echo(f"Warning: Could not load existing trades.csv: {e}")
                    click.echo("Falling back to regenerating all trades...")
                    tdf = new_trades
                    if dataset_path:
                        click.echo("Adding slippage data to trades...")
                        tdf = add_slippage_data(tdf, dataset_path, s3_endpoint_url)
            else:
                # regenerate_trades=True 或者不存在现有文件
                if regenerate_trades:
                    click.echo("Regenerating all trades data...")
                else:
                    click.echo("No existing trades.csv found, generating new trades data...")

                tdf = new_trades
                if dataset_path:
                    click.echo("Adding slippage data to trades...")
                    tdf = add_slippage_data(tdf, dataset_path, s3_endpoint_url)

            # Round numeric columns to 4 decimal places before saving
            numeric_cols = ["price", "ref_price", "slippage", "commission", "pnl"]
            for col in numeric_cols:
                if col in tdf.columns:
                    tdf[col] = tdf[col].round(4)

            tdf.to_csv(f"{output_dir}/trades.csv")

            rts = extract_roundtrips(tdf)
            rts = rts.merge(
                rdf.filter(["adj_last_eod_value"]),
                left_on="close_dt",
                right_index=True,
            )
            rts["account_pnl_pct"] = rts.pnl / rts.adj_last_eod_value
            rts = rts.drop(["adj_last_eod_value"], axis=1)
            rts.to_csv(f"{output_dir}/round_trips.csv", index=False)

    rdf.to_csv(f"{output_dir}/returns.csv")
    click.echo(f"完成 {output_dir}")
