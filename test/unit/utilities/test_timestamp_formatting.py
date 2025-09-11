"""Unit tests for timestamp_formatting function."""

from datetime import datetime

from src.utilities.timestamp_formatting import format_time_human_friendly


def test_format_time_zero_minutes():
    """Test formatting times with zero minutes returns just the hour."""
    # Test various hours with zero minutes
    test_cases = [
        (datetime(2023, 1, 1, 0, 0), "12"),  # Midnight
        (datetime(2023, 1, 1, 1, 0), "1"),  # 1 AM
        (datetime(2023, 1, 1, 6, 0), "6"),  # 6 AM
        (datetime(2023, 1, 1, 12, 0), "12"),  # Noon
        (datetime(2023, 1, 1, 13, 0), "1"),  # 1 PM
        (datetime(2023, 1, 1, 18, 0), "6"),  # 6 PM
        (datetime(2023, 1, 1, 23, 0), "11"),  # 11 PM
    ]

    for time, expected in test_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_with_minutes():
    """Test formatting times with non-zero minutes returns hour:minute format."""
    test_cases = [
        (datetime(2023, 1, 1, 0, 30), "12:30"),  # 12:30 AM
        (datetime(2023, 1, 1, 1, 15), "1:15"),  # 1:15 AM
        (datetime(2023, 1, 1, 6, 45), "6:45"),  # 6:45 AM
        (datetime(2023, 1, 1, 12, 30), "12:30"),  # 12:30 PM
        (datetime(2023, 1, 1, 13, 15), "1:15"),  # 1:15 PM
        (datetime(2023, 1, 1, 18, 45), "6:45"),  # 6:45 PM
        (datetime(2023, 1, 1, 23, 59), "11:59"),  # 11:59 PM
    ]

    for time, expected in test_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_edge_cases():
    """Test edge cases for time formatting."""
    # Test single digit minutes
    test_cases = [
        (datetime(2023, 1, 1, 12, 1), "12:01"),  # 12:01 PM
        (datetime(2023, 1, 1, 1, 5), "1:05"),  # 1:05 AM
        (datetime(2023, 1, 1, 6, 9), "6:09"),  # 6:09 AM
    ]

    for time, expected in test_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_noon_midnight():
    """Test special cases for noon and midnight."""
    # Noon and midnight with zero minutes
    assert format_time_human_friendly(datetime(2023, 1, 1, 12, 0)) == "12"
    assert format_time_human_friendly(datetime(2023, 1, 1, 0, 0)) == "12"

    # Noon and midnight with minutes
    assert format_time_human_friendly(datetime(2023, 1, 1, 12, 30)) == "12:30"
    assert format_time_human_friendly(datetime(2023, 1, 1, 0, 30)) == "12:30"


def test_format_time_am_pm_transitions():
    """Test AM/PM transitions (11 AM to 12 PM, 11 PM to 12 AM)."""
    # 11 AM to 12 PM
    assert format_time_human_friendly(datetime(2023, 1, 1, 11, 0)) == "11"
    assert format_time_human_friendly(datetime(2023, 1, 1, 12, 0)) == "12"

    # 11 PM to 12 AM (midnight)
    assert format_time_human_friendly(datetime(2023, 1, 1, 23, 0)) == "11"
    assert format_time_human_friendly(datetime(2023, 1, 1, 0, 0)) == "12"

    # With minutes
    assert format_time_human_friendly(datetime(2023, 1, 1, 11, 30)) == "11:30"
    assert format_time_human_friendly(datetime(2023, 1, 1, 12, 30)) == "12:30"
    assert format_time_human_friendly(datetime(2023, 1, 1, 23, 30)) == "11:30"
    assert format_time_human_friendly(datetime(2023, 1, 1, 0, 30)) == "12:30"


def test_format_time_various_hours():
    """Test various hours throughout the day."""
    # Test all hours from 0 to 23
    expected_results = [
        "12",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",  # 0-11 (12 AM to 11 AM)
        "12",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",  # 12-23 (12 PM to 11 PM)
    ]

    for hour in range(24):
        time = datetime(2023, 1, 1, hour, 0)
        expected = expected_results[hour]
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for hour {hour}, got {result}"


