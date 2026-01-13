from __future__ import annotations
from typing import Optional

import h5py
from allytools.units.length import Length
from scanner3d.test.base.album_settings import (
    AlbumSettings,
    AlbumTypes,
    ALBUM_TYPES_REG,
)


def _save_grid_step(group: h5py.Group, name: str, value) -> None:
    """
    Save GridStep = Union[int, Length] or None.

    - if None → attr f"{name}_mode" = "none"
    - if int  → dataset <name> (int64), attr mode="index"
    - if Length → dataset <name> (float64, mm), attr mode="mm"
    """
    mode_attr = f"{name}_mode"

    if value is None:
        group.attrs[mode_attr] = "none"
        return

    if isinstance(value, int):
        group.attrs[mode_attr] = "index"
        if name in group:
            del group[name]
        group.create_dataset(name, data=int(value))
        return

    if isinstance(value, Length):
        group.attrs[mode_attr] = "mm"
        if name in group:
            del group[name]
        group.create_dataset(name, data=float(value.value_mm))
        return

    raise TypeError(
        f"Unsupported type for {name}: {type(value)!r}; "
        "expected int | Length | None."
    )


def _load_grid_step(group: h5py.Group, name: str):
    """
    Inverse of _save_grid_step.
    """
    mode_attr = f"{name}_mode"
    mode = group.attrs.get(mode_attr, "none")

    if mode == "none":
        return None

    if name not in group:
        raise KeyError(f"Dataset '{name}' missing in group '{group.name}'")

    raw = group[name][()]

    if mode == "index":
        return int(raw)

    if mode == "mm":
        return Length(float(raw))

    raise ValueError(
        f"Unknown {mode_attr}={mode!r} in group '{group.name}'"
    )


def _save_length(group: h5py.Group, name: str, value: Optional[Length]) -> None:
    """
    Save Optional[Length] as mm.
    """
    mode_attr = f"{name}_mode"

    if value is None:
        group.attrs[mode_attr] = "none"
        return

    group.attrs[mode_attr] = "mm"
    if name in group:
        del group[name]
    group.create_dataset(name, data=float(value.value_mm))


def _load_length(group: h5py.Group, name: str) -> Optional[Length]:
    mode_attr = f"{name}_mode"
    mode = group.attrs.get(mode_attr, "none")

    if mode == "none":
        return None

    if name not in group:
        raise KeyError(f"Dataset '{name}' missing in group '{group.name}'")

    raw = group[name][()]
    if mode == "mm":
        return Length(float(raw))

    raise ValueError(
        f"Unknown {mode_attr}={mode!r} in group '{group.name}'"
    )


def save_album_settings(group: h5py.Group, settings: AlbumSettings) -> None:
    group.attrs["name"] = settings.name
    group.attrs["album_type"] = settings.album_type.name
    _save_grid_step(group, "dx", settings.dx)
    _save_grid_step(group, "dy", settings.dy)
    _save_length(group, "dz", settings.dz)

def load_album_settings(group: h5py.Group) -> AlbumSettings:
    """
    Reconstruct AlbumSettings from HDF5 group.
    """
    if "album_type" not in group.attrs:
        raise KeyError(
            f"Missing 'album_type' attribute in album_settings group '{group.name}'"
        )

    name = group.attrs.get("name", "Unnamed")
    type_name = group.attrs["album_type"]
    album_type = AlbumTypes[type_name]
    template = ALBUM_TYPES_REG[album_type]

    dx = _load_grid_step(group, "dx")
    dy = _load_grid_step(group, "dy")
    dz = _load_length(group, "dz")

    return AlbumSettings(
        name=name,
        album_type=album_type,
        template=template,
        dx=dx,
        dy=dy,
        dz=dz,
    )