from typing import Optional


def get_first_value_from_comma_separated_string(comma_separated_string: str) -> Optional[str]:
    if comma_separated_string:
        return comma_separated_string.split(sep=",")[0].strip()

    return None
