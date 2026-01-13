import logging
from contextlib import contextmanager
from typing import Optional, Tuple
from dataclasses import field,dataclass
from allytools.units import Length
from scanner3d.zemod.zemod_fields import ZeModFields
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.zemod.zemod import ZeMod
from scanner3d.zemod.zemod_lde import ZeModLDE
from scanner3d.zemod.zemod_wavelengths import ZeModWavelengths
from scanner3d.tuner.surface_manager import SurfaceManager
from scanner3d.tuner.field_manager import FieldManager
from scanner3d.tuner.wavelength_manager import WavelengthManager
from scanner3d.tuner.reverse_stack import RevertStack
from scanner3d.test.base.tuner_settings import TunerSettings, WavelengthCriteria, FocusDistanceCriteria
from scanner3d.tuner.profile import Profile
from scanner3d.scanner.scanner_ref import ScannerRef, create_scanner_ref
from isensor.sensor_positions import SensorPosition


log = logging.getLogger(__name__)
@dataclass(slots=True, kw_only=True)
class Tuner:
    zemod: ZeMod
    camera: Camera3D
    scanner_ref: ScannerRef | None = (None,)
    settings: TunerSettings = field(init=False)
    lde: ZeModLDE = field(init=False)
    fields: ZeModFields = field(init=False)
    wavelengths: ZeModWavelengths = field(init=False)
    fm: FieldManager | None = field(init=False, default=None)
    wm: WavelengthManager | None = field(init=False, default=None)
    sm: SurfaceManager | None = field(init=False, default=None)


    def __post_init__(self) -> None:
        self.lde = self.zemod.lde
        self.fields = self.zemod.sd.fields
        self.wavelengths = self.zemod.sd.wavelengths
        self.scanner_ref = create_scanner_ref(self.camera)
        log.debug("Tuner initialized")

    @contextmanager
    def tune(self, *, settings: TunerSettings):
        self.settings = settings
        self.fm = FieldManager(self.fields)
        self.wm = WavelengthManager(self.wavelengths)
        self.sm = SurfaceManager(self.zemod, self.lde)
        stack = RevertStack()
        with stack.session():
            stack.push(self.sm, self.wm, self.fm)
            self.fm.check_fields_n() #First ensure that only one field
            self.fm.ensure_field1_on_axis()
            self.wm.apply(primary_wavelength=self.get_wavelength())
            self.sm.apply(focus_distance=self.get_focus_distance())
            self.fm.apply(
                field_type=settings.field_type,
                normalization=settings.filed_normalization,
                test_field_number=settings.analysis_field_number,
                extra_field = self.get_extra_field(settings.extra_field_position))
            yield self

    def get_extra_field(
        self, field_position: Optional[SensorPosition]
    ) -> Optional[Tuple[float, float]]:
        if field_position is None:
            return None
        x_length, y_length = self.camera.sensor.grid.get_position(field_position)
        return x_length.value_mm, y_length.value_mm

    def get_focus_distance(self) -> Optional[Length]:
        if self.settings.focus_distance_criteria == FocusDistanceCriteria.BestFocus:
            return self.camera.z_range.z_focus
        if self.settings.focus_distance_criteria == FocusDistanceCriteria.AverageFocus:
            raise NotImplementedError("AverageFocus distance is not implemented yet")
        return None

    def get_wavelength(self) -> Optional[Length]:
        if self.settings.wavelength_criteria == WavelengthCriteria.Primary:
            return self.camera.primary_wavelength
        else:
            raise NotImplementedError("AverageFocus distance is not implemented yet")

    def get_profile(self) -> Profile:
        sd = self.zemod.sd
        wr = self.lde.get_surface_at(self.sm.wd_index)
        fr = self.lde.get_surface_at(self.sm.focus_index)
        return Profile(
            file=self.zemod.file_name,
            name=self.zemod.system_name,
            title=sd.title,
            author=sd.author,
            notes=sd.notes if sd.notes is not None else "",  # TODO do I need this?
            working_distance=wr.thickness,
            focusing_distance=fr.thickness,
            sensor_model=self.camera.sensor.sensor_model.model,
            objective_id=self.camera.objective.objectiveID.model,
            f_number=self.camera.objective.f_number
        )
