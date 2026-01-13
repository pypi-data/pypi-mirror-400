"""
GeometryConductorAC_CC.py

2D rectangular stack geometry for a striated coated-conductor model.

Strategy
-------------------
- Build a stack of rectangular layers aligned along x (width) and y (thickness):
    HTS
    Substrate
    optional Silver (top / bottom)
    optional Copper (top / bottom / left / right)
- Each layer is created as a Gmsh OpenCASCADE rectangle (surface).
- For the HTS layer we optionally striate the superconductor into
  multiple filaments separated by grooves, using rectangle cuts.
- After all layers are built:
    - We create a circular air region around the stack.
    - We classify boundary edges of each layer into Upper / Lower /
      LeftEdge / RightEdge using only bounding boxes (robust to OCC ops).
    - We create a consistent set of 2D/1D physical groups for
      FiQuS/GetDP (materials + interfaces + outer air boundary).

surface_tag = OCC surface entity (dim=2)
curve_tag = boundary curve entity (dim=1)
"""

import logging
import math
import os
from types import SimpleNamespace
from typing import Dict, Iterable, List, Optional, Tuple

import gmsh

import fiqus.data.DataFiQuSConductor as geom  # TODO
from fiqus.data.DataFiQuS import FDM
from fiqus.utils.Utils import GmshUtils, FilesAndFolders
from fiqus.data.DataConductor import CC, Conductor

logger = logging.getLogger("FiQuS")

# ---------------------------------------------------------------------------
# Small validation helpers
# ---------------------------------------------------------------------------

def _as_float(value, *, name: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a real number, got {value!r}") from exc
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite, got {out!r}")
    return out


def _require_positive(value, *, name: str) -> float:
    v = _as_float(value, name=name)
    if v <= 0.0:
        raise ValueError(f"{name} must be > 0, got {v:g}")
    return v


def _require_non_negative_optional(value, *, name: str) -> float:
    """
    Optional thickness rule:
    - None => treated as 0 (layer absent)
    - >= 0 => ok
    - < 0  => hard error
    """
    if value is None:
        return 0.0
    v = _as_float(value, name=name)
    if v < 0.0:
        raise ValueError(f"{name} must be >= 0, got {v:g}")
    return v


def _require_int_ge(value, *, name: str, min_value: int) -> Optional[int]:
    if value is None:
        return None
    try:
        iv = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc
    if iv < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got {iv}")
    return iv


# ---------------------------------------------------------------------------
# Base class: axis-aligned rectangular layer
# ---------------------------------------------------------------------------

class _RectLayerBase:
    """
    Common base for all axis-aligned rectangular layers (HTS, substrate,
    silver, copper).

    Responsibilities
    ----------------
    - Store the main OCC surface (surface_tag).
    - Maintain lists of boundary curves (curve_tags) and points (point_tags).
    - Classify boundary curves into semantic edges:
        "Upper", "Lower", "LeftEdge", "RightEdge"
      based solely on bounding boxes (robust after OCC boolean ops).
    """

    def __init__(self) -> None:
        self.surface_tag: Optional[int] = None
        self.curve_tags:  List[int]     = []
        self.point_tags:  List[int]     = []
        self.edge_tags:   Dict[str, List[int]] = {}

    # Basic OCC -> topology refresh

    def _refresh_from_surface(self) -> None:
        """
        Refresh curve_tags and point_tags from the current surface_tag.
        This should be called after any OCC operation (cut, fuse, etc.)
        that may re-tag curves/points.
        """
        if self.surface_tag is None:
            raise RuntimeError(
                f"{self.__class__.__name__} has no surface_tag to refresh from."
            )

        boundary = gmsh.model.getBoundary( [(2, self.surface_tag)], oriented=False, recursive=False )
        self.curve_tags = [c[1] for c in boundary]

        pts: List[int] = []
        for c in self.curve_tags:
            ends = gmsh.model.getBoundary( [(1, c)], oriented=False, recursive=False )
            pts.extend([p[1] for p in ends])

        # De-duplicate while preserving order
        self.point_tags = list(dict.fromkeys(pts))

    # Edge classification

    def _classify_edges_from_bbox(self, w: float, t: float, cx: float, cy: float ) -> None:
        """
        Classify boundary curves into:
            Upper / Lower / LeftEdge / RightEdge

        Strategy
        --------
        - For each boundary curve, read its bounding box.
        - Decide whether the curve is "horizontal" (dx >= dy) or
          "vertical" (dy > dx).
        - Among all horizontal curves:
            - Those with y close to the maximum are "Upper".
            - Those with y close to the minimum are "Lower".
        - Among all vertical curves:
            - Those with x close to the minimum are "LeftEdge".
            - Those with x close to the maximum are "RightEdge".
        - Tolerance is 5% of the global span in x/y for that set.

        This is robust against most OCC operations as long as the
        rectangle is still axis-aligned overall.
        OCC fragment/cut operations can split edges into multiple curves and reorder
        tags. Using curve bounding boxes lets us recover "Upper/Lower/Left/Right" as
        long as the overall layer remains axis-aligned.
        """
        horiz: List[Tuple[int, float]] = []   # (curve_tag, y_mid)
        vert:  List[Tuple[int, float]] = []   # (curve_tag, x_mid)

        for c in self.curve_tags:
            xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, c)
            dx = abs(xmax - xmin)
            dy = abs(ymax - ymin)

            if dx >= dy:
                # Mostly horizontal
                ymid = 0.5 * (ymin + ymax)
                horiz.append((c, ymid))
            else:
                # Mostly vertical
                xmid = 0.5 * (xmin + xmax)
                vert.append((c, xmid))

        if not horiz or not vert:
            raise RuntimeError(
                f"Could not find both horizontal and vertical edges for "
                f"surface {self.surface_tag}; curves={self.curve_tags}"
            )

        # Horizontal: Upper / Lower
        ys     = [ym for _, ym in horiz]
        y_min  = min(ys)
        y_max  = max(ys)
        span_y = max(y_max - y_min, 1e-12)   # avoid zero span
        tol_y  = 0.05 * span_y               # 5% band near extremes

        upper = [c for c, ym in horiz if (y_max - ym) <= tol_y]
        lower = [c for c, ym in horiz if (ym - y_min) <= tol_y]

        # Vertical: Left / Right
        xs     = [xm for _, xm in vert]
        x_min  = min(xs)
        x_max  = max(xs)
        span_x = max(x_max - x_min, 1e-12)
        tol_x  = 0.05 * span_x

        left  = [c for c, xm in vert if (xm - x_min) <= tol_x]
        right = [c for c, xm in vert if (x_max - xm) <= tol_x]

        edge_tags: Dict[str, List[int]] = {}
        if upper:
            edge_tags["Upper"] = upper
        if lower:
            edge_tags["Lower"] = lower
        if left:
            edge_tags["LeftEdge"] = left
        if right:
            edge_tags["RightEdge"] = right

        missing = {"Upper", "Lower", "LeftEdge", "RightEdge"} - set(edge_tags)
        if missing:
            raise RuntimeError(
                f"Edges not fully classified: {missing}; "
                f"curves={self.curve_tags}, horiz={horiz}, vert={vert}"
            )

        self.edge_tags = edge_tags

    # ---- public refresh API -----------------------------------------------

    def refresh_topology(self, w: float, t: float, cx: float, cy: float) -> None:
        """
        Re-pull curves/points from the current surface and re-classify edges.

        Subclasses that use multiple surfaces (e.g. striated HTS) can
        override this method but should call _refresh_from_surface and
        _classify_edges_from_bbox at some point.
        """
        self._refresh_from_surface()
        self._classify_edges_from_bbox(w, t, cx, cy)


