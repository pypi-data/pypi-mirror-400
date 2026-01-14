from __future__ import annotations

__all__ = ["NEVR"]

from typing import Any

from collektions.preconditions import require

from .nvr import _INVALID_NAME_PATTERN, INVALID_NAME_CHARS_DISPLAY, NVR
from .parse import parse_nevr, parse_nevr_or_none


class NEVR:
    """A class representing build/package name-epoch:version-release coordinates.

    This class supports iteration, allowing iterable unpacking behavior in
    assignment expressions, e.g.:

    ```python
    nevr = NEVR.from_string("curl-1:7.76.1-26.el9")
    name, epoch, version, release = nevr
    print(f"{name=} {epoch=} {version=} {release=}")
    # name=curl epoch=1 version=7.76.1 release=26.el9
    ```
    """

    def __init__(
        self, *, name: str, epoch: int = 0, version: str, release: str
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

    @classmethod
    def from_string(cls, nevr: str) -> NEVR:
        return parse_nevr(nevr, cls)

    @classmethod
    def from_string_or_none(cls, nevr: str | None) -> NEVR | None:
        return parse_nevr_or_none(nevr, cls)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, NEVR)
            and self._name == other.name
            and self._epoch == other.epoch
            and self._version == other.version
            and self._release == other.release
        )

    def __hash__(self) -> int:
        return hash((self._name, self._epoch, self._version, self._release))

    def __repr__(self) -> str:
        return f"NEVR(name={self._name!r}, epoch={self._epoch!r}, version={self._version!r}, release={self._release!r})"

    def __str__(self) -> str:
        epoch_string = f"{self._epoch}:" if self._epoch else ""
        return f"{self._name}-{epoch_string}{self._version}-{self._release}"

    def __iter__(self):
        return iter((self._name, self._epoch, self._version, self._release))

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

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding epoch information."""
        return NVR(name=self._name, version=self._version, release=self._release)

    def copy(self, **changes: Any) -> NEVR:
        state = self.to_dict()
        state.update({k: v for k, v in changes.items() if k in state})
        return NEVR(**state)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "epoch": self._epoch,
            "version": self._version,
            "release": self._release,
        }
