from typing import  Final
from scanner3d.scanner.scanner import Scanner
from scanner3d.camera3d import Camera3D, Camera3DTypes
from scanner3d.geo import Position, ZRange
from lensguild.objective import  ObjectivesDB
from isensor.sensors_db import SensorsDB
from allytools.units import Length, LengthUnit
from gosti.wavelength import Wavelength

Leo: Final[Scanner] = Scanner(
    name="Leo",
    cameras=(Camera3D(name="ReconCam0",
                      type=Camera3DTypes.Reconstruction,
                      objective=ObjectivesDB.NAVITAR_E3399_16_F5_6,
                      sensor=SensorsDB.SONY_IMX174,
                      position=Position(0, 0, 0, 0, 0, 0),
                      z_range=ZRange(z_min=Length(350.0),
                                     z_max=Length(1200.0),
                                     z_focus=Length(550.0)),
                      primary_wavelength=Wavelength(808)),
             ),
)
