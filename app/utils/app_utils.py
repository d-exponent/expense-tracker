def remove_none_properties(dict_data: dict) -> dict:
    to_filter = dict_data.copy()
    filtered = {key: value for key, value in to_filter.items() if value is not None}
    return filtered
