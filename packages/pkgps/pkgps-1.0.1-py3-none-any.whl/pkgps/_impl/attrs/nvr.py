from __future__ import annotations

__all__ = ["NVR"]


from attrs import asdict, evolve, field, frozen
from attrs.validators import matches_re, min_len

from ..parse import parse_nvr, parse_nvr_or_none


@frozen(kw_only=True)
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

    name: str = field(
        validator=matches_re(
            r"^[^<>=\s{}%]+$",
        )
    )
    """Name. Must not contain: < > = whitespace { } %"""
    version: str = field(validator=min_len(1))
    """Version."""
    release: str = field(validator=min_len(1))
    """Release."""

    copy = evolve
    to_dict = asdict

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
