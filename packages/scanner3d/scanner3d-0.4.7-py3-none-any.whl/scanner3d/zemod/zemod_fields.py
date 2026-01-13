from __future__ import annotations
from typing import TYPE_CHECKING
from scanner3d.zemod.core.indexed_collection import IndexedCollection
from scanner3d.zemod.zemod_field import ZeModField
from scanner3d.zemod.enums import ZeModFieldNormalizationType, ZeModFieldTypes
if TYPE_CHECKING:
    from zempy.zosapi.systemdata.protocols.i_fields import IFields
    from zempy.zosapi.systemdata.protocols.i_field import IField

from zempy.zosapi.systemdata.enums.field_type import FieldType
from zempy.zosapi.systemdata.enums.field_normalization_type import FieldNormalizationType

class ZeModFields(IndexedCollection[ZeModField, "IFields", "IField"]):
    __slots__ = ()

    def _native_count(self) -> int:
        return int(self.native.NumberOfFields)

    def _native_get(self, index: int) -> "IField":
        return self.native.GetField(index)

    def _native_add(self, x: float, y: float, w: float = 1.0) -> "IField":
        return self.native.AddField(float(x), float(y), float(w))

    def _native_delete_at(self, index:int) -> None:
        self.native.DeleteFieldAt(index)

    def _child_from_native(self, native_child: "IField") -> ZeModField:
        return ZeModField(native_child)

    @property
    def n_fields(self) -> int:
        return self.count

    def get_field(self, index: int) -> ZeModField:
        return self.get_child(index)

    def add_field(self, x: float, y: float, w: float = 1.0) -> ZeModField:
        return self.add_child(x, y, w)

    def get_field_type(self) -> ZeModFieldTypes:
        native_ft = self.native.GetFieldType()
        return ZeModFieldTypes(native_ft)

    def set_field_type(self, field_type: ZeModFieldTypes) -> None:
        self.native.SetFieldType(FieldType(field_type.value))

    def get_normalization(self) -> ZeModFieldNormalizationType:
        native_normalization = self.native.Normalization
        return ZeModFieldNormalizationType(native_normalization)

    def set_normalization(self, normalization: ZeModFieldNormalizationType):
        self.native.Normalization = normalization.value