def test_format_time_various_minutes():
    """Test various minute values."""
    # Test different minute values for the same hour
    base_hour = 2  # 2 AM
    test_cases = [
        (0, "2"),  # 2:00 AM
        (1, "2:01"),  # 2:01 AM
        (15, "2:15"),  # 2:15 AM
        (30, "2:30"),  # 2:30 AM
        (45, "2:45"),  # 2:45 AM
        (59, "2:59"),  # 2:59 AM
    ]

    for minutes, expected in test_cases:
        time = datetime(2023, 1, 1, base_hour, minutes)
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_afternoon_evening():
    """Test afternoon and evening hours specifically."""
    # Afternoon hours (1 PM to 5 PM)
    afternoon_cases = [
        (datetime(2023, 1, 1, 13, 0), "1"),  # 1 PM
        (datetime(2023, 1, 1, 14, 0), "2"),  # 2 PM
        (datetime(2023, 1, 1, 15, 0), "3"),  # 3 PM
        (datetime(2023, 1, 1, 16, 0), "4"),  # 4 PM
        (datetime(2023, 1, 1, 17, 0), "5"),  # 5 PM
    ]

    for time, expected in afternoon_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"

    # Evening hours (6 PM to 11 PM)
    evening_cases = [
        (datetime(2023, 1, 1, 18, 0), "6"),  # 6 PM
        (datetime(2023, 1, 1, 19, 0), "7"),  # 7 PM
        (datetime(2023, 1, 1, 20, 0), "8"),  # 8 PM
        (datetime(2023, 1, 1, 21, 0), "9"),  # 9 PM
        (datetime(2023, 1, 1, 22, 0), "10"),  # 10 PM
        (datetime(2023, 1, 1, 23, 0), "11"),  # 11 PM
    ]

    for time, expected in evening_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_early_morning():
    """Test early morning hours (12 AM to 5 AM)."""
    early_morning_cases = [
        (datetime(2023, 1, 1, 0, 0), "12"),  # 12 AM (midnight)
        (datetime(2023, 1, 1, 1, 0), "1"),  # 1 AM
        (datetime(2023, 1, 1, 2, 0), "2"),  # 2 AM
        (datetime(2023, 1, 1, 3, 0), "3"),  # 3 AM
        (datetime(2023, 1, 1, 4, 0), "4"),  # 4 AM
        (datetime(2023, 1, 1, 5, 0), "5"),  # 5 AM
    ]

    for time, expected in early_morning_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_morning():
    """Test morning hours (6 AM to 11 AM)."""
    morning_cases = [
        (datetime(2023, 1, 1, 6, 0), "6"),  # 6 AM
        (datetime(2023, 1, 1, 7, 0), "7"),  # 7 AM
        (datetime(2023, 1, 1, 8, 0), "8"),  # 8 AM
        (datetime(2023, 1, 1, 9, 0), "9"),  # 9 AM
        (datetime(2023, 1, 1, 10, 0), "10"),  # 10 AM
        (datetime(2023, 1, 1, 11, 0), "11"),  # 11 AM
    ]

    for time, expected in morning_cases:
        result = format_time_human_friendly(time)
        assert result == expected, f"Expected {expected} for {time}, got {result}"


def test_format_time_with_seconds():
    """Test that seconds are ignored (function only considers hour and minute)."""
    # Same time with different seconds should return same result
    time1 = datetime(2023, 1, 1, 12, 30, 0)
    time2 = datetime(2023, 1, 1, 12, 30, 30)
    time3 = datetime(2023, 1, 1, 12, 30, 59)

    result1 = format_time_human_friendly(time1)
    result2 = format_time_human_friendly(time2)
    result3 = format_time_human_friendly(time3)

    assert result1 == result2 == result3 == "12:30"


def test_format_time_different_dates():
    """Test that date doesn't affect time formatting."""
    # Same time on different dates should return same result
    time1 = datetime(2023, 1, 1, 14, 30)
    time2 = datetime(2023, 12, 31, 14, 30)
    time3 = datetime(2024, 6, 15, 14, 30)

    result1 = format_time_human_friendly(time1)
    result2 = format_time_human_friendly(time2)
    result3 = format_time_human_friendly(time3)

    assert result1 == result2 == result3 == "2:30"


def test_format_time_return_type():
    """Test that function returns a string."""
    test_times = [
        datetime(2023, 1, 1, 0, 0),
        datetime(2023, 1, 1, 12, 0),
        datetime(2023, 1, 1, 12, 30),
        datetime(2023, 1, 1, 23, 59),
    ]

    for time in test_times:
        result = format_time_human_friendly(time)
        assert isinstance(result, str), f"Expected string for {time}, got {type(result)}"
