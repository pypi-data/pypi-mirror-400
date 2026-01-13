from __future__ import annotations
from typing import TYPE_CHECKING, Optional, overload, Literal
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.tools.zemod_tool import ZeModTool
from scanner3d.zemod.tools.zemod_batch_raytrace_tool import ZeModBatchRayTraceTool
from scanner3d.zemod.tools.zemod_tool_settings import ZeModToolSettings
from scanner3d.zemod.tools.zemod_tool_list import ZeModToolList
from scanner3d.ray_trace.raytrace_settings import RayTraceSettings

if TYPE_CHECKING:
    from zempy.zosapi.tools.protocols.i_optical_system_tools import IOpticalSystemTools
    from zempy.zosapi.tools.protocols.i_system_tool import ISystemTool

class ZeModTools(NativeAdapter["IOpticalSystemTools"]):
    __slots__ = ("_active",)

    def __init__(self, native: "IOpticalSystemTools") -> None:
        super().__init__(native)
        self._active: Optional[ZeModTool] = None

    def _native_get_current(self) -> ISystemTool:
        return self.native.CurrentTool()

    def status(self) -> str:
        return  self.native.Status

    def progress(self) -> int:
        return  self.native.Progress

    def get_batch_ray_tracer(self) -> ZeModTool:
        native_tool = self.native.OpenBatchRayTrace()
        tool = ZeModTool(native_tool)
        return tool

    def run_quick_focus(self, settings: ZeModToolSettings) :
        return self.run_tool(ZeModToolList.QUICK_FOCUS, settings)

    @overload
    def run_tool(
        self,
        tool_type: Literal[ZeModToolList.BATCH_RAYTRACE],
        settings: RayTraceSettings,
    ) -> ZeModBatchRayTraceTool: ...

    @overload
    def run_tool(
        self,
        tool_type: ZeModToolList,
        settings: ZeModToolSettings,
    ) -> ZeModTool: ...

    def run_tool(self, tool_type: ZeModToolList, settings: ZeModToolSettings) -> ZeModTool:
        expected_type = tool_type.settings_type

        if settings is None:
            raise Exception(f"Cannot run tool {tool_type.method_name} without settings")

        if expected_type is not None and not isinstance(settings, expected_type):
            raise TypeError(
                f"Incorrect settings for tool {tool_type.name}: "
                f"expected {expected_type.__name__}, got {type(settings).__name__}"
            )
        open_method = getattr(self.native, tool_type.method_name)
        with open_method() as native_tool:
            tool_cls = tool_type.tool_cls
            tool = tool_cls(native_tool)
            tool.apply_settings(settings)
            tool.run_wait_for_completion()
            return tool


