# This file contains data types used by the macOS-specific build logic. See
# //tools/wheel:builder for the user interface.

from dataclasses import dataclass

from .common import PythonBinder, Role


@dataclass
class Platform:
    python_version_tuple: tuple[int, int]

    def __post_init__(self):
        pv_parts = tuple(map(str, self.python_version_tuple))
        self.python_version = ".".join(pv_parts)
        self.python_tag = "".join(pv_parts)


@dataclass
class Target:
    build_platform: Platform
    python_binder: PythonBinder
    test_platforms: tuple[Platform]

    def __post_init__(self):
        assert isinstance(self.test_platforms, tuple)

    def platform(self, role: Role, test_index: int | None = None) -> Platform:
        """Returns the Platform for the given `role`. For the test role, the
        `test_index` into the `self.test_platforms` tuple is required. For the
        build role, the `test_index` must be None."""
        if role == Role.BUILD:
            assert test_index is None
            return self.build_platform
        if role == Role.TEST:
            assert test_index is not None
            return self.test_platforms[test_index]
        raise NotImplementedError(role)
