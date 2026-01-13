from __future__ import annotations
from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import Protocol, List
import logging

log = logging.getLogger(__name__)

class Revertible(Protocol):
    """Anything that can revert itself."""
    def revert(self) -> None: ...

@dataclass(slots=True)
class RevertStack:
    """
    Holds a list of Revertible objects and ensures they are reverted in reverse order.
    Typically used as:

        stack = RevertStack()
        with stack.session():
            stack.push(manager1, manager2)
            # do stuff
        # managers auto-reverted on exit
    """
    items: List[Revertible] = field(default_factory=list)

    def push(self, *objs: Revertible) -> None:
        """Add one or more Revertible objects to the stack."""
        self.items.extend(objs)

    @contextmanager
    def session(self):
        """Context manager that guarantees all items are reverted in reverse order."""
        try:
            yield self
        finally:
            for obj in reversed(self.items):
                try:
                    obj.revert()
                except Exception:
                    log.exception("Failed to revert %r", obj)
