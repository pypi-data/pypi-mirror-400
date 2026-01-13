from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence
from numpy.typing import NDArray
from scanner3d.afs.i_shot_result import IShotResult, ShotResultType
from scanner3d.analysis.zernike_meta import ZernikeMeta
from gosti.zernike.zernike_aid import get_zernike_text_from_result
from gosti.zernike.parse_zenike_text import parse_zernike_text
from gosti.zernike.zernike_term import ZernikeTerm

@dataclass(frozen=True)
class ZernikeData(IShotResult[ZernikeMeta]):

    _terms: List[ZernikeTerm]
    _meta: ZernikeMeta

    @property
    def result_type(self) -> ShotResultType:
        return ShotResultType.ZERNIKE

    @property
    def shape(self) -> tuple[int, ...]:
        return (len(self._terms),)

    def get_raw(self) -> NDArray[np.float64]:
        coeffs = [t.coefficient for t in sorted(self._terms, key=lambda t: t.index)]
        return np.asarray(coeffs, dtype=np.float64)

    @property
    def meta(self) -> ZernikeMeta:
        return self._meta

    @property
    def terms(self) -> List[ZernikeTerm]:
        return self._terms


    @classmethod
    def from_result(cls, result) -> ZernikeData:
        """
        Build from a ZOSAPI result that supports GetTextFile(...).

        Typical usage:
            native = analysis.run()
            zern = ZernikeData.from_result(native)
        """
        text = get_zernike_text_from_result(result)
        return cls.from_text(text)

    @classmethod
    def from_dat_file(cls, path: Path | str) -> ZernikeData:
        """
        Build from a Zernike .DAT text file saved earlier.
        """
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        text = text.replace("\x00", "") # in case of old UTF-16 exports with stray NULs
        return cls.from_text(text)

    @classmethod
    def from_text(cls, text: str) -> "ZernikeData":
        report = parse_zernike_text(text)
        meta = ZernikeMeta.from_report(report)
        return cls(_terms=report.terms, _meta=meta)

    @classmethod
    def from_components(
        cls,
        coefficients: Sequence[float] | NDArray[np.float64],
        meta: ZernikeMeta,
        labels: Optional[Sequence[str]] = None,
    ) -> ZernikeData:
        arr = np.asarray(coefficients, dtype=np.float64)
        if arr.ndim != 1:
            raise ValueError(f"ZernikeData.from_components expects 1D coefficients, got shape {arr.shape}")
        n = arr.shape[0]
        if labels is None:
            labels = [""] * n
        elif len(labels) != n:
            raise ValueError(f"len(labels)={len(labels)} must match number of coefficients={n}")
        terms = [
            ZernikeTerm(index=i + 1, coefficient=float(arr[i]), label=labels[i])
            for i in range(n)]
        return cls(_terms=terms, _meta=meta)

    def __str__(self) -> str:
        lines: list[str] = []
        for t in sorted(self._terms, key=lambda x: x.index):
            if abs(t.coefficient) > 0:  # non-zero only
                label = f"  # {t.label}" if t.label else ""
                lines.append(f"Z {t.index:3d} : {t.coefficient: .8f}{label}")
        if not lines:
            return "ZernikeData: (all coefficients are zero)"
        return ("🌀ℤ Zernike Data\n" +
                "────────────────────────────\n" +
                "\n".join(lines))