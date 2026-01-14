from __future__ import annotations

__all__ = ["NVR"]

import re
from collections.abc import Iterator

from collektions.preconditions import require
from typing_extensions import Any

from .parse import parse_nvr, parse_nvr_or_none

# Invalid characters for RPM package names
# Based on RPM spec and real-world usage constraints
INVALID_NAME_CHARS_DISPLAY = "< > = whitespace { } %"
_INVALID_NAME_PATTERN = re.compile(r"[<>=\s{}%]")


class NVR:
    """A class representing build/package name-version-release coordinates.

    This class supports iteration, allowing iterable unpacking behavior in
    assignment expressions, e.g.:

    ```python
    nvr = NVR.from_string("curl-7.76.1-26.el9")
    name, version, release = nvr
    print(f"{name=} {version=} {release=}")
    # name=curl version=7.76.1 release=26.el9
    ```
    """

    def __init__(self, *, name: str, version: str, release: str) -> None:
        # Validate package name
        require(len(name) > 0, "Package name cannot be empty")
        invalid_match = _INVALID_NAME_PATTERN.search(name)
        require(
            invalid_match is None,
            f"Package name '{name}' contains invalid character {invalid_match.group() if invalid_match else ''}. "
            f"Prohibited characters: {INVALID_NAME_CHARS_DISPLAY}",
        )
        require(len(version) > 0, "Version cannot be empty")
        require(len(release) > 0, "Release cannot be empty")

        self._name = name
        self._version = version
        self._release = release

    @classmethod
    def from_string(cls, nvr: str) -> NVR:
        return parse_nvr(nvr, cls)

    @classmethod
    def from_string_or_none(cls, nvr: str | None) -> NVR | None:
        return parse_nvr_or_none(nvr, cls)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NVR)
            and self._name == other.name
            and self._version == other.version
            and self._release == other.release
        )

    def __hash__(self) -> int:
        return hash((self._name, self._version, self._release))

    def __repr__(self) -> str:
        return f"NVR(name={self._name!r}, version={self._version!r}, release={self._release!r})"

    def __str__(self) -> str:
        return f"{self._name}-{self._version}-{self._release}"

    def __iter__(self) -> Iterator[str]:
        return iter((self._name, self._version, self._release))

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def release(self) -> str:
        return self._release

    def copy(self, **changes: Any) -> NVR:
        state = self.to_dict()
        state.update({k: v for k, v in changes.items() if k in state})
        return NVR(**state)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self._name, "version": self._version, "release": self._release}
