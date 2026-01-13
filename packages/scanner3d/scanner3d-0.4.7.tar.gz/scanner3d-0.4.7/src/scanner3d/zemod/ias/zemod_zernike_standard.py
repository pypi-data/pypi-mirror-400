from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional, cast
from scanner3d.zemod.ias.zemod_ias import ZeModIAS, ZeModIASSettings
from scanner3d.zemod.enums.enums import ZeModSampleSizes

logger = logging.getLogger(__name__)
@dataclass(frozen=True, slots=True)
class ZeModZernikeStandardSettings(ZeModIASSettings):
    """High-level settings wrapper for Zernike Standard Coefficients IAS."""


    field_number: Optional[int] = None
    surface_number: Optional[int] = None
    wavelength_number: Optional[int] = None
    sample_size: Optional[ZeModSampleSizes] = None
    reference_obd_to_vertex: Optional[bool] = None
    sx: Optional[float] = None
    sy: Optional[float] = None
    sr: Optional[float] = None
    epsilon: Optional[float] = None
    maximum_number_of_terms: Optional[int] = None

    def apply_to(self, ias: ZeModIAS) -> None:
        """Apply stored settings to a concrete IAS_ZernikeStandardCoefficients instance."""
        native = ias.native

        # --- standard IAS selectors ---
        if self.field_number is not None:
            logger.debug(f"IAS: field_number = {self.field_number}")
            native.Field.SetFieldNumber(self.field_number)

        if self.wavelength_number is not None:
            logger.debug(f"IAS: wavelength_number = {self.wavelength_number}")
            native.Wavelength.SetWavelengthNumber(self.wavelength_number)

        if self.surface_number is not None:
            logger.debug(f"IAS: surface_number = {self.surface_number}")
            native.Surface.SetSurfaceNumber(self.surface_number)

        # --- Zernike Standard coefficients specific ---
        from zempy.zosapi.analysis.zernike_standard.protocols. \
            ias_zernike_standard_coefficients import (
                IAS_ZernikeStandardCoefficients,
            )

        native_zernike = cast(IAS_ZernikeStandardCoefficients, native)

        if self.sample_size is not None:
            logger.debug(f"IAS: sample_size = {self.sample_size.value}")
            native_zernike.SampleSize = self.sample_size.value

        if self.reference_obd_to_vertex is not None:
            logger.debug(
                "IAS: reference_obd_to_vertex = %s",
                self.reference_obd_to_vertex,
            )
            native_zernike.ReferenceOBDToVertex = bool(self.reference_obd_to_vertex)

        if self.sx is not None:
            logger.debug(f"IAS: sx = {self.sx}")
            native_zernike.Sx = float(self.sx)

        if self.sy is not None:
            logger.debug(f"IAS: sy = {self.sy}")
            native_zernike.Sy = float(self.sy)

        if self.sr is not None:
            logger.debug(f"IAS: sr = {self.sr}")
            native_zernike.Sr = float(self.sr)

        if self.epsilon is not None:
            logger.debug(f"IAS: epsilon = {self.epsilon}")
            native_zernike.Epsilon = float(self.epsilon)

        if self.maximum_number_of_terms is not None:
            logger.debug(
                "IAS: maximum_number_of_terms = %s",
                self.maximum_number_of_terms,
            )
            native_zernike.MaximumNumberOfTerms = int(self.maximum_number_of_terms)
