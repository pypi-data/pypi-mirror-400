from __future__ import annotations
import numpy as np
from allytools.units import  Length, LengthUnit
from typing import Optional, Tuple, TYPE_CHECKING
from imagera.plotter import plt_scalars2d, PltScalar2d, PlotParameters, CMaps
from imagera.image import ImageBundle


if TYPE_CHECKING:
    from scanner3d.afs.frame import Frame
    from scanner3d.afs.shot import Shot

def plot_frame(
    frame: Frame,
    plot_params: Optional[PlotParameters] = None,
    *,
    cmap=CMaps.JET,
    dpi: int = 300,
    fig_size_in: Tuple[Length, Length] = (Length(3, LengthUnit.INCH), Length(3, LengthUnit.INCH)),
    with_colorbar: bool = True,
    tile_titles: bool = False,
    mosaic_title: str | None = None,
) -> ImageBundle:
    profile = frame.profile
    default_title = (
        f"PSF Frame for {profile.objective_id}\n"
        f"with sensor {profile.sensor_model} at {profile.working_distance:.3f} mm"
    )
    title = mosaic_title or default_title
    if plot_params is None:
        plot_params = PlotParameters(cmap=cmap, dpi=dpi, size_in=fig_size_in)

    x_seq = np.asarray(frame.x_seq_mm, dtype=float)
    y_seq = np.asarray(frame.y_seq_mm, dtype=float)
    X, Y = np.meshgrid(x_seq, y_seq)           # (R, C)
    grid = np.stack((X, Y), axis=-1)           # (R, C, 2)

    # Frame.values is (n_shots, Ny, Nx) ordered in y-major grid
    R = len(y_seq)
    C = len(x_seq)
    Ny, Nx = frame.values.shape[-2:]
    values_array = frame.values.reshape(R, C, Ny, Nx)
    array_image =plt_scalars2d(
        grid=grid,
        values_array=values_array,
        params=plot_params,
        with_colorbar=with_colorbar,
        tile_titles=tile_titles,
        mosaic_title=title)
    return ImageBundle(array_image)


def plot_shot(
    shot: Shot,
    plot_params: Optional[PlotParameters] = None,
    *,
    plot_label: str | None = None,
    cmap=CMaps.JET,
    dpi: int = 300,
    fig_size_in: Tuple[Length, Length] = (Length(3, LengthUnit.INCH), Length(3, LengthUnit.INCH)),
    with_colorbar: bool = True,
    mosaic_title: str | None = None,
) -> ImageBundle:

    if plot_params is None:
        plot_params = PlotParameters(
            cmap=cmap,
            dpi=dpi,
            size_in=fig_size_in,
            with_colorbar=with_colorbar,
            plot_label=plot_label)

    scalar2d = PltScalar2d(
        shot.result.values,
        params=plot_params,
        extent=shot.result.extent,
        hide_ticks=False,
        show_lattice=True,
        lattice_color=(1, 1, 1, 0.4),
    )
    array_image = scalar2d.render(plot_label=plot_label)
    return ImageBundle(array_image)


