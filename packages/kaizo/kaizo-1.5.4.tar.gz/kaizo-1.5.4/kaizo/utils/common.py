import re
from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


def extract_variable(entry: str) -> tuple[str | None, str | None, str]:
    matched = re.match(r"^(\w*)\.(?:(\w+)\.)?\{(\w*)\}$", entry)
    if matched is None:
        return None, None, entry

    return matched.groups()
