from __future__ import annotations

__all__ = ["NEVR"]

from collections.abc import Mapping
from typing import Any

from pydantic import Field

from ..parse import parse_nevr, parse_nevr_or_none
from .ext import Frozen
from .nvr import NVR


class NEVR(Frozen):
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

    name: str = Field(pattern=r"^[^<>=\s{}%]+$")
    """Name. Must not contain: < > = whitespace { } %"""
    epoch: int = Field(default=0, ge=0)
    """Epoch."""
    version: str = Field(min_length=1)
    """Version."""
    release: str = Field(min_length=1)
    """Release."""

    @classmethod
    def from_string(cls, nevr: str) -> NEVR:
        return parse_nevr(nevr, cls)

    @classmethod
    def from_string_or_none(cls, nevr: str | None) -> NEVR | None:
        return parse_nevr_or_none(nevr, cls)

    def __str__(self) -> str:
        epoch_string = f"{self.epoch}:" if self.epoch else ""
        return f"{self.name}-{epoch_string}{self.version}-{self.release}"

    def __iter__(self):
        return iter((self.name, self.epoch, self.version, self.release))

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding epoch information."""
        return NVR(name=self.name, version=self.version, release=self.release)

    def copy(self, **changes: Any) -> NEVR:
        return self.model_copy(update=changes)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(mode="python")
