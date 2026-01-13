import h5py
import numpy as np
from typing import Tuple, Literal
from scanner3d.afs.frame import Frame

def read_vec(ds) -> np.ndarray:
    """Read HDF5 dataset that may be scalar () or vector; return 1-D float array."""
    arr = ds[()]  # works for scalar and array
    return np.atleast_1d(np.asarray(arr, dtype=float))


def suggest_chunks(shape: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    Suggest chunks so that the last 2 dims are stored as full 2D blocks.

    For shape (n_shots, Ny, Nx) this returns (1, Ny, Nx):
    one shot per chunk, full 2D PSF each time.
    """
    if len(shape) < 2:
        raise ValueError("Expected at least 2 dims (Ny, Nx).")
    f_ndim = len(shape) - 2
    return (1,) * f_ndim + (shape[-2], shape[-1])


def frame_name(frame: Frame) -> str:
    wd = frame.profile.working_distance
    return f"psf_frame_at_{wd:.2f}" if wd is not None else "psf_frame_at_unknown"




def resolve_h5_name(
    container: h5py.Group | h5py.File,
    base: str,
    on_conflict: Literal["error", "overwrite", "skip", "rename"],
    what: str = "item",
) -> tuple[str, bool]:
    """
    Resolve name conflicts inside an HDF5 group/file.

    Returns:
        (final_name, skip_flag)

    - If skip_flag is True, caller should skip creating/writing this item.
    - If final_name differs from base, 'rename' policy was applied.
    """
    name = base

    if name in container:
        if on_conflict == "error":
            raise ValueError(f"{what} '{name}' already exists.")
        elif on_conflict == "overwrite":
            del container[name]
        elif on_conflict == "skip":
            # Leave existing item as-is, but tell caller to skip.
            return name, True
        elif on_conflict == "rename":
            k = 1
            while f"{base}_{k:03d}" in container:
                k += 1
            name = f"{base}_{k:03d}"

    return name, False

