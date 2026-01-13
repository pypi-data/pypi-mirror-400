from scanner3d.zemod.ias.zemod_huygens_psf_settings import ZeModHuygensPsfSettings
from scanner3d.zemod.enums.enums import (
    ZeModSampleSizes,
    ZeModHuygensPsfType,
    ZeModHuygensShowAsTypes,
    ZeModRotations,
)

huygens_psf_settings = ZeModHuygensPsfSettings(
    field_number=1,
    wavelength_number=1,
    pupil_sample_size=ZeModSampleSizes.S_128x128,
    image_sample_size=ZeModSampleSizes.S_256x256,
    huygens_type=ZeModHuygensPsfType.Linear,
    show_as_type=ZeModHuygensShowAsTypes.FalseColor,
    rotation=ZeModRotations.Rotate_0,
    normalize=False,
    use_centroid=True,
    use_polarization=False,
    image_delta=0.2,
    configuration=1,
)
