from __future__ import annotations

__all__ = ["NEVRA"]

from attrs import asdict, evolve, field, frozen
from attrs.validators import ge, matches_re, min_len

from ..parse import parse_nevra, parse_nevra_or_none
from .nevr import NEVR
from .nvr import NVR
from .nvra import NVRA


@frozen(kw_only=True)
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
    arch: str
    """Architecture."""

    copy = evolve
    to_dict = asdict

    @classmethod
    def from_string(cls, nevra: str) -> NEVRA:
        return parse_nevra(nevra, cls)

    @classmethod
    def from_string_or_none(cls, nevra: str | None) -> NEVRA | None:
        return parse_nevra_or_none(nevra, cls)

    def __str__(self) -> str:
        epoch_string = f"{self.epoch}:" if self.epoch else ""
        return f"{self.name}-{epoch_string}{self.version}-{self.release}.{self.arch}"

    def __iter__(self):
        return iter((self.name, self.epoch, self.version, self.release, self.arch))

    @property
    def architecture(self) -> str:
        """An alias of `arch` for those who prefer the long-form name."""
        return self.arch

    def to_nvr(self) -> NVR:
        """Convert to NVR by discarding epoch and architecture information."""
        return NVR(name=self.name, version=self.version, release=self.release)

    def to_nevr(self) -> NEVR:
        """Convert to NEVR by discarding architecture information."""
        return NEVR(
            name=self.name, epoch=self.epoch, version=self.version, release=self.release
        )

    def to_nvra(self) -> NVRA:
        """Convert to NVRA by discarding epoch information."""
        return NVRA(
            name=self.name, version=self.version, release=self.release, arch=self.arch
        )
