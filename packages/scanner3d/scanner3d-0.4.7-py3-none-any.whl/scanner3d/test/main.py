import logging
from datetime import datetime
from scanner3d.test.base.test_factory import QUICK_TEST, ZERNIKE, FULL_TEST, BATCH
from allytools.files import ensure_folder
from zempy.bridge.zempy_session import zempy_session
from scanner3d.zemod.zemod import ZeMod
from scanner3d.test.log_setup import LoggerSetup
from scanner3d.test.base.test_suit import TestSuite
from scanner3d.camera3d.camera_under_test import CAMERA_LIST_FULL, SPIDER2PROC,LEO_GROUP, SPIDER2PROB, EVA1, EVA_GROUP
from scanner3d.test.result_path import get_output_dir
from scanner3d.test.result_registry import register_result

if __name__ == "__main__":
    base_output = get_output_dir()
    ensure_folder(base_output)
    global_summary_file = base_output / "global_summary.log"
    global_log = logging.getLogger("global_summary")
    if not global_log.handlers:
        fh = logging.FileHandler(global_summary_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        global_log.addHandler(fh)
    global_log.setLevel(logging.INFO)
    global_log.propagate = False
    all_failed: list[str] = []
    for c in SPIDER2PROB:
        camera = c.camera
        camera_output = base_output / f"{c.scanner_name}"
        ensure_folder(camera_output)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = camera_output / f"full_test_log_{timestamp}.log"
        root_log = LoggerSetup.configure(log_file=log_path)
        register_result(
            log_path,
            kind="log",
            scanner_name=c.scanner_name,
            camera_name=c.camera.name)
        root_log.info("=== Starting tests for %s [%d] ===", c.scanner_name, c.index)
        try:
            tests = TestSuite(optical_tests=QUICK_TEST)
            zmx_path = camera.objective.zmx_file
            with zempy_session(zmx_path) as (_zs, s):
                zemod = ZeMod.from_optical_system(s)
                tests.run(zemod=zemod, camera=camera, output_root=camera_output)
            failed = [t.test_name for t in tests if not t.success]
            all_failed.extend(failed)
            for t in tests:
                mark = "✔" if t.success else "✖"
                root_log.info("%s %s  %.2f s", mark, t.test_name, t.elapsed)
            if failed:
                global_log.error("%s [%d]: %d FAILED (%s)",c.scanner_name, c.index, len(failed), ", ".join(failed))
            else:
                global_log.info("%s [%d]: all %d tests passed.", c.scanner_name, c.index, len(tests.optical_tests))
        except Exception:
            root_log.exception("Unexpected error during tests")
            all_failed.append(f"{c.scanner_name}:unexpected")
            global_log.error("%s [%d]: unexpected error", c.scanner_name, c.index)
    if all_failed:
        global_log.error("Some tests failed: %s", ", ".join(all_failed))
    else:
        global_log.info("All cameras passed all tests.")