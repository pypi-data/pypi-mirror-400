from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import  Path
from typing import Generic, List, Iterator
from scanner3d.ray_trace.ray_batch import RayBatch, T_Ray
from scanner3d.h5.ray_batch.ray_batches_save import ray_batches_save

@dataclass
class RayBatches(Generic[T_Ray]):    
    batches: List[RayBatch[T_Ray]] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.batches)

    def __getitem__(self, idx: int) -> RayBatch[T_Ray]:
        return self.batches[idx]

    def __iter__(self) -> Iterator[RayBatch[T_Ray]]:
        return iter(self.batches)

    def append(self, batch: RayBatch[T_Ray]) -> None:
        self.batches.append(batch)

    def extend(self, batches: List[RayBatch[T_Ray]]) -> None:
        self.batches.extend(batches)

    @property
    def n(self) -> int:
        """Number of RayBatch objects."""
        return len(self.batches)

    def last(self) -> RayBatch[T_Ray]:
        """Return most recent batch."""
        if not self.batches:
            raise IndexError("RayBatches is empty")
        return self.batches[-1]

    def first(self) -> RayBatch[T_Ray]:
        """Return first batch."""
        if not self.batches:
            raise IndexError("RayBatches is empty")
        return self.batches[0]

    def save_to_h5(self, path: Path | str,**kwargs):
        return ray_batches_save(batches=self, path=Path(path), **kwargs)


