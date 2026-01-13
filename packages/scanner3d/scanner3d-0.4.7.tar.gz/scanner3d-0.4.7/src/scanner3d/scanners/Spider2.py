from typing import  Final
from scanner3d.scanner.scanner import Scanner
from scanner3d.camera3d import Camera3D, Camera3DTypes
from scanner3d.geo import Position, ZRange
from lensguild.objective import  ObjectivesDB
from isensor.sensors_db import SensorsDB
from allytools.units import Length
from gosti.wavelength import Wavelength


Spider2: Final[Scanner] = Scanner(
    name="Spider2",
    cameras=(Camera3D(name="ReconCam0",
                      type=Camera3DTypes.Reconstruction,
                      objective=ObjectivesDB.DSL935_F3_0_NIR,
                      sensor=SensorsDB.SONY_IMX547,
                      position=Position(0, 0, 0, 0, 0, 0),
                      z_range=ZRange(z_min=Length(200.0),
                                     z_max=Length(300.0),
                                     z_focus=Length(240.0)),
                      primary_wavelength=Wavelength(450)),
             ),
)