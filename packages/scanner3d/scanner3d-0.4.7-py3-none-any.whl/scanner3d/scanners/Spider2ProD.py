from typing import  Final
from scanner3d.scanner.scanner import Scanner
from scanner3d.camera3d import Camera3D, Camera3DTypes
from scanner3d.geo import Position, ZRange
from lensguild.objective import  ObjectivesDB
from isensor.sensors_db import SensorsDB
from allytools.units import Length
from gosti.wavelength import Wavelength


Spider2ProD: Final[Scanner] = Scanner(
    name="Spider2ProD",
    cameras=(Camera3D(name="ReconCam0",
                      type=Camera3DTypes.Reconstruction,
                      objective=ObjectivesDB.CIL052_F3_4_M12B_NIR,
                      sensor=SensorsDB.SONY_IMX547,
                      position=Position(0, 0, 0, 0, 0, 0),
                      z_range=ZRange(z_min=Length(190.0),
                                     z_max=Length(350.0),
                                     z_focus=Length(240.0)),
                      primary_wavelength=Wavelength(450)),
             ),
)