from datetime import datetime, timedelta


def remove_none_props_from_dict_recursive(data: dict) -> dict:
    assert isinstance(data, dict), "Data parameter must be a dict"

    data_copy = data.copy()
    filtered = {}

    for key, value in data_copy.items():
        # Filter out feilds with None values
        if value is not None:
            if isinstance(value, dict):
                filtered[key] = remove_none_props_from_dict_recursive(value)
            elif isinstance(value, list):
                new_list = []

                for i in value:
                    if isinstance(i, dict):  # Handle dicts in lists
                        new_list.append(remove_none_props_from_dict_recursive(i))
                    else:
                        new_list.append(i)
                filtered[key] = new_list
            else:
                filtered[key] = value

    return filtered


def strip_and_title(str: str):
    return str.strip().title()


def to_title_case(str) -> str:
    assert isinstance(str, str), "to_title_case only accepts strings as argument"

    words = str.split(" ")

    if len(words) == 1:
        return strip_and_title(words[0])

    titled_words = [strip_and_title(word) for word in words]
    return " ".join(titled_words)


class AddTIme:
    utc_date_now = datetime.utcnow()

    @classmethod
    def add_minutes(cls, mins: int):
        return cls.utc_date_now + timedelta(minutes=mins)

    @classmethod
    def add_seconds(cls, seconds: int):
        return cls.utc_date_now + timedelta(seconds=seconds)

    @classmethod
    def add_days(cls, days: int):
        return cls.utc_date_now + timedelta(days=days)

    @classmethod
    def add_months(cls, months: int):
        return cls.utc_date_now + timedelta(months=months)
