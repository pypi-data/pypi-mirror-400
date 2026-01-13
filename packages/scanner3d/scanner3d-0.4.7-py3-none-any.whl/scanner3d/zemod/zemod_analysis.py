from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.ias.zemod_ias import ZeModIAS
from scanner3d.zemod.iar.zemod_iar import ZeModIAR

if TYPE_CHECKING:
    from zempy.zosapi.analysis.protocols.ia_ import IA_
    from zempy.zosapi.analysis.ias.protocols.ias_ import IAS_
    from zempy.zosapi.analysis.iar.protocols.iar_ import IAR_


from zempy.zosapi.analysis.enums.analysis_idm import AnalysisIDM


class ZeModAnalysis(NativeAdapter["IA_"]):
    __slots__ = ("_settings", "analysis_idm", "_closed")

    def __init__(self, native: "IA_", analysis_idm: Optional[AnalysisIDM] = None) -> None:
        super().__init__(native)
        self.analysis_idm: Optional[AnalysisIDM] = analysis_idm
        self._settings: Optional[ZeModIAS] = None
        self._closed: bool = False

    def _native_settings(self):
        return self.native.GetSettings()

    def _native_run(self):
        return self.native.run()

    @property
    def settings(self) -> ZeModIAS:
        return ZeModIAS(self._native_settings())

    def run(self) -> ZeModIAR:
        return ZeModIAR(self._native_run())

    def close(self) -> None:
        if self._closed:
            return
        try:
            self.native.Close()
        finally:
            self._closed = True

    def __enter__(self) -> ZeModAnalysis:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __repr__(self) -> str:
        kind = self.analysis_idm.name if self.analysis_idm else "UNKNOWN"
        native_t = type(self.native).__name__
        return f"{self.__class__.__name__}(kind={kind}, closed={self._closed}, native={native_t})"

    __str__ = __repr__
