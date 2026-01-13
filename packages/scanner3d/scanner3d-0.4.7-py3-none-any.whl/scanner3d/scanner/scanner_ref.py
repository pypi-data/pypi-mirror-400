from dataclasses import dataclass
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.scanners.ScannersDB import ScannersDB

@dataclass(frozen=True, slots=True)
class ScannerRef:
    scanner_name: str
    camera_index: int

    def resolve(self)->Camera3D:
        """
        Lazily resolve to a real Camera3D using ScannersDB.
        Can be omitted if you prefer a separate helper instead.
        """

        scanner = ScannersDB.get_scanner(self.scanner_name)
        try:
            return scanner.cameras[self.camera_index]
        except IndexError as exc:
            raise LookupError(
                f"Camera index {self.camera_index} out of range "
                f"for scanner '{self.scanner_name}'"
            ) from exc

    def __str__(self) -> str:
        return (f"CameraRef(scanner='{self.scanner_name}', "
                f"index={self.camera_index}, ")


    __repr__ = __str__

def create_scanner_ref(camera) -> ScannerRef:
    scanner_name, cam_idx = ScannersDB.find_camera(camera)
    return ScannerRef(scanner_name=scanner_name,camera_index=cam_idx)


