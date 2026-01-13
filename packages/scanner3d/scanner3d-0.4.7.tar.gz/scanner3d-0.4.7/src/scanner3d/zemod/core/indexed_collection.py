from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict

# Type variables
N = TypeVar("N")        # native type for single wrapper
C = TypeVar("C")        # concrete child wrapper class
NCol = TypeVar("NCol")  # native collection type
NChild = TypeVar("NChild")  # native child type



class IndexedCollection(ABC, Generic[C, NCol, NChild]):
    """
    Generic base for any 1-based, index-addressable native collection
    that returns native children and supports add/delete-last operations.
    Caches wrapped children per index.
    """
    __slots__ = ("native", "_by_index")

    def __init__(self, native: NCol) -> None:
        self.native = native
        self._by_index: Dict[int, C] = {}
        self.rebuild_cache()


    @abstractmethod
    def _native_count(self) -> int:
        """Return number of items in the native collection."""
        ...

    @abstractmethod
    def _native_get(self, index: int) -> NChild:
        """Return native child at 1-based index."""
        ...

    @abstractmethod
    def _native_add(self, *args, **kwargs) -> NChild:
        """Add a native child (signature defined by concrete collection)."""
        ...

    @abstractmethod
    def _native_delete_at(self, index: int) -> None:
        """Delete the native child at the given 1-based index."""
        ...

    @abstractmethod
    def _child_from_native(self, native_child: NChild) -> C:
        """Wrap native child into a concrete adapter C."""
        ...


    @property
    def count(self) -> int:
        return self._native_count()

    def get_child(self, index: int) -> C:
        try:
            return self._by_index[index]
        except KeyError:
            raise IndexError(f"Index {index} out of range 1..{self.count}") from None

    def add_child(self, *args, **kwargs) -> C:
        native_child = self._native_add(*args, **kwargs)
        wrapped = self._child_from_native(native_child)
        self._by_index[self.count] = wrapped
        return wrapped

    def delete_at(self, index: int) -> None:
        if not (1 <= index <= self.count):
            raise IndexError(f"Index {index} out of range 1..{self.count}")
        if index == 1:
            logging.warning("Delete element with index 1 can lead to ambiguous behavior")
        self._native_delete_at(index)
        self.rebuild_cache()

    def rebuild_cache(self) -> None:
        self._by_index.clear()
        for i in range(1, self.count + 1):
            native_child = self._native_get(i)
            self._by_index[i] = self._child_from_native(native_child)

