from __future__ import annotations

__all__ = ["NEVR"]

from attrs import asdict, evolve, field, frozen
from attrs.validators import ge, matches_re, min_len
from typing_extensions import Self

from ..parse import parse_nevr, parse_nevr_or_none
from .nvr import NVR


@frozen(kw_only=True)
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

    name: str = field(
        validator=matches_re(
            r"^[^<>=\s{}%]+$",
        )
    )
    """Name. Must not contain: < > = whitespace { } %"""
    epoch: int = field(default=0, validator=ge(0))
    """Epoch."""
    version: str = field(validator=min_len(1))
    """Version."""
    release: str = field(validator=min_len(1))
    """Release."""

    copy = evolve
    to_dict = asdict

    @classmethod
    def from_string(cls, nevr: str) -> Self:
        return parse_nevr(nevr, cls)

    @classmethod
    def from_string_or_none(cls, nevr: str | None) -> Self | None:
        return parse_nevr_or_none(nevr, cls)

    def __str__(self) -> str:
        epoch_string = f"{self.epoch}:" if self.epoch else ""
        return f"{self.name}-{epoch_string}{self.version}-{self.release}"

    def __iter__(self):
        return iter((self.name, self.epoch, self.version, self.release))

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding epoch information."""
        return NVR(name=self.name, version=self.version, release=self.release)
