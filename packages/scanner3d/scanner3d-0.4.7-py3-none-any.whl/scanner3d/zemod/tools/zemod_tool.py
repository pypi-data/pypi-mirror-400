from __future__ import annotations
from typing import TYPE_CHECKING
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.tools.zemod_tool_settings import ZeModToolSettings

if TYPE_CHECKING:
    from zempy.zosapi.tools.protocols.i_system_tool import ISystemTool

class ZeModTool(NativeAdapter["ISystemTool"]):
    __slots__ = ("_settings", "analysis_idm", "_closed")

    def __init__(self, native: "ISystemTool") -> None:
        super().__init__(native)
        self._closed: bool = False

    def apply_settings(self, settings:ZeModToolSettings):
        settings.apply_to(self)

    def run_wait_for_completion(self):
        return self.native.RunAndWaitForCompletion()

    def run(self) -> bool:
        return self.native.Run()

    def close(self) -> None:
        if self._closed:
            return
        try:
            self.native.Close()
        finally:
            self._closed = True

    def __repr__(self) -> str:
        native_t = type(self.native).__name__
        return f"{self.__class__.__name__}(closed={self._closed}, native={native_t})"

    __str__ = __repr__
