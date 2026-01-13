from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.zemod_analysis import ZeModAnalysis
from zempy.zosapi.analysis.enums.analysis_idm import AnalysisIDM

if TYPE_CHECKING:
    from zempy.zosapi.analysis.protocols.i_analyses import IAnalyses
    from zempy.zosapi.analysis.protocols.ia_ import IA_

class ZeModAnalyses(NativeAdapter["IAnalyses"]):
    __slots__ = ("_active",)

    def __init__(self, native: "IAnalyses") -> None:
        super().__init__(native)
        self._active: list[ZeModAnalysis] = []

    @property
    def n_analyses(self) -> int:
        return int(self.native.NumberOfAnalyses)

    def _native_get(self, index_1based: int) -> "IA_":
        return self.native.Get_AnalysisAtIndex(index_1based)


    def new_analysis(self, analysis_idm: AnalysisIDM) -> ZeModAnalysis:
        native_analysis = self.native.New_Analysis(analysis_idm)
        a = ZeModAnalysis(native_analysis, analysis_idm=analysis_idm)
        self._active.append(a)
        return a


    def list_active(self) -> tuple[ZeModAnalysis, ...]:
        return tuple(self._active)

    def remove(self, a: ZeModAnalysis) -> None:
        try:
            self._active.remove(a)
        except ValueError:
            pass

    def close(self, a: ZeModAnalysis) -> None:
        a.close()
        self.remove(a)

    def close_all(self) -> None:
        """Close all analysis windows we created and forget the wrappers."""
        for a in list(self._active):
            try:
                a.close()
            finally:
                self.remove(a)

    def __len__(self) -> int:
        return self.n_analyses

    def __iter__(self) -> Iterator[IA_]:
        for i in range(1, self.n_analyses + 1):
            yield self._native_get(i)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(active={len(self._active)}, native={type(self.native).__name__})"

    __str__ = __repr__
