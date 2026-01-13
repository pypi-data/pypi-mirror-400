from dataclasses import dataclass, field
from typing import Tuple
from scanner3d.camera3d import Camera3D

@dataclass(frozen=True, slots=True)
class Scanner:
    name: str
    cameras: Tuple["Camera3D", ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        cam_list = ", ".join(c.name for c in self.cameras) if self.cameras else "—"
        return (
            f"🔭 Scanner '{self.name}'\n"
            f"────────────────────────\n"
            f"  cameras : {cam_list}\n"
            f"  count   : {len(self.cameras)}"
        )

    def __repr__(self) -> str:
        return f"Scanner(name={self.name!r}, cameras={[c.name for c in self.cameras]!r})"