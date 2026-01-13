"""
Component download orchestration.

Main entry point for downloading KiCad components from LCSC/EasyEDA.
"""

import logging

import requests

from easylcsc4kicad.download.footprint import create_footprint, get_footprint_info
from easylcsc4kicad.download.symbol import create_symbol

logger = logging.getLogger(__name__)


def download_component(
    component_id: str,
    output_dir: str = "easylcsc_lib",
    footprint_lib: str = "footprint",
    symbol_lib: str | None = None,
    symbol_path: str = "symbol",
    model_dir: str = "packages3d",
    model_base_variable: str = "",
    models: list[str] | None = None,
    create_footprint_flag: bool = True,
    create_symbol_flag: bool = True,
    skip_existing: bool = False,
) -> dict:
    """
    Download and generate KiCad component files from LCSC component ID.

    Args:
        component_id: LCSC part number (e.g., "C1337258")
        output_dir: Base output directory
        footprint_lib: Footprint library name
        symbol_lib: Symbol library name (default: component name)
        symbol_path: Subdirectory for symbols
        model_dir: Directory for 3D models
        model_base_variable: KiCad path variable for 3D models
        models: Model formats to download ("STEP", "WRL")
        create_footprint_flag: Whether to create footprint
        create_symbol_flag: Whether to create symbol
        skip_existing: Skip existing files

    Returns:
        Dict with status and created file paths
    """
    if models is None:
        models = ["STEP"]

    result = {
        "component_id": component_id,
        "success": False,
        "footprint": None,
        "symbol": None,
        "datasheet": None,
        "error": None,
    }

    logger.info(f"Downloading component: {component_id}")

    # Fetch component UUIDs from EasyEDA
    try:
        response = requests.get(
            f"https://easyeda.com/api/products/{component_id}/svgs",
            timeout=30,
        )
        data = response.json()

        if not data.get("success", False):
            result["error"] = f"Component not found: {component_id}"
            logger.error(result["error"])
            return result

    except requests.RequestException as e:
        result["error"] = f"Failed to fetch component: {e}"
        logger.error(result["error"])
        return result

    # Extract UUIDs
    component_data = data.get("result", [])
    if not component_data:
        result["error"] = "No component data returned"
        logger.error(result["error"])
        return result

    # Last item is footprint, others are symbols
    footprint_uuid = component_data[-1].get("component_uuid", "")
    symbol_uuids = [item.get("component_uuid", "") for item in component_data[:-1]]

    footprint_name = ""
    datasheet_link = ""

    # Create footprint
    if create_footprint_flag and footprint_uuid:
        footprint_ref, datasheet_link = create_footprint(
            component_id=component_id,
            footprint_uuid=footprint_uuid,
            output_dir=output_dir,
            footprint_lib=footprint_lib,
            model_dir=model_dir,
            model_base_variable=model_base_variable,
            models=models,
            skip_existing=skip_existing,
        )
        result["footprint"] = footprint_ref
        result["datasheet"] = datasheet_link
        footprint_name = footprint_ref.replace(".pretty", "") if footprint_ref else ""
    else:
        # Still need datasheet link even if not creating footprint
        if footprint_uuid:
            _, datasheet_link, _, _ = get_footprint_info(footprint_uuid)
            result["datasheet"] = datasheet_link

    # Create symbol
    if create_symbol_flag and symbol_uuids:
        symbol_name = create_symbol(
            component_id=component_id,
            symbol_component_uuids=symbol_uuids,
            footprint_name=footprint_name,
            datasheet_link=datasheet_link,
            library_name=symbol_lib,
            output_dir=output_dir,
            symbol_path=symbol_path,
            skip_existing=skip_existing,
        )
        result["symbol"] = symbol_name

    result["success"] = True
    logger.info(f"Component download complete: {component_id}")
    return result
