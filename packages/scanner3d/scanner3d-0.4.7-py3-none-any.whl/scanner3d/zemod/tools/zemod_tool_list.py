from enum import Enum
from typing import Optional, Type
from scanner3d.zemod.tools.zemod_tool_settings import ZeModToolSettings
from scanner3d.zemod.tools.zemod_tool import ZeModTool
from scanner3d.zemod.tools.zemod_batch_raytrace_tool import ZeModBatchRayTraceTool
from scanner3d.zemod.tools.quickfocus_settings import QuickFocusSettings
from scanner3d.ray_trace.raytrace_settings import RayTraceSettings


class ZeModToolList(Enum):
    QUICK_FOCUS = ("OpenQuickFocus", QuickFocusSettings, ZeModTool)
    BATCH_RAYTRACE = ("OpenBatchRayTrace", RayTraceSettings, ZeModBatchRayTraceTool)

    def __init__(
        self,
        method_name: str,
        settings_type: Optional[Type[ZeModToolSettings]],
        tool_cls: Type[ZeModTool],
    ):
        self.method_name = method_name
        self.settings_type = settings_type
        self.tool_cls = tool_cls
