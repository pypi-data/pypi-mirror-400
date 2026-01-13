from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict
from contextlib import AbstractContextManager
from scanner3d.afs.i_shot_result import IShotResult
from scanner3d.afs.i_shot_meta import IShotMeta
from scanner3d.zemod.ias.zemod_ias import ZeModIASSettings
from scanner3d.zemod.zemod_analysis import ZeModAnalysis
from scanner3d.zemod.zemod import ZeMod
from scanner3d.zemod.iar.zemod_iar import ZeModIAR
from scanner3d.test.settings.fft_psf import fft_psf_delta_0, fft_psf_delta_04
from scanner3d.test.settings.huygens_psf import huygens_psf_settings
from scanner3d.test.settings.zernike_standard import zernike_standard_37

class AnalysisTypes(Enum):
    FFT_PSF = auto()
    FFT_PSF_4 = auto()
    HUYGENS_PSF = auto()
    ZERNIKE_STANDARD = auto()


@dataclass
class AnalysisSettings:
    analysis_factory: Callable[[ZeMod], AbstractContextManager[ZeModAnalysis]]
    settings: ZeModIASSettings
    result_factory: Callable[[ZeModIAR], IShotResult[IShotMeta]]

    def get_analysis(self, zemod: ZeMod) -> AbstractContextManager[ZeModAnalysis]:
        return self.analysis_factory(zemod)

    def get_result(self, r: ZeModIAR) -> IShotResult[IShotMeta]:
        return self.result_factory(r)


ANALYSES_REGISTER: Dict[AnalysisTypes, AnalysisSettings] = {
    AnalysisTypes.FFT_PSF: AnalysisSettings(
        analysis_factory=lambda z: z.get_fftpsf(),
        settings=fft_psf_delta_0,
        result_factory=lambda r: r.get_data_grid(0),
    ),
    AnalysisTypes.FFT_PSF_4: AnalysisSettings(
        analysis_factory=lambda z: z.get_fftpsf(),
        settings=fft_psf_delta_04,
        result_factory=lambda r: r.get_data_grid(0),
    ),
    AnalysisTypes.HUYGENS_PSF: AnalysisSettings(
        analysis_factory=lambda z: z.get_huygens_psf(),
        settings=huygens_psf_settings,
        result_factory=lambda r: r.get_data_grid(0),
    ),
    AnalysisTypes.ZERNIKE_STANDARD: AnalysisSettings(
        analysis_factory=lambda z: z.get_zernike_standard_coefficients(),
        settings=zernike_standard_37,
        result_factory=lambda r: r.get_text_file(),
    ),
}
