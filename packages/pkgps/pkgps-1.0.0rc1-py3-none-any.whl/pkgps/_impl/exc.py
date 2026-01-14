from __future__ import annotations

from typing import NoReturn


class MalformedCoordinates(Exception):
    """Raised when a string representing coordinates cannot be parsed properly."""


def malformed_coordinates(
    offender: str, type_: str, initiating_exception: Exception | None = None
) -> NoReturn:
    raise MalformedCoordinates(
        f"Malformed {type_} {offender}"
    ) from initiating_exception
