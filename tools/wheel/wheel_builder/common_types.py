from dataclasses import dataclass
from enum import Enum

from .linux_types import Platform as LinuxPlatform
from .macos_types import Platform as MacPlatform


class PythonBinder(Enum):
    _value_: str

    NANOBIND = "nanobind"
    PYBIND11 = "pybind11"


class Role(Enum):
    _value_: str

    BUILD = "build"
    TEST = "test"


@dataclass
class Target:
    build_platform: LinuxPlatform | MacPlatform
    python_binder: PythonBinder
    test_platforms: tuple[LinuxPlatform | MacPlatform]

    def __post_init__(self):
        assert isinstance(self.test_platforms, tuple), self.test_platforms
        if isinstance(self.build_platform, LinuxPlatform):
            assert len(self.build_platform.python_version_tuple) == 3, (
                self.build_platform.python_version_tuple
            )
        else:
            assert len(self.build_platform.python_version_tuple) == 2, (
                self.build_platform.python_version_tuple
            )
        for test_platform in self.test_platforms:
            assert len(test_platform.python_version_tuple) == 2, (
                test_platform.python_version_tuple
            )

    def platform(
        self, role: Role, test_index: int | None = None
    ) -> LinuxPlatform | MacPlatform:
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
