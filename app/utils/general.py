from datetime import datetime, timedelta


def to_bool_to_int(object: any):
    return int(bool(object))


def remove_none_props_from_dict_recursive(data: dict) -> dict:
    """
    Remove all properties from a dictionary with None values.\n
    Dictionary in embedded lists are also be processed recursively.

    Args:
        data (dict): The dictionary to be processed
    Returns:
        dict : A processed dictionary without None property values
    """
    assert isinstance(data, dict), "Data parameter must be a dict"

    data_copy = data.copy()
    dict_items = data_copy.items()
    filtered = {}

    if len(dict_items) == 0:
        return filtered

    for key, value in dict_items:
        # Filter out properties with None values
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


def title_case_words(string) -> str:
    """
    Returns a string where each word is a title case
    Args:
        string (str): The string to be proceesed
    Returns:
        string (str): String with each word title cased
    """
    assert isinstance(string, str), "title_case_words only accepts strings as argument"

    def title_case_word(chars: str):
        return chars.strip().title()

    words = string.split(" ")
    if len(words) == 1:
        return title_case_word(words[0])

    titled_words = [title_case_word(word) for word in words]
    return " ".join(titled_words)


def add_minutes(minutes: int = 5):
    """
    Returns the current datetime plus added minutes
    Args:
        minutes (int): The number of minutes to be added to the current datetime
    Returns:
        datetime (datetime): New datetime with added minutes
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


def get_user_full_name(user):
    """
    Concatenates a user's first_name and last_name
    """
    has_first_last_names = user.first_name and user.last_name
    assert has_first_last_names, "The user must have a first_name and a last_name"
    return f"{user.first_name} {user.last_name}"
