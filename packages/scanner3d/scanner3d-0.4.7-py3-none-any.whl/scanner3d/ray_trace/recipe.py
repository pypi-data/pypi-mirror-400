from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, Tuple, Type, Any
from zempy.zosapi.tools.raytrace.results import Ray


@dataclass(frozen=True)
class Recipe:
    create: Callable[..., Any]                               # -> buffer
    add_one: Callable[..., None]                             # (buf, *coords)
    read_next: Callable[[Any], Any]                          # (buf) -> rec
    accept: Callable[[Any], bool]                            # record -> bool
    coord_iter: Callable[[], Iterable[Tuple]]                # yields tuples for add_one
    ray_class: Type[Ray]
