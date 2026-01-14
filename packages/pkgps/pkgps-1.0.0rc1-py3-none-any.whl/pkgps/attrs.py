__all__ = [
    "NEVR",
    "NEVRA",
    "NVR",
    "NVRA",
]

try:
    import attrs  # noqa: F401
except ImportError as cause:
    raise ImportError(
        "attrs not found: to use the attrs extensions please install with pkgps[attrs]"
    ) from cause

from ._impl.attrs import NEVR, NEVRA, NVR, NVRA
