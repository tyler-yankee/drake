# This file contains data types used by the macOS-specific build logic. See
# //tools/wheel:builder for the user interface.

from dataclasses import dataclass


@dataclass
class Platform:
    python_version_tuple: tuple[int, int]

    def __post_init__(self):
        pv_parts = tuple(map(str, self.python_version_tuple))
        self.python_version = ".".join(pv_parts)
        self.python_tag = "".join(pv_parts)
