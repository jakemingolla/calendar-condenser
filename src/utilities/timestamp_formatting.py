from datetime import datetime


def format_time_human_friendly(time: datetime) -> str:
    """Return a human-friendly string representation of the given time.

    Uses 12-hour time format.
    Ignores the minutes if it is 00.

    Examples:
    12:00 -> 12
    13:00 -> 1
    12:30 -> 12:30

    @param time: The time to format.
    @return: A human-friendly string representation of the given time.

    """
    # Convert to 12-hour format without zero-padding
    hour_12 = time.hour % 12
    if hour_12 == 0:
        hour_12 = 12

    if time.minute == 0:
        return str(hour_12)
    else:
        return f"{hour_12}:{time.minute:02d}"
