import os

import click
import pandas as pd
import numpy as np

from stellar_stats.data import _load_single_returns_file


def load_rebates_from_dir(account_dir):
    """Load rebates data from account directory."""
    rebates_file = os.path.join(account_dir, 'rebates.csv')
    if os.path.exists(rebates_file):
        try:
            return pd.read_csv(rebates_file, index_col=0, parse_dates=True)
        except Exception:
            pass
    return None


def generate_investors_from_cashflow(
    returns,
    investor_name,
    account_name,
    account_dir,
    rebate_threshold=0.01,
):
    """
    Generate investors.csv from returns data cashflow, excluding cash rebates.

    Parameters:
    - returns: DataFrame with returns data containing cashflow column
    - investor_name: String name to use for all investor entries
    - account_name: String account name
    - account_dir: Path to account directory
    - rebate_threshold: Threshold below which cashflows are considered rebates (fallback only)

    Returns:
    - DataFrame with investor data
    """
    if returns is None or "cashflow" not in returns.columns:
        raise ValueError("Returns data must contain a 'cashflow' column")

    # Try to load explicit rebates data first
    rebates_data = load_rebates_from_dir(account_dir)
    
    if rebates_data is not None and len(rebates_data) > 0:
        # Use explicit rebates.csv data
        # Align rebates data with returns index
        aligned_rebates = rebates_data.reindex(returns.index, fill_value=0)
        rebate_amounts = aligned_rebates["rebate_amount"]
        
        # Calculate non-rebate cashflows
        non_rebate_cashflows = returns["cashflow"] - rebate_amounts
        
        # Get significant cashflows (non-zero after rebate exclusion)
        significant_mask = non_rebate_cashflows != 0
        significant_cashflows = returns[significant_mask].copy()
        significant_cashflows["effective_cashflow"] = non_rebate_cashflows[significant_mask]
        
    else:
        # Fall back to threshold-based detection
        # Simple threshold-based rebate detection
        cashflows = returns["cashflow"]
        rebate_mask = (cashflows.abs() <= rebate_threshold) & (cashflows != 0)
        
        # Get significant cashflows (non-rebate)
        significant_mask = ~rebate_mask & (cashflows != 0)
        significant_cashflows = returns[significant_mask].copy()
        significant_cashflows["effective_cashflow"] = significant_cashflows["cashflow"]

    if len(significant_cashflows) == 0:
        print("No significant cashflows found after filtering rebates")
        return pd.DataFrame(columns=["name", "account", "date", "cashflow"])

    # Create investor data
    investor_data = []
    for date, row in significant_cashflows.iterrows():
        investor_data.append(
            {
                "name": investor_name,
                "account": account_name,
                "date": date.strftime("%Y-%m-%d"),
                "cashflow": row["effective_cashflow"],
            }
        )

    investors_df = pd.DataFrame(investor_data)
    return investors_df


@click.command("gen-investors")
@click.argument("account_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--investor-name", required=True, help="Name of the investor")
@click.option(
    "--rebate-threshold",
    default=0.01,
    type=float,
    help="Threshold below which cashflows are considered rebates",
)
@click.option(
    "--output",
    "-o",
    help="Output file path (default: investors.csv in account directory)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Override existing investors.csv file",
)
def gen_investors(account_dir, investor_name, rebate_threshold, output, force):
    """Generate investors.csv for account directory from cashflow data"""
    try:
        # Get account name from directory
        account_name = os.path.basename(os.path.abspath(account_dir))
        
        # Check for existing investors.csv file
        if output is None:
            output = os.path.join(account_dir, "investors.csv")
        
        if os.path.exists(output) and not force:
            click.echo(f"investors.csv already exists at {output}. Use --force to override.", err=True)
            raise click.Abort()

        # Load returns data from directory
        returns = _load_single_returns_file(account_dir)
        if returns is None:
            click.echo(f"No returns file found in {account_dir}", err=True)
            raise click.Abort()

        # Generate investors data
        investors_df = generate_investors_from_cashflow(
            returns, investor_name, account_name, account_dir, rebate_threshold
        )

        # Save to CSV
        investors_df.to_csv(output, index=False)
        click.echo(
            f"Generated investors.csv with {len(investors_df)} entries at: {output}"
        )

    except Exception as e:
        click.echo(f"Error generating investors.csv: {str(e)}", err=True)
        raise click.Abort()