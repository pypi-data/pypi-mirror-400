import logging
from dataclasses import field, dataclass
from typing import Optional, Tuple
from scanner3d.tuner.base_manager import BaseManager, _SENTINEL
from scanner3d.zemod.zemod_fields import ZeModFields
from scanner3d.zemod.zemod_field import ZeModField
from scanner3d.zemod.enums import ZeModFieldTypes, ZeModFieldNormalizationType


log = logging.getLogger(__name__)
@dataclass(slots=True)
class FieldManager(BaseManager):
    """
    Manages system fields:
      - Ensures first field is on-axis (0,0) within tolerance.
      - Syncs field type.
      - Supports revert() to restore original type and first-field XY.
    """
    fields: ZeModFields

    _test_field_number: int = field(init=False, default=_SENTINEL, repr=False)
    _orig_type: ZeModFieldTypes | object = field(init=False, default=_SENTINEL, repr=False)
    _orig_norm: ZeModFieldNormalizationType | object = field(init=False, default=_SENTINEL, repr=False)
    _orig_xy: tuple[float, float] | object = field(init=False, default=_SENTINEL, repr=False)

    def apply (self,
               *,
               field_type: ZeModFieldTypes,
               normalization: ZeModFieldNormalizationType,
               test_field_number:Optional[int],
               extra_field:Optional[Tuple[float, float]]) -> None:
        #self.check_fields_n()
        #self.ensure_field1_on_axis()
        self.set_test_field_number(test_field_number)
        self.sync_setting(
            label="field type",
            get=self.fields.get_field_type,
            set_=self.fields.set_field_type,
            target=field_type,
            orig_attr="_orig_type",
        )
        self.sync_setting(
            label="normalization",
            get=self.fields.get_normalization,
            set_=self.fields.set_normalization,
            target=normalization,
            orig_attr="_orig_norm",
        )

        if extra_field is not None:
            x_mm = extra_field[0]
            y_mm = extra_field[1]
            self.add_edge_field(x_mm, y_mm)

    @property
    def test_field_number(self) -> int:
        return self._test_field_number

    def set_test_field_number(self, n: int) -> None:
        if n is None:
            log.warning("No test field specified. Default field (1) will be used.")
            self._test_field_number = 1
            return
        if not (1 <= n <= self.fields.n_fields):
            log.error(
                "Invalid field number %d. Valid range is 1..%d.",
                n, self.fields.n_fields
            )
            raise ValueError(f"Field number {n} is out of valid range.")
        self._test_field_number = n

    def get_test_field(self)->ZeModField:
        log.debug("Field manger provide field number %d", self.test_field_number)
        return self.fields.get_field(self.test_field_number)

    def check_fields_n(self, keep: int = 1) -> None:
        n_before = self.fields.n_fields
        if n_before > keep:
            log.warning("system has %d fields (> %d); trimming to %d. not reversible in run-time",n_before,keep, keep)
            for i in range(n_before, keep, -1):
                try:
                    self.fields.delete_at(i)
                    log.debug("removed extra field #%d", i)
                except Exception as e:
                    log.exception("failed to remove field #%d (%s)", i, e)

        n_after = self.fields.n_fields
        log.debug("Check total fields number done, should be only %d left - %d", keep, n_after)

    def ensure_field1_on_axis(self, tol: float = 0.0) -> None:
        cls = self.__class__.__name__
        f = self.fields.get_field(1)
        def get_xy() -> tuple[float, float]:
            return float(f.x), float(f.y)
        log.debug("Field one set on axis  (%f, %f)", f.x, f.y)

        def set_xy(val: tuple[float, float]) -> None:
            f.x, f.y = val
        cur = get_xy()
        if abs(cur[0]) <= tol and abs(cur[1]) <= tol:
            if self._orig_xy is _SENTINEL:
                self._orig_xy = cur
                log.debug("%s.capture XY: original first-field=(%.3f, %.3f)", cls, cur[0], cur[1])
            log.debug("%s.ensure_axis_first_field: already on-axis (%.3f, %.3f) within tol=%.3g",
                      cls, cur[0], cur[1], tol)
            return

        self.sync_setting(
            label="first-field XY",
            get=get_xy,
            set_=set_xy,
            target=(0.0, 0.0),
            orig_attr="_orig_xy",
        )

    def add_edge_field(self, x: float, y: float) -> None:
        n = self.fields.n_fields
        if n == 1:
            self.fields.add_field(x, y)
            log.info("created field #2 at (%.3f, %.3f)", x, y)
        else:
            f2 = self.fields.get_field(2)
            oldx, oldy = float(f2.x), float(f2.y)
            if (oldx, oldy) != (x, y):
                log.info("field #2 (%.3f, %.3f) -> (%.3f, %.3f) — not reversible at runtime",
                         oldx, oldy, x, y)
                f2.x, f2.y = x, y
            else:
                log.debug("field #2 already at (%.3f, %.3f)", x, y)



    def _revert_specs(self):
        # 1) field type
        yield dict(
            label="type",
            get=self.fields.get_field_type,
            set_=self.fields.set_field_type,
            orig_attr="_orig_type",
        )
        # 2) normalization
        yield dict(
            label="normalization",
            get=self.fields.get_normalization,
            set_=self.fields.set_normalization,
            orig_attr="_orig_norm",
        )
        # 3) first-field XY as a tuple
        f1 = self.fields.get_field(1)
        yield dict(
            label="first-field XY",
            get=lambda: (float(f1.x), float(f1.y)),
            set_=lambda xy: setattr(f1, "x", xy[0]) or setattr(f1, "y", xy[1]),
            orig_attr="_orig_xy",
        )

    def revert(self) -> None:
        did_anything = False
        for spec in self._revert_specs():
            # each spec: label, get, set_, orig_attr
            changed = self._revert_setting(**spec)
            did_anything = did_anything or changed

        if not did_anything:
            log.debug("%s.revert: nothing to revert (no captured changes)", self.__class__.__name__)