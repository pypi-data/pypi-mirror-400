import logging
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path
from allytools.strings import sanitize
from scanner3d.ray_trace.raytrace_settings import RayTraceSettings
from scanner3d.ray_trace.ray_batch_type import REQUIRED_FOR_TEST
from scanner3d.ray_trace.ray_batches import RayBatches
from scanner3d.ray_trace.ray_batch import RayBatch
from scanner3d.tuner.tuner import Tuner
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.zemod.zemod import ZeMod
from scanner3d.zemod.tools.zemod_tool_list import ZeModToolList
from scanner3d.test.base.optical_test import OpticalTest
from scanner3d.test.result_registry import register_result
from scanner3d.test.base.aid import save_settings


log = logging.getLogger(__name__)
@dataclass
class BatchRayTraceTest(OpticalTest):
    base_settings: RayTraceSettings

    def run(
            self,
            *,
            zemod: ZeMod,
            camera: Camera3D,
            output_root: Path,
            tuner: Tuner) -> list[Tuple[str, bool]]:
        self._prepare_output(output_root)
        self._prepare_context(tuner=tuner, camera=camera)
        updated_settings = self.base_settings.replace_grid(camera = camera)
        ok = []
        with tuner.tune(settings=self.tuner_settings):
            ray_batches = RayBatches()
            for batch_type in REQUIRED_FOR_TEST:
                to_surface = batch_type.to_surface(zemod.lde)
                log.info("RayBatch  will be calculated at surface %d", to_surface)
                zemod_tool = zemod.tools.run_tool(ZeModToolList.BATCH_RAYTRACE, updated_settings.replace_surface(to_surface))
                batch = RayBatch.compute(
                    batch_type=batch_type,
                    rays=zemod_tool.rays,
                    x_lin=zemod_tool.generic_tracer.x_lin,
                    y_lin=zemod_tool.generic_tracer.y_lin,
                    process_time=zemod_tool.generic_tracer.process_time,
                    settings=updated_settings.replace_surface(to_surface))
                ray_batches.append(batch)
                filename = self.h5_filename()
                ray_batches.save_to_h5(path=filename, compression="gzip", compression_opts=4)
                save_settings(self.tuner_settings, self.test_folder)
                save_settings(updated_settings, self.test_folder)
                log.info("RayBatch %s saved to HDF5: %s", batch.batch_type.value, filename)
            register_result(
                path=Path(filename),
                kind="ray_batch_h5",
                test_name       = sanitize(self.test_name),
                scanner_name    = sanitize(self.scanner_name),
                settings_name   = sanitize(self.base_settings.name))
            ok.append([self.test_name, self.verify_h5()])
        return ok

    def h5_filename(self)->Path:
        return  Path(f"{self.test_folder / sanitize(self.scanner_name)}_{sanitize(self.test_name)}_{sanitize(self.base_settings.name)}.h5")

    def verify_h5(self) -> bool:
        filename =self.h5_filename()
        exists = filename.exists()
        size = filename.stat().st_size if exists else 0
        ok = exists and size > 0
        if not ok:
            log.warning(
                "h5 output verification failed: exists=%s size=%s frames=%d",
                exists, size)
        else:
            log.info("test - %s successfully done", self.test_name)
        return ok