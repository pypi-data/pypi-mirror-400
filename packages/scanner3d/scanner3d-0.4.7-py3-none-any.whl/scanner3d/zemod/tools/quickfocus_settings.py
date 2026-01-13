from __future__ import annotations
import logging
from dataclasses import dataclass
from allytools.types.validate_cast import validate_cast
from scanner3d.zemod.tools.zemod_tool import ZeModTool
from scanner3d.zemod.tools.zemod_tool_settings import ZeModToolSettings
from scanner3d.zemod.enums import ZeModQuickFocusCriterion
from zempy.zosapi.tools.general.protocols.quickfocus.i_quick_focus import IQuickFocus


logger = logging.getLogger(__name__)
@dataclass(frozen=True)
class QuickFocusSettings (ZeModToolSettings):
    criterion: ZeModQuickFocusCriterion = ZeModQuickFocusCriterion.SpotSizeRadial
    use_centroid: bool = True

    def apply_to(self, tool: ZeModTool) -> None:
        native = validate_cast(tool.native, IQuickFocus)
        logger.debug(f"QuickFocus settings: criterion = {self.criterion }")
        native.Criterion =self.criterion
        logger.debug(f"QuickFocus settings: use centroid = {self.use_centroid }")
        native.UseCentroid =self.use_centroid