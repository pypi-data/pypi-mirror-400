from __future__ import annotations
from typing import Protocol


class IShotMeta(Protocol):
    """
    Marker/base protocol for all metadata types that can be attached
    to a Shot result (grid meta, Zernike meta, etc.).

    You can later add truly common fields/methods here if you find some.
    For now it's an empty Protocol, just to tie things together.
    """
    ...
