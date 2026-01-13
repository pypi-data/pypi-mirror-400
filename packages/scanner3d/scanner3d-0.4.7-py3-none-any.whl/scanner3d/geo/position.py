from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True, slots=True)
class Position:
    x: float
    y: float
    z: float
    roll: float  # rotation about X
    pitch: float # rotation about Y
    yaw: float   # rotation about Z

    def as_position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    def as_radians(self) -> tuple[float, float, float]:
        roll_r, pitch_r, yaw_r = map(np.radians, (self.roll, self.pitch, self.yaw))
        return float(roll_r), float(pitch_r), float(yaw_r)

    def rotation_matrix(self) -> np.ndarray:
        """Return 3×3 rotation matrix (ZYX convention)."""
        cr, sr = np.cos(np.radians(self.roll)), np.sin(np.radians(self.roll))
        cp, sp = np.cos(np.radians(self.pitch)), np.sin(np.radians(self.pitch))
        cy, sy = np.cos(np.radians(self.yaw)), np.sin(np.radians(self.yaw))
        # Rz(yaw) * Ry(pitch) * Rx(roll)
        return np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp,   cp*sr,            cp*cr]
        ], dtype=np.float64)
