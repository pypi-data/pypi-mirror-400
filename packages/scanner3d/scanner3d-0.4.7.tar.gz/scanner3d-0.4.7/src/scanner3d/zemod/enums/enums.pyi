from enum import Enum
from typing import Any


class ZeModFftPsfType(Enum):
    Linear: "ZeModFftPsfType"
    Log: "ZeModFftPsfType"
    Phase: "ZeModFftPsfType"
    Real: "ZeModFftPsfType"
    Imaginary: "ZeModFftPsfType"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModFieldNormalizationType(Enum):
    Radial: "ZeModFieldNormalizationType"
    Rectangular: "ZeModFieldNormalizationType"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModFieldTypes(Enum):
    Angle: "ZeModFieldTypes"
    ObjectHeight: "ZeModFieldTypes"
    ParaxialImageHeight: "ZeModFieldTypes"
    RealImageHeight: "ZeModFieldTypes"
    TheodoliteAngle: "ZeModFieldTypes"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModHuygensPsfType(Enum):
    Linear: "ZeModHuygensPsfType"
    Log_Minus_1: "ZeModHuygensPsfType"
    Log_Minus_2: "ZeModHuygensPsfType"
    Log_Minus_3: "ZeModHuygensPsfType"
    Log_Minus_4: "ZeModHuygensPsfType"
    Log_Minus_5: "ZeModHuygensPsfType"
    Real: "ZeModHuygensPsfType"
    Imaginary: "ZeModHuygensPsfType"
    Phase: "ZeModHuygensPsfType"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModHuygensShowAsTypes(Enum):
    Surface: "ZeModHuygensShowAsTypes"
    Contour: "ZeModHuygensShowAsTypes"
    GreyScale: "ZeModHuygensShowAsTypes"
    InverseGreyScale: "ZeModHuygensShowAsTypes"
    FalseColor: "ZeModHuygensShowAsTypes"
    InverseFalseColor: "ZeModHuygensShowAsTypes"
    TrueColor: "ZeModHuygensShowAsTypes"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModPsfRotation(Enum):
    CW0: "ZeModPsfRotation"
    CW90: "ZeModPsfRotation"
    CW180: "ZeModPsfRotation"
    CW270: "ZeModPsfRotation"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModPsfSampling(Enum):
    PsfS_32x32: "ZeModPsfSampling"
    PsfS_64x64: "ZeModPsfSampling"
    PsfS_128x128: "ZeModPsfSampling"
    PsfS_256x256: "ZeModPsfSampling"
    PsfS_512x512: "ZeModPsfSampling"
    PsfS_1024x1024: "ZeModPsfSampling"
    PsfS_2048x2048: "ZeModPsfSampling"
    PsfS_4096x4096: "ZeModPsfSampling"
    PsfS_8192x8192: "ZeModPsfSampling"
    PsfS_16384x16384: "ZeModPsfSampling"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModQuickFocusCriterion(Enum):
    SpotSizeRadial: "ZeModQuickFocusCriterion"
    SpotSizeXOnly: "ZeModQuickFocusCriterion"
    SpotSizeYOnly: "ZeModQuickFocusCriterion"
    RMSWavefront: "ZeModQuickFocusCriterion"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModRaysType(Enum):
    Real: "ZeModRaysType"
    Paraxial: "ZeModRaysType"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModRotations(Enum):
    Rotate_0: "ZeModRotations"
    Rotate_90: "ZeModRotations"
    Rotate_180: "ZeModRotations"
    Rotate_270: "ZeModRotations"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...


class ZeModSampleSizes(Enum):
    S_32x32: "ZeModSampleSizes"
    S_64x64: "ZeModSampleSizes"
    S_128x128: "ZeModSampleSizes"
    S_256x256: "ZeModSampleSizes"
    S_512x512: "ZeModSampleSizes"
    S_1024x1024: "ZeModSampleSizes"
    S_2048x2048: "ZeModSampleSizes"
    S_4096x4096: "ZeModSampleSizes"
    S_8192x8192: "ZeModSampleSizes"
    S_16384x16384: "ZeModSampleSizes"

    @property
    def value(self) -> Any: ...

    @property
    def native(self) -> Any: ...

    def __int__(self) -> int: ...

