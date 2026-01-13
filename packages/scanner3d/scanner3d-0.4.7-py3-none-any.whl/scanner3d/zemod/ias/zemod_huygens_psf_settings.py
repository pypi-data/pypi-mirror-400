from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional, cast
from scanner3d.zemod.ias.zemod_ias import ZeModIAS, ZeModIASSettings
from scanner3d.zemod.enums.enums import (
    ZeModSampleSizes,
    ZeModHuygensPsfType,
    ZeModHuygensShowAsTypes,
    ZeModRotations,
)

logger = logging.getLogger(__name__)
@dataclass(frozen=True, slots=True)
class ZeModHuygensPsfSettings(ZeModIASSettings):

    field_number: Optional[int] = None
    wavelength_number: Optional[int] = None
    pupil_sample_size: Optional[ZeModSampleSizes] = None
    image_sample_size: Optional[ZeModSampleSizes] = None
    huygens_type: Optional[ZeModHuygensPsfType] = None
    show_as_type: Optional[ZeModHuygensShowAsTypes] = None
    rotation: Optional[ZeModRotations] = None
    normalize: Optional[bool] = None
    use_centroid: Optional[bool] = None
    use_polarization: Optional[bool] = None
    image_delta: Optional[float] = None
    configuration: Optional[int] = None

    def apply_to(self, ias: ZeModIAS) -> None:
        native = ias.native

        if self.field_number is not None:
            logger.debug(f"IAS: field_number = {self.field_number}")
            native.Field.SetFieldNumber(self.field_number)

        if self.wavelength_number is not None:
            logger.debug(f"IAS: wavelength_number = {self.wavelength_number}")
            native.Wavelength.SetWavelengthNumber(self.wavelength_number)


        from zempy.zosapi.analysis.huygens_psf.protocols.ias_huygens_psf import IAS_HuygensPsf
        native_psf = cast(IAS_HuygensPsf, native)


        if self.pupil_sample_size is not None:
            logger.debug(f"IAS: pupil_sample_size = {self.pupil_sample_size.value}")
            native_psf.PupilSampleSize = self.pupil_sample_size.value

        if self.image_sample_size is not None:
            logger.debug(f"IAS: image_sample_size = {self.image_sample_size.value}")
            native_psf.ImageSampleSize = self.image_sample_size.value

        if self.huygens_type is not None:
            logger.debug(f"IAS: huygens_type = {self.huygens_type.value}")
            native_psf.Type = self.huygens_type.value

        if self.show_as_type is not None:
            logger.debug(f"IAS: show_as_type = {self.show_as_type.value}")
            native_psf.ShowAsType = self.show_as_type.value

        if self.rotation is not None:
            logger.debug(f"IAS: rotation = {self.rotation.value}")
            native_psf.Rotation = self.rotation.value

        if self.normalize is not None:
            logger.debug(f"IAS: normalize = {self.normalize}")
            native_psf.Normalize = bool(self.normalize)

        if self.use_centroid is not None:
            logger.debug(f"IAS: use_centroid = {self.use_centroid}")
            native_psf.UseCentroid = bool(self.use_centroid)

        if self.use_polarization is not None:
            logger.debug(f"IAS: use_polarization = {self.use_polarization}")
            native_psf.UsePolarization = bool(self.use_polarization)

        if self.image_delta is not None:
            logger.debug(f"IAS: image_delta = {self.image_delta}")
            native_psf.ImageDelta = float(self.image_delta)

        if self.configuration is not None:
            logger.debug(f"IAS: configuration = {self.configuration}")
            native_psf.Configuration = int(self.configuration)
