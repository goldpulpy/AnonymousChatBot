from datetime import date, timedelta


def get_times() -> tuple[date]:
    """
    Get start of the day, start of the day week ago, start of the day month ago

    :return tuple[date]: Tuple of date objects
    """

    today = date.today()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=30)

    return today, week_ago, month_ago
