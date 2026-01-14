"""
Test cases for the normalize_futures_symbol function
"""

from stellar_stats.utils import normalize_futures_symbol


def test_basic_conversion():
    """Test basic symbol standardization"""
    # Test case: TA001 in 2020 should become TA2001
    result = normalize_futures_symbol("TA001", 2020)
    assert result == "TA2001"

    # Test case: TA901 in 2020 should become TA2901
    result = normalize_futures_symbol("TA901", 2020)
    assert result == "TA2901"


def test_year_digit_logic():
    """Test the year digit logic for contract year calculation"""
    # When year digit (0) < trading_year last digit (0), should add 10
    result = normalize_futures_symbol("TA001", 2020)
    assert result == "TA2001"

    # When year digit (1) > trading_year last digit (0), should not add 10
    result = normalize_futures_symbol("TA101", 2020)
    assert result == "TA2101"

    # When year digit (3) = trading_year last digit (3), should not add 10
    result = normalize_futures_symbol("TA303", 2023)
    assert result == "TA2303"

    # When year digit (5) > trading_year last digit (3), should not add 10
    result = normalize_futures_symbol("TA501", 2023)
    assert result == "TA2501"


def test_different_commodities():
    """Test with different commodity codes"""
    # Single letter commodity
    result = normalize_futures_symbol("A001", 2020)
    assert result == "A2001"

    # Two letter commodity
    result = normalize_futures_symbol("RB001", 2021)
    assert result == "RB3001"

    # Three letter commodity
    result = normalize_futures_symbol("CU001", 2022)
    assert result == "CU3001"


def test_different_months():
    """Test with different month codes"""
    # January
    result = normalize_futures_symbol("TA001", 2020)
    assert result == "TA2001"

    # December
    result = normalize_futures_symbol("TA012", 2020)
    assert result == "TA2012"

    # Mid-year month
    result = normalize_futures_symbol("TA006", 2020)
    assert result == "TA2006"


def test_edge_cases_year_boundaries():
    """Test edge cases around year boundaries"""
    # Year 2019 (ending in 9) with contract year 0
    result = normalize_futures_symbol("TA001", 2019)
    assert result == "TA2001"

    # Year 2019 (ending in 9) with contract year 9
    result = normalize_futures_symbol("TA901", 2019)
    assert result == "TA1901"

    # Year 2030 (ending in 0) with contract year 1
    result = normalize_futures_symbol("TA101", 2030)
    assert result == "TA3101"


def test_lowercase_input():
    """Test that lowercase input is properly handled"""
    result = normalize_futures_symbol("ta001", 2020)
    assert result == "TA2001"

    result = normalize_futures_symbol("rb901", 2021)
    assert result == "RB2901"


def test_invalid_formats():
    """Test invalid format inputs return original string"""
    # No digits
    result = normalize_futures_symbol("TABC", 2020)
    assert result == "TABC"

    # Wrong digit pattern (too many digits)
    result = normalize_futures_symbol("TA0001", 2020)
    assert result == "TA0001"

    # Wrong digit pattern (too few digits)
    result = normalize_futures_symbol("TA01", 2020)
    assert result == "TA01"

    # No letters
    result = normalize_futures_symbol("001", 2020)
    assert result == "001"

    # Mixed invalid format
    result = normalize_futures_symbol("T1A01", 2020)
    assert result == "T1A01"

    # Empty string
    result = normalize_futures_symbol("", 2020)
    assert result == ""


def test_year_calculation_comprehensive():
    """Comprehensive test for year calculation logic"""
    test_cases = [
        # (trading_code, trading_year, expected_result)
        ("TA001", 2020, "TA2001"),  # 0 < 0, add 10
        ("TA101", 2020, "TA2101"),  # 1 > 0, no add
        ("TA201", 2020, "TA2201"),  # 2 > 0, no add
        ("TA901", 2020, "TA2901"),  # 9 > 0, no add
        ("TA001", 2021, "TA3001"),  # 0 < 1, add 10
        ("TA101", 2021, "TA2101"),  # 1 = 1, no add
        ("TA201", 2021, "TA2201"),  # 2 > 1, no add
        ("TA901", 2021, "TA2901"),  # 9 > 1, no add
        ("TA001", 2029, "TA3001"),  # 0 < 9, add 10
        ("TA901", 2029, "TA2901"),  # 9 = 9, no add
    ]

    for trading_code, trading_year, expected in test_cases:
        result = normalize_futures_symbol(trading_code, trading_year)
        assert result == expected, (
            f"Failed for {trading_code}, {trading_year}: expected {expected}, got {result}"
        )


def test_various_trading_years():
    """Test with various trading years"""
    # Test years from different decades
    years_to_test = [2015, 2020, 2025, 2030, 2035]

    for year in years_to_test:
        result = normalize_futures_symbol("TA001", year)
        # Calculate expected year based on the function logic
        contract_year = year - (year % 10) + 0  # year_digit is 0 from TA001
        if contract_year < year:
            contract_year += 10
        assert result == f"TA{contract_year % 100:02d}01"
