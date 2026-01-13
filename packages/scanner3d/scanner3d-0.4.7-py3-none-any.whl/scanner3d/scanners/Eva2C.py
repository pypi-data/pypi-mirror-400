from typing import  Final
from scanner3d.scanner.scanner import Scanner
from scanner3d.camera3d import Camera3D, Camera3DTypes
from scanner3d.geo import Position, ZRange
from lensguild.objective import  ObjectivesDB
from isensor.sensors_db import SensorsDB
from allytools.units import Length, LengthUnit
from gosti.wavelength import Wavelength


Eva2C: Final[Scanner] = Scanner(
    name="Eva2B",
    cameras=(Camera3D(name="ReconCam0",
                      type=Camera3DTypes.Reconstruction,
                      objective=ObjectivesDB.DSL934_F4_0_NIR,
                      sensor=SensorsDB.SONY_IMX900,
                      position=Position(0, 0, 0, 0, 0, 0),
                      z_range=ZRange(z_min=Length(350.0),
                                     z_max=Length(800.0),
                                     z_focus=Length(550.0)),
                      primary_wavelength=Wavelength(450)),
             ),
)