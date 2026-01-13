from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from scanner3d.afs.i_shot_meta import IShotMeta
from gosti.zernike.zernike_report import ZernikeReport

@dataclass(frozen=True)
class ZernikeMeta(IShotMeta):
    """
    Summary metrics that we want to use as Shot meta.
    """
    pv_to_chief: Optional[float]
    pv_to_centroid: Optional[float]

    rms_to_chief_rays: Optional[float]
    rms_to_centroid_rays: Optional[float]

    rms_to_chief_fit: Optional[float]
    rms_to_centroid_fit: Optional[float]

    variance_rays: Optional[float]
    variance_fit: Optional[float]

    strehl_rays: Optional[float]
    strehl_fit: Optional[float]

    rms_fit_error: Optional[float]
    max_fit_error: Optional[float]

    @classmethod
    def from_report(cls, r: ZernikeReport) -> ZernikeMeta:
        return cls(
            pv_to_chief=r.pv_to_chief,
            pv_to_centroid=r.pv_to_centroid,
            rms_to_chief_rays=r.rms_to_chief_rays,
            rms_to_centroid_rays=r.rms_to_centroid_rays,
            rms_to_chief_fit=r.rms_to_chief_fit,
            rms_to_centroid_fit=r.rms_to_centroid_fit,
            variance_rays=r.variance_rays,
            variance_fit=r.variance_fit,
            strehl_rays=r.strehl_rays,
            strehl_fit=r.strehl_fit,
            rms_fit_error=r.rms_fit_error,
            max_fit_error=r.max_fit_error)

    def __str__(self) -> str:
        def fmt(x: Optional[float]) -> str:
            if x is None:
                return "—"
            return f"{x:.4g}"
        rows = [
            ("PV to chief",           fmt(self.pv_to_chief)),
            ("PV to centroid",        fmt(self.pv_to_centroid)),
            ("RMS rays → chief",      fmt(self.rms_to_chief_rays)),
            ("RMS rays → centroid",   fmt(self.rms_to_centroid_rays)),
            ("RMS fit → chief",       fmt(self.rms_to_chief_fit)),
            ("RMS fit → centroid",    fmt(self.rms_to_centroid_fit)),
            ("Variance (rays)",       fmt(self.variance_rays)),
            ("Variance (fit)",        fmt(self.variance_fit)),
            ("Strehl (rays)",         fmt(self.strehl_rays)),
            ("Strehl (fit)",          fmt(self.strehl_fit)),
            ("RMS fit error",         fmt(self.rms_fit_error)),
            ("Max fit error",         fmt(self.max_fit_error)),
        ]
        left_width = max(len(label) for label, _ in rows)
        body = "\n".join(f"{label:<{left_width}} : {value}" for label, value in rows)
        return (f"ℹ️ Zernike Meta data\n"
                f"────────────────────────────\n"
                f"{body}")