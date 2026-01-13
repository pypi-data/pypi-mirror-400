from __future__ import annotations
from typing import Protocol, TypeVar
import numpy as np
from numpy.typing import NDArray
from enum import Enum
from scanner3d.afs.i_shot_meta import IShotMeta

TMeta = TypeVar("TMeta", bound=IShotMeta)

class ShotResultType(str, Enum):
    GRID = "Data Grid"
    ZERNIKE = "Zernike"

class IShotResult(Protocol[TMeta]):
    """
    Generic payload for a Shot:
      - raw numeric array (1D, 2D, ...)
      - its shape
      - metadata object describing it
    """

    def get_raw(self) -> NDArray[np.float64]:
        """
        Return the underlying data as a float64 ndarray, suitable for
        generic consumers that don't care about the concrete type.
        """

        ...

    @property
    def meta(self) -> TMeta: ...

    @property
    def shape(self) -> tuple[int, ...]: ...

    @property
    def result_type(self) -> ShotResultType: ...
