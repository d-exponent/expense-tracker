def remove_none_props_from_dict_recursive(dict_data: dict) -> dict:
    to_modify = dict_data.copy()
    modified_dict = {}

    for key, value in to_modify.items():
        if value is not None:
            if isinstance(value, dict):
                modified_dict[key] = remove_none_props_from_dict_recursive(value)
            else:
                modified_dict[key] = value

    return modified_dict
