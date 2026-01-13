from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, cast
import logging

from scanner3d.zemod.ias.zemod_ias import ZeModIAS, ZeModIASSettings
from scanner3d.zemod.enums.enums import ZeModPsfSampling, ZeModPsfRotation, ZeModFftPsfType

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ZeModFftPsfSettings(ZeModIASSettings):
    field_number: Optional[int] = None
    wavelength_number: Optional[int] = None
    surface_number: Optional[int] = None
    sample_size: Optional[ZeModPsfSampling] = None
    output_size: Optional[ZeModPsfSampling] = None
    rotation: Optional[ZeModPsfRotation] = None
    image_delta: Optional[float] = None
    use_polarization: Optional[bool] = None
    normalize: Optional[bool] = None
    psf_type: Optional[ZeModFftPsfType] = None

    def apply_to(self, ias: ZeModIAS) -> None:
        native = ias.native

        # --- standard IAS ---
        if self.field_number is not None:
            logger.debug(f"IAS: field_number = {self.field_number}")
            native.Field.SetFieldNumber(self.field_number)

        if self.wavelength_number is not None:
            logger.debug(f"IAS: wavelength_number = {self.wavelength_number}")
            native.Wavelength.SetWavelengthNumber(self.wavelength_number)

        if self.surface_number is not None:
            logger.debug(f"IAS: surface_number = {self.surface_number}")
            native.Surface.SetSurfaceNumber(self.surface_number)

        # --- FFT-PSF specific ---
        from zempy.zosapi.analysis.fftpsf.protocols.ias_fft_psf import IAS_FftPsf
        native_psf = cast(IAS_FftPsf, native)

        if self.sample_size is not None:
            logger.debug(f"IAS: sample_size = {self.sample_size.value}")
            native_psf.SampleSize = self.sample_size.value

        if self.output_size is not None:
            logger.debug(f"IAS: output_size = {self.output_size.value}")
            native_psf.OutputSize = self.output_size.value

        if self.rotation is not None:
            logger.debug(f"IAS: rotation = {self.rotation.value}")
            native_psf.Rotation = self.rotation.value

        if self.image_delta is not None:
            logger.debug(f"IAS: image_delta = {self.image_delta}")
            native_psf.ImageDelta = float(self.image_delta)

        if self.use_polarization is not None:
            logger.debug(f"IAS: use_polarization = {self.use_polarization}")
            native_psf.UsePolarization = bool(self.use_polarization)

        if self.normalize is not None:
            logger.debug(f"IAS: normalize = {self.normalize}")
            native_psf.Normalize = bool(self.normalize)

        if self.psf_type is not None:
            logger.debug(f"IAS: psf_type = {self.psf_type.value}")
            native_psf.Type = self.psf_type.value
