from allytools.units import Length, LengthUnit
from scanner3d.test.base.album_settings import AlbumSettings, ALBUM_TYPES_REG, AlbumTypes

album_major_frame_5 = AlbumSettings(
    name= "Major 5 Frames",
    album_type=AlbumTypes.MAJOR_FRAMES,
    template=ALBUM_TYPES_REG[AlbumTypes.MAJOR_FRAMES],
    dx=5,
    dy=5,
    dz=None,
)

album_major_frame_3 = AlbumSettings(
    name= "Major 3 Frames",
    album_type=AlbumTypes.MAJOR_FRAMES,
    template=ALBUM_TYPES_REG[AlbumTypes.MAJOR_FRAMES],
    dx=3,
    dy=3,
    dz=None,
)

album_radial_detailed = AlbumSettings(
    name= "Radial Detailed",
    album_type=AlbumTypes.RADIAL,
    template=ALBUM_TYPES_REG[AlbumTypes.RADIAL],
    dx=Length(50, LengthUnit.UM),
    dy=None,
    dz=Length(5),
)

album_radial_quick = AlbumSettings(
    name="Radial Quick",
    album_type=AlbumTypes.RADIAL,
    template=ALBUM_TYPES_REG[AlbumTypes.RADIAL],
    dx=Length(500, LengthUnit.UM),
    dy=None,
    dz=Length(50),
)

album_sparse_grid_detailed = AlbumSettings(
    name="Sparse Grid Detailed",
    album_type=AlbumTypes.SPARSE_GRID,
    template=ALBUM_TYPES_REG[AlbumTypes.SPARSE_GRID],
    dx=50,
    dy=50,
    dz=Length(5),
)

album_sparse_grid_quick = AlbumSettings(
    name="Sparse Grid Quick",
    album_type=AlbumTypes.SPARSE_GRID,
    template=ALBUM_TYPES_REG[AlbumTypes.SPARSE_GRID],
    dx=500,
    dy=500,
    dz=Length(50),
)