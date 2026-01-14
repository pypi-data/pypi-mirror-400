from __future__ import annotations

__all__ = ["NVRA"]

from collections.abc import Mapping
from typing import Any

from pydantic import Field

from ..parse import parse_nvra, parse_nvra_or_none
from .ext import Frozen
from .nvr import NVR


class NVRA(Frozen):
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

    name: str = Field(pattern=r"^[^<>=\s{}%]+$")
    """Name. Must not contain: < > = whitespace { } %"""
    version: str = Field(min_length=1)
    """Version."""
    release: str = Field(min_length=1)
    """Release."""
    arch: str
    """Architecture."""

    @classmethod
    def from_string(cls, nvra: str) -> NVRA:
        return parse_nvra(nvra, cls)

    @classmethod
    def from_string_or_none(cls, nvra: str | None) -> NVRA | None:
        return parse_nvra_or_none(nvra, cls)

    def __str__(self) -> str:
        return f"{self.name}-{self.version}-{self.release}.{self.arch}"

    def __iter__(self):
        return iter((self.name, self.version, self.release, self.arch))

    @property
    def architecture(self) -> str:
        """An alias of `arch` for those who prefer the long-form name."""
        return self.arch

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding architecture information."""
        return NVR(name=self.name, version=self.version, release=self.release)

    def copy(self, **changes: Any) -> NVRA:
        return self.model_copy(update=changes)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(mode="python")
