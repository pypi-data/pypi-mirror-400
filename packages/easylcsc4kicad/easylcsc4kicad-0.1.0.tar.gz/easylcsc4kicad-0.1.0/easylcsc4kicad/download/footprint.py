"""
Footprint generation for KiCad.

Generates KiCad footprint files (.kicad_mod) from EasyEDA component data.
Uses KicadModTree library for footprint generation.
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from math import pow, sqrt

import requests
from KicadModTree import (
    Arc,
    Circle,
    Footprint,
    KicadFileHandler,
    Line,
    Model,
    Pad,
    Polygon,
    RectFill,
    RectLine,
    Text,
    Translation,
    Vector2D,
)

from easylcsc4kicad.download.model3d import download_step_model, download_wrl_model

logger = logging.getLogger(__name__)

# Layer mapping from EasyEDA to KiCad
LAYER_MAP = {
    "1": "F.Cu",
    "2": "B.Cu",
    "3": "F.SilkS",
    "4": "B.Silks",
    "5": "F.Paste",
    "6": "B.Paste",
    "7": "F.Mask",
    "8": "B.Mask",
    "10": "Edge.Cuts",
    "12": "F.Fab",
    "99": "F.SilkS",
    "100": "F.SilkS",
    "101": "F.SilkS",
}


@dataclass
class FootprintInfo:
    """Accumulator for footprint metadata during generation."""

    max_x: float = -10000
    max_y: float = -10000
    min_x: float = 10000
    min_y: float = 10000
    footprint_name: str = ""
    output_dir: str = ""
    footprint_lib: str = ""
    model_base_variable: str = ""
    model_dir: str = ""
    origin: tuple = (0, 0)
    models: list | None = None

    def __post_init__(self):
        if self.models is None:
            self.models = ["STEP"]


def mil2mm(data: float | str) -> float:
    """Convert mils to millimeters."""
    return float(data) / 3.937


def get_footprint_info(footprint_uuid: str) -> tuple[str, str, list, tuple]:
    """
    Fetch footprint data from EasyEDA API.

    Args:
        footprint_uuid: Footprint component UUID

    Returns:
        Tuple of (footprint_name, datasheet_link, shape_data, translation)
    """
    try:
        response = requests.get(
            f"https://easyeda.com/api/components/{footprint_uuid}",
            timeout=30,
        )
        if response.status_code != 200:
            logger.error(f"Failed to fetch footprint: {footprint_uuid}")
            return ("", "", [], (0, 0))

        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return ("", "", [], (0, 0))

    result = data.get("result", {})
    data_str = result.get("dataStr", {})

    footprint_shape = data_str.get("shape", [])
    x = data_str.get("head", {}).get("x", 0)
    y = data_str.get("head", {}).get("y", 0)

    # Get datasheet link
    try:
        datasheet_link = data_str.get("head", {}).get("c_para", {}).get("link", "")
    except (KeyError, AttributeError):
        datasheet_link = ""
        logger.debug("No datasheet link found")

    # Get footprint name
    footprint_name = (
        result.get("title", "NoName")
        .replace(" ", "_")
        .replace("/", "_")
        .replace("(", "_")
        .replace(")", "_")
    )

    return (footprint_name, datasheet_link, footprint_shape, (x, y))


def create_footprint(
    component_id: str,
    footprint_uuid: str,
    output_dir: str,
    footprint_lib: str = "footprint",
    model_dir: str = "packages3d",
    model_base_variable: str = "",
    models: list[str] | None = None,
    skip_existing: bool = False,
) -> tuple[str, str]:
    """
    Create KiCad footprint from EasyEDA component data.

    Args:
        component_id: LCSC component ID (e.g., "C1337258")
        footprint_uuid: Footprint component UUID
        output_dir: Output directory
        footprint_lib: Footprint library name
        model_dir: Directory for 3D models
        model_base_variable: KiCad path variable for 3D models
        models: List of model formats to download ("STEP", "WRL")
        skip_existing: Skip if footprint already exists

    Returns:
        Tuple of (footprint_reference, datasheet_link)
    """
    if models is None:
        models = ["STEP"]

    logger.info("Creating footprint...")

    # Fetch footprint data
    footprint_name, datasheet_link, footprint_shape, translation = get_footprint_info(
        footprint_uuid
    )

    if not footprint_name:
        logger.error("Failed to get footprint info")
        return ("", "")

    # Check skip existing
    fp_path = os.path.join(output_dir, footprint_lib, f"{footprint_name}.kicad_mod")
    if skip_existing and os.path.isfile(fp_path):
        logger.info(f"Footprint {footprint_name} already exists, skipping")
        return (f"{footprint_lib}:{footprint_name}", datasheet_link)

    # Initialize KiCad footprint
    kicad_mod = Footprint(f'"{footprint_name}"')
    kicad_mod.setDescription(f"{footprint_name} footprint")
    kicad_mod.setTags(f"{footprint_name} footprint {component_id}")

    footprint_info = FootprintInfo(
        footprint_name=footprint_name,
        output_dir=output_dir,
        footprint_lib=footprint_lib,
        model_base_variable=model_base_variable,
        model_dir=model_dir,
        origin=translation,
        models=models,
    )

    # Process each shape element
    for line in footprint_shape:
        args = [i for i in line.split("~") if i]
        if not args:
            continue

        model = args[0]
        handler = FOOTPRINT_HANDLERS.get(model)
        if handler:
            handler(args[1:], kicad_mod, footprint_info)
        else:
            logger.debug(f"Unknown footprint element: {model}")

    # Set footprint type
    if any(
        isinstance(child, Pad) and child.type == Pad.TYPE_THT
        for child in kicad_mod.getAllChilds()
    ):
        kicad_mod.setAttribute("through_hole")
    else:
        kicad_mod.setAttribute("smd")

    # Apply translation
    kicad_mod.insert(Translation(-mil2mm(translation[0]), -mil2mm(translation[1])))

    # Update bounds with translation
    footprint_info.max_x -= mil2mm(translation[0])
    footprint_info.max_y -= mil2mm(translation[1])
    footprint_info.min_x -= mil2mm(translation[0])
    footprint_info.min_y -= mil2mm(translation[1])

    # Add reference and value text
    kicad_mod.append(
        Text(
            type="reference",
            text="REF**",
            at=[
                (footprint_info.min_x + footprint_info.max_x) / 2,
                footprint_info.min_y - 2,
            ],
            layer="F.SilkS",
        )
    )
    kicad_mod.append(
        Text(
            type="user",
            text="${REFERENCE}",
            at=[
                (footprint_info.min_x + footprint_info.max_x) / 2,
                (footprint_info.min_y + footprint_info.max_y) / 2,
            ],
            layer="F.Fab",
        )
    )
    kicad_mod.append(
        Text(
            type="value",
            text=footprint_name,
            at=[
                (footprint_info.min_x + footprint_info.max_x) / 2,
                footprint_info.max_y + 2,
            ],
            layer="F.Fab",
        )
    )

    # Save footprint
    lib_dir = os.path.join(output_dir, footprint_lib)
    os.makedirs(lib_dir, exist_ok=True)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(fp_path)
    logger.info(f"Created footprint: {fp_path}")

    return (f"{footprint_lib}:{footprint_name}", datasheet_link)


# -----------------------------------------------------------------------------
# Footprint Handlers
# -----------------------------------------------------------------------------


def _h_track(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Track/line handler."""
    width = mil2mm(data[0])

    # Handle optional prefix at index 2
    if "$" in data[2]:
        points = [mil2mm(p) for p in data[3].split(" ") if p]
    else:
        points = [mil2mm(p) for p in data[2].split(" ") if p]

    for i in range(len(points) // 2 - 1):
        start = [points[2 * i], points[2 * i + 1]]
        end = [points[2 * i + 2], points[2 * i + 3]]

        layer = LAYER_MAP.get(data[1], "F.SilkS")

        # Update bounds
        info.max_x = max(info.max_x, start[0], end[0])
        info.min_x = min(info.min_x, start[0], end[0])
        info.max_y = max(info.max_y, start[1], end[1])
        info.min_y = min(info.min_y, start[1], end[1])

        kicad_mod.append(Line(start=start, end=end, width=width, layer=layer))


def _h_pad(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Pad handler."""
    try:
        TOPLAYER = "1"
        BOTTOMLAYER = "2"
        MULTILAYER = "11"

        shape_type = data[0]
        at = [mil2mm(data[1]), mil2mm(data[2])]
        size = [mil2mm(data[3]), mil2mm(data[4])]
        layer = data[5]
        pad_number = data[6]
        drill_diameter = float(mil2mm(data[7])) * 2
        drill_size = drill_diameter

        # Some shapes don't have polygon coordinates at index 8
        # Insert empty data to realign later indices
        if shape_type == "ELLIPSE" or (shape_type == "OVAL" and layer != MULTILAYER):
            data.insert(8, "")

        # Parse rotation - may be at different index depending on shape
        try:
            rotation = float(data[9])
        except (ValueError, IndexError):
            rotation = 0.0

        # Parse drill offset
        try:
            drill_offset = float(mil2mm(data[11]))
        except (ValueError, IndexError):
            drill_offset = 0.0

        primitives = ""

        # Determine pad type and layers
        if layer == MULTILAYER:
            pad_type = Pad.TYPE_THT
            pad_layer = Pad.LAYERS_THT
        elif layer == TOPLAYER:
            pad_type = Pad.TYPE_SMT
            pad_layer = Pad.LAYERS_SMT
        elif layer == BOTTOMLAYER:
            pad_type = Pad.TYPE_SMT
            pad_layer = ["B.Cu", "B.Mask", "B.Paste"]
        else:
            pad_type = Pad.TYPE_SMT
            pad_layer = Pad.LAYERS_SMT

        # Determine pad shape
        if shape_type == "OVAL":
            shape = Pad.SHAPE_OVAL
            if drill_offset == 0:
                drill_size = drill_diameter
            elif (drill_diameter < drill_offset) ^ (size[0] > size[1]):
                drill_size = [drill_diameter, drill_offset]
            else:
                drill_size = [drill_offset, drill_diameter]
        elif shape_type == "RECT":
            shape = Pad.SHAPE_RECT
            if drill_offset == 0:
                drill_size = drill_diameter
            else:
                drill_size = [drill_diameter, drill_offset]
        elif shape_type == "ELLIPSE":
            shape = Pad.SHAPE_CIRCLE
        elif shape_type == "POLYGON":
            shape = Pad.SHAPE_CUSTOM
            points = []
            for i, coord in enumerate(data[8].split(" ")):
                points.append(mil2mm(coord) - at[i % 2])
            primitives = [Polygon(nodes=zip(points[::2], points[1::2], strict=True))]
            size = [0.1, 0.1]
            drill_size = 1 if drill_offset == 0 else [drill_diameter, drill_offset]
        else:
            shape = Pad.SHAPE_OVAL

        # Update bounds
        info.max_x = max(info.max_x, at[0])
        info.min_x = min(info.min_x, at[0])
        info.max_y = max(info.max_y, at[1])
        info.min_y = min(info.min_y, at[1])

        kicad_mod.append(
            Pad(
                number=pad_number,
                type=pad_type,
                shape=shape,
                at=at,
                size=size,
                rotation=rotation,
                drill=drill_size,
                layers=pad_layer,
                primitives=primitives,
            )
        )
    except Exception as e:
        logger.debug(f"Failed to add PAD: {e}")


def _h_arc(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Arc handler."""
    try:
        svg_path = data[3] if "$" in data[2] else data[2]

        pattern = (
            r"M\s*([\d\.\-]+)[\s,*?]([\d\.\-]+)\s?A\s*([\d\.\-]+)[\s,*?]"
            r"([\d\.\-]+) ([\d\.\-]+) (\d) (\d) ([\d\.\-]+)[\s,*?]([\d\.\-]+)"
        )
        match = re.search(pattern, svg_path)

        if not match:
            logger.debug("Failed to parse ARC")
            return

        start_x, start_y = float(match.group(1)), float(match.group(2))
        rx, ry = float(match.group(3)), float(match.group(4))
        large_arc_flag = int(match.group(6))
        sweep_flag = int(match.group(7))
        end_x, end_y = float(match.group(8)), float(match.group(9))

        width = mil2mm(data[0])
        start_x = mil2mm(start_x)
        start_y = mil2mm(start_y)
        mid_x = mil2mm(rx)
        mid_y = mil2mm(ry)
        end_x = mil2mm(end_x)
        end_y = mil2mm(end_y)

        start = [start_x, start_y]
        end = [end_x, end_y]
        if sweep_flag == 0:
            start, end = end, start

        mid = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
        vec1 = Vector2D(mid[0] - start[0], mid[1] - start[1])

        length_squared = mid_x * mid_y - pow(vec1.distance_to((0, 0)), 2)
        if length_squared < 0:
            length_squared = 0
            large_arc_flag = 1

        vec2 = vec1.rotate(-90) if large_arc_flag == 1 else vec1.rotate(90)
        magnitude = sqrt(vec2[0] ** 2 + vec2[1] ** 2)
        if magnitude > 0:
            vec2 = Vector2D(vec2[0] / magnitude, vec2[1] / magnitude)

        length = sqrt(length_squared)
        cen = Vector2D(mid) + vec2 * length

        layer = LAYER_MAP.get(data[1], "F.SilkS")

        kicad_mod.append(
            Arc(start=start, end=end, width=width, center=cen, layer=layer)
        )

    except Exception as e:
        logger.debug(f"Failed to add ARC: {e}")


def _h_circle(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Circle handler."""
    if data[4] == "100":  # Skip circles on pads
        return

    center = [mil2mm(data[0]), mil2mm(data[1])]
    radius = mil2mm(data[2])
    width = mil2mm(data[3])
    layer = LAYER_MAP.get(data[4], "F.SilkS")

    kicad_mod.append(Circle(center=center, radius=radius, width=width, layer=layer))


def _h_solidregion(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Solid region handler (edge cuts)."""
    try:
        if data[2] == "npth":
            if "A" in data[1]:
                logger.debug("Complex Edge.Cuts shape not handled")
                return

            matches = re.findall(
                r"(?:M|L)\s+([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)", data[1]
            )
            points = [(mil2mm(m[0]), mil2mm(m[1])) for m in matches]
            kicad_mod.append(Polygon(nodes=points, layer="Edge.Cuts"))
    except Exception as e:
        logger.debug(f"Failed to add SOLIDREGION: {e}")


def _h_svgnode(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """SVG node handler (3D model reference)."""
    try:
        svg_data = json.loads(data[0])
        attrs = svg_data.get("attrs", {})

        model_uuid = attrs.get("uuid", "")
        c_origin = attrs.get("c_origin", "0,0").split(",")
        z_offset = attrs.get("z", "0")
        rotation = attrs.get("c_rotation", "0,0,0")

        if not model_uuid:
            return

        # Calculate model position
        tx = (float(c_origin[0]) - info.origin[0]) / 100
        ty = -(float(c_origin[1]) - info.origin[1]) / 100
        tz = float(z_offset) / 100

        rot = [-float(r) for r in rotation.split(",")]

        # Download models and add to footprint
        model_dir = os.path.join(info.output_dir, info.footprint_lib, info.model_dir)

        if "STEP" in info.models:
            step_path = os.path.join(model_dir, f"{info.footprint_name}.step")
            if download_step_model(model_uuid, step_path):
                # Build model path for footprint
                if info.model_base_variable:
                    if info.model_base_variable.startswith("$"):
                        path_name = (
                            f'"{info.model_base_variable}/'
                            f'{info.model_dir}/{info.footprint_name}.step"'
                        )
                    else:
                        path_name = (
                            f'"$({info.model_base_variable})/'
                            f'{info.model_dir}/{info.footprint_name}.step"'
                        )
                else:
                    path_name = f"{info.model_dir}/{info.footprint_name}.step"

                kicad_mod.append(Model(filename=path_name, at=[tx, ty, tz], rotate=rot))

        if "WRL" in info.models:
            wrl_path = os.path.join(model_dir, f"{info.footprint_name}.wrl")
            if download_wrl_model(model_uuid, wrl_path) and not any(
                isinstance(c, Model) for c in kicad_mod.getAllChilds()
            ):
                # Only add WRL if STEP wasn't added
                if info.model_base_variable:
                    if info.model_base_variable.startswith("$"):
                        path_name = (
                            f'"{info.model_base_variable}/'
                            f'{info.model_dir}/{info.footprint_name}.wrl"'
                        )
                    else:
                        path_name = (
                            f'"$({info.model_base_variable})/'
                            f'{info.model_dir}/{info.footprint_name}.wrl"'
                        )
                else:
                    path_name = f"{info.model_dir}/{info.footprint_name}.wrl"

                kicad_mod.append(Model(filename=path_name, at=[tx, ty, tz], rotate=rot))

    except Exception as e:
        logger.debug(f"Failed to process SVGNODE: {e}")


def _h_via(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """VIA handler (not supported, warning only)."""
    logger.debug("VIA not supported - check datasheet for heat dissipation")


def _h_rect(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Rectangle handler."""
    x_start = float(mil2mm(data[0]))
    y_start = float(mil2mm(data[1]))
    x_delta = float(mil2mm(data[2]))
    y_delta = float(mil2mm(data[3]))
    start = [x_start, y_start]
    end = [x_start + x_delta, y_start + y_delta]
    width = mil2mm(data[7])
    layer = LAYER_MAP.get(data[4], "F.SilkS")

    if width == 0:
        kicad_mod.append(RectFill(start=start, end=end, layer=layer))
    else:
        kicad_mod.append(RectLine(start=start, end=end, width=width, layer=layer))


def _h_hole(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """NPTH hole handler."""
    kicad_mod.append(
        Pad(
            number="",
            type=Pad.TYPE_NPTH,
            shape=Pad.SHAPE_CIRCLE,
            at=[mil2mm(data[0]), mil2mm(data[1])],
            size=mil2mm(data[2]) * 2,
            rotation=0,
            drill=mil2mm(data[2]) * 2,
            layers=Pad.LAYERS_NPTH,
        )
    )


def _h_text(data: list, kicad_mod: Footprint, info: FootprintInfo) -> None:
    """Text handler."""
    try:
        kicad_mod.append(
            Text(
                type="user",
                at=[mil2mm(data[1]), mil2mm(data[2])],
                text=data[8],
                layer="F.SilkS",
            )
        )
    except (ValueError, IndexError):
        logger.debug("Failed to add TEXT")


# Handler registry
FOOTPRINT_HANDLERS = {
    "TRACK": _h_track,
    "PAD": _h_pad,
    "ARC": _h_arc,
    "CIRCLE": _h_circle,
    "SOLIDREGION": _h_solidregion,
    "SVGNODE": _h_svgnode,
    "VIA": _h_via,
    "RECT": _h_rect,
    "HOLE": _h_hole,
    "TEXT": _h_text,
}
