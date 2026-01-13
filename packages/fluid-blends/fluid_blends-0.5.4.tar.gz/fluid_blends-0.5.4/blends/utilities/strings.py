def split_on_last_dot(string: str) -> tuple[str, str]:
    portions = string.rsplit(".", maxsplit=1)
    expected_portions_after_split = 2
    if len(portions) == expected_portions_after_split:
        return portions[0], portions[1]
    return portions[0], ""
