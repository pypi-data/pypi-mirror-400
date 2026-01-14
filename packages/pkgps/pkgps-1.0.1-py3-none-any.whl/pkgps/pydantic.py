__all__ = [
    "NEVR",
    "NEVRA",
    "NVR",
    "NVRA",
]

try:
    import pydantic  # noqa: F401
except ImportError as cause:
    raise ImportError(
        "pydantic not found: to use the pydantic extensions please install with pkgps[pydantic]"
    ) from cause

from ._impl.pydantic import NEVR, NEVRA, NVR, NVRA
