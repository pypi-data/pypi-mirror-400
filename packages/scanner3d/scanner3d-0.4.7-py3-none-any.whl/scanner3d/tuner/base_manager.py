from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Final, Protocol, runtime_checkable, Any, Callable, TypeVar
from allytools.strings import obj_to_str
_SENTINEL: Final = object()
T = TypeVar("T")


log = logging.getLogger(__name__)
@runtime_checkable
class Revertible(Protocol):
    def apply(self, *args: Any, **kwargs: Any) -> None: ...
    def revert(self)    -> None: ...

@dataclass(slots=True)
class BaseManager(Revertible):
    """Capture-once / Revert-later pattern."""
    _captured: bool = field(init=False, default=False, repr=False)

    def capture_once(self, fn: Callable[[], None]) -> None:
        if not self._captured:
            fn()
            self._captured = True

    # helpers
    @staticmethod
    def set_if_diff(setter: Callable[[Any], None], old: Any, new: Any) -> bool:
        if old != new:
            setter(new)
            return True
        return False

    def sync_setting(
            self,
            *,
            label: str,
            get: Callable[[], T],
            set_: Callable[[T], None],
            target: T,
            orig_attr: str,
    ) -> None:
        cls = self.__class__.__name__
        if getattr(self, orig_attr) is _SENTINEL:
            orig = get()
            setattr(self, orig_attr, orig)
            log.debug("%s.capture %s: original=%s", cls, label, obj_to_str(orig))
        cur = get()
        if cur != target:
            log.info("%s.sync_%s: %s -> %s", cls, label, obj_to_str(cur), obj_to_str(target))
            set_(target)
        else:
            log.debug("%s.sync_%s: already %s (no change)", cls, label, obj_to_str(cur))

    def _revert_setting(
        self,
        *,
        label: str,
        get: Callable[[], T],
        set_: Callable[[T], None],
        orig_attr: str,
    ) -> bool:
        """Revert one captured setting if it changed; return True if changed."""
        cls = self.__class__.__name__
        orig = getattr(self, orig_attr)
        if orig is _SENTINEL:
            return False  # nothing captured for this attribute

        cur = get()
        if cur != orig:
            # nice enum/tuple printing via _name_or_val
            log.info("%s.revert %s: %s -> %s", cls, label, obj_to_str(cur), obj_to_str(orig))
            set_(orig)  # type: ignore[arg-type]
            return True
        else:
            log.debug("%s.revert %s: unchanged (%s)", cls, label, obj_to_str(cur))
            return False