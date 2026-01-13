from __future__ import annotations
import logging
from allytools.units import Length, LengthUnit
from typing import Optional
from dataclasses import dataclass, field
from scanner3d.tuner.base_manager import BaseManager, _SENTINEL
from scanner3d.zemod.zemod_wavelengths import ZeModWavelengths

log = logging.getLogger(__name__)

@dataclass(slots=True)
class WavelengthManager(BaseManager):
    """
    Keeps Zemax model's primary wavelength (index=1) consistent with the camera wavelength (µm).
    Captures original state for revert() and logs all operations.
    """
    wavelengths: ZeModWavelengths
    _orig_w1: float | object = field(init=False, default=_SENTINEL, repr=False)

    def check_wavelength_n(self):
        n = self.wavelengths.n_wavelengths
        if n > 1:
            log.warning("system has %d wavelengths (>1); can lead to ambiguous results",n)

    def apply(self, *, primary_wavelength: Optional[Length]) -> None:

        self.check_wavelength_n()
        if primary_wavelength is not None:
            primary_wavelength_um = primary_wavelength.to(LengthUnit.UM) #TODO check system units
            def get_w1() -> float:
                return float(self.wavelengths.get_wavelength(1).value)
            def set_w1(v: float) -> None:
                self.wavelengths.get_wavelength(1).value = float(v)

            self.sync_setting(  # public alias to _sync_setting for consistency
                label="primary wavelength (µm)",
                get=get_w1,
                set_=set_w1,
                target=primary_wavelength_um,
                orig_attr="_orig_w1",
            )


    def _revert_specs(self):
        def get_w1() -> float:
            return float(self.wavelengths.get_wavelength(1).value)

        def set_w1(v: float) -> None:
            self.wavelengths.get_wavelength(1).value = float(v)

        yield dict(
            label="primary wavelength (µm)",
            get=get_w1,
            set_=set_w1,
            orig_attr="_orig_w1",
        )

    def revert(self) -> None:
        did_anything = False
        for spec in self._revert_specs():
            changed = self._revert_setting(**spec)
            did_anything |= changed

        if not did_anything:
            log.debug("%s.revert: nothing to revert (no captured changes)", self.__class__.__name__)
