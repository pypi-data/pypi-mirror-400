import logging
from typing import Optional
from scanner3d.zemod.zemod_lde import ZeModLDE
from scanner3d.tuner.base_manager import _SENTINEL

log = logging.getLogger(__name__)

def find_index_by_comment(
    *,
    lde: ZeModLDE,
    desired_comment: str,
    default_index: int,
    default_description: str,
) -> Optional[int]:

    if lde is _SENTINEL:
        log.error("LDE reference is _SENTINEL (uninitialized).")
        return None

    if desired_comment is None:
        log.error("desired_comment is None.")
        return None

    for i in range(lde.n_surfaces):
        s = lde.get_surface_at(i)
        if s.comment == desired_comment:
            log.debug("Found surface %d with comment %r", i, desired_comment)
            return i
    if 0 <= default_index < lde.n_surfaces:
        log.warning(
            "Surface not found by comment %r — falling back to %s (index %d)",
            desired_comment, default_description, default_index
        )
        return default_index

    log.error(
        "Surface not found by comment %r and fallback index %d is out of range [0, %d].",
        desired_comment, default_index, max(lde.n_surfaces - 1, -1)
    )
    return None