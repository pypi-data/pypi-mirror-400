from __future__ import annotations
import logging
import numpy as np
from typing import TYPE_CHECKING
from numpy.typing import NDArray
from allytools.units import Length
from scanner3d.test.base.analysis_settings import AnalysisSettings
from scanner3d.afs.i_shot_result import IShotResult
from scanner3d.afs.i_shot_meta import IShotMeta
from scanner3d.zemod.iar.i_grid_meta import IGridMeta

if TYPE_CHECKING:
    from scanner3d.zemod.zemod_field import ZeModField
    from scanner3d.zemod.zemod_analysis import ZeModAnalysis

log = logging.getLogger(__name__)
class Shot:
    __slots__ = ("_result", "_field_x", "_field_y")

    def __init__(
        self,
        *,
        result: IShotResult[IShotMeta],
        field_x: Length,
        field_y: Length,
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Direct construction of Shot is not allowed. "
                "Use compute(...) to calculate it from Zemax, "
                "or from_components() to reconstruct it.")

        self._result = result
        self._field_x = field_x
        self._field_y = field_y

    @classmethod
    def from_components(
        cls,
        *,
        result: IShotResult[IShotMeta],
        field_x: Length,
        field_y: Length,
    ) -> Shot:
        return cls(
            result=result,
            field_x=field_x,
            field_y=field_y,
            _internal=True,
        )

    @classmethod
    def compute(
        cls,
        *,
        field: ZeModField,
        analysis: ZeModAnalysis,
        analysis_settings: AnalysisSettings,
        x: Length,
        y: Length,
    ) -> Shot:
        xf = float(x.value_mm)
        yf = float(y.value_mm)
        field.set_xy(xf, yf)
        result_native = analysis.run()
        if analysis_settings.result_factory is not None:
            shot_result: IShotResult[IShotMeta] = analysis_settings.get_result(result_native)
        else:
            raise Exception("no method defined for AnalysisSettings.result_factory")
        return cls(result=shot_result, field_x=x, field_y=y, _internal=True)

    @property
    def field_x(self) -> Length:
        return self._field_x

    @property
    def field_y(self) -> Length:
        return self._field_y

    @property
    def result(self) -> IShotResult[IShotMeta]:
        return self._result

    @property
    def meta(self) -> IShotMeta:
        return self._result.meta

    @property
    def raw_data(self) -> NDArray[np.float64]:
        return self._result.get_raw()

    @property
    def shape(self) -> tuple[int, ...]:
        return self._result.shape

    @property
    def min(self) -> float:
        try:
            return float(np.nanmin(self.raw_data))
        except ValueError:
            return float("nan")

    @property
    def max(self) -> float:
        try:
            return float(np.nanmax(self.raw_data))
        except ValueError:
            return float("nan")

    def plot(self, *args, **kwargs):

        if not isinstance(self.meta, IGridMeta):
            raise RuntimeError(
                "plot() is only available for grid results (IDataGrid). "
                "This Shot contains a non-grid result (e.g. Zernike)."
            )
        from scanner3d.afs.plotter import plot_shot
        return plot_shot(self, *args, **kwargs)

    def __str__(self) -> str:
        return (
            "📸Shot\n"
            "────────────────────────────\n"
            f"  field: x={self.field_x.value_mm:.2f} [mm], y={self.field_y.value_mm:.2f} [mm],\n"
            f"  shape={self.shape}, min={self.min:.4g}, max={self.max:.4g}\n")