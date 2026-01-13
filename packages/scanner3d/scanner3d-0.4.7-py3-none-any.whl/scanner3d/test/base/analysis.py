from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Tuple
from pathlib import Path
from allytools.strings import sanitize
from allytools.files import ensure_folder
from scanner3d.tuner.tuner import Tuner
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.zemod.zemod import ZeMod
from scanner3d.afs.album import Album
from scanner3d.test.base.album_settings import AlbumSettings
from scanner3d.test.base.analysis_settings import AnalysisSettings
from scanner3d.test.base.aid import save_settings
from scanner3d.test.base.optical_test import OpticalTest
from scanner3d.test.result_registry import register_result

log = logging.getLogger(__name__)
@dataclass
class Analysis(OpticalTest):
    analysis_settings: AnalysisSettings
    albums_settings: list[AlbumSettings]

    def run(
            self,
            *,
            zemod: ZeMod,
            camera: Camera3D,
            output_root: Path,
            tuner: Tuner) -> list[Tuple[str, bool]]:
        self._prepare_output(output_root)
        self._prepare_context(tuner=tuner, camera=camera)
        ok = []
        with tuner.tune(settings=self.tuner_settings):
                with self.analysis_settings.get_analysis(zemod) as analysis:
                    analysis.settings.apply_settings(self.analysis_settings.settings)
                    for album_settings in self.albums_settings:
                        album_folder = self.test_folder / album_settings.name
                        ensure_folder(album_folder)
                        x_seq =album_settings.get_x_seq(self.camera.sensor.grid)
                        y_seq =album_settings.get_y_seq(self.camera.sensor.grid)
                        z_seq =album_settings.get_z_seq(self.camera.z_range)
                        album = Album.compute(
                            tuner=tuner,
                            analysis=analysis,
                            analysis_settings=self.analysis_settings,
                            album_settings=album_settings,
                            x_seq=x_seq,
                            y_seq=y_seq,
                            z_seq=z_seq)
                        if album_settings.enable_image_save:
                            self.save_album_image(album, album_folder)
                        if album_settings.enable_h5_save:
                            self.save_album(album, album_folder)
                        save_settings(album.album_settings, album_folder)
                        save_settings(self.tuner_settings, album_folder)
                        save_settings(analysis.settings.native, album_folder)
                        ok.append([album_settings.name, self.verify_album_file(album)])
        return ok

    def __str__(self) -> str:
        params = ", ".join(
            f"{k}={v!s}"
            for k, v in self.__dict__.items()
            if k not in {"output_root", "success", "elapsed"}
        )
        return f"{self.test_name}({params})"

    def save_album_image(self, album: Album, album_folder: Path):
        for f in album.frames:
            base = self.get_album_filename(album_folder)
            filename = base.with_name(f"{base.stem}_{f.z_mm:.1f}.png")
            image_bundle = f.plot()
            image_bundle.save(str(filename))
            log.info("Frame saved as image: %s", filename)

    def save_album(self, album: Album, album_folder: Path, *, on_conflict: str = "overwrite"):
        filename = self.get_album_filename(album_folder).with_suffix(".h5")
        album.save(path=filename, on_conflict=on_conflict)
        log.info("Album saved with %d frames to HDF5: %s", album.n_frames, filename)
        register_result(
            filename,
            kind="album_h5",
            test_name       = sanitize(self.test_name),
            scanner_name    = sanitize(self.scanner_name),
            settings_name   = sanitize(album.album_settings.name))

    def verify_album_file(self, album: Album) -> bool:
        album_folder = self.test_folder / album.album_settings.name
        filename = self.get_album_filename(album_folder).with_suffix(".h5")
        exists = filename.exists()
        size = filename.stat().st_size if exists else 0
        ok = exists and size > 0 and album.n_frames > 0
        if not ok:
            log.warning(
                "Album output verification failed: exists=%s size=%s frames=%d",
                exists,
                size,
                album.n_frames)
        else:
            log.info("test - %s successfully done", self.test_name)
        return ok
    def get_album_filename(self, album_folder: Path) -> Path:
        return album_folder / f"{sanitize(self.scanner_name)}_{sanitize(self.test_name)}_{sanitize(album_folder.name)}"