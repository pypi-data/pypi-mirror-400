from __future__ import annotations

__all__ = ["NEVRA"]

from typing import Any

from collektions.preconditions import require

from .nevr import NEVR
from .nvr import _INVALID_NAME_PATTERN, INVALID_NAME_CHARS_DISPLAY, NVR
from .nvra import NVRA
from .parse import parse_nevra, parse_nevra_or_none


class NEVRA:
    """A class representing build/package name-epoch:version-release.architecture coordinates.

    This class supports iteration, allowing iterable unpacking behavior in
    assignment expressions, e.g.:

    ```python
    nevra = NEVRA.from_string("curl-1:7.76.1-26.el9.aarch64")
    name, epoch, version, release, arch = nevra
    print(f"{name=} {epoch=} {version=} {release=} {arch=}")
    # name=curl epoch=1 version=7.76.1 release=26.el9 arch=aarch64
    ```
    """

    def __init__(
        self, *, name: str, epoch: int = 0, version: str, release: str, arch: str
    ) -> None:
        # Validate package name
        require(len(name) > 0, "Package name cannot be empty")
        invalid_match = _INVALID_NAME_PATTERN.search(name)
        require(
            invalid_match is None,
            f"Package name '{name}' contains invalid character {invalid_match.group() if invalid_match else ''}. "
            f"Prohibited characters: {INVALID_NAME_CHARS_DISPLAY}",
        )
        require(epoch >= 0, "epoch must be a positive integer")
        require(len(version) > 0, "Version cannot be empty")
        require(len(release) > 0, "Release cannot be empty")

        self._name = name
        self._epoch = epoch
        self._version = version
        self._release = release
        self._arch = arch

    @classmethod
    def from_string(cls, nevra: str) -> NEVRA:
        return parse_nevra(nevra, cls)

    @classmethod
    def from_string_or_none(cls, nevra: str | None) -> NEVRA | None:
        return parse_nevra_or_none(nevra, cls)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NEVRA)
            and self._name == other.name
            and self._epoch == other.epoch
            and self._version == other.version
            and self._release == other.release
            and self._arch == other.arch
        )

    def __hash__(self) -> int:
        return hash((self._name, self._epoch, self._version, self._release, self._arch))

    def __repr__(self) -> str:
        return f"NEVRA(name={self._name!r}, epoch={self._epoch!r}, version={self._version!r}, release={self._release!r}, arch={self._arch!r})"

    def __str__(self) -> str:
        epoch_string = f"{self._epoch}:" if self._epoch else ""
        return (
            f"{self._name}-{epoch_string}{self._version}-{self._release}.{self._arch}"
        )

    def __iter__(self):
        return iter((self._name, self._epoch, self._version, self._release, self._arch))

    @property
    def name(self) -> str:
        return self._name

    @property
    def epoch(self) -> int:
        return self._epoch

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
        """Convert to NVR by discarding epoch and architecture information."""
        return NVR(name=self._name, version=self._version, release=self._release)

    def to_nevr(self) -> NEVR:
        """Convert to NEVR by discarding architecture information."""
        return NEVR(
            name=self._name,
            epoch=self._epoch,
            version=self._version,
            release=self._release,
        )

    def to_nvra(self) -> NVRA:
        """Convert to NVRA by discarding epoch information."""
        return NVRA(
            name=self._name,
            version=self._version,
            release=self._release,
            arch=self._arch,
        )

    def copy(self, **changes: Any) -> NEVRA:
        state = self.to_dict()
        state.update({k: v for k, v in changes.items() if k in state})
        return NEVRA(**state)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "epoch": self._epoch,
            "version": self._version,
            "release": self._release,
            "arch": self._arch,
        }
