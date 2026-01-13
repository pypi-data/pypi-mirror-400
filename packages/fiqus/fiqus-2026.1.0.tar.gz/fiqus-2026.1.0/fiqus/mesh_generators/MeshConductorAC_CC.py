"""
MeshConductorAC_CC.py

2D mesh generator for the coated-conductor (CACCC) model.

Assumptions / contract with GeometryConductorAC_CC
--------------------------------------------------
- Geometry is axis-aligned: x = tape width, y = tape thickness.
- The imported .xao file must contain the physical groups expected by this
  module (e.g. HTS, optional HTS_Grooves, Substrate, SilverTop/Bottom,
  CopperTop/Bottom/Left/Right, Air, Air_Outer, Air_Inner, and boundary/interface
  curve groups).

Meshing strategy
----------------
- HTS: structured (transfinite) meshing. If HTS is striated, filaments are
  meshed as transfinite quads, while grooves can remain unstructured triangles
  (but with aligned boundary node counts).
- Copper: uniform target element size via a background field (single knob:
  copper_elem_scale). We intentionally avoid transfinite on copper to preserve
  uniform spacing.
- Air: optionally controlled by air_boundary_mesh_size_ratio on Air_Outer.
  Boundary sizing can act as a fallback when no background field is used.
"""


import os
import logging
from typing import Any, Dict, List, Optional

import gmsh

from fiqus.data import RegionsModelFiQuS  # noqa: F401  (used later for regions)
from fiqus.utils.Utils import GmshUtils, FilesAndFolders  # noqa: F401
from fiqus.data.RegionsModelFiQuS import RegionsModel  # noqa: F401
from fiqus.data.DataConductor import CC, Conductor


from fiqus.mesh_generators.MeshConductorAC_Strand import Mesh as BaseMesh

logger = logging.getLogger("FiQuS")

occ = gmsh.model.occ


