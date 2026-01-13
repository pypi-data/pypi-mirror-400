from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from functools import cached_property
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.systemdata.protocols.i_system_data import ISystemData
    from zempy.zosapi.systemdata.protocols.isd_title_notes import ISDTitleNotes

log = logging.getLogger(__name__)
class ZeModSD(NativeAdapter["ISystemData"]):

    @property
    def wavelengths_native(self):
        return self.native.Wavelengths

    @property
    def fields_native(self):
        return self.native.Fields

    @cached_property
    def wavelengths(self):
        from scanner3d.zemod.zemod_wavelengths import ZeModWavelengths
        return ZeModWavelengths(self.wavelengths_native)

    @cached_property
    def fields(self):
        from scanner3d.zemod.zemod_fields import ZeModFields
        return ZeModFields(self.fields_native)


    @property
    def title(self) -> str:
        return self.native.TitleNotes.Title

    @property
    def author(self) -> str:
        return self.native.TitleNotes.Author

    @property
    def notes(self) -> str:
        return self.native.TitleNotes.Notes