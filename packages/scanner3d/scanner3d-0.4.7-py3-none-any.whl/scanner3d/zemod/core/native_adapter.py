from __future__ import annotations
from functools import cached_property
from typing import Generic, TypeVar, Set, Type
import logging

T = TypeVar("T")
log = logging.getLogger(__name__)
class NativeAdapter(Generic[T]):
    __cached_props__: Set[str] = set()
    def __init__(self, native: T):
        self.native = native

    @classmethod
    def _cached_property_names(cls: Type) -> Set[str]:
        names: Set[str] = set(cls.__dict__.get("__cached_props__", set()))
        for base in cls.__mro__:
            for name, attr in getattr(base, "__dict__", {}).items():
                if isinstance(attr, cached_property):
                    names.add(name)
        return names

    def invalidate_cached(self, *names: str) -> int:
        removed = 0
        if names:
            to_drop = set(names)
        else:
            to_drop = self._cached_property_names()

        for n in to_drop:
            if n in self.__dict__:
                self.__dict__.pop(n, None)
                removed += 1
        if removed:
            log.debug("%s: invalidated cached properties: %s",
                      self.__class__.__name__, ", ".join(to_drop))
        return removed

    def invalidate_all_cached(self) -> int:
        return self.invalidate_cached()

    def __str__(self) -> str:
        return str(self.native)
