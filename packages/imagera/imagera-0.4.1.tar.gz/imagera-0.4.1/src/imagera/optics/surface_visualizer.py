from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Protocol, runtime_checkable

import numpy as np

try:
    import pyvista as pv
except Exception:  # pragma: no cover
    pv = None  # type: ignore[assignment]


ScalarMode = Literal["none", "auto", "z", "custom"]

@dataclass(frozen=True)
class PyVistaSurfaceVizConfig:
    stride: int = 2
    show_edges: bool = False
    wireframe: bool = False
    smooth_shading: bool = True
    show_axes: bool = True
    show_bounds: bool = False
    background: str = "white"
    close_v_seam: bool = True  # generalization of close_phi_seam


@dataclass
class PyVistaSurfaceVisualizer:
    cfg: PyVistaSurfaceVizConfig = PyVistaSurfaceVizConfig()

    def _downsample(self, A: np.ndarray) -> np.ndarray:
        s = max(1, int(self.cfg.stride))
        if A.ndim == 3:
            return A[::s, ::s, :]
        if A.ndim == 2:
            return A[::s, ::s]
        raise ValueError(f"Expected 2D or 3D array, got shape {A.shape}")

    def _close_v_seam_2d(self, A: np.ndarray) -> np.ndarray:
        # duplicate first column to end
        return np.concatenate([A, A[:, :1]], axis=1)

    def _close_v_seam_3d(self, A: np.ndarray) -> np.ndarray:
        # duplicate first column to end (keeping last dimension = 3)
        return np.concatenate([A, A[:, :1, :]], axis=1)

    def to_mesh(
        self,
        surface: SurfaceABC,
        scalar: ScalarMode = "auto",
        custom_scalar: Optional[np.ndarray] = None,
        scalar_name: str = "scalar",
    ) -> "pv.PolyData":
        """
        Build a PolyData surface mesh with point normals + optional scalars.

        We create a StructuredGrid then extract its surface (PolyData).
        Normals are attached from surface.normals() (important for optical correctness).
        """
        if pv is None:
            raise ImportError("pyvista is not installed. Install with: pip install pyvista vtk")

        P = self._downsample(surface.points())   # (n_u, n_v, 3)
        N = self._downsample(surface.normals())  # (n_u, n_v, 3)

        if P.shape != N.shape:
            raise ValueError(f"points shape {P.shape} must match normals shape {N.shape}")

        close = bool(self.cfg.close_v_seam and surface.is_periodic_v())
        if close:
            P = self._close_v_seam_3d(P)
            N = self._close_v_seam_3d(N)

        X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
        grid = pv.StructuredGrid(X, Y, Z)

        # Extract surface triangles/quads
        mesh = grid.extract_surface()

        # Attach normals as point data (VTK expects (n_points, 3))
        mesh.point_data["Normals"] = N.reshape(-1, 3, order="F")

        # Attach scalars
        if scalar != "none":
            if scalar == "z":
                data2d = Z if not close else Z  # already closed in P
                name = "z"
            elif scalar == "custom":
                if custom_scalar is None:
                    raise ValueError("custom_scalar must be provided when scalar='custom'")
                if custom_scalar.ndim != 2:
                    raise ValueError(f"custom_scalar must be 2D, got {custom_scalar.shape}")
                # Note: custom scalar is on the *original* grid, so downsample it
                data2d = self._downsample(custom_scalar)
                if close:
                    data2d = self._close_v_seam_2d(data2d)
                name = scalar_name
            elif scalar == "auto":
                name = surface.default_scalar_name()
                data2d = self._downsample(surface.scalar(name))
                if close:
                    data2d = self._close_v_seam_2d(data2d)
            else:
                raise ValueError(f"Unknown scalar mode: {scalar}")
            mesh.point_data[name] = np.asarray(data2d, dtype=float).ravel(order="F")
        return mesh

    def show_3d(
        self,
        surface: SurfaceABC,
        title: str = "",
        scalar: ScalarMode = "auto",
        custom_scalar: Optional[np.ndarray] = None,
        scalar_name: str = "scalar",
        clim: Optional[tuple[float, float]] = None,
    ) -> "pv.Plotter":
        if pv is None:
            raise ImportError("pyvista is not installed. Install with: pip install pyvista vtk")

        mesh = self.to_mesh(
            surface,
            scalar=scalar,
            custom_scalar=custom_scalar,
            scalar_name=scalar_name,
        )

        plotter = pv.Plotter(title=title)
        plotter.set_background(self.cfg.background)

        scalars_name = None
        if scalar != "none":
            scalars_name = (
                "z" if scalar == "z"
                else (scalar_name if scalar == "custom" else surface.default_scalar_name())
            )

        plotter.add_mesh(
            mesh,
            scalars=scalars_name,
            show_edges=self.cfg.show_edges,
            style="wireframe" if self.cfg.wireframe else "surface",
            smooth_shading=self.cfg.smooth_shading,
            clim=clim,
        )

        if self.cfg.show_axes:
            plotter.show_axes()
        if self.cfg.show_bounds:
            plotter.show_bounds(grid="front", location="outer")

        plotter.show()
        return plotter

    def show_3d_qt(
        self,
        surface: SurfaceABC,
        title: str = "",
        scalar: ScalarMode = "auto",
        custom_scalar: Optional[np.ndarray] = None,
        scalar_name: str = "scalar",
        clim: Optional[tuple[float, float]] = None,
    ):
        if pv is None:
            raise ImportError("pyvista is not installed. Install with: pip install pyvista vtk")
        try:
            from pyvistaqt import BackgroundPlotter
        except Exception as e:
            raise ImportError("pyvistaqt is not installed. Install with: pip install pyvistaqt") from e

        mesh = self.to_mesh(
            surface,
            scalar=scalar,
            custom_scalar=custom_scalar,
            scalar_name=scalar_name,
        )

        plotter = BackgroundPlotter(title=title)
        plotter.set_background(self.cfg.background)

        scalars_name = None
        if scalar != "none":
            scalars_name = (
                "z" if scalar == "z"
                else (scalar_name if scalar == "custom" else surface.default_scalar_name())
            )

        plotter.add_mesh(
            mesh,
            scalars=scalars_name,
            show_edges=self.cfg.show_edges,
            style="wireframe" if self.cfg.wireframe else "surface",
            smooth_shading=self.cfg.smooth_shading,
            clim=clim,
        )

        if self.cfg.show_axes:
            plotter.show_axes()
        if self.cfg.show_bounds:
            plotter.show_bounds(grid="front", location="outer")

        return plotter
