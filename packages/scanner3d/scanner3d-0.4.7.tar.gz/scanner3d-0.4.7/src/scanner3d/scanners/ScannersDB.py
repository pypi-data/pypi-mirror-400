from __future__ import annotations
from typing import Final, Mapping, Dict, Tuple
from types import MappingProxyType
from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path
from allytools.db import FrozenDB
from scanner3d.scanner.scanner import Scanner as _Scanner
from scanner3d.camera3d.camera3d import Camera3D

_PKG_NAME = __package__ or ""
_PKG_DIR = Path(__file__).parent

def _is_scanner(obj) -> bool:
    return obj.__class__ is _Scanner

def _discover_scanners() -> Dict[str, _Scanner]:
    registry: Dict[str, _Scanner] = {}
    module_names = []
    for m in iter_modules([str(_PKG_DIR)]):
        if m.ispkg:
            continue
        if m.name in {"ScannersDB", "__init__"} or m.name.startswith("_"):
            continue
        module_names.append(m.name)
    module_names.sort()
    for mod_name in module_names:
        try:
            mod = import_module(f".{mod_name}", package=_PKG_NAME) if _PKG_NAME else import_module(mod_name)
        except Exception as exc:
            raise ImportError(f"Failed to import scanner module '{mod_name}': {exc}") from exc

        for attr_name, value in vars(mod).items():
            if attr_name.startswith("_"):
                continue
            if _is_scanner(value):
                if attr_name in registry:
                    prev = registry[attr_name]
                    raise ValueError(
                        f"Duplicate scanner name '{attr_name}' found in module '{mod_name}'. "
                        "Each scanner variable name must be unique across modules."
                    )
                registry[attr_name] = value

    return registry

_REGISTRY: Dict[str, _Scanner] = _discover_scanners()
REGISTRY: Final[Mapping[str, _Scanner]] = MappingProxyType(_REGISTRY)

class ScannersDB(metaclass=FrozenDB):
    __slots__ = ()
    REGISTRY: Final[Mapping[str, _Scanner]] = REGISTRY
    for _name, _scanner in _REGISTRY.items():
        locals()[_name] = _scanner
    del _name, _scanner

    @classmethod
    def get_scanner(cls, name: str) -> _Scanner:
        try:
            return cls.REGISTRY[name]
        except KeyError as e:
            available = ", ".join(sorted(cls.REGISTRY.keys())) or "<none>"
            raise KeyError(f"Unknown scanner '{name}'. Available: {available}") from e

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(sorted(cls.REGISTRY.keys()))

    @classmethod
    def find_camera(cls, camera: Camera3D) -> Tuple[str, int]:
        """
        Given a Camera3D instance from ScannersDB, return (scanner_name, camera_index).
        """
        for scanner_name, scanner in cls.REGISTRY.items():
            for idx, cam in enumerate(scanner.cameras):
                if cam is camera or cam == camera:
                    return scanner_name, idx
        raise ValueError("Camera not found in ScannersDB.REGISTRY")

    @classmethod
    def __getattr__(cls, name: str):
        if name in cls.REGISTRY:
            return cls.REGISTRY[name]
        raise AttributeError(name)

    @classmethod
    def __dir__(cls):
        return sorted(set(super().__dir__()) | set(cls.REGISTRY.keys()))


__all__ = ["ScannersDB", *sorted(REGISTRY.keys())]
