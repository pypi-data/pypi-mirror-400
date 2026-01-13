from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
if TYPE_CHECKING:
    from scanner3d.zemod.tools.zemod_tool import ZeModTool

@runtime_checkable
class ZeModToolSettings(Protocol):
    def apply_to(self, tool: ZeModTool) -> None: ...