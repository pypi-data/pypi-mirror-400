from __future__ import annotations

import os
from enum import EnumMeta
from types import ModuleType
from typing import Optional, Any

import scanner3d.zemod.enums.enums as zemod_enums


def generate_enum_stubs(module: ModuleType, pyi_path: Optional[str] = None) -> str:

    if pyi_path is None:
        module_file = module.__file__
        if module_file is None:
            raise RuntimeError(f"Module {module.__name__} has no __file__")
        base, _ = os.path.splitext(module_file)
        pyi_path = base + ".pyi"

    lines: list[str] = [
        "from enum import Enum",
        "from typing import Any",
        "",
        "",
    ]

    items = sorted(module.__dict__.items(), key=lambda kv: kv[0])

    for name, obj in items:
        if not name.startswith("ZeMod"):
            continue
        if not isinstance(obj, EnumMeta):
            continue

        lines.append(f"class {name}(Enum):")

        # --- Enum members ---
        for member in obj:
            lines.append(f'    {member.name}: "{name}"')

        lines.append("")
        # --- Properties and methods ---
        lines.append("    @property")
        lines.append("    def value(self) -> Any: ...")
        lines.append("")
        lines.append("    @property")
        lines.append("    def native(self) -> Any: ...")
        lines.append("")
        lines.append("    def __int__(self) -> int: ...")
        lines.append("")
        lines.append("")

    text = "\n".join(lines)

    os.makedirs(os.path.dirname(pyi_path), exist_ok=True)
    with open(pyi_path, "w", encoding="utf-8") as f:
        f.write(text)

    return pyi_path


if __name__ == "__main__":
    path = generate_enum_stubs(zemod_enums)
    print(f"Written stub: {path}")
