from __future__ import annotations
from scanner3d.test.base.analysis import Analysis
from scanner3d.test.base.batch_raytrace_test import BatchRayTraceTest
from scanner3d.test.base.analysis_settings import ANALYSES_REGISTER, AnalysisTypes
from scanner3d.test.base.tuner_settings import album_settings, matrix_settings
from scanner3d.ray_trace.raytrace_settings import normal_unpolarized_quick, normal_unpolarized_full
from scanner3d.test.base.optical_test import OpticalTest
from scanner3d.test.base.albums import (
    album_major_frame_5,
    album_major_frame_3,
    album_radial_detailed,
    album_radial_quick,
    album_sparse_grid_detailed,
    album_sparse_grid_quick)


fft_psf_quick = Analysis(
    test_name="FFT PSF Quick",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.FFT_PSF],
    tuner_settings=album_settings,
    albums_settings=[album_major_frame_3, album_radial_quick, album_sparse_grid_quick],
)

fft_psf = Analysis(
    test_name="FFT PSF",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.FFT_PSF],
    tuner_settings=album_settings,
    albums_settings=[album_major_frame_5, album_radial_detailed, album_sparse_grid_detailed],
)

fft_psf_4 = Analysis(
    test_name="FFT PSF 04",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.FFT_PSF_4],
    tuner_settings=album_settings,
    albums_settings=[album_radial_detailed],
)

huygens_psf_quick = Analysis(
    test_name="Huygens PSF Quick",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.HUYGENS_PSF],
    tuner_settings=album_settings,
    albums_settings=[album_major_frame_3, album_radial_quick, ],
)

huygens_psf = Analysis(
    test_name="Huygens PSF",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.HUYGENS_PSF],
    tuner_settings=album_settings,
    albums_settings=[album_radial_detailed],
)

zernike_quick = Analysis(
    test_name="Zernike Quick",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.ZERNIKE_STANDARD],
    tuner_settings=album_settings,
    albums_settings=[album_radial_quick,album_sparse_grid_quick],
)

zernike = Analysis(
    test_name="Zernike Standard",
    analysis_settings=ANALYSES_REGISTER[AnalysisTypes.ZERNIKE_STANDARD],
    tuner_settings=album_settings,
    albums_settings=[album_radial_detailed],
)
batch_raytrace_quick = BatchRayTraceTest(
    test_name="Batch ray trace quick",
    base_settings=normal_unpolarized_quick,
    tuner_settings=matrix_settings)

batch_raytrace = BatchRayTraceTest(
    test_name="Batch ray trace full",
    base_settings=normal_unpolarized_full,
    tuner_settings=matrix_settings)


ZERNIKE: list[OpticalTest] = [zernike_quick]
QUICK_TEST: list[OpticalTest] = [fft_psf_quick, batch_raytrace_quick, zernike_quick]
FULL_TEST: list[OpticalTest] = [fft_psf, batch_raytrace, zernike]
BATCH: list[OpticalTest] = [batch_raytrace_quick]
