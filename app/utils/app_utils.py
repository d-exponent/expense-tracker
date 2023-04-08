from datetime import datetime, timedelta


def remove_none_props_from_dict_recursive(data: dict) -> dict:
    data_copy = data.copy()

    filtered = {}

    for key, value in data_copy.items():
        if value is not None:
            if isinstance(value, dict):
                filtered[key] = remove_none_props_from_dict_recursive(value)
            else:
                filtered[key] = value

    return filtered


def strip_and_title(str: str):
    return str.strip().title()


def to_title_case(str) -> str:
    words = str.split(" ")

    if len(words) == 1:
        return strip_and_title(words[0])

    titled_words = [strip_and_title(word) for word in words]
    return " ".join(titled_words)


def add_minutes(mins: int):
    return datetime.utcnow() + timedelta(minutes=mins)


def add_seconds(seconds: int):
    return datetime.utcnow() + timedelta(seconds=seconds)


def add_days(days: int):
    return datetime.utcnow() + timedelta(days=days)


def add_months(months: int):
    return datetime.utcnow() + timedelta(months=months)