# ---------------------------------------------------------------------------
# HTS layer: optional striation into filaments + grooves
# ---------------------------------------------------------------------------

class HTSLayer(_RectLayerBase):
    """
    2D HTS layer, optionally striated into multiple filaments.

    Geometric parameters
    --------------------
    - HTS_thickness, HTS_width
    - HTS_center_x, HTS_center_y

    Striation model
    ---------------
    If (n_striations > 1 and striation_w > 0):
        - We build a full-width HTS rectangle.
        - We build (N - 1) vertical groove rectangles.
        - We OCC-cut the grooves out of the HTS.
        - The remaining islands are HTS filaments.
        - Grooves are kept as separate surfaces.

    Bookkeeping
    -----------
    - self.surface_tag:
        - monolithic HTS: the only HTS surface
        - striated HTS: representative filament tag (for legacy code)
    - self.filament_tags: list of all HTS filament surface IDs
    - self.groove_tags:   list of all groove surface IDs
    """

    def __init__(
        self,
        HTS_thickness: float,
        HTS_width: float,
        HTS_center_x: float,
        HTS_center_y: float,
        number_of_filaments: Optional[int] = None,
        gap_between_filaments: Optional[float] = None,
    ) -> None:
        super().__init__()

        self.HTS_thickness = float(HTS_thickness)
        self.HTS_width     = float(HTS_width)
        self.HTS_center_x  = float(HTS_center_x)
        self.HTS_center_y  = float(HTS_center_y)

        # Striation parameters
        self.n_striations = (
            int(number_of_filaments) if number_of_filaments is not None else None
        )
        self.striation_w = (
            float(gap_between_filaments)
            if gap_between_filaments is not None
            else None
        )

        # After cutting
        self.filament_tags: List[int] = []  # HTS islands
        self.groove_tags:   List[int] = []  # Groove surfaces



    
    def _refresh_from_surface(self) -> None:
        """
        Refresh boundary curves/points for the HTS layer.

        Notes on striated HTS
        ---------------------
        When striation is enabled, the HTS is represented by multiple OCC surfaces
        (one per filament). For boundary and interface physical groups we treat the
        HTS as the *union of filaments* and recover its boundary by collecting the
        boundaries of all filament surfaces.

        This deliberately ignores groove surfaces: grooves are separate regions and
        must not be part of the HTS conductor boundary.

        Fallback
        --------
        If HTS is monolithic (no filaments), we fall back to the base implementation
        using self.surface_tag.
        """

        if self.filament_tags:
            curves: List[int] = []

            for s in self.filament_tags:
                boundary = gmsh.model.getBoundary( [(2, s)], oriented=False, recursive=False )
                curves.extend( [c[1] for c in boundary] )

            self.curve_tags = list(dict.fromkeys(curves))

            pts: List[int] = []
            for c in self.curve_tags:
                ends = gmsh.model.getBoundary( [(1, c)], oriented=False, recursive=False )
                pts.extend( [p[1] for p in ends] )
            self.point_tags = list(dict.fromkeys(pts))
        else:
            super()._refresh_from_surface()



    def build_HTS(self) -> int:
        """
        Build a 2D rectangular HTS layer centered at (HTS_center_x, HTS_center_y).

        If striation parameters are valid, cut the HTS into multiple
        filaments by removing narrow vertical grooves.

        Returns
        -------
        int
            A representative HTS surface tag (for backward compatibility).
        """
        x0 = self.HTS_center_x - self.HTS_width / 2.0
        y0 = self.HTS_center_y - self.HTS_thickness / 2.0

        # Base full-width HTS rectangle
        base_tag = gmsh.model.occ.addRectangle( x0, y0, 0.0, self.HTS_width, self.HTS_thickness )
        self.surface_tag = base_tag  # initial monolithic tag

        grooves_occ: List[Tuple[int, int]] = []  # [(2, tag), ...]
        self.groove_tags   = []
        self.filament_tags = []

        # Decide whether to striate
        if (
            self.n_striations is not None
            and self.n_striations > 1
            and self.striation_w is not None
            and self.striation_w > 0.0
        ):
            N = self.n_striations
            gw = self.striation_w

            total_groove = gw * (N - 1)
            if total_groove >= self.HTS_width:
                logger.warning(
                    "[Geom-CC] Requested HTS striations do not fit in HTS width; "
                    "skipping striation (N=%d, gw=%.3g, W=%.3g).",
                    N,
                    gw,
                    self.HTS_width,
                )
            else:
                # Ensure:
                #   N * filament_width + (N - 1) * gw = HTS_width
                filament_w = (self.HTS_width - total_groove) / N

                x_left = x0
                for i in range(N - 1):
                    # Position of groove i between filament i and i+1
                    xg = x_left + (i + 1) * filament_w + i * gw
                    gtag = gmsh.model.occ.addRectangle( xg, y0, 0.0, gw, self.HTS_thickness )
                    grooves_occ.append((2, gtag))
                    self.groove_tags.append(gtag)

                # Cut grooves out of HTS:
                #   removeObject=True  -> base HTS replaced by its parts
                #   removeTool=False   -> keep the groove rectangles as surfaces
                cut_objs, _ = gmsh.model.occ.cut( [(2, base_tag)], grooves_occ, removeObject=True, removeTool=False )

                if not cut_objs:
                    raise RuntimeError("[Geom-CC] HTS striation cut produced no surfaces.")

                self.filament_tags = [e[1] for e in cut_objs]
                # Representative tag (for legacy code paths)
                self.surface_tag = self.filament_tags[0]

        gmsh.model.occ.synchronize()
        self.refresh_topology()

        return self.surface_tag


    def refresh_topology(self) -> None:
        """
        Refresh HTS topology and edge classification using global
        HTS bounding box parameters.
        """
        super().refresh_topology(
            self.HTS_width,
            self.HTS_thickness,
            self.HTS_center_x,
            self.HTS_center_y,
        )

    # Physical groups

    def create_physical_groups(self, name_prefix: str = "HTS") -> Dict[str, int]:
        """
        Create physical groups for the HTS layer, its filaments, grooves,
        and edges.

        2D groups
        ---------
        - name_prefix:
            all HTS filaments together (monolithic or striated).
        - name_prefix_Filament_i:
            individual HTS filaments (ordered left-to-right).
        - name_prefix_Grooves:
            all grooves together (if any).
        - name_prefix_Groove_i:
            individual groove surfaces (ordered left-to-right).

        1D edge groups
        --------------
        - name_prefix_Upper
        - name_prefix_Lower
        - name_prefix_LeftEdge
        - name_prefix_RightEdge
        """
        if self.surface_tag is None and not self.filament_tags:
            raise RuntimeError("build_HTS() must be called before create_physical_groups().")

        out: Dict[str, int] = {}

        # Helper for left-to-right ordering
        def x_center_surf(tag: int) -> float:
            xmin, _, _, xmax, _, _ = gmsh.model.getBoundingBox(2, tag)
            return 0.5 * (xmin + xmax)

        # Surfaces: all filaments together (striation-aware)
        if self.filament_tags:
            surf_tags = self.filament_tags
        else:
            surf_tags = [self.surface_tag]

        pg = gmsh.model.addPhysicalGroup(2, surf_tags)
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        # Per-filament surface groups
        if self.filament_tags:
            for idx, s in enumerate( sorted(self.filament_tags, key=x_center_surf), start=1 ):
                pg_f   = gmsh.model.addPhysicalGroup(2, [s])
                name_f = f"{name_prefix}_Filament_{idx}"
                gmsh.model.setPhysicalName(2, pg_f, name_f)
                out[name_f] = pg_f

        # Groove surface groups
        if self.groove_tags:
            # All grooves together
            pg_all_g   = gmsh.model.addPhysicalGroup(2, self.groove_tags)
            name_all_g = f"{name_prefix}_Grooves"
            gmsh.model.setPhysicalName(2, pg_all_g, name_all_g)
            out[name_all_g] = pg_all_g

            # Individual grooves: left -> right
            for idx, s in enumerate( sorted(self.groove_tags, key=x_center_surf), start=1 ):
                pg_g   = gmsh.model.addPhysicalGroup(2, [s])
                name_g = f"{name_prefix}_Groove_{idx}"
                gmsh.model.setPhysicalName(2, pg_g, name_g)
                out[name_g] = pg_g

        # Edge groups (union over all filaments)
        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


