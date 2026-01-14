from __future__ import annotations

from typing import TypeVar

from .exc import MalformedCoordinates, malformed_coordinates

Class = TypeVar("Class")


def parse_nvr(nvr: str, cls: type[Class]) -> Class:
    try:
        n, v, r = nvr.rsplit("-", 2)
        # this is written in a really obtuse way to make mypy happy about
        # Class not having keyword arguments while respecting that implementations
        # of NVR all have keyword-arg-only constructors and same goes for the other
        # parsing functions
        kwargs = {"name": n, "version": v, "release": r}
        return cls(**kwargs)
    except ValueError as ve:
        malformed_coordinates(nvr, cls.__name__, initiating_exception=ve)


def parse_nvr_or_none(nvr: str | None, cls: type[Class]) -> Class | None:
    if nvr is None:
        return None
    try:
        return parse_nvr(nvr, cls)
    except MalformedCoordinates:
        return None


def parse_nvra(nvra: str, cls: type[Class]) -> Class:
    try:
        n, v, ra = nvra.rsplit("-", 2)
        r, a = ra.rsplit(".", 1)
        kwargs = {"name": n, "version": v, "release": r, "arch": a}
        return cls(**kwargs)
    except ValueError as ve:
        malformed_coordinates(nvra, cls.__name__, initiating_exception=ve)


def parse_nvra_or_none(nvra: str | None, cls: type[Class]) -> Class | None:
    if nvra is None:
        return None
    try:
        return parse_nvra(nvra, cls)
    except MalformedCoordinates:
        return None


def parse_nevr(nevr: str, cls: type[Class]) -> Class:
    try:
        n, ev, r = nevr.rsplit("-", 2)
        # technically try/except is not needed for splitting ev apart
        # because split here will result in at least a one-item list meaning
        # `rest` will be an empty list in the worst case
        # however the constructor does further validation, which should raise
        # MalformedCoordinates so everything is consolidated here
        *rest, v = ev.split(":", 1)
        e: int = int(rest[0]) if rest else 0
        kwargs = {
            "name": n,
            "epoch": e,
            "version": v,
            "release": r,
        }
        return cls(**kwargs)
    except ValueError as ve:
        malformed_coordinates(nevr, cls.__name__, initiating_exception=ve)


def parse_nevr_or_none(nevr: str | None, cls: type[Class]) -> Class | None:
    if nevr is None:
        return None
    try:
        return parse_nevr(nevr, cls)
    except MalformedCoordinates:
        return None


def parse_nevra(nevra: str, cls: type[Class]) -> Class:
    try:
        n, ev, ra = nevra.rsplit("-", 2)
        # technically try/except is not needed for splitting ev apart
        # because split here will result in at least a one-item list meaning
        # `rest` will be an empty list in the worst case
        # however the constructor does further validation, which should raise
        # MalformedCoordinates so everything is consolidated here
        *rest, v = ev.split(":", 1)
        r, a = ra.rsplit(".", 1)
        e: int = int(rest[0]) if rest else 0
        kwargs = {"name": n, "epoch": e, "version": v, "release": r, "arch": a}
        return cls(**kwargs)
    except ValueError as ve:
        malformed_coordinates(nevra, cls.__name__, initiating_exception=ve)


def parse_nevra_or_none(nevra: str | None, cls: type[Class]) -> Class | None:
    if nevra is None:
        return None
    try:
        return parse_nevra(nevra, cls)
    except MalformedCoordinates:
        return None
