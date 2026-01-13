"""
Materials Project MCP Server
Provides full material data access via mp-api
"""

import json
import os
from typing import Optional, Any
from datetime import datetime

from fastmcp import FastMCP
from mp_api.client import MPRester

API_KEY = os.environ.get("MP_API_KEY")
if not API_KEY:
    raise ValueError(
        "MP_API_KEY environment variable is required. "
        "Get your API key from https://materialsproject.org/api"
    )

mcp = FastMCP("materials-project")


def serialize_object(obj: Any) -> Any:
    """Recursively serialize objects to JSON-compatible format"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [serialize_object(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): serialize_object(v) for k, v in obj.items()}
    if hasattr(obj, 'as_dict'):
        return serialize_object(obj.as_dict())
    if hasattr(obj, '__dict__'):
        return serialize_object(obj.__dict__)
    return str(obj)


def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            if len(v) > 0 and isinstance(v[0], dict):
                for i, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep).items())
            else:
                items.append((new_key, json.dumps(v, default=str)))
        else:
            items.append((new_key, v))
    return dict(items)


SUMMARY_FIELDS = [
    "material_id",
    "formula_pretty",
    "formula_anonymous",
    "chemsys",
    "composition",
    "composition_reduced",
    "elements",
    "nelements",
    "nsites",
    "volume",
    "density",
    "density_atomic",
    "symmetry",
    "structure",
    "energy_per_atom",
    "formation_energy_per_atom",
    "energy_above_hull",
    "is_stable",
    "equilibrium_reaction_energy_per_atom",
    "decomposes_to",
    "band_gap",
    "cbm",
    "vbm",
    "efermi",
    "is_gap_direct",
    "is_metal",
    "is_magnetic",
    "ordering",
    "total_magnetization",
    "total_magnetization_normalized_vol",
    "total_magnetization_normalized_formula_units",
    "num_magnetic_sites",
    "num_unique_magnetic_sites",
    "bulk_modulus",
    "shear_modulus",
    "universal_anisotropy",
    "homogeneous_poisson",
    "e_total",
    "e_ionic",
    "e_electronic",
    "n",
    "e_ij_max",
    "weighted_surface_energy_EV_PER_ANG2",
    "weighted_surface_energy",
    "weighted_work_function",
    "surface_anisotropy",
    "shape_factor",
    "has_reconstructed",
    "possible_species",
    "has_props",
    "theoretical",
    "database_IDs",
]


@mcp.tool
def fetch_full_material_data(
    material_ids: Optional[str] = None,
    formula: Optional[str] = None,
    chemsys: Optional[str] = None,
    elements: Optional[str] = None,
    band_gap_min: Optional[float] = None,
    band_gap_max: Optional[float] = None,
    is_stable: Optional[bool] = None,
    is_metal: Optional[bool] = None,
    is_magnetic: Optional[bool] = None,
    num_results: int = 10
) -> str:
    """
    Fetch full material data from Materials Project using summary.search.

    Args:
        material_ids: Comma-separated material IDs (e.g., "mp-149,mp-1234")
        formula: Chemical formula (e.g., "Si", "Fe2O3")
        chemsys: Chemical system (e.g., "Li-Fe-O")
        elements: Comma-separated elements to include (e.g., "Si,O")
        band_gap_min: Minimum band gap in eV
        band_gap_max: Maximum band gap in eV
        is_stable: Filter for thermodynamically stable materials
        is_metal: Filter for metallic materials
        is_magnetic: Filter for magnetic materials
        num_results: Maximum number of results (default 10)

    Returns:
        JSON string with full material data including thermodynamic, electronic,
        mechanical, magnetic, and symmetry properties.
    """
    try:
        with MPRester(API_KEY) as mpr:
            search_params = {"num_chunks": 1, "chunk_size": num_results}

            if material_ids:
                ids = [mid.strip() for mid in material_ids.split(",")]
                search_params["material_ids"] = ids

            if formula:
                search_params["formula"] = formula

            if chemsys:
                search_params["chemsys"] = chemsys

            if elements:
                elem_list = [e.strip() for e in elements.split(",")]
                search_params["elements"] = elem_list

            if band_gap_min is not None or band_gap_max is not None:
                bg_min = band_gap_min if band_gap_min is not None else 0
                bg_max = band_gap_max if band_gap_max is not None else 100
                search_params["band_gap"] = (bg_min, bg_max)

            if is_stable is not None:
                search_params["is_stable"] = is_stable

            if is_metal is not None:
                search_params["is_metal"] = is_metal

            if is_magnetic is not None:
                search_params["is_magnetic"] = is_magnetic

            search_params["fields"] = SUMMARY_FIELDS

            docs = mpr.materials.summary.search(**search_params)

            results = []
            for doc in docs:
                doc_dict = serialize_object(doc)
                flat_dict = flatten_dict(doc_dict)
                results.append(flat_dict)

            output = {
                "status": "success",
                "count": len(results),
                "query_params": {k: str(v) for k, v in search_params.items() if k != "fields"},
                "data": results,
                "timestamp": datetime.now().isoformat()
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2)


@mcp.tool
def get_structure_details(material_id: str) -> str:
    """
    Get detailed crystal structure information for a specific material.

    Args:
        material_id: Materials Project ID (e.g., "mp-149")

    Returns:
        JSON string with lattice parameters, atomic sites, coordinates,
        space group, and other structural details.
    """
    try:
        with MPRester(API_KEY) as mpr:
            structure = mpr.get_structure_by_material_id(material_id)

            lattice = structure.lattice
            lattice_info = {
                "a": lattice.a,
                "b": lattice.b,
                "c": lattice.c,
                "alpha": lattice.alpha,
                "beta": lattice.beta,
                "gamma": lattice.gamma,
                "volume": lattice.volume,
                "matrix": lattice.matrix.tolist()
            }

            sites = []
            for site in structure.sites:
                site_info = {
                    "species": str(site.specie),
                    "coords_fractional": list(site.frac_coords),
                    "coords_cartesian": list(site.coords),
                    "properties": serialize_object(site.properties) if site.properties else {}
                }
                sites.append(site_info)

            analyzer_data = {}
            try:
                from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
                sga = SpacegroupAnalyzer(structure)
                analyzer_data = {
                    "space_group_symbol": sga.get_space_group_symbol(),
                    "space_group_number": sga.get_space_group_number(),
                    "crystal_system": sga.get_crystal_system(),
                    "point_group": sga.get_point_group_symbol(),
                    "hall_symbol": sga.get_hall()
                }
            except Exception:
                pass

            output = {
                "status": "success",
                "material_id": material_id,
                "formula": structure.composition.reduced_formula,
                "lattice": lattice_info,
                "num_sites": len(sites),
                "sites": sites,
                "symmetry": analyzer_data,
                "timestamp": datetime.now().isoformat()
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "material_id": material_id,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2)


@mcp.tool
def search_materials_by_property(
    property_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    num_results: int = 20
) -> str:
    """
    Search materials by specific property ranges.

    Args:
        property_name: Property to search (band_gap, formation_energy_per_atom,
                      energy_above_hull, bulk_modulus, shear_modulus, density, volume)
        min_value: Minimum value for the property
        max_value: Maximum value for the property
        num_results: Maximum number of results

    Returns:
        JSON string with materials matching the property criteria.
    """
    valid_properties = {
        "band_gap": "band_gap",
        "formation_energy": "formation_energy_per_atom",
        "formation_energy_per_atom": "formation_energy_per_atom",
        "energy_above_hull": "energy_above_hull",
        "bulk_modulus": "bulk_modulus",
        "shear_modulus": "shear_modulus",
        "density": "density",
        "volume": "volume",
        "total_magnetization": "total_magnetization"
    }

    if property_name.lower() not in valid_properties:
        return json.dumps({
            "status": "error",
            "message": f"Invalid property. Valid options: {list(valid_properties.keys())}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

    prop_key = valid_properties[property_name.lower()]

    try:
        with MPRester(API_KEY) as mpr:
            search_params = {
                "num_chunks": 1,
                "chunk_size": num_results,
                "fields": SUMMARY_FIELDS
            }

            min_val = min_value if min_value is not None else -1e10
            max_val = max_value if max_value is not None else 1e10
            search_params[prop_key] = (min_val, max_val)

            docs = mpr.materials.summary.search(**search_params)

            results = []
            for doc in docs:
                doc_dict = serialize_object(doc)
                flat_dict = flatten_dict(doc_dict)
                results.append(flat_dict)

            output = {
                "status": "success",
                "count": len(results),
                "property_searched": property_name,
                "range": {"min": min_value, "max": max_value},
                "data": results,
                "timestamp": datetime.now().isoformat()
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2)


@mcp.tool
def get_phase_diagram_info(chemsys: str) -> str:
    """
    Get phase diagram information for a chemical system.

    Args:
        chemsys: Chemical system (e.g., "Li-Fe-O", "Si-O")

    Returns:
        JSON string with phase diagram entries and stability information.
    """
    try:
        with MPRester(API_KEY) as mpr:
            entries = mpr.get_entries_in_chemsys(chemsys)

            entry_data = []
            for entry in entries:
                entry_info = {
                    "entry_id": str(entry.entry_id),
                    "composition": str(entry.composition.reduced_formula),
                    "energy": entry.energy,
                    "energy_per_atom": entry.energy_per_atom,
                    "correction": entry.correction,
                    "parameters": serialize_object(entry.parameters) if hasattr(entry, 'parameters') else {}
                }
                entry_data.append(entry_info)

            output = {
                "status": "success",
                "chemsys": chemsys,
                "num_entries": len(entry_data),
                "entries": entry_data,
                "timestamp": datetime.now().isoformat()
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "chemsys": chemsys,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2)


@mcp.tool
def compare_materials(material_ids: str) -> str:
    """
    Compare multiple materials side by side.

    Args:
        material_ids: Comma-separated material IDs (e.g., "mp-149,mp-1234,mp-5678")

    Returns:
        JSON string with comparison table of key properties.
    """
    try:
        ids = [mid.strip() for mid in material_ids.split(",")]

        with MPRester(API_KEY) as mpr:
            docs = mpr.materials.summary.search(
                material_ids=ids,
                fields=SUMMARY_FIELDS
            )

            comparison = []
            for doc in docs:
                doc_dict = serialize_object(doc)

                key_props = {
                    "material_id": doc_dict.get("material_id"),
                    "formula": doc_dict.get("formula_pretty"),
                    "band_gap_eV": doc_dict.get("band_gap"),
                    "is_metal": doc_dict.get("is_metal"),
                    "formation_energy_eV_atom": doc_dict.get("formation_energy_per_atom"),
                    "energy_above_hull_eV_atom": doc_dict.get("energy_above_hull"),
                    "is_stable": doc_dict.get("is_stable"),
                    "density_g_cm3": doc_dict.get("density"),
                    "volume_A3": doc_dict.get("volume"),
                    "nsites": doc_dict.get("nsites"),
                    "is_magnetic": doc_dict.get("is_magnetic"),
                    "total_magnetization": doc_dict.get("total_magnetization"),
                    "bulk_modulus_GPa": doc_dict.get("bulk_modulus", {}).get("vrh") if isinstance(doc_dict.get("bulk_modulus"), dict) else doc_dict.get("bulk_modulus"),
                    "shear_modulus_GPa": doc_dict.get("shear_modulus", {}).get("vrh") if isinstance(doc_dict.get("shear_modulus"), dict) else doc_dict.get("shear_modulus"),
                    "symmetry_symbol": doc_dict.get("symmetry", {}).get("symbol") if isinstance(doc_dict.get("symmetry"), dict) else None,
                    "crystal_system": doc_dict.get("symmetry", {}).get("crystal_system") if isinstance(doc_dict.get("symmetry"), dict) else None,
                }
                comparison.append(key_props)

            output = {
                "status": "success",
                "num_materials": len(comparison),
                "comparison": comparison,
                "timestamp": datetime.now().isoformat()
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
