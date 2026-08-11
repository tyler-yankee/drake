# This file contains data types used by the Linux-specific build logic. See
# //tools/wheel:builder for the user interface.

from dataclasses import dataclass
from enum import Enum


class PythonManager(Enum):
    _value_: str

    PIP = "pip"
    UV = "uv"


@dataclass
class Platform:
    name: str
    version: str
    alias: str
    python_version_tuple: tuple[int, ...]
    python_manager: PythonManager = PythonManager.PIP

    def __post_init__(self):
        pv_parts = tuple(map(str, self.python_version_tuple))
        self.python_version_full = ".".join(pv_parts)
        self.python_version = ".".join(pv_parts[:2])
        self.python_tag = "".join(pv_parts[:2])
