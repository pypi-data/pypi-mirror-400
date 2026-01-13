from scanner3d.zemod.ias.zemod_zernike_standard import ZeModZernikeStandardSettings
from scanner3d.zemod.enums.enums import (
    ZeModSampleSizes,
    ZeModHuygensPsfType,
    ZeModHuygensShowAsTypes,
    ZeModRotations,
)

zernike_standard_37 = ZeModZernikeStandardSettings(
    field_number=1,
    wavelength_number=1,
    surface_number=5,
    sample_size=ZeModSampleSizes.S_128x128,
    reference_obd_to_vertex=False,
    sx=0,
    sy=0,
    sr=0,
    maximum_number_of_terms=37)
