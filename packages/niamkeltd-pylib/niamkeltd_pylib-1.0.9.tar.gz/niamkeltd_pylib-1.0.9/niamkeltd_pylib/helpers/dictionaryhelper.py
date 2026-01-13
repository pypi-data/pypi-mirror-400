from typing import Dict

def safe_get(dictionary: Dict, keys: list[str], default=None):
    """Get a value from a dictionary which contains nested dictionaries."""

    for key in keys:

        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]

        else:
            return default

    return dictionary