# ---------------------------------------------------------------------------
# Substrate layer: underneath HTS
# ---------------------------------------------------------------------------

class SubstrateLayer(_RectLayerBase):
    """
    2D rectangular substrate, placed directly underneath the HTS layer.

    - Shares a flat interface with the HTS bottom.
    - Same width and x-center as HTS.
    """

    def __init__(self, substrate_thickness: float) -> None:
        super().__init__()

        self.substrate_thickness       = float(substrate_thickness)
        self.width: Optional[float]    = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None

    def build_substrate(self, hts: HTSLayer) -> int:
        """
        Place the substrate directly under the provided HTS layer
        (touching at the HTS bottom).

        Parameters
        ----------
        hts : HTSLayer
            The HTS layer that must already be built.

        Returns
        -------
        int
            The OCC surface tag of the substrate.
        """
        if hts.surface_tag is None:
            raise RuntimeError(
                "HTS layer must be built before building the substrate."
            )

        w  = hts.HTS_width
        t  = hts.HTS_thickness
        cx = hts.HTS_center_x
        cy = hts.HTS_center_y - t / 2.0 - self.substrate_thickness / 2.0

        self.width    = w
        self.center_x = cx
        self.center_y = cy

        x0 = cx - w / 2.0
        y0 = cy - self.substrate_thickness / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, w, self.substrate_thickness)

        gmsh.model.occ.synchronize()
        self.refresh_topology()
        return self.surface_tag

    def refresh_topology(self) -> None:
        if self.width is None or self.center_x is None or self.center_y is None:
            raise RuntimeError("Substrate geometry not yet initialized.")
        super().refresh_topology(
            self.width,
            self.substrate_thickness,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "Substrate") -> Dict[str, int]:
        """
        Create physical groups for the substrate layer and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_substrate() must be called before create_physical_groups().")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


# ---------------------------------------------------------------------------
# Silver layers: thin stabilizer above HTS / below substrate
# ---------------------------------------------------------------------------

class SilverTopLayer(_RectLayerBase):
    """
    Top silver layer placed directly above HTS (and directly below CopperTop).

    This layer:
    - Has same width and x-center as HTS.
    - Touches the HTS upper surface (or can be removed via config).
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width: Optional[float] = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None


    def build_over(self, hts: HTSLayer) -> int:
        """
        Place the top silver layer directly above the HTS layer.
        """
        if hts.surface_tag is None:
            raise RuntimeError("HTS must be built before the top Silver layer.")

        w  = hts.HTS_width
        cx = hts.HTS_center_x
        cy = hts.HTS_center_y + hts.HTS_thickness / 2.0 + self.thickness / 2.0

        self.width    = w
        self.center_x = cx
        self.center_y = cy

        x0 = cx - w / 2.0
        y0 = cy - self.thickness / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle( x0, y0, 0.0, w, self.thickness )

        gmsh.model.occ.synchronize()
        self.refresh_topology()
        return self.surface_tag

    def refresh_topology(self) -> None:
        if self.width is None or self.center_x is None or self.center_y is None:
            raise RuntimeError("SilverTop geometry not yet initialized.")
        super().refresh_topology(
            self.width,
            self.thickness,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "SilverTop") -> Dict[str, int]:
        """
        Create physical groups for the top silver layer and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_over() must be called before creating PGs.")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            epg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, epg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = epg

        return out


class SilverBottomLayer(_RectLayerBase):
    """
    Bottom silver layer placed directly under the substrate
    (and directly above CopperBottom).
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width: Optional[float]    = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None


    def build_under(self, sub: SubstrateLayer) -> int:
        """
        Place SilverBottom directly under the Substrate layer (touching
        at the interface).
        """
        if sub.surface_tag is None:
            raise RuntimeError("Substrate must be built before the bottom Silver layer.")

        w  = sub.width
        cx = sub.center_x
        cy = sub.center_y - sub.substrate_thickness / 2.0 - self.thickness / 2.0

        if w is None or cx is None or cy is None:
            raise RuntimeError("Substrate geometry not yet initialized.")

        self.width    = w
        self.center_x = cx
        self.center_y = cy

        x0 = cx - w / 2.0
        y0 = cy - self.thickness / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, w, self.thickness)

        gmsh.model.occ.synchronize()
        self.refresh_topology()
        return self.surface_tag

    def refresh_topology(self) -> None:
        if self.width is None or self.center_x is None or self.center_y is None:
            raise RuntimeError("SilverBottom geometry not yet initialized.")
        super().refresh_topology(
            self.width,
            self.thickness,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "SilverBottom") -> Dict[str, int]:
        """
        Create physical groups for the bottom silver layer and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_under() must be called before creating PGs.")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            epg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, epg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = epg

        return out


# ---------------------------------------------------------------------------
# Copper layers: bottom / top / left / right
# ---------------------------------------------------------------------------

class CopperBottomLayer(_RectLayerBase):
    """
    Lower 2D copper layer placed directly under a base layer:

    - Under SilverBottom if present;
    - Otherwise directly under Substrate.

    This is handled in the geometry builder (Generate_geometry).
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width: Optional[float]    = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None

    def build_under(self, base_layer: _RectLayerBase) -> int:
        """
        Place CopperBottom directly under the given base_layer.

        base_layer can be:
        - SubstrateLayer
        - SilverBottomLayer
        """
        if base_layer.surface_tag is None:
            raise RuntimeError("Base layer must be built before CopperBottom.")

        if isinstance(base_layer, SubstrateLayer):
            w       = base_layer.width
            cx      = base_layer.center_x
            cy_base = base_layer.center_y
            t_base  = base_layer.substrate_thickness

        elif isinstance(base_layer, SilverBottomLayer):
            w       = base_layer.width
            cx      = base_layer.center_x
            cy_base = base_layer.center_y
            t_base  = base_layer.thickness

        else:
            raise TypeError(
                "CopperBottomLayer.build_under() expected SubstrateLayer or "
                f"SilverBottomLayer, got {type(base_layer)!r}."
            )

        if w is None or cx is None or cy_base is None:
            raise RuntimeError("Base layer geometry not yet initialized.")

        # Center of CopperBottom: just below the base layer
        cy = cy_base - t_base / 2.0 - self.thickness / 2.0

        self.width    = w
        self.center_x = cx
        self.center_y = cy

        x0 = cx - w / 2.0
        y0 = cy - self.thickness / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, w, self.thickness)

        gmsh.model.occ.synchronize()
        self.refresh_topology()
        return self.surface_tag

    def refresh_topology(self) -> None:
        if self.width is None or self.center_x is None or self.center_y is None:
            raise RuntimeError("CopperBottom geometry not yet initialized.")
        super().refresh_topology(
            self.width,
            self.thickness,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "CopperBottom") -> Dict[str, int]:
        """
        Create physical groups for the lower copper layer and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_under() must be called before create_physical_groups().")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


class CopperTopLayer(_RectLayerBase):
    """
    Top 2D copper layer placed directly above:

    - SilverTop layer if present, otherwise
    - directly above the HTS layer.
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width: Optional[float]    = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None

    def build_over(self, base_layer: _RectLayerBase) -> int:
        """
        Place CopperTop directly above `base_layer`.

        base_layer can be:
        - HTSLayer
        - SilverTopLayer
        """
        if base_layer.surface_tag is None:
            raise RuntimeError("Base layer must be built before CopperTop.")

        # Case 1: HTS as base
        if isinstance(base_layer, HTSLayer):
            w       = base_layer.HTS_width
            cx      = base_layer.HTS_center_x
            cy_base = base_layer.HTS_center_y
            t_base  = base_layer.HTS_thickness

        # Case 2: SilverTop as base
        elif isinstance(base_layer, SilverTopLayer):
            w       = base_layer.width
            cx      = base_layer.center_x
            cy_base = base_layer.center_y
            t_base  = base_layer.thickness

        else:
            raise TypeError(
                "CopperTopLayer.build_over() expected HTSLayer or "
                f"SilverTopLayer, got {type(base_layer)!r}."
            )

        if w is None or cx is None or cy_base is None:
            raise RuntimeError("Base layer geometry not yet initialized.")

        cy = cy_base + t_base / 2.0 + self.thickness / 2.0

        self.width    = w
        self.center_x = cx
        self.center_y = cy

        x0 = cx - w / 2.0
        y0 = cy - self.thickness / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, w, self.thickness)

        gmsh.model.occ.synchronize()
        self.refresh_topology()
        return self.surface_tag

    def refresh_topology(self) -> None:
        if self.width is None or self.center_x is None or self.center_y is None:
            raise RuntimeError("CopperTop geometry not yet initialized.")
        super().refresh_topology(
            self.width,
            self.thickness,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "CopperTop") -> Dict[str, int]:
        """
        Create physical groups for the top copper layer and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_over() must be called before create_physical_groups().")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


class CopperLeftLayer(_RectLayerBase):
    """
    Left copper shim, placed directly to the left of the HTS + Substrate
    (and optionally CopperBottom/CopperTop if present).

    Height is from:
        bottom of (CopperBottom or Substrate)
        to
        top of (CopperTop or HTS)
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width     = self.thickness  # Horizontal size
        self.height: Optional[float]   = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None

    def build_left_of(
        self,
        hts: HTSLayer,
        sub: SubstrateLayer,
        cu_bottom: Optional["CopperBottomLayer"] = None,
        cu_top:    Optional["CopperTopLayer"]    = None,
    ) -> int:
        """
        Build CopperLeft against the left edges of HTS and Substrate,
        extending vertically to cover the full bottom/top stack.
        """
        if hts.surface_tag is None or sub.surface_tag is None:
            raise RuntimeError("HTS and Substrate must be built before CopperLeft.")

        if sub.width is None or sub.center_x is None or sub.center_y is None:
            raise RuntimeError("Substrate geometry not yet initialized.")

        # Vertical limits
        if cu_top is not None:
            y_top = cu_top.center_y + cu_top.thickness / 2.0
        else:
            y_top = hts.HTS_center_y + hts.HTS_thickness / 2.0

        if cu_bottom is not None:
            y_bot = cu_bottom.center_y - cu_bottom.thickness / 2.0
        else:
            y_bot = sub.center_y - sub.substrate_thickness / 2.0

        self.height = y_top - y_bot
        if self.height <= 0.0:
            raise RuntimeError(f"CopperLeft height <= 0 (y_top={y_top}, y_bot={y_bot}).")

        # Horizontal placement: flush with leftmost face of HTS/Substrate
        x_left_face = min(
            hts.HTS_center_x - hts.HTS_width / 2.0,
            sub.center_x - sub.width / 2.0,
        )

        self.center_x = x_left_face - self.thickness / 2.0
        self.center_y = 0.5 * (y_top + y_bot)

        x0 = self.center_x - self.thickness / 2.0
        y0 = self.center_y - self.height / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, self.thickness, self.height)

        gmsh.model.occ.synchronize()
        self._refresh_from_surface()
        self._classify_edges_from_bbox(
            self.thickness,
            self.height,
            self.center_x,
            self.center_y,
        )

        return self.surface_tag

    def refresh_topology(self) -> None:
        if (
            self.height is None
            or self.center_x is None
            or self.center_y is None
        ):
            raise RuntimeError("CopperLeft geometry not yet initialized.")
        self._refresh_from_surface()
        self._classify_edges_from_bbox(
            self.thickness,
            self.height,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "CopperLeft") -> Dict[str, int]:
        """
        Create physical groups for the left copper shim and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_left_of() must be called before creating PGs.")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


class CopperRightLayer(_RectLayerBase):
    """
    Right copper shim, symmetric counterpart of CopperLeftLayer.
    """

    def __init__(self, thickness: float) -> None:
        super().__init__()
        self.thickness = float(thickness)
        self.width     = self.thickness
        self.height: Optional[float]   = None
        self.center_x: Optional[float] = None
        self.center_y: Optional[float] = None

    def build_right_of(
        self,
        hts: HTSLayer,
        sub: SubstrateLayer,
        cu_bottom: Optional["CopperBottomLayer"] = None,
        cu_top:    Optional["CopperTopLayer"]    = None,
    ) -> int:
        """
        Build CopperRight against the right edges of HTS and Substrate.
        """
        if hts.surface_tag is None or sub.surface_tag is None:
            raise RuntimeError("HTS and Substrate must be built before CopperRight.")

        if sub.width is None or sub.center_x is None or sub.center_y is None:
            raise RuntimeError("Substrate geometry not yet initialized.")

        if cu_top is not None:
            y_top = cu_top.center_y + cu_top.thickness / 2.0
        else:
            y_top = hts.HTS_center_y + hts.HTS_thickness / 2.0

        if cu_bottom is not None:
            y_bot = cu_bottom.center_y - cu_bottom.thickness / 2.0
        else:
            y_bot = sub.center_y - sub.substrate_thickness / 2.0

        self.height = y_top - y_bot
        if self.height <= 0.0:
            raise RuntimeError(f"CopperRight height <= 0 (y_top={y_top}, y_bot={y_bot}).")

        x_right_face = max(
            hts.HTS_center_x + hts.HTS_width / 2.0,
            sub.center_x + sub.width / 2.0,
        )

        self.center_x = x_right_face + self.thickness / 2.0
        self.center_y = 0.5 * (y_top + y_bot)

        x0 = self.center_x - self.thickness / 2.0
        y0 = self.center_y - self.height / 2.0

        self.surface_tag = gmsh.model.occ.addRectangle(x0, y0, 0.0, self.thickness, self.height)

        gmsh.model.occ.synchronize()
        self._refresh_from_surface()
        self._classify_edges_from_bbox(
            self.thickness,
            self.height,
            self.center_x,
            self.center_y,
        )

        return self.surface_tag

    def refresh_topology(self) -> None:
        if (
            self.height is None
            or self.center_x is None
            or self.center_y is None
        ):
            raise RuntimeError("CopperRight geometry not yet initialized.")
        self._refresh_from_surface()
        self._classify_edges_from_bbox(
            self.thickness,
            self.height,
            self.center_x,
            self.center_y,
        )

    def create_physical_groups(self, name_prefix: str = "CopperRight") -> Dict[str, int]:
        """
        Create physical groups for the right copper shim and its edges.
        """
        if self.surface_tag is None:
            raise RuntimeError("build_right_of() must be called before creating PGs.")

        out: Dict[str, int] = {}

        pg = gmsh.model.addPhysicalGroup(2, [self.surface_tag])
        gmsh.model.setPhysicalName(2, pg, name_prefix)
        out[name_prefix] = pg

        for name, tags in self.edge_tags.items():
            edge_pg = gmsh.model.addPhysicalGroup(1, tags)
            gmsh.model.setPhysicalName(1, edge_pg, f"{name_prefix}_{name}")
            out[f"{name_prefix}_{name}"] = edge_pg

        return out


# ---------------------------------------------------------------------------
# High-level geometry builder
# ---------------------------------------------------------------------------

class Generate_geometry:
    """
    Generate a 2D geometry of the CACCC model and save as .brep / .xao.

    Responsibilities
    ----------------
    - Initialize a Gmsh OCC model for the given magnet_name.
    - Instantiate and build each layer:
        HTS, Substrate, optional SilverTop / SilverBottom,
        optional CopperTop / CopperBottom / CopperLeft / CopperRight.
    - Create an enclosing circular air region and cut out all solids.
    - Refresh topology and create physical groups:
        - material regions (2D)
        - layer edges (1D)
        - inter-layer interfaces (1D)
        - air outer boundary (1D)
    - Write:
        <magnet_name>.brep
        <magnet_name>.xao
    """

    def __init__(
        self,
        fdm: FDM,
        inputs_folder_path: str,
        verbose: bool = True,
        *,
        initialize_gmsh: bool = True,
        create_model: bool = True,
        create_physical_groups: Optional[bool] = None,
        wipe_physical_groups: Optional[bool] = None,
        write_files: Optional[bool] = None,
        clear_gmsh_on_finalize: Optional[bool] = None,
        external_gu: Optional[GmshUtils] = None,
    ) -> None:

        self.fdm = fdm
        self.inputs_folder_path = inputs_folder_path

        self.model_folder = os.path.join(os.getcwd())
        self.magnet_name  = fdm.general.magnet_name

        self.model_file        = os.path.join(self.model_folder, f"{self.magnet_name}.brep")
        self.xao_file = os.path.join(self.model_folder, f"{self.magnet_name}.xao")

        self.verbose = verbose
        self.gu      = external_gu if external_gu is not None else GmshUtils(self.model_folder, self.verbose)

        # When embedded in another builder (e.g. TSTC 2D stack),
        # we must not re-initialize Gmsh, and must not create a new model.
        self._create_model = bool(create_model)


        embedded = not self._create_model

        # Standalone defaults (embedded=False): behave like before.
        # Embedded defaults (embedded=True): do NOT clear / wipe / write unless requested.
        self._create_physical_groups = (
            bool(create_physical_groups)
            if create_physical_groups is not None
            else (not embedded)
        )
        self._wipe_physical_groups = (
            bool(wipe_physical_groups)
            if wipe_physical_groups is not None
            else (not embedded)
        )
        self._write_files = (
            bool(write_files)
            if write_files is not None
            else (not embedded)
        )
        self._clear_gmsh_on_finalize = (
            bool(clear_gmsh_on_finalize)
            if clear_gmsh_on_finalize is not None
            else (not embedded)
        )


        conductor_dict = self.fdm.conductors

        if not conductor_dict:
            raise KeyError(
                "fdm.conductors is empty: cannot build CC geometry. "
                "Expected at least one conductor entry."
            )

        # Preferred legacy key (many FiQuS models use this)
        selected_conductor_name = self.fdm.magnet.solve.conductor_name
        if selected_conductor_name in conductor_dict:
            selected_conductor: Conductor = conductor_dict[selected_conductor_name]
        else:
            raise ValueError(
                f"Conductor name: {selected_conductor_name} not present in the conductors section"
            )

        if initialize_gmsh:
            self.gu.initialize(verbosity_Gmsh=fdm.run.verbosity_Gmsh)

            # OCC warnings (0 = silenced in terminal)
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.option.setNumber("General.Verbosity", 0)

        # All built layers are stored here (by name)
        self.layers: Dict[str, object] = {}
        self._model_ready = False


        # Reference center for this CC cross-section (used for placement and air centering)
        self._geom_center_x: float = 0.0
        self._geom_center_y: float = 0.0


        # the strand is a Union[Round, Rectangular, CC, Homogenized]
        strand = selected_conductor.strand
        if not isinstance(strand, CC):
            raise TypeError(
                f"Expected strand type 'CC' for CACCC geometry, got {type(strand)}"
            )

        # Store this CC strand so all generate_* methods can use it
        self.cc_strand = strand
        s = self.cc_strand  # shorthand

        # ------------------------------------------------------------------
        # Geometry sanity checks (enforced here, not in magnet.geometry model)
        # ------------------------------------------------------------------
        # Mandatory base layer dimensions must be > 0
        _require_positive(
            s.HTS_width,
            name=f"conductors.{selected_conductor_name}.strand.HTS_width",
        )
        _require_positive(
            s.HTS_thickness,
            name=f"conductors.{selected_conductor_name}.strand.HTS_thickness",
        )
        _require_positive(
            s.substrate_thickness,
            name=f"conductors.{selected_conductor_name}.strand.substrate_thickness",
        )

        # Striation parameters
        n_fil = _require_int_ge(
            getattr(s, "number_of_filaments", None),
            name=f"conductors.{selected_conductor_name}.strand.number_of_filaments",
            min_value=1,
        )
        gap = getattr(s, "gap_between_filaments", None)
        gap_v = _require_non_negative_optional(
            gap,
            name=f"conductors.{selected_conductor_name}.strand.gap_between_filaments",
        )

        if n_fil is not None and n_fil > 1:
            if gap is None or gap_v <= 0.0:
                raise ValueError(
                    "HTS striation requested (number_of_filaments > 1) but "
                    "gap_between_filaments is missing or <= 0."
                )

            total_groove = gap_v * (n_fil - 1)
            hts_w = float(s.HTS_width)
            if total_groove >= hts_w:
                raise ValueError(
                    f"Total groove width {total_groove:g} >= HTS_width {hts_w:g}. "
                    "Reduce gap_between_filaments or number_of_filaments."
                )

        # ------------------------------------------------------------------
        # Layer inclusion logic (thickness-based only, but negatives are errors)
        # ------------------------------------------------------------------
        ag_top = _require_non_negative_optional(
            getattr(getattr(s, "silver_thickness", None), "top", None),
            name=f"conductors.{selected_conductor_name}.strand.silver_thickness.top",
        )
        ag_bot = _require_non_negative_optional(
            getattr(getattr(s, "silver_thickness", None), "bottom", None),
            name=f"conductors.{selected_conductor_name}.strand.silver_thickness.bottom",
        )

        cu_top = _require_non_negative_optional(
            getattr(getattr(s, "copper_thickness", None), "top", None),
            name=f"conductors.{selected_conductor_name}.strand.copper_thickness.top",
        )
        cu_bot = _require_non_negative_optional(
            getattr(getattr(s, "copper_thickness", None), "bottom", None),
            name=f"conductors.{selected_conductor_name}.strand.copper_thickness.bottom",
        )
        cu_left = _require_non_negative_optional(
            getattr(getattr(s, "copper_thickness", None), "left", None),
            name=f"conductors.{selected_conductor_name}.strand.copper_thickness.left",
        )
        cu_right = _require_non_negative_optional(
            getattr(getattr(s, "copper_thickness", None), "right", None),
            name=f"conductors.{selected_conductor_name}.strand.copper_thickness.right",
        )

        self._use_silver_top = ag_top > 0.0
        self._use_silver_bottom = ag_bot > 0.0

        self._use_copper_top = cu_top > 0.0
        self._use_copper_bottom = cu_bot > 0.0
        self._use_copper_left = cu_left > 0.0
        self._use_copper_right = cu_right > 0.0




    # Internal helpers
    def _ensure_model(self) -> None:
        """
        Ensure there is an active Gmsh model.

        In embedded mode (create_model=False), we assume the caller already did:
            gmsh.model.add(...)
        """
        if self._model_ready:
            return

        if getattr(self, "_create_model", True):
            gmsh.model.add(self.magnet_name)

        self._model_ready = True


    # Layer builders
    def generate_HTS_layer(self, center_x: float = 0.0, center_y: float = 0.0) -> None:
        """
        Build a single HTS layer (2D) centered at (center_x, center_y).

        Striation parameters (from CC strand):
        - number_of_filaments
        - gap_between_filaments
        """
        self._ensure_model()

        # Save reference center so other steps (e.g. air disk) can follow placement.
        self._geom_center_x = float(center_x)
        self._geom_center_y = float(center_y)

        s = self.cc_strand  # CC instance

        layer = HTSLayer(
            HTS_thickness=float(s.HTS_thickness),
            HTS_width=float(s.HTS_width),
            HTS_center_x=float(center_x),
            HTS_center_y=float(center_y),
            number_of_filaments=s.number_of_filaments,
            gap_between_filaments=s.gap_between_filaments,
        )

        layer.build_HTS()
        self.layers["HTS"] = layer




    def generate_silver_top_layer(self) -> None:
        """
        Build the SilverTop layer directly above HTS (if enabled).
        """
        self._ensure_model()

        if not self._use_silver_top:
            logger.info("[Geom-CC] Skipping SilverTop layer (thickness == 0).")
            return

        if "HTS" not in self.layers:
            raise RuntimeError("HTS must be built before top Silver.")

        s = self.cc_strand

        Ag = SilverTopLayer(thickness=float(s.silver_thickness.top))
        Ag.build_over(self.layers["HTS"])
        self.layers["SilverTop"] = Ag



    def generate_substrate_layer(self) -> None:
        """
        Build the substrate layer directly under the HTS (shared interface).
        """
        self._ensure_model()

        if "HTS" not in self.layers:
            raise RuntimeError(
                "HTS layer must be built before substrate. "
                "Call generate_HTS_layer() first."
            )

        hts = self.layers["HTS"]
        s = self.cc_strand

        substrate = SubstrateLayer(substrate_thickness=float(s.substrate_thickness))
        substrate.build_substrate(hts)
        self.layers["Substrate"] = substrate


    def generate_silver_bottom_layer(self) -> None:
        """
        Build the bottom Silver layer directly under the Substrate
        (shared interface), if enabled.
        """
        self._ensure_model()

        if not self._use_silver_bottom:
            logger.info("[Geom-CC] Skipping SilverBottom layer (config disabled).")
            return

        if "Substrate" not in self.layers:
            raise RuntimeError("Substrate must be built before bottom Silver.")

        sub = self.layers["Substrate"]
        s = self.cc_strand

        AgB = SilverBottomLayer(thickness=float(s.silver_thickness.bottom))
        AgB.build_under(sub)
        self.layers["SilverBottom"] = AgB



    def generate_copper_bottom_layer(self) -> None:
        """
        Build CopperBottom directly under the bottom-most central layer:

        - Under SilverBottom if it exists,
        - Otherwise directly under Substrate.

        (Side shims are handled separately.)
        """
        self._ensure_model()

        if not self._use_copper_bottom:
            logger.info("[Geom-CC] Skipping CopperBottom layer (config disabled).")
            return

        s = self.cc_strand

        if "Substrate" not in self.layers:
            raise RuntimeError("Substrate must be built before CopperBottom.")

        base_layer = self.layers.get("SilverBottom", None)
        if base_layer is None:
            base_layer = self.layers["Substrate"]

        cuL = CopperBottomLayer(thickness=float(s.copper_thickness.bottom))
        cuL.build_under(base_layer)
        self.layers["CopperBottom"] = cuL


    def generate_copper_top_layer(self) -> None:
        """
        Build CopperTop directly above HTS (or above SilverTop if present).
        """
        self._ensure_model()

        if not self._use_copper_top:
            logger.info("[Geom-CC] Skipping CopperTop layer (config disabled).")
            return

        s = self.cc_strand

        if "HTS" not in self.layers:
            raise RuntimeError("HTS must be built before CopperTop.")

        hts = self.layers["HTS"]
        cuT = CopperTopLayer(thickness=float(s.copper_thickness.top))
        silver_top = self.layers.get("SilverTop", None)

        if silver_top is not None:
            cuT.build_over(silver_top)
        else:
            cuT.build_over(hts)

        self.layers["CopperTop"] = cuT



    def generate_copper_left_layer(self) -> None:
        """
        Build CopperLeft against the left edges of HTS + Substrate,
        extended vertically to cover the whole stack (CuBottom / CuTop if present).
        """
        self._ensure_model()

        if not self._use_copper_left:
            logger.info("[Geom-CC] Skipping CopperLeft layer (config disabled).")
            return

        s = self.cc_strand

        if "HTS" not in self.layers or "Substrate" not in self.layers:
            raise RuntimeError("Build HTS and Substrate before CopperLeft.")

        cuL = CopperLeftLayer(thickness=float(s.copper_thickness.left))

        cuL.build_left_of(
            self.layers["HTS"],
            self.layers["Substrate"],
            cu_bottom=self.layers.get("CopperBottom"),
            cu_top=self.layers.get("CopperTop"),
        )

        self.layers["CopperLeft"] = cuL


    def generate_copper_right_layer(self) -> None:
        """
        Build CopperRight against the right edges of HTS + Substrate,
        extended vertically to cover the whole stack (CuBottom / CuTop if present).
        """
        self._ensure_model()

        if not self._use_copper_right:
            logger.info("[Geom-CC] Skipping CopperRight layer (config disabled).")
            return

        s = self.cc_strand

        if "HTS" not in self.layers or "Substrate" not in self.layers:
            raise RuntimeError("Build HTS and Substrate before CopperRight.")

        cuR = CopperRightLayer(thickness=float(s.copper_thickness.right))

        cuR.build_right_of(
            self.layers["HTS"],
            self.layers["Substrate"],
            cu_bottom=self.layers.get("CopperBottom"),
            cu_top=self.layers.get("CopperTop"),
        )

        self.layers["CopperRight"] = cuR


    # Air region

    def generate_air_region(self) -> None:
        g = self.fdm.magnet.geometry
        R = _require_positive(g.air_radius, name="magnet.geometry.air_radius")

        # -------------------------------
        # 1) Collect all inner surfaces
        # -------------------------------
        inner: List[int] = []
        for L in self.layers.values():
            if hasattr(L, "filament_tags") and getattr(L, "filament_tags"):
                inner.extend(getattr(L, "filament_tags"))

            if hasattr(L, "groove_tags") and getattr(L, "groove_tags"):
                inner.extend(getattr(L, "groove_tags"))

            elif getattr(L, "surface_tag", None) is not None:
                tag = getattr(L, "surface_tag")

                if tag not in inner:
                    inner.append(tag)

        # Defensive: collapse exact duplicates before any boolean ops
        gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()

        # -----------------------------------------------------
        # 2) Enforce conformity inside the conductor stack
        #    (split all touching rectangles so they share edges)
        # -----------------------------------------------------
        # Fragmenting the conductor stack first enforces conformal interfaces:
        # touching layers/filaments share identical curve entities, which makes
        # interface physical groups and meshing constraints reliable.
        all_rects       = [(2, s) for s in inner]
        frag_conduct, _ = gmsh.model.occ.fragment(all_rects, [])
        gmsh.model.occ.synchronize()


        # Rebuild 'inner' from the fragment result (their tags can change)
        inner = [ent[1] for ent in frag_conduct]

        # ------------------------------------
        # 3) Create the Air disk 
        # ------------------------------------
        # Robust air centering:
        # compute the bbox of the *actual* conductor surfaces and center the air on that.
        xmin = float("inf")
        ymin = float("inf")
        xmax = float("-inf")
        ymax = float("-inf")

        for s_tag in inner:
            bxmin, bymin, _, bxmax, bymax, _ = gmsh.model.getBoundingBox(2, int(s_tag))
            xmin = min(xmin, float(bxmin))
            ymin = min(ymin, float(bymin))
            xmax = max(xmax, float(bxmax))
            ymax = max(ymax, float(bymax))

        if not (xmin < xmax and ymin < ymax):
            # Fallback (should not happen unless inner is empty / invalid)
            cx = float(getattr(self, "_geom_center_x", 0.0))
            cy = float(getattr(self, "_geom_center_y", 0.0))
        else:
            cx = 0.5 * (xmin + xmax)
            cy = 0.5 * (ymin + ymax)

        disk = gmsh.model.occ.addDisk(cx, cy, 0.0, R, R)


        # Fragment(disk, inner) splits the disk into multiple surfaces:
        # one is the exterior air region, others may be trapped pockets.
        # The largest disk-derived surface is taken as the physical Air domain.
        out_dimtags, out_map = gmsh.model.occ.fragment(
            [(2, disk)],
            [(2, s) for s in inner],
        )
        gmsh.model.occ.synchronize()


        # out_map[0] corresponds to the object list = [(2, disk)]
        disk_pieces = out_map[0] if out_map and out_map[0] else []
        if not disk_pieces:
            raise RuntimeError("Air fragment produced no disk-derived pieces (unexpected).")

        # Pick the largest disk-derived piece as the Air region
        air_ent = max(
            disk_pieces,
            key=lambda e: float(gmsh.model.occ.getMass(e[0], e[1])),
        )
        air_tag = int(air_ent[1])

        self.layers["Air"] = SimpleNamespace(surface_tag=air_tag)



    # Topology + physical groups

    def _refresh_all(self) -> None:
        """
        After OCC cleanup, update curve/point lists and edge classification
        for all rectangular layers that implement refresh_topology().
        """
        for L in self.layers.values():
            if hasattr(L, "refresh_topology"):
                L.refresh_topology()  # type: ignore[call-arg]


    def _create_all_physical_groups(self, name_prefix: str = "") -> None:
        """
        Create all material + interface + air physical groups.

        If name_prefix != "":
            all physical group names become: "<name_prefix>_<OriginalName>"
            and spaces in the original name are replaced by underscores.
        """
        prefix = str(name_prefix).strip()

        # Embedded mode: do not wipe physical groups by default, because other builders
        # may have already created groups in the same Gmsh model.
        # Use name_prefix to avoid naming collisions across repeated CC instances.
        if self._wipe_physical_groups:
            gmsh.model.removePhysicalGroups()
        elif not prefix:
            raise ValueError(
                "name_prefix must be non-empty when wipe_physical_groups=False "
                "(otherwise physical group names will collide)."
            )



        prefix = str(name_prefix).strip()

        def _pref(name: str) -> str:
            if not prefix:
                return name
            safe = str(name).replace(" ", "_")
            return f"{prefix}_{safe}"

        # Layer physical groups (2D + edges)
        if "HTS" in self.layers:
            self.layers["HTS"].create_physical_groups(_pref("HTS"))  # type: ignore[arg-type]

        if "Substrate" in self.layers:
            self.layers["Substrate"].create_physical_groups(_pref("Substrate"))  # type: ignore[arg-type]

        if "SilverTop" in self.layers:
            self.layers["SilverTop"].create_physical_groups(_pref("SilverTop"))  # type: ignore[arg-type]

        if "SilverBottom" in self.layers:
            self.layers["SilverBottom"].create_physical_groups(_pref("SilverBottom"))  # type: ignore[arg-type]

        if "CopperBottom" in self.layers:
            self.layers["CopperBottom"].create_physical_groups(_pref("CopperBottom"))  # type: ignore[arg-type]

        if "CopperTop" in self.layers:
            self.layers["CopperTop"].create_physical_groups(_pref("CopperTop"))  # type: ignore[arg-type]

        if "CopperLeft" in self.layers:
            self.layers["CopperLeft"].create_physical_groups(_pref("CopperLeft"))  # type: ignore[arg-type]

        if "CopperRight" in self.layers:
            self.layers["CopperRight"].create_physical_groups(_pref("CopperRight"))  # type: ignore[arg-type]

        # Interfaces (1D)
        # Interface convention:
        # We define each interface using the boundary curves of ONE of the adjacent
        # layers (typically the "lower" layer's upper edge or vice versa). Because we
        # fragment the stack earlier, both sides should reference the same curve IDs.
        # Interfaces (1D)

        if "Substrate" in self.layers and "SilverBottom" in self.layers:
            iface = self.layers["Substrate"].edge_tags["Lower"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("Substrate_SilverBottom_Interface"))

        if "SilverBottom" in self.layers and "CopperBottom" in self.layers:
            iface = self.layers["SilverBottom"].edge_tags["Lower"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("SilverBottom_CopperBottom_Interface"))

        if (
            "Substrate" in self.layers
            and "CopperBottom" in self.layers
            and "SilverBottom" not in self.layers
        ):
            iface = self.layers["CopperBottom"].edge_tags["Upper"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("Substrate_CopperBottom_Interface"))

        if "HTS" in self.layers and "Substrate" in self.layers:
            iface = self.layers["Substrate"].edge_tags["Upper"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("Buffer Layer"))

        if "HTS" in self.layers and "SilverTop" in self.layers:
            iface = self.layers["HTS"].edge_tags["Upper"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("HTS_Silver_Interface"))

        if "SilverTop" in self.layers and "CopperTop" in self.layers:
            iface = self.layers["SilverTop"].edge_tags["Upper"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("SilverTop_CopperTop_Interface"))

        if (
            "HTS" in self.layers
            and "CopperTop" in self.layers
            and "SilverTop" not in self.layers
        ):
            iface = self.layers["HTS"].edge_tags["Upper"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("HTS_CopperTop_Interface"))

        if "CopperLeft" in self.layers and "HTS" in self.layers:
            iface = self.layers["HTS"].edge_tags["LeftEdge"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("HTS_CopperLeft_Interface"))

        if "CopperLeft" in self.layers and "Substrate" in self.layers:
            iface = self.layers["Substrate"].edge_tags["LeftEdge"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("Substrate_CopperLeft_Interface"))

        if "CopperRight" in self.layers and "HTS" in self.layers:
            iface = self.layers["HTS"].edge_tags["RightEdge"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("HTS_CopperRight_Interface"))

        if "CopperRight" in self.layers and "Substrate" in self.layers:
            iface = self.layers["Substrate"].edge_tags["RightEdge"]  # type: ignore[index]
            pg_if = gmsh.model.addPhysicalGroup(1, iface)
            gmsh.model.setPhysicalName(1, pg_if, _pref("Substrate_CopperRight_Interface"))

        # Air (surface + outer/inner boundary + inner boundary + one point for gauging)
        if "Air" in self.layers:
            air_tag = self.layers["Air"].surface_tag  # type: ignore[attr-defined]

            pg_s = gmsh.model.addPhysicalGroup(2, [air_tag])
            gmsh.model.setPhysicalName(2, pg_s, _pref("Air"))

            b = gmsh.model.getBoundary([(2, air_tag)], oriented=False, recursive=False)
            cand = [c[1] for c in b]

            outer_curves: List[int] = []
            for ctag in cand:
                try:
                    _, up = gmsh.model.getAdjacencies(1, ctag)
                    if len(up) == 1 and up[0] == air_tag:
                        outer_curves.append(ctag)
                except Exception:
                    pass

            if not outer_curves:
                lengths = [(ctag, gmsh.model.occ.getMass(1, ctag)) for ctag in cand]
                max_len = max((L for _, L in lengths), default=0.0)
                if max_len > 0.0:
                    outer_curves = [
                        ctag for ctag, L in lengths
                        if abs(L - max_len) <= 1e-9 * max_len
                    ]

            pg_c = gmsh.model.addPhysicalGroup(1, outer_curves)
            gmsh.model.setPhysicalName(1, pg_c, _pref("Air_Outer"))

            inner_curves = [ctag for ctag in cand if ctag not in outer_curves]
            pg_c = gmsh.model.addPhysicalGroup(1, inner_curves)
            gmsh.model.setPhysicalName(1, pg_c, _pref("Air_Inner"))


            # One point on the air boundary for gauging the scalar magnetic potential phi
            adj = gmsh.model.getAdjacencies(1, outer_curves[0])
            point = adj[1][0] # downward, [1], to get dimension 0 and first element to grab a single point tag
            pg_c = gmsh.model.addPhysicalGroup(0, [point])
            gmsh.model.setPhysicalName(0, pg_c, _pref("Gauging_point"))



    # Finalize
    def finalize_and_write(self, name_prefix: str = "") -> None:
        """
        Perform final OCC synchronize, refresh topology, recreate all
        physical groups, and write .brep and .xao.
        """
        gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()

        # Refresh topology after final OCC operations.
        self._refresh_all()

        # Create physical groups BEFORE writing .xao so they are embedded.
        if self._create_physical_groups:
            self._create_all_physical_groups(name_prefix=name_prefix)

        # Only write files if requested (standalone default: True).
        if self._write_files:
            gmsh.write(self.model_file)
            gmsh.write(self.xao_file)

        if self.fdm.run.launch_gui and self._create_model:
            self.gu.launch_interactive_GUI()
        elif self._clear_gmsh_on_finalize:
            gmsh.clear()





    # Loading an existing geometry
    def load_geometry(self, gui: bool = False) -> None:
        """
        Load an existing .brep geometry and optionally launch the GUI.
        """
        gmsh.open(self.model_file)
        if gui:
            self.gu.launch_interactive_GUI()