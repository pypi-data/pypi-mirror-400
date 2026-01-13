from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Iterable

from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.iar.data_grid.zemod_data_grid import ZeModDataGrid
from scanner3d.zemod.iar.data_grid_rgb.zemod_data_grid_rgb import ZeModDataGridRgb
from scanner3d.analysis.zernike_data import ZernikeData
from scanner3d.analysis.zernike_meta import ZernikeMeta

if TYPE_CHECKING:
    from scanner3d.zemod.iar.data_grid.i_data_grid import IDataGrid
    from scanner3d.afs.i_shot_result import IShotResult
    from zempy.zosapi.analysis.iar.protocols.iar_ import IAR_
    from zempy.zosapi.analysis.data.protocols.iar_data_grid import IAR_DataGrid
    from zempy.zosapi.analysis.data.protocols.iar_data_grid_rgb import IAR_DataGridRgb
    from zempy.zosapi.analysis.data.protocols.iar_data_series import IAR_DataSeries
    from zempy.zosapi.analysis.data.protocols.iar_data_series_rgb import IAR_DataSeriesRgb
    from zempy.zosapi.analysis.data.protocols.iar_data_scatter_points import IAR_DataScatterPoints
    from zempy.zosapi.analysis.data.protocols.iar_data_scatter_points_rgb import IAR_DataScatterPointsRgb
    from zempy.zosapi.analysis.data.protocols.iar_ray_data import IAR_RayData
    from zempy.zosapi.analysis.data.protocols.iar_path_analysis_data import IAR_PathAnalysisData
    from zempy.zosapi.analysis.data.protocols.iar_spot_data_result_matrix import IAR_SpotDataResultMatrix
    from zempy.zosapi.analysis.data.protocols.iar_nsc_single_ray_trace_data import IAR_NSCSingleRayTraceData
    from zempy.zosapi.analysis.data.protocols.iar_critical_ray_data import IAR_CriticalRayData
    from zempy.zosapi.analysis.data.protocols.iar_header_data import IAR_HeaderData
    from zempy.zosapi.analysis.data.protocols.iar_meta_data import IAR_MetaData
    from zempy.zosapi.analysis.protocols.i_message import IMessage



class ZeModIAR(NativeAdapter["IAR_"]):
    """
    High-level wrapper around ZOSAPI.Analysis.Data.IAR_.

    Exposes:
      - Scalar metadata (description, date, lens file)
      - Data grids (wrapped as ZeModDataGrid)
      - RGB grids, series, scatter points, rays, spot/path/NSC data, messages (native protocols)
    """
    __slots__ = ()

    @property
    def metadata(self) -> IAR_MetaData:
        return self.native.MetaData

    @property
    def header(self) -> IAR_HeaderData:
        return self.native.HeaderData

    @property
    def description(self) -> str:
        # convenience alias
        return self.native.MetaData.FeatureDescription

    @property
    def date_iso(self) -> str:
        return self.native.MetaData.DateISO

    @property
    def lens_file(self) -> str:
        return self.native.MetaData.LensFile

    def get_data_grid(self, index: int) -> IDataGrid:
        """Return a single data grid wrapped as ZeModDataGrid."""
        return ZeModDataGrid(self.native.GetDataGrid(index))

    def get_first_grid(self) -> IDataGrid:
        """Convenience: first grid as ZeModDataGrid."""
        return self.get_data_grid(0)

    @property
    def number_of_data_grids(self) -> int:
        return self.native.NumberOfDataGrids

    def iter_data_grids(self) -> Iterable[IDataGrid]:
        """Iterate over all grids as ZeModDataGrid wrappers."""
        for i in range(self.native.NumberOfDataGrids):
            yield self.get_data_grid(i)

    # If you ever want *raw* IAR_DataGrid objects:
    @property
    def data_grids_raw(self) -> Sequence[IAR_DataGrid]:
        return self.native.DataGrids

    def get_text_file(self) -> IShotResult[ZernikeMeta]:
        zernike_data = ZernikeData.from_result(self.native)
        return zernike_data

    def get_data_grid_rgb(self, index: int) -> IDataGrid:
        return ZeModDataGridRgb(self.native.GetDataGridRgb(index))

    @property
    def number_of_data_grids_rgb(self) -> int:
        return self.native.NumberOfDataGridsRgb

    @property
    def data_grids_rgb(self) -> Sequence[IAR_DataGridRgb]:
        return self.native.DataGridsRgb

    # ------------------------------------------------------------------
    # Data series
    # ------------------------------------------------------------------
    def get_data_series(self, index: int) -> IAR_DataSeries:
        return self.native.GetDataSeries(index)

    @property
    def number_of_data_series(self) -> int:
        return self.native.NumberOfDataSeries

    @property
    def data_series(self) -> Sequence[IAR_DataSeries]:
        return self.native.DataSeries

    def get_data_series_rgb(self, index: int) -> IAR_DataSeriesRgb:
        return self.native.GetDataSeriesRgb(index)

    @property
    def number_of_data_series_rgb(self) -> int:
        return self.native.NumberOfDataSeriesRgb

    @property
    def data_series_rgb(self) -> Sequence[IAR_DataSeriesRgb]:
        return self.native.DataSeriesRgb

    # ------------------------------------------------------------------
    # Scatter points
    # ------------------------------------------------------------------
    def get_data_scatter_points(self, index: int) -> IAR_DataScatterPoints:
        return self.native.GetDataScatterPoint(index)

    @property
    def number_of_data_scatter_points(self) -> int:
        return self.native.NumberOfDataScatterPoints

    @property
    def data_scatter_points(self) -> Sequence[IAR_DataScatterPoints]:
        return self.native.DataScatterPoints

    def get_data_scatter_points_rgb(self, index: int) -> IAR_DataScatterPointsRgb:
        return self.native.GetDataScatterPointRgb(index)

    @property
    def number_of_data_scatter_points_rgb(self) -> int:
        return self.native.NumberOfDataScatterPointsRgb

    @property
    def data_scatter_points_rgb(self) -> Sequence[IAR_DataScatterPointsRgb]:
        return self.native.DataScatterPointsRgb

    # ------------------------------------------------------------------
    # Ray data
    # ------------------------------------------------------------------
    def get_ray_data(self, index: int) -> IAR_RayData:
        return self.native.GetRayData(index)

    @property
    def number_of_ray_data(self) -> int:
        return self.native.NumberOfRayData

    @property
    def ray_data(self) -> Sequence[IAR_RayData]:
        return self.native.RayData

    @property
    def critical_ray_data(self) -> IAR_CriticalRayData:
        return self.native.CriticalRayData

    # ------------------------------------------------------------------
    # Path / spot / NSC
    # ------------------------------------------------------------------
    @property
    def path_analysis_data(self) -> IAR_PathAnalysisData:
        return self.native.PathAnalysisData

    @property
    def spot_data(self) -> IAR_SpotDataResultMatrix:
        return self.native.SpotData

    @property
    def nsc_single_ray_trace_data(self) -> IAR_NSCSingleRayTraceData:
        return self.native.NSCSingleRayTraceData

    # ------------------------------------------------------------------
    # Messages / text export
    # ------------------------------------------------------------------
    def get_message(self, index: int) -> IMessage:
        return self.native.GetMessageAt(index)

    @property
    def number_of_messages(self) -> int:
        return self.native.NumberOfMessages

    @property
    def messages(self) -> Sequence[IMessage]:
        return self.native.Messages


