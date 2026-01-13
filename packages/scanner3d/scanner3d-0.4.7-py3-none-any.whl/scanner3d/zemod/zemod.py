from __future__ import annotations
import logging
from functools import cached_property
from typing import TYPE_CHECKING
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.zemod_analyses import ZeModAnalyses
from scanner3d.zemod.zemod_analysis import ZeModAnalysis
from scanner3d.zemod.zemod_sd import ZeModSD
from scanner3d.zemod.zemod_lde import ZeModLDE
from scanner3d.zemod.tools.zemod_tools import ZeModTools

from zempy.zosapi.analysis.enums.analysis_idm import AnalysisIDM



if TYPE_CHECKING:
    from zempy.zosapi.system.protocols.i_optical_system import IOpticalSystem
    from zempy.zosapi.systemdata.protocols.isd_title_notes import ISDTitleNotes

log = logging.getLogger(__name__)
class ZeMod(NativeAdapter["IOpticalSystem"]):
    __slots__ = ()

    @property
    def tools(self) -> ZeModTools:
        return ZeModTools(self.native.Tools)

    @cached_property
    def analyses(self) -> ZeModAnalyses:
        return ZeModAnalyses(self.native.Analyses)

    @cached_property
    def sd(self) -> ZeModSD:
        return ZeModSD(self.native.SystemData)

    @cached_property
    def lde(self) -> ZeModLDE:
        return ZeModLDE(self.native.LDE)

    @classmethod
    def from_optical_system(cls, optical_system: "IOpticalSystem") -> "ZeMod":
        return cls(optical_system)

    #Sshort cut for tasks in recipe
    def get_fftpsf(self) -> ZeModAnalysis:
        return self.analyses.new_analysis(AnalysisIDM.FftPsf)

    def get_huygens_psf(self) -> ZeModAnalysis:
        return self.analyses.new_analysis(AnalysisIDM.HuygensPsf)

    def get_raytracer(self):
        return self.tools.get_batch_ray_tracer()

    def get_zernike_standard_coefficients(self) -> ZeModAnalysis:
        return self.analyses.new_analysis(AnalysisIDM.ZernikeStandardCoefficients)

    @property
    def file_name(self)->str:
        return self.native.SystemFile

    @property
    def system_name(self)->str:
        return self.native.SystemName