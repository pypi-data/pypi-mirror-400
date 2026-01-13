RAYBATCH_H5_VERSION = "1.0"

class RayBatchH5:
    """Names of datasets/attrs inside one RayBatch group."""
    FORMAT_VERSION = "format_version"

    # optional default group name for a single-batch file
    GROUP = "ray_batch"

    # grid / ray-trace meta
    GRID = "grid"           # dataset, shape (2,)
    TO_SURFACE = "to_surface"
    WAVE_NUMBER = "wave_number"
    RAYS_TYPE = "rays_type"     # string repr of enum or type
    METHOD = "method"           # string repr of tool/method
    PROCESS_TIME = "process_time"
    BATCH_TYPE = "batch_type"   # <--- NEW

    X_LIN = "x_lin"         # dataset, shape (gx,)
    Y_LIN = "y_lin"         # dataset, shape (gy,)

    # per-ray values
    FIELD_NAMES = "field_names"  # 1D string dataset: ["x", "y", "z", ...]
    VALUES = "values"            # 2D float dataset: (N, n_fields)
