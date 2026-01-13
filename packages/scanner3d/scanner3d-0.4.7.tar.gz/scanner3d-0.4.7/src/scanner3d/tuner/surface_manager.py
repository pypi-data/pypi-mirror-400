from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from allytools.units import Length, LengthUnit
from scanner3d.tuner.base_manager import BaseManager, _SENTINEL
from scanner3d.zemod.tools.quickfocus_settings import QuickFocusSettings
from scanner3d.zemod.zemod import ZeMod
from scanner3d.zemod.zemod_lde import ZeModLDE
from scanner3d.zemod.zemod_row import ZeModRow
from scanner3d.tuner.find_index_by_comment import find_index_by_comment
from scanner3d.tuner.constants import WD_COMMENT, FOCUS_COMMENT

log = logging.getLogger(__name__)


@dataclass(slots=True)
class SurfaceManager(BaseManager):
    zemod: ZeMod
    lde: ZeModLDE
    wd_index: int = field(init=False, default=_SENTINEL, repr=False)
    focus_index: int = field(init=False, default=_SENTINEL, repr=False)
    _orig_wd_t: float | object = field(init=False, default=_SENTINEL, repr=False)
    _orig_fc_t: float | object = field(init=False, default=_SENTINEL, repr=False)

    def apply(self, *, focus_distance: Optional[Length] = None) -> None:
        self._ensure_indices()
        if focus_distance is None:
            log.debug("SurfaceManager.apply: no WD provided; nothing to do.")
            return
        working_distance_mm = focus_distance.to(LengthUnit.MM)
        self.quick_focus(working_distance_mm)

    def get_wd_row(self) -> ZeModRow:
        return self.lde.get_surface_at(self.wd_index)

    def quick_focus(self, target_mm: Optional[float]) -> None:
        """
        Set WD surface thickness to target_mm (mm) via sync_setting, capture Focus, then quick_focus().
        """
        if target_mm is None:
            log.debug("quick_focus: target_mm is None -> no action.")
            return

        self._ensure_indices()
        log.info(
            "quick_focus: target_mm=%.6f (wd_index=%s, focus_index=%s)",
            target_mm, self.wd_index, self.focus_index)

        def wd_thickness_get() -> float:
            return float(self.lde.get_surface_at(self.wd_index).thickness)

        def wd_thickness_set(v: float) -> None:
            self.lde.get_surface_at(self.wd_index).thickness = float(v)

        def fc_thickness_get() -> float:
            return float(self.lde.get_surface_at(self.focus_index).thickness)

        def fc_thickness_set(_: float) -> None:
            pass

        self.sync_setting(
            label="wd_thickness",
            get=wd_thickness_get,
            set_=wd_thickness_set,
            target=float(target_mm),
            orig_attr="_orig_wd_t")

        cur_fc = fc_thickness_get()
        self.sync_setting(
            label="focus_thickness",
            get=fc_thickness_get,
            set_=fc_thickness_set,            # won't be called because target == current
            target=cur_fc,
            orig_attr="_orig_fc_t")
        try:
            log.debug("quick_focus: calling zemod.quick_focus() …")
            default_settings = QuickFocusSettings() #TODO default params?
            self.zemod.tools.run_quick_focus(default_settings)
            new_fc = fc_thickness_get()
            log.debug("quick_focus: Focus after zemod.quick_focus() = %.6f", new_fc)
        except Exception as e:
            log.exception("quick_focus: zemod.quick_focus() failed: %s", e)
            raise

    def revert(self) -> None:
        """
        Restore previously captured WD/Focus thicknesses (if captured and changed).
        """
        self._ensure_indices()
        log.info("revert: attempting to restore original WD/Focus thicknesses.")

        # Accessors
        def wd_get() -> float:
            return float(self.lde.get_surface_at(self.wd_index).thickness)

        def wd_set(v: float) -> None:
            self.lde.get_surface_at(self.wd_index).thickness = float(v)

        def fc_get() -> float:
            return float(self.lde.get_surface_at(self.focus_index).thickness)

        def fc_set(v: float) -> None:
            self.lde.get_surface_at(self.focus_index).thickness = float(v)

        # Revert WD
        self._revert_setting(
            label="wd_thickness",
            get=wd_get,
            set_=wd_set,
            orig_attr="_orig_wd_t")

        # Revert Focus
        self._revert_setting(
            label="focus_thickness",
            get=fc_get,
            set_=fc_set,
            orig_attr="_orig_fc_t")

        log.info("revert: done.")

    def _ensure_indices(self) -> None:
        """Make sure wd_index and focus_index are resolved."""
        if self.wd_index is _SENTINEL or self.focus_index is _SENTINEL:
            self.wd_index, self.focus_index = self._locate_surfaces()
            log.debug("_ensure_indices: wd_index=%s, focus_index=%s",
                      self.wd_index, self.focus_index)

    def _locate_surfaces(self) -> tuple[int, int]:
        """
        Find the WD and Focus surface indices by comments; fallback to first and penultimate.
        """
        wd = find_index_by_comment(
            lde=self.lde,
            desired_comment=WD_COMMENT,
            default_index=0,
            default_description="first surface")

        # total surfaces (handle attr or callable)
        total = getattr(self.lde, "n_surfaces", None)
        total = int(total() if callable(total) else total)
        penultimate = max(0, total - 2)
        fc = find_index_by_comment(
            lde=self.lde,
            desired_comment=FOCUS_COMMENT,
            default_index=penultimate,
            default_description="penultimate surface")
        log.debug("_locate_surfaces: WD=%d, Focus=%d (total=%d)", wd, fc, total)
        return wd, fc
