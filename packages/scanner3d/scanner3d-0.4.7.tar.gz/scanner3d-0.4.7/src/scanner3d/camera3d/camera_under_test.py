from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Iterator, Tuple

from scanner3d.scanner.scanner import Scanner
from scanner3d.camera3d.camera3d import Camera3D
from scanner3d.scanners.ScannersDB import ScannersDB


@dataclass(frozen=True)
class CameraUnderTest:
    scanner: Scanner
    index: int

    @property
    def camera(self) -> Camera3D:
        """Return the actual camera object from this scanner."""
        return self.scanner.cameras[self.index]

    @property
    def scanner_name(self) -> str:
        """Name used for folder creation."""
        return self.scanner.name


@dataclass(frozen=True)
class CameraGroup:
    """Immutable group of cameras under test."""
    name: str
    cameras: Tuple[CameraUnderTest, ...]

    def __iter__(self) -> Iterator[CameraUnderTest]:
        return iter(self.cameras)

    def __len__(self) -> int:
        return len(self.cameras)

    @property
    def scanner_names(self) -> list[str]:
        return [c.scanner_name for c in self.cameras]

    def with_index(self, index: int) -> "CameraGroup":
        """Return a new group with a different index for all cameras."""
        return CameraGroup(
            name=self.name,
            cameras=tuple(
                CameraUnderTest(scanner=c.scanner, index=index)
                for c in self.cameras
            ),
        )

CAMERA_LIST_FULL = CameraGroup(
    name="ALL",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Spider2,     index=0),
        CameraUnderTest(scanner=ScannersDB.Spider2ProC, index=0),
        CameraUnderTest(scanner=ScannersDB.Eva1,        index=0),
        CameraUnderTest(scanner=ScannersDB.Eva2A,       index=0),
        CameraUnderTest(scanner=ScannersDB.Eva2B,       index=0),
        CameraUnderTest(scanner=ScannersDB.Leo,         index=0),
        CameraUnderTest(scanner=ScannersDB.Leo2A,       index=0),
    ),
)

SPIDER2 = CameraGroup(
    name="Spider2",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Spider2, index=0),
    ),
)

SPIDER2PROC = CameraGroup(
    name="Spider2Pro",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Spider2ProC, index=0),
    ),
)

SPIDER2PROB = CameraGroup(
    name="Spider2ProB",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Spider2ProB, index=0),
    ),
)

LEO_GROUP = CameraGroup(
    name="LeoGroup",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Leo,   index=0),
        CameraUnderTest(scanner=ScannersDB.Leo2A, index=0),
    ),
)

SPIDER_GROUP = CameraGroup(
    name="LeoGroup",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Spider2, index=0),
        CameraUnderTest(scanner=ScannersDB.Spider2ProC, index=0),
    ),
)

EVA1= CameraGroup(
    name="LeoGroup",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Eva1,   index=0),
    ),
)


EVA_GROUP= CameraGroup(
    name="LeoGroup",
    cameras=(
        CameraUnderTest(scanner=ScannersDB.Eva1,   index=0),
        CameraUnderTest(scanner=ScannersDB.Eva2A, index=0),
        CameraUnderTest(scanner=ScannersDB.Eva2B, index=0),
    ),
)