class Mesh(BaseMesh):
    """
    Mesh generator for the CACCC (coated-conductor) 2D cross-section.
    This class reuses the conductor-AC base Mesh from
    MeshConductorAC_Strand.
    """

    def __init__(self, fdm, verbose: bool = True) -> None:
        """
        Initialize the CACCC mesh generator.

        Parameters
        ----------
        fdm : object
            FiQuS data model instance.
        verbose : bool, optional
            If True, gmsh terminal output is enabled. Defaults to True.
        """
        super().__init__(fdm, verbose)

        # Shortcuts to CACCC-specific geometry and mesh sections.
        # These correspond to DataFiQuSConductorAC_CC.CACCCGeometry
        # and DataFiQuSConductorAC_CC.CACCCMesh.
        self.cc_geom = self.cacdm.geometry
        self.cc_mesh = self.cacdm.mesh

        # Pull the CC strand from conductors
        conductor_dict = self.fdm.conductors
        selected_conductor_name = self.fdm.magnet.solve.conductor_name
        if selected_conductor_name in conductor_dict:
            selected_conductor: Conductor = conductor_dict[selected_conductor_name]
        else:
            raise ValueError(
                f"Conductor name: {selected_conductor_name} not present in the conductors section"
            )
        strand = selected_conductor.strand

        if not isinstance(strand, CC):
            raise TypeError(
                f"Expected strand type 'CC' for CACCC mesh, got {type(strand)}"
            )

        self.cc_strand = strand  # CC instance (HTS_width, HTS_thickness, etc.)

        # Helper dictionaries populated in generate_mesh().
        # They will be reused in later steps (mesh size fields, regions, ...).
        self.physical_surfaces_by_name: Dict[str, Dict[str, Any]] = {}
        self.physical_curves_by_name:   Dict[str, Dict[str, Any]] = {}
        self.physical_points_by_name:   Dict[str, Dict[str, Any]] = {}

        # HTS base mesh sizes (x and y) computed from geometry + mesh parameters.
        self.hts_base_size_x: Optional[float] = None
        self.hts_base_size_y: Optional[float] = None

        # Canonical number of nodes along the tape width (x-direction),
        # used for HTS and later propagated to other layers.
        self.horizontal_nodes_x: Optional[int] = None

        # Equivalent superconducting width (sum of filament widths only)
        # and corresponding reference horizontal element size.
        self.equiv_hts_filament_width: Optional[float] = None
        self.hts_ref_size_x_filaments: Optional[float] = None

        # Horizontal element densities (elements per unit length) for
        # HTS filaments and grooves.
        self.hts_density_x_filaments: Optional[float] = None
        self.hts_density_x_grooves: Optional[float] = None

        # Per-surface horizontal node counts (top/bottom HTS edges).
        # Keys are surface tags (2D entities).
        self.hts_nodes_x_filaments: Dict[int, int] = {}
        self.hts_nodes_x_grooves: Dict[int, int] = {}

        # Approximate vertical discretisation per stacked layer
        # (Substrate, Silver*, CopperTop/Bottom, HTS). These are
        # derived from the HTS vertical reference size and the
        # per-layer *_elem_scale parameters.
        self.vertical_elems_by_layer:   Dict[str, int] = {}
        self.layer_base_size_y:       Dict[str, float] = {}


    # ------------------------------------------------------------------ #
    # Internal helpers: physical groups & mesh parameters
    # ------------------------------------------------------------------ #

    def _collect_physical_groups(self) -> None:
        """
        Populate helper dictionaries for physical groups (surfaces/curves/points).

        This method scans all physical groups present in the current gmsh model
        and fills:
        - self.physical_surfaces_by_name  (dim=2)
        - self.physical_curves_by_name    (dim=1)
        - self.physical_points_by_name    (dim=0)

        Keys are the physical names (strings). Values store both:
        - phys_tag  : used later in the .regions file / GetDP mappings
        - entities  : used for meshing constraints (curve/surface tags)

            {
                "dim": <int>,        # 0, 1 or 2
                "phys_tag": <int>,   # physical group tag
                "entities": [int],   # list of entity tags (points/curves/surfaces)
            }

        The method is idempotent and can be called multiple times after
        gmsh.model.occ.synchronize().
        """

        self.physical_surfaces_by_name.clear()
        self.physical_curves_by_name.clear()
        self.physical_points_by_name.clear()

        phys_groups = gmsh.model.getPhysicalGroups()

        for dim, pg_tag in phys_groups:

            name = gmsh.model.getPhysicalName(dim, pg_tag)
            entity_tags: List[int] = gmsh.model.getEntitiesForPhysicalGroup(dim, pg_tag)

            meta: Dict[str, Any]   = { "dim": dim, "phys_tag": pg_tag, "entities": entity_tags }
            if dim == 2:
                self.physical_surfaces_by_name[name] = meta

            elif dim == 1:
                self.physical_curves_by_name[name]   = meta

            elif dim == 0:
                self.physical_points_by_name[name]   = meta



    def _compute_hts_and_layer_mesh_parameters(self) -> None:
        """
        Compute the HTS base mesh sizes and approximate vertical
        discretisation parameters for the stacked metal layers.

        HTS:
            - Uses HTS_n_elem_width / HTS_n_elem_thickness to define
              base element sizes hts_base_size_x / hts_base_size_y.

        Other layers (Substrate, Silver*, CopperTop/Bottom):
            - Derive a default element count from the HTS vertical
              reference size h_ref = hts_base_size_y and the layer
              thickness (from geometry bounding boxes).
            - Multiply that default count by the YAML *_elem_scale
              (substrate_elem_scale, silver_elem_scale,
              copper_elem_scale) when provided.
            - Store the final counts and corresponding base sizes in:
                * self.vertical_elems_by_layer[layer_name]
                * self.layer_base_size_y[layer_name]
        """

        # HTS geometry and mesh parameters
        s     = self.cc_strand

        W     = s.HTS_width
        T_hts = s.HTS_thickness
        n_w   = self.cc_mesh.HTS_n_elem_width
        n_t   = self.cc_mesh.HTS_n_elem_thickness

        # Canonical node count along width: used for HTS and for all
        # tape-internal horizontal boundaries.
        self.horizontal_nodes_x = int(n_w) + 1

        # Base HTS element sizes.
        self.hts_base_size_x = W / float(n_w)
        self.hts_base_size_y = T_hts / float(n_t)

        # Initialise per-layer containers
        self.vertical_elems_by_layer = {}
        self.layer_base_size_y = {}

        # Register HTS itself as reference.
        self.vertical_elems_by_layer["HTS"] = int(n_t)
        self.layer_base_size_y["HTS"] = self.hts_base_size_y

        # Reference vertical size from HTS.
        h_ref = self.hts_base_size_y

        # Definition of stacked layers and which YAML scale to use.
        # CopperLeft/Right are not part of the vertical stack and are
        # deliberately ignored here.
        layer_definitions = {
            "Substrate":    ("substrate_elem_scale", "substrate layer"),
            "SilverBottom": ("silver_elem_scale",    "silver bottom layer"),
            "SilverTop":    ("silver_elem_scale",    "silver top layer"),
            "CopperBottom": ("copper_elem_scale",    "copper bottom layer"),
            "CopperTop":    ("copper_elem_scale",    "copper top layer"),
        }

        for layer_name, (scale_attr, layer_desc) in layer_definitions.items():

            meta = self.physical_surfaces_by_name.get(layer_name)

            # Safety block for optional layers that may be missing.
            if meta is None:
                continue

            surface_tags = list(meta.get("entities", []))


            # Assumption: layers are axis-aligned (x = width, y = thickness).
            # We infer layer thickness from the y-extent of OCC bounding boxes.
            #
            # Note on *_elem_scale semantics:
            # *_elem_scale scales the *number of elements* (larger -> finer,
            # smaller -> coarser), not the characteristic length directly.
            #
            # Compute thickness in the stacking (y) direction from the union of
            # all surfaces in this layer.

            min_y = float("inf")
            max_y = float("-inf")

            for surf_tag in surface_tags:
                _, ymin, _, _, ymax, _ = gmsh.model.getBoundingBox(2, surf_tag)
                if ymin < min_y:
                    min_y = ymin
                if ymax > max_y:
                    max_y = ymax

            thickness = max_y - min_y

            # Default element count if we used the same vertical size
            # as the HTS: n_default ~ thickness / h_ref.
            n_default = max(1, int(round(thickness / h_ref)))

            # Apply YAML scale factor on the element count, if provided.
            scale_value = getattr(self.cc_mesh, scale_attr, None)
            if scale_value is None or scale_value <= 0.0:
                n_layer    = n_default
                scale_used = 1.0
                
            else:
                n_layer    = max(1, int(round(float(scale_value) * n_default)))
                scale_used = float(scale_value)

            # Corresponding base element size in this layer.
            h_layer = thickness / float(n_layer)

            # Store results
            self.vertical_elems_by_layer[layer_name] = n_layer
            self.layer_base_size_y[layer_name]       = h_layer



    def _apply_air_boundary_mesh_size(self) -> None:
        """
        Set the air mesh size from the outer air boundary curve only
        (physical group 'Air_Outer').

        The size is:
            h_air = air_boundary_mesh_size_ratio * HTS_width

        With MeshSizeExtendFromBoundary=1, this boundary size propagates
        naturally into the air region.

        Note:
        - If a background mesh field is active, it may override point-based
          sizes in parts of the domain. We still set boundary sizing to keep
          behaviour robust as a fallback/default when fields are absent.
        """

        ratio = getattr(self.cc_mesh, "air_boundary_mesh_size_ratio", None)
        if ratio is None or float(ratio) <= 0.0:
            return

        if getattr(self.cc_strand, "HTS_width", None) is None:
            raise ValueError("HTS_width is not defined; cannot compute air boundary size.")

        h_air = float(ratio) * float(self.cc_strand.HTS_width)

        meta = self.physical_curves_by_name.get("Air_Outer")
        if meta is None:
            logger.warning("[Mesh-CC] No 'Air_Outer' physical group found.")
            return

        curve_tags = list(meta.get("entities", []))

        point_tags: list[int] = []
        for ctag in curve_tags:
            down_tags, _ = gmsh.model.getAdjacencies(1, ctag)  # points on curve
            point_tags.extend(down_tags)

        point_tags = list(dict.fromkeys(point_tags))

        gmsh.model.mesh.setSize([(0, ptag) for ptag in point_tags], h_air)

        # Make boundary sizing propagate into air
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)

        logger.info("[Mesh-CC] Air outer boundary size set: h_air=%.6g (ratio=%.6g)", h_air, float(ratio))




    def _apply_uniform_copper_mesh_field(self) -> None:
        """
        Uniform copper sizing with a single knob, and *no* copper-to-air
        transition logic.

        - Copper size: controlled by copper_elem_scale (relative to HTS base size).
        - Air size: optionally set as a constant target value (h_air) inside the
          background field, with an additional boundary-based air knob handled
          separately on 'Air_Outer'.
        - Background field: Min( constant_air , copper_inside_only )

        Result:
        - "Uniform copper" here means the *target size inside copper* is constant.
          Shared boundaries may still be influenced by transfinite node-count
          constraints from neighbouring layers.
        - Air is controlled by a coarse constant target size (or by boundary sizing
          if the field is not used / as a fallback).
        """

        copper_layers = ["CopperTop", "CopperBottom", "CopperLeft", "CopperRight"]

        copper_surface_tags: list[int] = []
        for name in copper_layers:
            copper_surface_tags.extend(self._get_layer_surface_tags(name))
        copper_surface_tags = list(dict.fromkeys(copper_surface_tags))

        if not copper_surface_tags:
            logger.info("[Mesh-CC] No copper surfaces found; skipping copper mesh field.")
            return

        # --------------------------------------------------------------
        # Copper size from single knob: copper_elem_scale
        # --------------------------------------------------------------
        scale_value = getattr(self.cc_mesh, "copper_elem_scale", None)
        if scale_value is None or float(scale_value) <= 0.0:
            scale_value = 1.0
        scale_value = float(scale_value)

        if self.hts_base_size_x is None:
            raise RuntimeError(
                "hts_base_size_x not computed; cannot derive copper target size."
            )

        h_base = float(self.hts_base_size_x)
        h_cu = h_base / scale_value

        # --------------------------------------------------------------
        # Air size from outer-circle knob: air_boundary_mesh_size_ratio
        # --------------------------------------------------------------
        ratio = getattr(self.cc_mesh, "air_boundary_mesh_size_ratio", None)
        if ratio is not None and getattr(self.cc_strand, "HTS_width", None) is not None:
            h_air = float(ratio) * float(self.cc_strand.HTS_width)
        else:
            # Fallback if knob is not present
            h_air = 20.0 * h_base

        # --------------------------------------------------------------
        # Field A: constant air size everywhere
        # --------------------------------------------------------------
        f_air = gmsh.model.mesh.field.add("MathEval")
        gmsh.model.mesh.field.setString(f_air, "F", f"{h_air}")

        # --------------------------------------------------------------
        # Field B: constant size inside copper only (Restrict).
        # Restrict applies the copper size only inside the listed copper surfaces;
        # outside those surfaces it returns a very large value, so Min(air, restrict)
        # naturally selects the air target in the air domain.
        # --------------------------------------------------------------
        f_cu_const = gmsh.model.mesh.field.add("MathEval")
        gmsh.model.mesh.field.setString(f_cu_const, "F", f"{h_cu}")

        f_cu_inside = gmsh.model.mesh.field.add("Restrict")
        gmsh.model.mesh.field.setNumber(f_cu_inside, "InField", f_cu_const)
        gmsh.model.mesh.field.setNumbers(f_cu_inside, "SurfacesList", copper_surface_tags)

        # --------------------------------------------------------------
        # Background = min(air everywhere, copper inside)
        # --------------------------------------------------------------
        f_min = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", [f_air, f_cu_inside])
        gmsh.model.mesh.field.setAsBackgroundMesh(f_min)

        # Let fine boundary sizes propagate into neighbouring domains (air grading).
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)

        logger.info(
            "[Mesh-CC] Air+copper constant background mesh: "
            "h_air=%.6g (ratio=%s), h_cu=%.6g (scale=%.6g, h_base=%.6g)",
            h_air,
            str(ratio),
            h_cu,
            scale_value,
            h_base,
        )








    # ------------------------------------------------------------------ #
    # Internal helpers: access to physical surfaces
    # ------------------------------------------------------------------ #

    def _get_layer_surface_tags(self, layer_name: str) -> List[int]:
        """
        Return surface tags for a given 2D layer physical group.

        Parameters
        ----------
        layer_name : str
            Name of the 2D physical group, e.g. "Substrate", "SilverTop".

        Returns
        -------
        list of int
            List of surface tags 
        """
        meta = self.physical_surfaces_by_name.get(layer_name)
        if not meta:
            return []
        return list(meta.get("entities", []))



    def _get_hts_surface_tags(self) -> List[int]:
        """
        Return surface tags for HTS-related regions.

        We treat:
        - "HTS"            : all HTS filaments together (monolithic or striated).
        - "HTS_Grooves"    : groove surfaces (if present, created as
                             "HTS_Grooves" physical group by geometry).

        as a single logical HTS layer for transfinite meshing. This
        ensures that filaments and grooves (if any) share a consistent
        structured discretisation.
        """
        tags: List[int] = []

        meta_hts = self.physical_surfaces_by_name.get("HTS")
        if meta_hts:
            tags.extend(meta_hts.get("entities", []))

        meta_grooves = self.physical_surfaces_by_name.get("HTS_Grooves")
        if meta_grooves:
            tags.extend(meta_grooves.get("entities", []))

        # De-duplicate while preserving order.
        return list(dict.fromkeys(tags))
    


    def _apply_transfinite_to_hts(self) -> None:
        """
        Build a structured (transfinite) mesh for HTS filaments, and keep
        groove regions (HTS_Grooves) unstructured.

        - Filaments ("HTS" physical group):
            * Horizontal edges: transfinite with 'Bump' distribution.
            * Vertical edges: uniform spacing.
            * Surfaces: transfinite + recombine -> quadrilateral mesh.

        - Grooves ("HTS_Grooves" physical group):
            * Boundary curves still get transfinite node counts so that
              they align with neighbouring HTS and metal layers.
            * BUT we do NOT call setTransfiniteSurface / setRecombine,
              so the interior of grooves is meshed as unstructured triangles.
        """
        # All HTS-related 2D surfaces (filaments + grooves).
        surface_tags = self._get_hts_surface_tags()

        # ------------------------------------------------------------------
        # Step 1: total filament width and reference Δx.
        # ------------------------------------------------------------------
        filament_meta = self.physical_surfaces_by_name.get("HTS", {})
        filament_surface_tags: List[int] = list(
            filament_meta.get("entities", [])
        )

        equiv_width_filaments = 0.0
        for surf_tag in filament_surface_tags:
            xmin, _, _, xmax, _, _ = gmsh.model.getBoundingBox(2, surf_tag)
            dx = xmax - xmin
            if dx > 0.0:
                equiv_width_filaments += dx

        n_tot = float(self.cc_mesh.HTS_n_elem_width)

        # Reset per-surface maps by default.
        self.hts_nodes_x_filaments = {}
        self.hts_nodes_x_grooves = {}

        if equiv_width_filaments > 0.0 and n_tot > 0.0:
            # Reference horizontal cell size in superconducting material:
            #   Δx_ref = W_SC / N_tot
            # where W_SC is the sum of all filament widths.
            h_ref_x = equiv_width_filaments / n_tot
            self.equiv_hts_filament_width = equiv_width_filaments
            self.hts_ref_size_x_filaments = h_ref_x

            logger.debug(
                "[Mesh-CC] HTS equivalent filament width = %.6g, "
                "HTS reference horizontal size (filaments) = %.6g",
                equiv_width_filaments,
                h_ref_x,
            )

            # ------------------------------------------------------------------
            # Step 2: horizontal element densities in filaments and grooves.
            # ------------------------------------------------------------------
            # Elements per unit length in filaments:
            #   λ_fil = N_tot / W_SC  (≈ 1 / Δx_ref)
            lambda_fil = n_tot / equiv_width_filaments

            # Groove density ratio (fewer elements in grooves).
            groove_ratio = getattr(
                self.cc_mesh, "HTS_groove_elem_density_ratio", None
            )
            if groove_ratio is None or groove_ratio <= 0.0:
                groove_ratio = 0.25

            lambda_groove = groove_ratio * lambda_fil

            self.hts_density_x_filaments = lambda_fil
            self.hts_density_x_grooves = lambda_groove

            logger.debug(
                "[Mesh-CC] HTS filament density (lambda_fil) = %.6g, "
                "groove density ratio = %.6g, "
                "groove density (lambda_groove) = %.6g",
                lambda_fil,
                groove_ratio,
                lambda_groove,
            )

            # ------------------------------------------------------------------
            # Step 3: per-surface horizontal node counts.
            # ------------------------------------------------------------------
            groove_min_elems = getattr(
                self.cc_mesh, "HTS_groove_min_elems", None
            )
            if groove_min_elems is None or groove_min_elems < 1:
                groove_min_elems = 1

            # --- Filaments: N_i ≈ λ_fil * width_i ---
            for surf_tag in filament_surface_tags:
                xmin, _, _, xmax, _, _ = gmsh.model.getBoundingBox(2, surf_tag)
                width = xmax - xmin
                if width <= 0.0:
                    continue

                n_elem_f = max(1, int(round(lambda_fil * width)))
                n_nodes_x_f = n_elem_f + 1  # nodes = elements + 1

                self.hts_nodes_x_filaments[surf_tag] = n_nodes_x_f

                logger.debug(
                    "[Mesh-CC] HTS filament surface %d: width = %.6g, "
                    "n_elem = %d, n_nodes_x = %d",
                    surf_tag,
                    width,
                    n_elem_f,
                    n_nodes_x_f,
                )

            # --- Grooves: fewer elements per unit length ---
            groove_meta = self.physical_surfaces_by_name.get(
                "HTS_Grooves", {}
            )
            groove_surface_tags: List[int] = list(
                groove_meta.get("entities", [])
            )

            for surf_tag in groove_surface_tags:
                xmin, _, _, xmax, _, _ = gmsh.model.getBoundingBox(2, surf_tag)
                width = xmax - xmin
                if width <= 0.0:
                    continue

                n_elem_g = int(round(lambda_groove * width))
                n_elem_g = max(groove_min_elems, n_elem_g)
                n_nodes_x_g = n_elem_g + 1

                self.hts_nodes_x_grooves[surf_tag] = n_nodes_x_g

                logger.debug(
                    "[Mesh-CC] HTS groove surface %d: width = %.6g, "
                    "n_elem = %d, n_nodes_x = %d",
                    surf_tag,
                    width,
                    n_elem_g,
                    n_nodes_x_g,
                )

        else:
            # Fallback: no HTS-specific filament logic.
            self.equiv_hts_filament_width = None
            self.hts_ref_size_x_filaments = None
            self.hts_density_x_filaments  = None
            self.hts_density_x_grooves    = None
            self.hts_nodes_x_filaments    = {}
            self.hts_nodes_x_grooves      = {}

        # ------------------------------------------------------------------
        # Step 4: Apply transfinite curves.
        #
        # - Horizontal curves (dx >= dy): 'Bump' with surf_n_nodes_x nodes.
        # - Vertical curves (dy > dx): uniform 'Progression' with n_nodes_y.
        #
        # Then:
        #   - setTransfiniteSurface + Recombine ONLY for filament surfaces.
        #   - Grooves: NO setTransfiniteSurface / NO Recombine -> unstructured.
        # ------------------------------------------------------------------

        # Global vertical node count (same for all HTS surfaces).
        n_t = self.cc_mesh.HTS_n_elem_thickness
        n_nodes_y = int(n_t) + 1

        # Fallback horizontal node count if per-surface info is missing.
        n_w = self.cc_mesh.HTS_n_elem_width
        fallback_n_nodes_x = (
            self.horizontal_nodes_x
            if self.horizontal_nodes_x is not None
            else int(n_w) + 1
        )

        # Bump coefficient for clustering along width.
        bump_coef = getattr(self.cc_mesh, "bump_coef", None)
        if bump_coef is None or bump_coef <= 0.0:
            bump_coef = 0.01

        # Re-build sets of filament and groove surfaces for classification.
        filament_meta = self.physical_surfaces_by_name.get("HTS", {})
        filament_surface_set = set(filament_meta.get("entities", []))

        groove_meta = self.physical_surfaces_by_name.get("HTS_Grooves", {})
        groove_surface_set = set(groove_meta.get("entities", []))

        # Track all HTS boundary curves so other routines can skip them.
        self.hts_boundary_curves = set()

        for surf_tag in surface_tags:
            # Horizontal node count for this specific surface.
            if surf_tag in self.hts_nodes_x_filaments:
                surf_n_nodes_x = self.hts_nodes_x_filaments[surf_tag]
            elif surf_tag in self.hts_nodes_x_grooves:
                surf_n_nodes_x = self.hts_nodes_x_grooves[surf_tag]
            else:
                surf_n_nodes_x = fallback_n_nodes_x

            # Get boundary curves of this HTS region.
            boundary = gmsh.model.getBoundary(
                [(2, surf_tag)], oriented=False, recursive=False
            )
            curve_tags = [c[1] for c in boundary if c[0] == 1]
            curve_tags = list(dict.fromkeys(curve_tags))

            for ctag in curve_tags:
                xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, ctag)
                dx = abs(xmax - xmin)
                dy = abs(ymax - ymin)

                # Mark as HTS boundary curve.
                self.hts_boundary_curves.add(ctag)

                if dx >= dy:
                    # Horizontal curve -> controls columns (along tape width).
                    gmsh.model.mesh.setTransfiniteCurve(
                        ctag,
                        surf_n_nodes_x,
                        "Bump",
                        float(bump_coef),
                    )
                else:
                    # Vertical curve -> controls rows (through thickness).
                    gmsh.model.mesh.setTransfiniteCurve(
                        ctag,
                        n_nodes_y,
                        "Progression",
                        1.0,
                    )

            # --- Surface-level transfinite / recombine behaviour ---
            if surf_tag in filament_surface_set:
                # Filaments: fully structured quads.
                gmsh.model.mesh.setTransfiniteSurface(surf_tag)
                gmsh.model.mesh.setRecombine(2, surf_tag)
            elif surf_tag in groove_surface_set:
                # Grooves: DO NOT set transfinite surface and DO NOT recombine.
                # The 2D mesher will generate an unstructured triangular mesh
                # inside, but boundary node distributions are still honoured.
                continue
            else:
                # Should not happen (all HTS surfaces are either filament
                # or groove), but keep a safe fallback.
                gmsh.model.mesh.setTransfiniteSurface(surf_tag)


    def _apply_horizontal_boundary_subdivisions_for_side_copper(self) -> None:
        """
        Apply transfinite subdivisions along the tape width direction for
        CopperLeft / CopperRight so that their horizontal boundaries use the
        same column pattern as the HTS / stacked layers.
        """

        # Canonical horizontal node count along the tape width.
        n_nodes_horizontal = self.horizontal_nodes_x
        if n_nodes_horizontal is None or n_nodes_horizontal <= 1:
            # Fallback to HTS_n_elem_width + 1 if something went wrong.
            n_w = self.cc_mesh.HTS_n_elem_width
            n_nodes_horizontal = int(n_w) + 1

        # Air surfaces: used to detect copper-air edges that we want
        # to keep coarser than the internal tape interfaces.
        air_surface_tags = set(self._get_layer_surface_tags("Air"))

        layer_names = ["CopperLeft", "CopperRight"]

        for layer_name in layer_names:
            surface_tags = self._get_layer_surface_tags(layer_name)

            for surf_tag in surface_tags:
                boundary = gmsh.model.getBoundary(
                    [(2, surf_tag)], oriented=False, recursive=False
                )
                curve_tags = [c[1] for c in boundary if c[0] == 1]
                curve_tags = list(dict.fromkeys(curve_tags))

                for ctag in curve_tags:
                    xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, ctag)
                    dx = abs(xmax - xmin)
                    dy = abs(ymax - ymin)

                    # Only curves that run mainly along x (tape width).
                    if dx >= dy:
                        # Check if this horizontal edge touches air.
                        higher_dim_tags, _ = gmsh.model.getAdjacencies(1, ctag)

                        if any(s in air_surface_tags for s in higher_dim_tags):
                            # Copper–air edge: keep this much coarser than internal
                            # tape interfaces to avoid over-refining the surrounding air.
                            # Heuristic: ~2.5% of the internal column count.
                            n_outer = max(
                                2, int(round(0.025 * n_nodes_horizontal))
                            )
                            gmsh.model.mesh.setTransfiniteCurve(
                                ctag,
                                n_outer,
                                "Progression",
                                1.0,
                            )
                            continue

                        # Internal horizontal interface: align with tape columns.
                        gmsh.model.mesh.setTransfiniteCurve(
                            ctag,
                            n_nodes_horizontal,
                            "Progression",
                            1.0,
                        )


    def _apply_vertical_boundary_subdivisions_for_side_copper(self) -> None:
        """
        Apply transfinite node counts to vertical boundary curves of
        CopperLeft / CopperRight that are adjacent to the Air region.
        """
        # Requires _compute_hts_and_layer_mesh_parameters() to have run
        # (hts_base_size_y set).
        h_ref = self.hts_base_size_y

        # YAML scale for copper; <= 0 or None -> use 1.0 (no extra scaling)
        scale_value = getattr(self.cc_mesh, "copper_elem_scale", None)
        if scale_value is None or scale_value <= 0.0:
            scale_value = 1.0

        # Air surfaces, to detect copper-air vertical edges
        air_surface_tags = set(self._get_layer_surface_tags("Air"))

        layer_names = ["CopperLeft", "CopperRight"]

        for layer_name in layer_names:
            surface_tags = self._get_layer_surface_tags(layer_name)

            for surf_tag in surface_tags:
                boundary = gmsh.model.getBoundary( [(2, surf_tag)], oriented=False, recursive=False )
                curve_tags = [ c[1] for c in boundary if c[0] == 1 ]
                curve_tags = list(dict.fromkeys(curve_tags))

                for ctag in curve_tags:
                    xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, ctag)
                    dx = abs(xmax - xmin)
                    dy = abs(ymax - ymin)

                    # We only care about vertical curves here.
                    if dy <= dx:
                        continue

                    # Check if this vertical curve touches Air.
                    higher_dim_tags, _ = gmsh.model.getAdjacencies(1, ctag)
                    if not any(s in air_surface_tags for s in higher_dim_tags):
                        # Internal copper-tape edge: stacked-layer logic handles it.
                        continue

                    thickness = dy
                    n_default = max(1, int(round(thickness / h_ref)))
                    n_layer   = max(1, int(round(scale_value * n_default)))
                    n_nodes_vertical = n_layer + 1

                    gmsh.model.mesh.setTransfiniteCurve(
                        ctag,
                        n_nodes_vertical,
                        "Progression",
                        1.0,
                    )


    def _apply_vertical_boundary_subdivisions_to_non_hts_layers(self) -> None:
        """
        Apply transfinite node counts to boundary curves of non-HTS, non-copper
        stacked layers (Substrate, Silver*), based on:
        - vertical_elems_by_layer[layer] for vertical curves (thickness dir),
        - self.horizontal_nodes_x for horizontal curves (width dir).

        Copper is intentionally excluded here to preserve more uniform copper
        node spacing controlled by the background sizing field.
        """

        # Horizontal node count along the tape width.
        n_nodes_horizontal = self.horizontal_nodes_x

        # Set of all HTS-related surfaces: used to avoid overriding
        # transfinite settings on HTS boundary curves.
        hts_surface_tags = set(self._get_hts_surface_tags())

        # Non-HTS stacked layers that we want to control in the vertical
        # (thickness) direction and in the horizontal (width) direction
        # via the canonical column count.
        layer_names = [
            "Substrate",
            "SilverBottom",
            "SilverTop",
        ]


        for layer_name in layer_names:
            n_layer = self.vertical_elems_by_layer.get(layer_name)

            if n_layer is None:
                continue

            surface_tags = self._get_layer_surface_tags(layer_name)

            # Number of nodes on vertical curves = number of elements + 1
            n_nodes_vertical = int(n_layer) + 1

            for surf_tag in surface_tags:
                # Get boundary curves of this surface
                boundary   = gmsh.model.getBoundary( [(2, surf_tag)], oriented=False, recursive=False )
                curve_tags = [c[1] for c in boundary if c[0] == 1]
                curve_tags = list(dict.fromkeys(curve_tags))

                for ctag in curve_tags:
                    # If this curve is shared with an HTS surface,
                    # skip it so the HTS progression is preserved.
                    higher_dim_tags, _ = gmsh.model.getAdjacencies(1, ctag)
                    if any(s in hts_surface_tags for s in higher_dim_tags):
                        logger.debug(
                            "[Mesh-CC]'%s' curve %d touches HTS; "
                            "skipping non-HTS transfinite constraint.",
                            layer_name,
                            ctag,
                        )
                        continue

                    xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, ctag)
                    dx = abs(xmax - xmin)
                    dy = abs(ymax - ymin)

                    if dy > dx:
                        # Predominantly vertical curve: control thickness direction
                        gmsh.model.mesh.setTransfiniteCurve(
                            ctag, n_nodes_vertical, "Progression", 1.0
                        )
                    else:
                        # Predominantly horizontal curve: enforce common columns.
                        # For SilverTop outer boundary, use a Bump distribution to mimic HTS clustering.
                        if layer_name == "SilverTop":
                            bump_coef = getattr(self.cc_mesh, "bump_coef", None)

                            if bump_coef is None or float(bump_coef) <= 0.0:
                                # Fallback: reuse HTS bump coefficient (or default)
                                bump_coef = getattr(self.cc_mesh, "bump_coef", None)

                            if bump_coef is None or float(bump_coef) <= 0.0:
                                bump_coef = 0.01

                            gmsh.model.mesh.setTransfiniteCurve(
                                ctag, n_nodes_horizontal, "Bump", float(bump_coef)
                            )
                        else:
                            gmsh.model.mesh.setTransfiniteCurve(
                                ctag, n_nodes_horizontal, "Progression", 1.0
                            )




    def _apply_progression_on_substrate_vertical_sides(self) -> None:
        """
        Apply a 'Progression' distribution on the vertical side boundary
        curves of the substrate, clustering nodes toward the HTS side (top in y).
        """
        r = getattr(self.cc_mesh, "substrate_side_progression", None)
        if r is None:
            return

        r = float(r)
        if r <= 1.0:
            return

        n_layer = self.vertical_elems_by_layer.get("Substrate")
        if n_layer is None:
            return
        n_nodes_vertical = int(n_layer) + 1

        substrate_surface_tags = self._get_layer_surface_tags("Substrate")
        if not substrate_surface_tags:
            return

        # All HTS-related surfaces (HTS + grooves) to detect the top interface curve.
        hts_surface_tags = set(self._get_hts_surface_tags())

        # Collect candidate curves: substrate boundary curves that are vertical
        # and do NOT touch HTS (so we keep the HTS/substrate interface unchanged).
        candidate_curve_tags: list[int] = []

        for surf_tag in substrate_surface_tags:
            boundary = gmsh.model.getBoundary(
                [(2, surf_tag)], oriented=False, recursive=False
            )
            curve_tags = [c[1] for c in boundary if c[0] == 1]
            curve_tags = list(dict.fromkeys(curve_tags))

            for ctag in curve_tags:
                # Skip curves that touch HTS surfaces (top interface).
                higher_dim_tags, _ = gmsh.model.getAdjacencies(1, ctag)
                if any(s in hts_surface_tags for s in higher_dim_tags):
                    continue

                xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, ctag)
                dx = abs(xmax - xmin)
                dy = abs(ymax - ymin)

                # Only vertical-ish curves (substrate left/right sides).
                if dy <= dx:
                    continue

                candidate_curve_tags.append(ctag)

        candidate_curve_tags = list(dict.fromkeys(candidate_curve_tags))
        if not candidate_curve_tags:
            logger.info(
                "[Mesh-CC] No substrate vertical side curves found for Progression."
            )
            return

        # Apply progression with refinement toward *top end* (larger y).
        for ctag in candidate_curve_tags:
            endpoints = gmsh.model.getBoundary(
                [(1, ctag)], oriented=True, recursive=False
            )
            point_tags = [p[1] for p in endpoints if p[0] == 0]

            if len(point_tags) < 2:
                continue

            p_start = point_tags[0]
            p_end = point_tags[-1]

            _, y0, _ = gmsh.model.getValue(0, p_start, [])
            _, y1, _ = gmsh.model.getValue(0, p_end, [])

            # Progression behaviour:
            # - ratio > 1 -> smallest segments near start
            # - ratio < 1 -> smallest segments near end
            #
            # Note: refinement direction depends on curve orientation.
            # We infer which endpoint is "top" by comparing point y-coordinates
            # and invert the progression ratio accordingly.
            #
            # We want smallest segments near the *top* (higher y).
            if y0 >= y1:
                prog = r
            else:
                prog = 1.0 / r

            gmsh.model.mesh.setTransfiniteCurve(
                ctag,
                n_nodes_vertical,
                "Progression",
                float(prog),
            )




    # ------------------------------------------------------------------ #
    #                           Public API
    # ------------------------------------------------------------------ #

    def generate_mesh(self, geom_folder: str) -> None:

        geo_unrolled_path = os.path.join(geom_folder, f"{self.magnet_name}.xao")

        # The .xao file is produced by GeometryConductorAC_CC and must contain the
        # expected physical group names used throughout this meshing routine
        # (HTS, optional HTS_Grooves, metal layers, Air, Air_Outer, etc.).
        gmsh.open(geo_unrolled_path)
        occ.synchronize()

        logger.debug("[Mesh-CC] OCC model synchronized after loading geometry file.")

        # Collect all physical groups into helper dictionaries that will
        # be reused in later steps (mesh fields, regions, ...).
        self._collect_physical_groups()

        # HTS base mesh sizes and vertical element counts.
        self._compute_hts_and_layer_mesh_parameters()

        # Transfinite meshing for HTS (filaments + grooves or monolithic).
        self._apply_transfinite_to_hts()

        # Apply transfinite constraints only to non-copper stacked layers
        # (Substrate, Silver*) so we do not distort copper node spacing.
        self._apply_vertical_boundary_subdivisions_to_non_hts_layers()

        # Refine substrate vertical sides near the HTS side using Progression.
        # This overrides the uniform 'Progression, 1.0' set above for those curves.
        self._apply_progression_on_substrate_vertical_sides()


        # Copper is handled by a uniform size field (no transfinite on copper curves).
        self._apply_uniform_copper_mesh_field()



        # -----------------------------------------------------------------
        # Global mesh size scaling and actual 2D mesh generation
        # -----------------------------------------------------------------
        scaling_global = self.cc_mesh.scaling_global

        # MeshSizeFactor scales characteristic lengths (point sizes, background
        # field values, etc.). Transfinite constraints are node *counts* and are
        # not affected by this factor.
        gmsh.option.setNumber("Mesh.MeshSizeFactor", float(scaling_global))

        # Boundary-based air sizing knob (fallback/default behaviour).
        # Note: a background field (if active) can override sizes in parts of the
        # domain; this still provides a robust air sizing rule when fields are not used.
        self._apply_air_boundary_mesh_size()

        # -----------------------------------------------------------------
        # Generate 1D first to "freeze" transfinite curve discretisations,
        # then generate 2D. This avoids Gmsh re-meshing/compacting 1D curves
        # when strong background fields are present.
        # -----------------------------------------------------------------
        gmsh.model.mesh.generate(1)
        gmsh.model.mesh.generate(2)

        # Generate cohomology basis functions (cuts) for transport current handling with h-phi-formulation
        self.generate_cuts()

        # Generate region file for easy access to physical groups from, e.g., the .pro template
        self.generate_regions_file()

        # Save the mesh to <magnet_name>.msh and optionally launch the GUI.
        gui = getattr(self.fdm.run, "launch_gui", False)
        self.save_mesh(gui=gui)

        logger.info( "[Mesh-CC] Mesh generation and saving complete. Mesh file: '%s'.", self.mesh_file )


    # -----------------------------------------------------------------
    # Generation of .regions file
    # -----------------------------------------------------------------

    def generate_regions_file(self) -> None:
        """
        Construct the .regions YAML file for the 2D CACCC conductor model.
        """
        # Initialise the RegionsModel container
        rm = RegionsModel()

        # Powered - HTS
        rm.powered["HTS"] = RegionsModelFiQuS.Powered()
        powered = rm.powered["HTS"]

        # Initialise list-valued fields
        for fld in ("vol", "surf", "surf_th", "surf_in", "surf_out", "curve", "surf_insul"):
            getattr(powered, fld).names   = []
            getattr(powered, fld).numbers = []

        # Terminal volume placeholders (not used in 2D but required structurally)
        powered.vol_in  = RegionsModelFiQuS.Region(name=None, number=None)
        powered.vol_out = RegionsModelFiQuS.Region(name=None, number=None)

        # Convention: for 2D models we store surface physical tags in the "vol"
        # fields to keep the RegionsModel structure compatible with 3D templates
        # and existing .pro logic.
        if "HTS" in self.physical_surfaces_by_name:
            meta = self.physical_surfaces_by_name["HTS"]
            powered.vol.names   = ["HTS"]
            powered.vol.numbers = [meta["phys_tag"]]

        # HTS boundary curves
        for edge_name in ["HTS_Upper", "HTS_Lower", "HTS_LeftEdge", "HTS_RightEdge"]:
            if edge_name in self.physical_curves_by_name:
                meta = self.physical_curves_by_name[edge_name]
                powered.surf_th.names.append(edge_name)
                powered.surf_th.numbers.append(meta["phys_tag"])


        # Induced - Substrate + Stabilizer layers
        rm.induced["Stabilizer"] = RegionsModelFiQuS.Induced()
        induced = rm.induced["Stabilizer"]

        # Initialise all induced list-valued fields
        for fld in ("vol", "surf_th", "surf_in", "surf_out", "cochain"):
            getattr(induced, fld).names   = []
            getattr(induced, fld).numbers = []

        # Metallic layer volumes (2D surfaces)
        metal_layers = [
            "Substrate",
            "SilverTop", "SilverBottom",
            "CopperTop", "CopperBottom",
            "CopperLeft", "CopperRight",
        ]

        for layer in metal_layers:
            if layer in self.physical_surfaces_by_name:
                meta = self.physical_surfaces_by_name[layer]
                induced.vol.names.append(layer)
                induced.vol.numbers.append(meta["phys_tag"])

        # Outer air boundary shared with the stabilizer
        if "Air_Outer" in self.physical_curves_by_name:
            meta = self.physical_curves_by_name["Air_Outer"]
            induced.surf_out.names   = ["Air_Outer"]
            induced.surf_out.numbers = [meta["phys_tag"]]

        # Metallic layer boundary edges
        edge_suffixes = ["Upper", "Lower", "LeftEdge", "RightEdge"]

        for layer in metal_layers:
            for suffix in edge_suffixes:
                name = f"{layer}_{suffix}"
                if name in self.physical_curves_by_name:
                    meta = self.physical_curves_by_name[name]
                    induced.surf_th.names.append(name)
                    induced.surf_th.numbers.append(meta["phys_tag"])

        # Explicit interface curves between layers
        interface_groups = [
            "Buffer Layer",
            "HTS_Silver_Interface",
            "HTS_CopperTop_Interface",
            "HTS_CopperLeft_Interface",
            "HTS_CopperRight_Interface",
            "SilverTop_CopperTop_Interface",
            "SilverBottom_CopperBottom_Interface",
            "Substrate_SilverBottom_Interface",
            "Substrate_CopperBottom_Interface",
            "Substrate_CopperLeft_Interface",
            "Substrate_CopperRight_Interface",
        ]

        for name in interface_groups:
            if name in self.physical_curves_by_name:
                meta = self.physical_curves_by_name[name]
                induced.surf_th.names.append(name)
                induced.surf_th.numbers.append(meta["phys_tag"])


        # Air region
        if "Air" in self.physical_surfaces_by_name:
            meta = self.physical_surfaces_by_name["Air"]
            rm.air.vol.name   = "Air"
            rm.air.vol.number = meta["phys_tag"]

        if "Air_Outer" in self.physical_curves_by_name:
            meta = self.physical_curves_by_name["Air_Outer"]
            rm.air.surf.name   = "Air_Outer"
            rm.air.surf.number = meta["phys_tag"]

        if "Air_Inner" in self.physical_curves_by_name:
            meta = self.physical_curves_by_name["Air_Inner"]
            rm.air.line.name   = "Air_Inner"
            rm.air.line.number = meta["phys_tag"]

        if "Gauging_point" in self.physical_points_by_name:
            meta = self.physical_points_by_name["Gauging_point"]
            rm.air.point.names   = ["Gauging_point"]
            rm.air.point.numbers = [meta["phys_tag"]]

        # Cut for transport current
        if "Cut" in self.physical_curves_by_name:
            meta = self.physical_curves_by_name["Cut"]
            rm.air.cochain.names   = ["Cut"]
            rm.air.cochain.numbers = [meta["phys_tag"]]


        # Write the regions file and log
        FilesAndFolders.write_data_to_yaml(self.regions_file, rm.model_dump())
        logger.info(f"[Mesh-CC] Regions file written to: {self.regions_file}")


    def generate_cuts(self) -> None:
        """
        Generate cohomology basis functions for the CACCC model.
        """
        # Transport current cut
        air_inner = self.physical_curves_by_name["Air_Inner"]
        air_surf = self.physical_surfaces_by_name["Air"]
        
        # Request one 1D cut cycle (homology) and the corresponding 1D cohomology
        # basis inside the Air surface. This supports transport-current handling in
        # h-phi formulations.
        gmsh.model.mesh.addHomologyRequest(
            "Homology", domainTags=[air_inner["phys_tag"]], dims=[1]
        )
        gmsh.model.mesh.addHomologyRequest(
            "Cohomology", domainTags=[air_surf["phys_tag"]], dims=[1]
        )

        # computeHomology() returns tags of generated chains/physical groups.
        # The indexing below follows Gmsh's returned ordering for our request pair.
        cuts = gmsh.model.mesh.computeHomology()

        # Rearrange so that positive currents have deterministic orientation.
        gmsh.model.mesh.clearHomologyRequests()
        gmsh.plugin.setString(
            "HomologyPostProcessing",
            "PhysicalGroupsOfOperatedChains",
            str(cuts[1][1]),
        )
        gmsh.plugin.setString(
            "HomologyPostProcessing",
            "PhysicalGroupsOfOperatedChains2",
            str(cuts[0][1]),
        )
        gmsh.plugin.run("HomologyPostProcessing")

        # Store the physical group tag for later use (e.g. writing to the regions file).
        # The "+1" matches the physical group id created by the post-processing plugin.
        meta: Dict[str, Any] = {"dim": 1, "phys_tag": cuts[1][1] + 1}
        self.physical_curves_by_name["Cut"] = meta
