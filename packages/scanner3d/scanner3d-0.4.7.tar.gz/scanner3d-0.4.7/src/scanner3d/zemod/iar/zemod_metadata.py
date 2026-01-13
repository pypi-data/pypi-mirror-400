from __future__ import annotations
from typing import TYPE_CHECKING, Optional, cast
from datetime import datetime, timedelta
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.analysis.data.protocols.iar_meta_data import IAR_MetaData


def _to_datetime(value) -> datetime:
    if value is None:
        raise ValueError("MetaData.Date is unexpectedly None")

    # COM/OLE automation date
    if hasattr(value, "ToOADate"):
        return datetime(1899, 12, 30) + timedelta(days=float(value.ToOADate()))

    if isinstance(value, datetime):
        return value

    raise TypeError(f"Unexpected Date type: {type(value)}")


class ZeModMetaData(NativeAdapter["IAR_MetaData"]):
    """
    ZeMod wrapper for IAR_MetaData.
    Follows the same style as ZeModDataGrid.
    """
    __slots__ = ()

    @property
    def feature_description(self) -> str:
        return cast(str, self.native.FeatureDescription)

    @property
    def lens_file(self) -> str:
        return cast(str, self.native.LensFile)

    @property
    def lens_title(self) -> str:
        return cast(str, self.native.LensTitle)

    @property
    def date(self) -> datetime:
        return _to_datetime(self.native.Date)

    @property
    def date_iso(self) -> Optional[str]:
        dt = self.native.Date
        return _to_datetime(dt).isoformat() if dt else None

    def __repr__(self) -> str:
        try:
            dt = self.date.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            dt = "None"

        return (
            f"ZeModMetaData("
            f"Feature='{self.feature_description}', "
            f"Lens='{self.lens_title}', "
            f"Date={dt})"
        )
