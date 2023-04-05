from datetime import datetime, timedelta

def remove_none_properties(dict_data: dict) -> dict:
    to_filter = dict_data.copy()
    filtered = {key: value for key, value in to_filter.items() if value is not None}
    return filtered


def add_minutes(mins: int):
    return datetime.utcnow() + timedelta(minutes=mins)


def add_seconds(seconds: int):
    return datetime.utcnow() + timedelta(seconds=seconds)


def add_days(days: int):
    return datetime.utcnow() + timedelta(days=days)


def add_months(months: int):
    return datetime.utcnow() + timedelta(months=months)
