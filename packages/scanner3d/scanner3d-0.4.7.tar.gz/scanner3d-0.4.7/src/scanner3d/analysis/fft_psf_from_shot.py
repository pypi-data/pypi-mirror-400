from allytools.logger import get_logger
from allytools.units import Length, LengthUnit
from scanner3d.afs.shot import Shot
from gosti.fft_psf.fft_psf import FftPsf
from gosti.fft_psf.fft_psf_from_array import fft_psf_from_array
from scanner3d.zemod.iar.i_grid_meta import IGridMeta
from allytools.types import validate_cast

log = get_logger(__name__)
def fft_psf_from_shot(
        *,
        shot: Shot, wavelength: Length) -> FftPsf:
    meta:IGridMeta = validate_cast(shot.meta,IGridMeta)
    fft_psf = fft_psf_from_array(
        values=shot.raw_data,
        field_x=shot.field_x,
        field_y=shot.field_y,
        min_x=meta.min_x,
        min_y=meta.min_y,
        dx=meta.dx,
        dy=meta.dy,
        wavelength=wavelength)
    log.debug(" FFT PSF created from Shot: shape=%s",shot.shape)
    return fft_psf
