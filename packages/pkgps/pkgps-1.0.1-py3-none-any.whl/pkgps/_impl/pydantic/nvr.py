from __future__ import annotations

__all__ = ["NVR"]

from collections.abc import Mapping
from typing import Any

from pydantic import Field

from ..parse import parse_nvr, parse_nvr_or_none
from .ext import Frozen


class NVR(Frozen):
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

    name: str = Field(pattern=r"^[^<>=\s{}%]+$")
    """Name. Must not contain: < > = whitespace { } %"""
    version: str = Field(min_length=1)
    """Version."""
    release: str = Field(min_length=1)
    """Release."""

    @classmethod
    def from_string(cls, nvr: str) -> NVR:
        return parse_nvr(nvr, cls)

    @classmethod
    def from_string_or_none(cls, nvr: str | None) -> NVR | None:
        return parse_nvr_or_none(nvr, cls)

    def __str__(self) -> str:
        return f"{self.name}-{self.version}-{self.release}"

    def __iter__(self):
        return iter((self.name, self.version, self.release))

    def copy(self, **changes: Any) -> NVR:
        return self.model_copy(update=changes)

    def to_dict(self) -> Mapping[str, Any]:
        return self.model_dump(mode="python")
