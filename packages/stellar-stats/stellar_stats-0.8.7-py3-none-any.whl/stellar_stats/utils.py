import glob
import os
import re
from string import Template

import pandas as pd
import streamlit as st
from tabulate import tabulate


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def get_latest_modified_time(directory):
    # Get list of all files in directory
    files = glob.glob(directory + "/*")

    # Get the last modified times for all files
    last_modified_times = [os.path.getmtime(file) for file in files]

    # Return the latest modification time
    return max(last_modified_times, default=0)


def show_col_desc(df, cols, dtype="float"):
    result = []
    for col in cols:
        result.append(df[col].describe().to_frame().T)
    desc = pd.concat(result)
    if dtype == "float":
        floatfmt = ("", ",.0f", ".3%", ".3%", ".3%", ".3%", ".3%", ".3%", ".3%")
    else:
        floatfmt = "g"
    st.markdown(tabulate(desc, headers="keys", tablefmt="github", floatfmt=floatfmt))


def refresh_cache(datadirs):
    last_modified = 0
    for acct in datadirs:
        # Handle both single directories and lists of directories (strategies)
        dirs_to_check = (
            datadirs[acct] if isinstance(datadirs[acct], list) else [datadirs[acct]]
        )

        for data_dir in dirs_to_check:
            ts = get_latest_modified_time(data_dir)
            if ts > last_modified:
                last_modified = ts

    last_data = st.session_state.get("last_data", 0)
    if last_data < last_modified:
        print("Cache data updated")
        st.cache_data.clear()
        st.session_state.last_data = last_modified


def normalize_futures_symbol(trading_code, trading_year):
    """根据交易代码和时间戳动态生成标准symbol

    Args:
        trading_code: 如 TA001
        trading_year: 交易时间戳的年份

    Returns:
        标准symbol，如 TA2001
    """
    # 使用正则表达式解析交易代码
    # 匹配格式：字母前缀 + 数字年份(1位) + 数字月份(2位)
    match = re.match(r"^([A-Z]+)(\d)(\d{2})$", trading_code.upper())
    if not match:
        return trading_code  # 如果格式不匹配，返回原代码

    prefix, year_digit, month = match.groups()
    year_digit = int(year_digit)

    contract_year = trading_year - (trading_year % 10) + year_digit
    if contract_year < trading_year:
        contract_year += 10

    # 生成标准symbol：前缀 + 年份后两位 + 月份
    standard_symbol = f"{prefix}{contract_year % 100:02d}{month}"
    return standard_symbol
