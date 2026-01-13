from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, kw_only=True)
class Profile:
    file: str
    name: str
    title: str
    author:str
    notes:str
    working_distance: float
    focusing_distance: float
    sensor_model: str
    objective_id: str
    f_number: float



