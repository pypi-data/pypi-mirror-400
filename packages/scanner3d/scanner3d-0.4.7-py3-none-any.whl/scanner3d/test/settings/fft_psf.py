from scanner3d.zemod.ias.zemode_fftpsf_settings import ZeModFftPsfSettings
from scanner3d.zemod.enums.enums import ZeModPsfRotation, ZeModFftPsfType, ZeModPsfSampling


fft_psf_delta_02 = ZeModFftPsfSettings(
    field_number=1,
    wavelength_number=1,
    surface_number=0,
    sample_size=ZeModPsfSampling.PsfS_128x128,
    output_size=ZeModPsfSampling.PsfS_256x256,
    rotation=ZeModPsfRotation.CW0,
    image_delta=0.2,
    use_polarization=False,
    normalize=False,
    psf_type=ZeModFftPsfType.Linear,
)

fft_psf_delta_04 = ZeModFftPsfSettings(
    field_number=1,
    wavelength_number=1,
    surface_number=0,
    sample_size=ZeModPsfSampling.PsfS_128x128,
    output_size=ZeModPsfSampling.PsfS_256x256,
    rotation=ZeModPsfRotation.CW0,
    image_delta=0.4,
    use_polarization=False,
    normalize=False,
    psf_type=ZeModFftPsfType.Linear,
)

fft_psf_delta_0 = ZeModFftPsfSettings(
    field_number=1,
    wavelength_number=1,
    surface_number=0,
    sample_size=ZeModPsfSampling.PsfS_128x128,
    output_size=ZeModPsfSampling.PsfS_256x256,
    rotation=ZeModPsfRotation.CW0,
    image_delta=0,
    use_polarization=False,
    normalize=False,
    psf_type=ZeModFftPsfType.Linear,
)