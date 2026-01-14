import json
import os
from functools import partial

import pandas as pd
import tushare as ts
from dotenv import load_dotenv

def _get_default_benchmarks():
    """Get default benchmark names for UI display."""
    return [
        "南华商品指数",
        "沪深300指数", 
        "标普500指数",
        "纳斯达克综指"
    ]


def load_config():
    """Load configuration from stellar_stats_config.json."""
    # Load environment variables
    load_dotenv()
    
    json_config_path = "stellar_stats_config.json"
    if os.path.exists(json_config_path):
        return _load_json_config(json_config_path)
    else:
        # Auto-discover accounts if no config file
        return _load_auto_config()


def _load_json_config(json_path):
    """Load configuration from stellar_stats_config.json."""
    with open(json_path, 'r') as f:
        config = json.load(f)
    
    # Setup tushare API
    tushare_token = os.getenv("TUSHARE_TOKEN")
    pro = ts.pro_api(tushare_token) if tushare_token else None
    
    # Process strategies into accounts and datadirs
    strategies = config.get("strategies", {})
    accounts = []
    datadirs = {}
    strategy_info = {}
    
    for strategy_id, strategy_config in strategies.items():
        strategy_name = strategy_config.get("name", strategy_id)
        accounts.append(strategy_id)
        
        # Collect all account directories for this strategy
        account_dirs = []
        for account in strategy_config.get("accounts", []):
            account_dir = account["account_dir"]
            if os.path.isdir(account_dir):
                account_dirs.append(account_dir)
        
        datadirs[strategy_id] = account_dirs
        strategy_info[strategy_id] = {
            "name": strategy_name,
            "description": strategy_config.get("description", ""),
            "accounts": strategy_config.get("accounts", [])
        }
    
    # Setup benchmark names for UI display
    default_benchmarks = _get_default_benchmarks()
    custom_benchmark_names = list(config.get("settings", {}).get("benchmarks", {}).keys())
    # Remove duplicates while preserving order
    benchmark_names = default_benchmarks + [name for name in custom_benchmark_names if name not in default_benchmarks]
    
    # Add auth setting for JSON config
    config["auth"] = True
    
    return config, pro, accounts, datadirs, benchmark_names, strategy_info


def _load_auto_config():
    """Auto-discover accounts when no config file exists."""
    # Setup tushare API
    tushare_token = os.getenv("TUSHARE_TOKEN")
    pro = ts.pro_api(tushare_token) if tushare_token else None
    
    # Auto-discover account directories
    accounts = [
        d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")
    ]
    datadirs = {d: d for d in accounts}
    
    # Setup default benchmarks and strategy info
    benchmark_names = _get_default_benchmarks()
    strategy_info = {}  # No strategy info in auto-discovery mode
    
    cfg = None  # No config file, return None to indicate auto-discovery mode
    
    return cfg, pro, accounts, datadirs, benchmark_names, strategy_info


def sort_accounts_by_mtime(accounts, datadirs):
    """Sort accounts by modification time of their returns file."""

    def sort_mtime(x):
        # Handle both single directories and lists of directories
        dirs_to_check = datadirs[x] if isinstance(datadirs[x], list) else [datadirs[x]]
        
        latest_mtime = 0
        for data_dir in dirs_to_check:
            if os.path.exists(f"{data_dir}/returns.csv"):
                path = f"{data_dir}/returns.csv"
            elif os.path.exists(f"{data_dir}/returns.hdf"):
                path = f"{data_dir}/returns.hdf"
            elif os.path.exists(f"{data_dir}/returns.parquet"):
                path = f"{data_dir}/returns.parquet"
            else:
                continue
            
            mtime = os.path.getmtime(path)
            latest_mtime = max(latest_mtime, mtime)

        return latest_mtime

    accounts.sort(key=sort_mtime, reverse=True)
    return accounts