import numpy as np
import pandas as pd
import pytest

from stellar_stats.stats import (
    adjust_last_eod_value,
    gen_perf,
    get_underwater,
    moving_average,
)


def test_get_underwater():
    navs = pd.Series([100, 110, 105, 115, 100, 90])
    result = get_underwater(navs)

    expected = pd.Series([0, 0, -0.0454545, 0, -0.1304348, -0.2173913])
    pd.testing.assert_series_equal(result, expected, rtol=1e-6)


def test_moving_average():
    navs = pd.Series([100, 110, 105, 115, 100, 90])
    result = moving_average(navs, 3)

    expected = pd.Series([np.nan, np.nan, 105, 110, 106.666667, 101.666667])
    pd.testing.assert_series_equal(result, expected, rtol=1e-6)
