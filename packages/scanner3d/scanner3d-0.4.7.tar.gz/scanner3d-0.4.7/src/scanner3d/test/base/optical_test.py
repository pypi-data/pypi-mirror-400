from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.tuner.tuner import Tuner
from scanner3d.test.base.tuner_settings import TunerSettings

@dataclass
class OpticalTest(ABC):
    test_name: str
    tuner_settings: TunerSettings
    test_folder: Optional[Path] = field(default=None, init=False)
    camera: Optional[Camera3D] = field(default=None, init=False)
    scanner_name: Optional[str] = field(default=None, init=False)
    elapsed: float = field(default=0.0, init=False)
    success: bool = field(default=False, init=False)

    def _prepare_output(self, root: Path):
        """Create output folder: root/name"""
        self.test_folder = root / self.test_name
        self.test_folder.mkdir(parents=True, exist_ok=True)

    def _prepare_context(self, *, tuner: Tuner, camera: Camera3D):
        """Store common runtime objects."""
        self.camera = camera
        self.scanner_name = tuner.scanner_ref.scanner_name

    @abstractmethod
    def run(
            self,
            *,
            zemod,
            camera: Camera3D,
            output_root: Path,
            tuner: Tuner) -> list[Tuple[str, bool]]:
        raise NotImplementedError
