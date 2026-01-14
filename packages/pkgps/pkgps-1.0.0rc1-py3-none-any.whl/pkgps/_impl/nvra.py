from __future__ import annotations

__all__ = ["NVRA"]

from typing import Any

from collektions.preconditions import require

from .nvr import _INVALID_NAME_PATTERN, INVALID_NAME_CHARS_DISPLAY, NVR
from .parse import parse_nvra, parse_nvra_or_none


class NVRA:
    """A class representing build/package name-version-release.architecture coordinates.

    This class supports iteration, allowing iterable unpacking behavior in
    assignment expressions, e.g.:

    ```python
    nvra = NVRA.from_string("curl-7.76.1-26.el9.aarch64")
    name, version, release, arch = nvra
    print(f"{name=} {version=} {release=} {arch=}")
    # name=curl version=7.76.1 release=26.el9 arch=aarch64
    ```
    """

    def __init__(self, *, name: str, version: str, release: str, arch: str) -> None:
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
        self._arch = arch

    @classmethod
    def from_string(cls, nvra: str) -> NVRA:
        return parse_nvra(nvra, cls)

    @classmethod
    def from_string_or_none(cls, nvra: str | None) -> NVRA | None:
        return parse_nvra_or_none(nvra, cls)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NVRA)
            and self._name == other.name
            and self._version == other.version
            and self._release == other.release
            and self._arch == other.arch
        )

    def __hash__(self) -> int:
        return hash((self._name, self._version, self._release, self._arch))

    def __repr__(self) -> str:
        return f"NVRA(name={self._name!r}, version={self._version!r}, release={self._release!r}, arch={self._arch!r})"

    def __str__(self) -> str:
        return f"{self._name}-{self._version}-{self._release}.{self._arch}"

    def __iter__(self):
        return iter((self._name, self._version, self._release, self._arch))

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def release(self) -> str:
        return self._release

    @property
    def arch(self) -> str:
        return self._arch

    @property
    def architecture(self) -> str:
        """An alias of `arch` for those who prefer the long-form name."""
        return self._arch

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding architecture information."""
        return NVR(name=self._name, version=self._version, release=self._release)

    def copy(self, **changes: Any) -> NVRA:
        state = self.to_dict()
        state.update({k: v for k, v in changes.items() if k in state})
        return NVRA(**state)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "version": self._version,
            "release": self._release,
            "arch": self._arch,
        }
