from __future__ import annotations
import h5py
from scanner3d.scanner.scanner_ref import ScannerRef


class ScannerRefH5:
    SCANNER_NAME = "scanner_name"
    CAMERA_INDEX = "camera_index"


def save_camera_ref(*, scanner_grp: h5py.Group, ref: ScannerRef) -> None:
    scanner_grp.attrs[ScannerRefH5.SCANNER_NAME] = ref.scanner_name
    scanner_grp.attrs[ScannerRefH5.CAMERA_INDEX] = ref.camera_index


def load_camera_ref(scanner_grp: h5py.Group) -> ScannerRef | None:
    if (ScannerRefH5.SCANNER_NAME not in scanner_grp.attrs or
        ScannerRefH5.CAMERA_INDEX not in scanner_grp.attrs):
        return None

    return ScannerRef(
        scanner_name=str(scanner_grp.attrs[ScannerRefH5.SCANNER_NAME]),
        camera_index=int(scanner_grp.attrs[ScannerRefH5.CAMERA_INDEX]),
    )
