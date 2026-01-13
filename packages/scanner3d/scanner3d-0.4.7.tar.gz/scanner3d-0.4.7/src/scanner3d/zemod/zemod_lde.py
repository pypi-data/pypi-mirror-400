from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Iterator
from scanner3d.zemod.core.indexed_collection import IndexedCollection
from scanner3d.zemod.zemod_row   import ZeModRow

if TYPE_CHECKING:
    from zempy.zosapi.editors.lde.protocols.i_lens_data_editor import ILensDataEditor
    from zempy.zosapi.editors.lde.protocols.ilde_row import ILDERow

log = logging.getLogger(__name__)


def get_row_comment(row: ZeModRow) -> str:
    return row.comment


def set_thickness(row: ZeModRow, thickness: float) -> None:
    row.thickness = thickness


class ZeModLDE(IndexedCollection[ZeModRow, "ILensDataEditor", "ILDERow"]):
    """
    Wrapper for the Lens Data Editor (LDE).

    Indexing follows Zemax convention:
      - First surface index = 0 (object surface)
      - Last surface index  = n_surfaces - 1
    """

    # ---- Native bridge ----
    def _native_count(self) -> int:
        return int(self.native.NumberOfSurfaces)

    def _native_get(self, index: int) -> "ILDERow":
        # Zemax is 0-based → no index shift
        return self.native.GetSurfaceAt(index)

    def _native_add(self) -> "ILDERow":
        return self.native.AddSurface()

    def _native_delete_at(self, index:int) -> None:
        self.native.RemoveSurfaceAt(index)

    def _child_from_native(self, native_child: "ILDERow") -> ZeModRow:
        return ZeModRow(native_child)

    # ---- Public API ----
    @property
    def n_surfaces(self) -> int:
        """Total number of surfaces (last index + 1)."""
        return self.count

    def _check_index(self, index: int) -> None:
        if not (0 <= index < self.n_surfaces):
            raise IndexError(f"surface index {index} out of range [0, {self.n_surfaces - 1}]")

    def get_surface_at(self, index: int) -> ZeModRow:
        self._check_index(index)
        return self._child_from_native(self._native_get(index))

    def get_first_surface(self) -> ZeModRow:
        """Return surface 0 (object surface)."""
        return self.get_surface_at(0)

    def get_last_surface(self) -> ZeModRow:
        """Return last surface (index n_surfaces - 1)."""
        return self.get_surface_at(self.n_surfaces - 1)

    def __len__(self) -> int:
        return self.n_surfaces

    def __iter__(self) -> Iterator[ZeModRow]:
        for i in range(self.n_surfaces):
            yield self.get_surface_at(i)
