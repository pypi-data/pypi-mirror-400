from __future__ import annotations
from pathlib import Path
import importlib
import inspect
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType
    from typing import ClassVar, Mapping


# --- Ensure the project "src" directory is on sys.path ---
_THIS_FILE = Path(__file__).resolve()
# Assuming layout: .../src/scanner3d/scanners/generate_scannersdb_stub.py
_SRC_DIR = _THIS_FILE.parents[2]  # .../src
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# --- Compute PKG_MOD automatically based on this file's folder ---
# Example:
#   _THIS_FILE = .../src/scanner3d/scanners/generate_scannersdb_stub.py
#   _PACKAGE_DIR = .../src/scanner3d/scanners
#   _REL_PACKAGE = scanner3d/scanners
#   PKG_MOD = "scanner3d.scanners.ScannersDB"
_PACKAGE_DIR = _THIS_FILE.parent
_REL_PACKAGE = _PACKAGE_DIR.relative_to(_SRC_DIR)
PKG_MOD = ".".join(_REL_PACKAGE.parts + ("ScannersDB",))

def _format_return_type(obj) -> str:
    import inspect
    from typing import Any

    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return "Any"

    ret = sig.return_annotation
    if ret is inspect.Signature.empty:
        return "None"

    # --- string annotations ---
    if isinstance(ret, str):
        # normalize _Scanner → Scanner
        clean = ret.lstrip("_")
        if clean == "Scanner":
            return "Scanner"
        return clean

    # --- direct class types ---
    name = getattr(ret, "__name__", None)
    if name:
        # normalize private classes
        clean = name.lstrip("_")
        if clean == "Scanner":
            return "Scanner"
        return clean

    return "Any"

def main() -> int:
    try:
        mod: ModuleType = importlib.import_module(PKG_MOD)
    except Exception as exc:
        print(f"[ERROR] Failed to import {PKG_MOD}: {exc}", file=sys.stderr)
        print(
            "Hint: run from project root or ensure PYTHONPATH includes the 'src' folder.",
            file=sys.stderr,
        )
        return 1

    ScannersDB = getattr(mod, "ScannersDB", None)
    if ScannersDB is None:
        print(f"[ERROR] {PKG_MOD} has no 'ScannersDB' symbol.", file=sys.stderr)
        return 1

    registry = getattr(ScannersDB, "REGISTRY", None)
    if not registry:
        print("[ERROR] ScannersDB.REGISTRY is empty or missing.", file=sys.stderr)
        return 1

    # --- Collect methods defined directly on ScannersDB ---
    # Look into __dict__ so we see descriptors (classmethod/staticmethod)
    method_specs: list[tuple[str, str, str]] = []  # (name, kind, return_type)

    for name, value in ScannersDB.__dict__.items():
        if name.startswith("_"):
            continue
        if name == "REGISTRY":
            continue

        if isinstance(value, classmethod):
            func = value.__func__
            ret_str = _format_return_type(func)
            method_specs.append((name, "cls", ret_str))

        elif isinstance(value, staticmethod):
            func = value.__func__
            ret_str = _format_return_type(func)
            method_specs.append((name, "static", ret_str))

        elif inspect.isfunction(value):
            # instance method (probably none here, but we support it)
            ret_str = _format_return_type(value)
            method_specs.append((name, "inst", ret_str))

        else:
            # not a method (some other class attribute) – ignore
            continue

    # Sort for deterministic output
    method_specs.sort(key=lambda t: t[0])

    # --- Build .pyi content ---
    lines: list[str] = ["from typing import ClassVar, Mapping, Tuple", "from scanner3d.scanner.scanner import Scanner",
                        "", "REGISTRY: Mapping[str, Scanner]", "", "class ScannersDB:",
                        "    REGISTRY: ClassVar[Mapping[str, Scanner]]"]

    # Per-scanner attributes from REGISTRY
    for name in sorted(registry.keys()):
        lines.append(f"    {name}: ClassVar[Scanner]")

    # Methods defined on ScannersDB
    if method_specs:
        lines.append("")
        for meth_name, kind, ret_str in method_specs:
            if kind == "cls":
                lines.append("    @classmethod")
                lines.append(
                    f"    def {meth_name}(cls, *args, **kwargs) -> {ret_str}: ..."
                )
            elif kind == "static":
                lines.append("    @staticmethod")
                lines.append(
                    f"    def {meth_name}(*args, **kwargs) -> {ret_str}: ..."
                )
            else:  # instance method
                lines.append(
                    f"    def {meth_name}(self, *args, **kwargs) -> {ret_str}: ..."
                )

    # Write next to the implementation module (same folder)
    pyi_path = _THIS_FILE.with_name("ScannersDB.pyi")
    pyi_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote stub: {pyi_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
