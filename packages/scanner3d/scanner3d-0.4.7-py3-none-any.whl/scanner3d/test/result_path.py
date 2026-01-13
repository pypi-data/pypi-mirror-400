from __future__ import annotations
from pathlib import Path
import scanner3d

OUTPUT_DIR_NAME = "test_results"


def get_project_root() -> Path:
    """
    Return the project root folder, i.e. the parent of 'src'.
    """
    pkg_dir = Path(scanner3d.__file__).resolve().parent  # .../src/scanner3d
    return pkg_dir.parent.parent                         # .../Scanner3D


def get_output_dir(create: bool = True) -> Path:
    """
    Return the canonical output directory for scanner3d.

    Example: D:/Pycharm/Scanner3D/output
    """
    root = get_project_root()
    out_dir = root / OUTPUT_DIR_NAME
    if create:
        out_dir.mkdir(exist_ok=True)
    return out_dir
