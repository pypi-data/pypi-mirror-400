from __future__ import annotations
import time
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from scanner3d.tuner.tuner import Tuner
from scanner3d.test.base.optical_test import OpticalTest

if TYPE_CHECKING:
    from scanner3d.camera3d.camera3d import Camera3D
    from scanner3d.zemod.zemod import ZeMod

log = logging.getLogger(__name__)
@dataclass
class TestSuite:
    optical_tests: list[OpticalTest]
    tuner: Tuner | None = field(init=False, default=None)

    def names(self) -> list[str]:
        return [t.test_name for t in self.optical_tests]


    def __iter__(self):
        return iter(self.optical_tests)

    def run(self, zemod :ZeMod, camera:Camera3D, output_root: Path) -> None:
        self.tuner = Tuner(zemod=zemod, camera= camera)
        for optical_test in self.optical_tests:
            log.info("=== Running test: %s ===", optical_test.test_name)
            start_time = time.perf_counter()
            try:
                ok = optical_test.run(zemod=zemod,camera=camera,output_root=output_root,tuner=self.tuner)
                optical_test.elapsed = time.perf_counter() - start_time
                all_ok = bool(ok) and all(passed for _, passed in ok)
                optical_test.success = all_ok
                for album_name, passed in ok:
                    log.info(
                        "Analysis %s, Album %s -> %s (%.2f s) ===",
                        optical_test.test_name,
                        album_name,
                        "PASS" if passed else "FAIL",
                        optical_test.elapsed,
                    )
                log.info(
                    "=== Analysis %s is over %.2f s ===",
                    optical_test.test_name, optical_test.elapsed)
            except Exception:
                optical_test.elapsed = time.perf_counter() - start_time
                log.exception("Analysis crashed: %s (%.2f s)", optical_test.test_name, optical_test.elapsed)
                optical_test.success = False


