from typing import Any


def is_list_of_str(thing: Any):
    if not isinstance(thing, list):
        return False

    for item in thing:
        if not isinstance(item, str):
            return False

    return True
