import os

import click
import pandas as pd
import numpy as np

from stellar_stats.data import _load_single_returns_file


@click.command("gen-rebates")
@click.argument("account_dir", type=click.Path(exists=True))
@click.option(
    "--rebate-threshold",
    default=0.01,
    type=float,
    help="Threshold below which cashflows are considered rebates",
)
@click.option(
    "--output",
    "-o",
    help="Output file path (default: rebates.csv in account directory)",
)
def gen_rebates(account_dir, rebate_threshold, output):
    """Generate rebates.csv from account directory cashflow data"""
    try:
        # Load returns data using the existing function from data.py
        returns = _load_single_returns_file(account_dir)
        if returns is None:
            click.echo(f"No returns data found in {account_dir}", err=True)
            raise click.Abort()

        # Generate rebates data using the same logic as adjust_rebate
        if "cashflow" not in returns or "today_pnl" not in returns:
            click.echo("No cashflow data found in returns. Cannot generate rebates.", err=True)
            raise click.Abort()

        # Detect rebates: positive cashflows below threshold
        rebate_mask = (returns.cashflow > 0) & (
            returns.cashflow / returns.account_value < rebate_threshold
        )
        
        # Get rebate amounts
        rebate_amounts = returns["cashflow"] * rebate_mask
        
        # Filter out zero rebates
        rebates_with_amounts = rebate_amounts[rebate_amounts > 0]
        
        if len(rebates_with_amounts) == 0:
            click.echo("No rebates found with the given threshold.")
            rebates_df = pd.DataFrame(columns=["date", "account", "rebate_amount"])
        else:
            # Create rebates DataFrame
            rebates_data = []
            account_name = os.path.basename(account_dir)
            for date, amount in rebates_with_amounts.items():
                rebates_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "account": account_name,
                    "rebate_amount": amount
                })
            
            rebates_df = pd.DataFrame(rebates_data)

        # Determine output file path
        if output is None:
            output = os.path.join(account_dir, "rebates.csv")

        # Save to CSV
        rebates_df.to_csv(output, index=False)
        
        total_rebates = rebates_df["rebate_amount"].sum() if len(rebates_df) > 0 else 0
        click.echo(
            f"Generated rebates.csv with {len(rebates_df)} entries (total: {total_rebates:,.0f}) at: {output}"
        )

    except Exception as e:
        click.echo(f"Error generating rebates.csv: {str(e)}", err=True)
        raise click.Abort()