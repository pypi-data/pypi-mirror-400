from typing import ClassVar, Mapping, Tuple
from scanner3d.scanner.scanner import Scanner

REGISTRY: Mapping[str, Scanner]

class ScannersDB:
    REGISTRY: ClassVar[Mapping[str, Scanner]]
    Eva1: ClassVar[Scanner]
    Eva2A: ClassVar[Scanner]
    Eva2B: ClassVar[Scanner]
    Eva2C: ClassVar[Scanner]
    Leo: ClassVar[Scanner]
    Leo2A: ClassVar[Scanner]
    Spider2: ClassVar[Scanner]
    Spider2ProB: ClassVar[Scanner]
    Spider2ProC: ClassVar[Scanner]
    Spider2ProD: ClassVar[Scanner]

    @classmethod
    def find_camera(cls, *args, **kwargs) -> Tuple[str, int]: ...
    @classmethod
    def get_scanner(cls, *args, **kwargs) -> Scanner: ...
    @classmethod
    def names(cls, *args, **kwargs) -> tuple[str, ...]: ...
