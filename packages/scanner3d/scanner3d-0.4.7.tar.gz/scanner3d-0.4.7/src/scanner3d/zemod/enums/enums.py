from zempy.zosapi.systemdata.enums.field_type import FieldType
from zempy.zosapi.tools.raytrace.enums.rays_type import RaysType
from zempy.zosapi.systemdata.enums.field_normalization_type import FieldNormalizationType
from zempy.zosapi.analysis.fftpsf.enums.fft_psf_type import FftPsfType
from zempy.zosapi.analysis.fftpsf.enums.psf_sampling import PsfSampling
from zempy.zosapi.analysis.fftpsf.enums.psf_rotation import PsfRotation
from zempy.zosapi.analysis.enums.sample_sizes import SampleSizes
from zempy.zosapi.analysis.ias.enums.huygens_psf_types import HuygensPsfTypes
from zempy.zosapi.analysis.enums.huygens_show_as_types import HuygensShowAsTypes
from zempy.zosapi.analysis.ias.enums.rotations import Rotations
from zempy.zosapi.tools.general.enums.quick_focus_criterion import QuickFocusCriterion

from enum import Enum
from typing import Type

def clone_enum(name: str, native_enum: Type[Enum]) -> Type[Enum]:
    """
    Create a bridge Enum whose members mirror the native enum.
    Each member's value *is* the native enum member.
    """
    # Build mapping: {"Name": native_enum.Name}
    mapping = {member.name: member for member in native_enum}

    # Create enum dynamically
    cls = Enum(name, mapping)

    # Attach helpers
    @property
    def native(self):
        return self.value

    def __int__(self):
        return int(self.value)

    setattr(cls, "native", native)
    setattr(cls, "__int__", __int__)

    return cls

ZeModFieldTypes = clone_enum("ZeModFieldTypes", FieldType) # type: ignore[assignment]
ZeModRaysType    = clone_enum("ZeModRaysType", RaysType) # type: ignore[assignment]
ZeModFieldNormalizationType = clone_enum("ZeModFieldNormalizationType", FieldNormalizationType) # type: ignore[assignment]
ZeModPsfRotation = clone_enum("ZeModFieldPsfRotation", PsfRotation) # type: ignore[assignment]
ZeModPsfSampling = clone_enum("ZeModPsfSampling", PsfSampling) # type: ignore[assignment]
ZeModFftPsfType = clone_enum("ZeModFftPsfType", FftPsfType)  # type: ignore[assignment]
ZeModSampleSizes = clone_enum("ZeModSampleSizes", SampleSizes) # type: ignore[assignment]
ZeModHuygensPsfType = clone_enum("ZeModHuygensPsfType", HuygensPsfTypes) # type: ignore[assignment]
ZeModHuygensShowAsTypes= clone_enum("ZeModHuygensShowAsTypes", HuygensShowAsTypes) # type: ignore[assignment]
ZeModRotations = clone_enum("ZeModRotations", Rotations) # type: ignore[assignment]
ZeModQuickFocusCriterion = clone_enum("ZeModQuickFocusCriterion", QuickFocusCriterion) # type: ignore[assignment]
