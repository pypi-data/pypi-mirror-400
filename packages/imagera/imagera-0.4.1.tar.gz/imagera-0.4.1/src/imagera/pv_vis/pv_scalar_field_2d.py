import numpy as np
import pyvista as pv
from enum import Enum
from allytools.logger import get_logger

class ZMode(Enum):
    FIELD = "field"
    FLAT  = "flat"

log = get_logger(__name__)

def pv_scalar_field_2d(
    *,
    x: np.ndarray,
    y: np.ndarray,
    field: np.ndarray,
    mask=None,
    scalar_name: str = "field",
    z_mode: ZMode = ZMode.FIELD,
    z_scale: float = 1.0,
    scalar_scale: float = 1.0,
    show_axes: bool = True,
    show_scalar_bar: bool = True,
    nan_policy: str = "mask",   # "mask" or "keep"
    clim: str | tuple[float, float] | None = None,  # None | "robust" | (vmin, vmax)
) -> pv.Plotter:

    field = np.asarray(field, dtype=float)
    if field.ndim != 2:
        raise ValueError("field must be a 2D array (ny, nx).")

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y)
    elif x.ndim == 2 and y.ndim == 2:
        X, Y = x, y
    else:
        raise ValueError("x and y must both be 1D or both be 2D arrays.")

    if X.shape != field.shape or Y.shape != field.shape:
        raise ValueError(f"Shape mismatch: X{X.shape}, Y{Y.shape}, field{field.shape} must match.")

    # Build / combine mask
    if mask is None:
        mask = np.isfinite(field) if nan_policy == "mask" else np.ones_like(field, dtype=bool)
    else:
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != field.shape:
            raise ValueError(f"mask shape {mask.shape} must match field shape {field.shape}.")
        if nan_policy == "mask":
            mask &= np.isfinite(field)

    # Scalars for coloring (set outside-mask to NaN so ranges behave nicely)
    scalars = (field * scalar_scale).astype(float, copy=False)
    scalars = scalars.copy()
    scalars[~mask] = np.nan

    # Optional auto z-scale ONLY if user didn't intentionally set it
    if z_mode is ZMode.FIELD and z_scale == 1.0:
        valid = mask & np.isfinite(field)
        f = field[valid]
        if f.size:
            field_ptp = float(np.nanmax(f) - np.nanmin(f))
            xy_ptp = float(max(np.ptp(X), np.ptp(Y)))
            if field_ptp > 0 and xy_ptp > 0:
                z_scale = 0.5 * xy_ptp / field_ptp
                log.info("auto z_scale applied: %g", z_scale)

    # Geometry Z
    if z_mode is ZMode.FIELD:
        Z = (field * z_scale).astype(float)
        Z = Z.copy()
        Z[~mask] = np.nan  # avoid crazy bounds from invalid regions
    elif z_mode is ZMode.FLAT:
        Z = np.zeros_like(field, dtype=float)
    else:
        raise ValueError(f"Unsupported z_mode: {z_mode}")

    grid = pv.StructuredGrid(X[:, :, None], Y[:, :, None], Z[:, :, None])

    # StructuredGrid point ordering is Fortran-like
    grid.point_data[scalar_name] = scalars.ravel(order="F")
    grid.point_data["__mask__"] = mask.astype(np.uint8).ravel(order="F")

    th = grid.threshold(0.5, scalars="__mask__", preference="point")
    surf = th.extract_surface()

    # Determine color limits (robust helps when a few outliers ruin the colormap)
    add_mesh_kwargs = dict(scalars=scalar_name, show_scalar_bar=show_scalar_bar)
    if clim == "robust":
        s = surf.point_data[scalar_name]
        s = s[np.isfinite(s)]
        if s.size:
            vmin, vmax = np.percentile(s, [2, 98])
            add_mesh_kwargs["clim"] = (float(vmin), float(vmax))
    elif isinstance(clim, tuple):
        add_mesh_kwargs["clim"] = clim

    p = pv.Plotter()
    p.add_mesh(surf, **add_mesh_kwargs)

    if show_axes:
        p.show_axes()

    # Key for “white screen”: force a sensible view
    p.reset_camera()
    p.view_xy()

    return p
