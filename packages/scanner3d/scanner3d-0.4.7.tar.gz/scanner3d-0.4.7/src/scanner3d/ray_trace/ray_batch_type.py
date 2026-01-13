from enum import Enum

class RayBatchType(Enum):
    OnLastSurface   = "ray batch traced to image (last surface)"
    OnZeroSurface      = "ray batch traced to object (zero surface)"

    def to_surface(self, lde) -> int:
        return _RBT_TO_SURFACE[self](lde)

_RBT_TO_SURFACE = {
    RayBatchType.OnZeroSurface:  lambda lde: 0,
    RayBatchType.OnLastSurface: lambda lde: lde.n_surfaces - 1,
}

REQUIRED_FOR_TEST = frozenset({
    RayBatchType.OnLastSurface,
    RayBatchType.OnZeroSurface,
})