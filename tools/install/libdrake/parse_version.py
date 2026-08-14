"""Parse the version stamp file and produce a CMake cache-style script file
which specifies the variable substitutions needed for drake-config.cmake."""

import argparse
from pathlib import Path
import re
import sys
import textwrap


class DrakeVersion:
    VERSION_TAG = "STABLE_VERSION"

    def __init__(self, stamp_file: Path, output_file: Path):
        self.stamp_file = stamp_file
        self.output_file = output_file
        self.version_full = None
        self.version_parts = None

    @staticmethod
    def _check_version(version: str) -> bool:
        """Check if our version string conforms to PEP 440."""
        return (
            re.match(
                r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)"
                r"(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?"
                r"(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?"
                r"([+][a-z0-9]+([-_\.][a-z0-9]+)*)?$",
                version,
            )
            is not None
        )

    def _parse_stamp(self) -> None:
        """
        Extract full version and version parts from version stamp file.

        If a version is specified, the input file should contain a line
        starting with 'STABLE_VERSION', which should be three space-separated
        words; the tag, the full version, and the git SHA.

        This extracts the (full) version identifier, as well as the individual
        numeric parts (separated by '.') of the version. Any pre-release,
        'dev', 'post', and/or local identifier (i.e. portion following a '+')
        is discarded when extracting the version parts. If version information
        is not found, self.version_* attributes remain `None`.
        """
        # Read input.
        stamp = self.stamp_file.read_text(encoding="utf-8")
        for line in stamp:
            if line.startswith(self.VERSION_TAG):
                tag, version_full, _git_sha = line.strip().split()
                assert tag == self.VERSION_TAG, tag

                # Check version format and extract numerical components.
                if not self._check_version(version_full):
                    raise ValueError(f"Version {version_full} is not valid")
                if re.match(r"^[1-9][0-9]*!", version_full):
                    raise ValueError(
                        f"Version {version_full} contains an epoch,"
                        " which is not supported at this time"
                    )

                m = re.match(r"^[0-9.]+", version_full)
                assert m, version_full

                # Check for sufficient version parts (note: user and continuous
                # builds may have more than three parts) and pad to ensure we
                # always have four.
                version_parts = m.group(0).split(".")
                if len(version_parts) < 4:
                    if len(version_parts) == 3:
                        version_parts.append(0)
                    else:
                        raise ValueError(
                            f"Version {version_full} does not have enough parts"
                        )

                self.version_full = version_full
                self.version_parts = tuple(map(int, version_parts))

    def _write_version_info(self) -> None:
        """Write version information to CMake cache-style script."""
        if self.version_full is None:
            # The full version is reported as "unknown", but the numeric
            # components are reported as 0 so that they remain usable as
            # integers, e.g. in the DRAKE_VERSION_* preprocessor macros in
            # drake/version.h.
            self.output_file.write_text(
                textwrap.dedent("""
                set(DRAKE_VERSION "unknown")
                set(DRAKE_VERSION_MAJOR "0")
                set(DRAKE_VERSION_MINOR "0")
                set(DRAKE_VERSION_PATCH "0")
                set(DRAKE_VERSION_TWEAK "0")
            """)
            )
        else:
            self.output_file.write_text(
                textwrap.dedent(f"""
                set(DRAKE_VERSION "{self.version_full}")
                set(DRAKE_VERSION_MAJOR "{self.version_parts[0]}")
                set(DRAKE_VERSION_MINOR "{self.version_parts[1]}")
                set(DRAKE_VERSION_PATCH "{self.version_parts[2]}")
                set(DRAKE_VERSION_TWEAK "{self.version_parts[3]}")
            """)
            )

    def parse_version(self) -> None:
        """Parse the version stamp file and write to output."""
        self._parse_stamp()
        self._write_version_info()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        type=Path,
        help="Path to file optionally containing stamp version.",
    )
    parser.add_argument("output", type=Path, help="Path to output file.")
    args = parser.parse_args(argv)

    version = DrakeVersion(args.input, args.output)
    version.parse_version()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
