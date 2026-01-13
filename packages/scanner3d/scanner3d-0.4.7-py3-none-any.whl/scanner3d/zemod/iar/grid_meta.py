from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from allytools.units import  Length, LengthUnit
from scanner3d.zemod.iar.i_grid_meta import IGridMeta

if TYPE_CHECKING:
    from zempy.zosapi.analysis.data.protocols.iar_data_grid import IAR_DataGrid
    from scanner3d.zemod.iar.data_grid.data_grid import DataGrid


@dataclass(slots=True)
class GridMeta(IGridMeta):
    _min_x: Length
    _min_y: Length
    _dx: Length
    _dy: Length
    _description: str = ""
    _x_label: str = ""
    _y_label: str = ""
    _value_label: str = ""

    @property
    def min_x(self) -> Length:
        return self._min_x

    @property
    def min_y(self) -> Length:
        return self._min_y

    @property
    def dx(self) -> Length:
        return self._dx

    @property
    def dy(self) -> Length:
        return self._dy

    @property
    def description(self) -> str:
        return self._description

    @property
    def x_label(self) -> str:
        return self._x_label

    @property
    def y_label(self) -> str:
        return self._y_label

    @property
    def value_label(self) -> str:
        return self._value_label

    # --- constructors / factories ---

    @classmethod
    def from_zempy(cls, dg: "IAR_DataGrid") -> "GridMeta":
        """
        Extract GridMeta from any zempy IAR_* object that exposes
        MinX, MinY, Dx, Dy, Description, XLabel, YLabel, ValueLabel.
        """

        def safe_str(obj, name: str) -> str:
            return str(getattr(obj, name, ""))

        def safe_float(obj, name: str) -> float:
            return float(getattr(obj, name, 0.0))

        return cls(
            _min_x      =   Length(safe_float(dg, "MinX"), LengthUnit.UM),
            _min_y      =   Length(safe_float(dg, "MinY"), LengthUnit.UM),
            _dx         =   Length(safe_float(dg, "Dx"), LengthUnit.UM),
            _dy         =   Length(safe_float(dg, "Dy"),LengthUnit.UM),
            _description=   safe_str(dg, "Description"),
            _x_label    =   safe_str(dg, "XLabel"),
            _y_label    =   safe_str(dg, "YLabel"),
            _value_label=   safe_str(dg, "ValueLabel"))

    @classmethod
    def from_grid(cls, grid: "DataGrid") -> "GridMeta":
        """Build metadata snapshot from any IDataGrid implementation."""
        return cls(
            _min_x=grid.min_x,
            _min_y=grid.min_y,
            _dx=grid.dx,
            _dy=grid.dy,
            _description=getattr(grid, "description", ""),
            _x_label=getattr(grid, "x_label", ""),
            _y_label=getattr(grid, "y_label", ""),
            _value_label=getattr(grid, "value_label", ""),
        )
