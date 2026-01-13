"""
Symbol generation for KiCad.

Generates KiCad symbol library files (.kicad_sym) from EasyEDA component data.
Uses string templates - no external dependencies required.
"""

import logging
import os
import re
from dataclasses import dataclass
from math import acos, cos, pi, sin, sqrt

import requests

logger = logging.getLogger(__name__)

# KiCad symbol library header/footer
SYMBOL_LIB_HEADER = """\
(kicad_symbol_lib (version 20210201) (generator EasyLCSC4KiCAD)
"""
SYMBOL_LIB_FOOTER = ")\n"

# Value types to extract from component data
SUPPORTED_VALUE_TYPES = [
    "Resistance",
    "Capacitance",
    "Inductance",
    "Frequency",
]


@dataclass
class KicadSymbol:
    """Accumulator for symbol drawing primitives."""

    drawing: str = ""
    pin_names_hide: str = "(pin_names hide)"
    pin_numbers_hide: str = "(pin_numbers hide)"


def mil2mm(data: float | str) -> float:
    """Convert mils to millimeters."""
    return float(data) / 3.937


def create_symbol(
    component_id: str,
    symbol_component_uuids: list[str],
    footprint_name: str,
    datasheet_link: str,
    library_name: str | None,
    output_dir: str,
    symbol_path: str = "symbol",
    skip_existing: bool = False,
) -> str | None:
    """
    Create KiCad symbol from EasyEDA component data.

    Args:
        component_id: LCSC component ID (e.g., "C1337258")
        symbol_component_uuids: List of symbol UUIDs from component
        footprint_name: Associated footprint name
        datasheet_link: Datasheet URL
        library_name: Symbol library name (default: component title)
        output_dir: Output directory
        symbol_path: Subdirectory for symbols
        skip_existing: Skip if symbol already exists

    Returns:
        Created symbol name, or None if failed
    """
    kicad_symbol = KicadSymbol()
    component_name = ""
    symbol_prefix = "U"
    component_types_values: list[tuple[str, str]] = []

    for i, component_uuid in enumerate(symbol_component_uuids):
        try:
            response = requests.get(
                f"https://easyeda.com/api/components/{component_uuid}",
                timeout=30,
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch symbol data: {component_uuid}")
                continue

            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Request error fetching symbol: {e}")
            continue

        result = data.get("result", {})
        symbol_shape = result.get("dataStr", {}).get("shape", [])

        # Get symbol prefix
        try:
            symbol_prefix = (
                result.get("packageDetail", {})
                .get("dataStr", {})
                .get("head", {})
                .get("c_para", {})
                .get("pre", "U")
                .replace("?", "")
            )
        except (KeyError, AttributeError):
            symbol_prefix = "U"

        # Get component title
        component_title = (
            result.get("title", "Unknown")
            .replace(" ", "_")
            .replace(".", "_")
            .replace("/", "{slash}")
            .replace("\\", "{backslash}")
            .replace("<", "{lt}")
            .replace(">", "{gt}")
            .replace(":", "{colon}")
            .replace('"', "{dblquote}")
        )

        # Extract value types
        c_para = result.get("dataStr", {}).get("head", {}).get("c_para", {})
        for value_type in SUPPORTED_VALUE_TYPES:
            if value_type in c_para:
                component_types_values.append((value_type, c_para[value_type]))

        if not component_name:
            component_name = component_title
            component_title += "_0"

        # Skip first symbol if multiple (it's typically a duplicate)
        if len(symbol_component_uuids) >= 2 and i == 0:
            continue

        # Get translation for coordinate conversion
        translation = (
            result.get("dataStr", {}).get("head", {}).get("x", 0),
            result.get("dataStr", {}).get("head", {}).get("y", 0),
        )

        logger.info(f"Creating symbol {component_title}")
        kicad_symbol.drawing += f'\n    (symbol "{component_title}_1"'

        # Process each shape element
        for line in symbol_shape:
            args = [i for i in line.split("~") if i]
            if not args:
                continue

            model = args[0]
            handler = SYMBOL_HANDLERS.get(model)
            if handler:
                handler(args[1:], translation, kicad_symbol)
            else:
                logger.debug(f"Unknown symbol element: {model}")

        kicad_symbol.drawing += "\n    )"

    if not component_name:
        logger.error("Failed to create symbol: no component data")
        return None

    # Use component name as library name if not specified
    if not library_name:
        library_name = component_name

    # Build filename
    symbol_dir = os.path.join(output_dir, symbol_path)
    filename = os.path.join(symbol_dir, f"{library_name}.kicad_sym")

    # Check skip existing
    if skip_existing and os.path.exists(filename):
        logger.info(f"Symbol {component_name} already exists, skipping")
        return component_name

    # Build symbol template
    type_values_props = _get_type_values_properties(6, component_types_values)

    template = f"""\
  (symbol "{component_name}" {kicad_symbol.pin_names_hide} {kicad_symbol.pin_numbers_hide} (in_bom yes) (on_board yes)
    (property "Reference" "{symbol_prefix}" (id 0) (at 0 1.27 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{component_name}" (id 1) (at 0 -2.54 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "{footprint_name}" (id 2) (at 0 -10.16 0)
      (effects (font (size 1.27 1.27) italic) hide)
    )
    (property "Datasheet" "{datasheet_link}" (id 3) (at -2.286 0.127 0)
      (effects (font (size 1.27 1.27)) (justify left) hide)
    )
    (property "ki_keywords" "{component_id}" (id 4) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "LCSC" "{component_id}" (id 5) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    {type_values_props}{kicad_symbol.drawing}
  )
"""

    # Ensure directory exists
    os.makedirs(symbol_dir, exist_ok=True)

    # Write or update library
    if os.path.exists(filename):
        _update_library(filename, component_name, template, skip_existing)
    else:
        with open(filename, "w") as f:
            f.write(SYMBOL_LIB_HEADER)
            f.write(template)
            f.write(SYMBOL_LIB_FOOTER)
        logger.info(f"Created symbol library: {filename}")

    return component_name


def _get_type_values_properties(start_index: int, values: list[tuple[str, str]]) -> str:
    """Generate property strings for value types."""
    return "\n".join(
        f"""(property "{vtype}" "{vvalue}" (id {start_index + i}) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )"""
        for i, (vtype, vvalue) in enumerate(values)
    )


def _update_library(
    filename: str,
    component_name: str,
    template: str,
    skip_existing: bool,
) -> None:
    """Update existing symbol library with new/updated symbol."""
    with open(filename, "rb+") as f:
        content = f.read().decode()

        if f'symbol "{component_name}"' in content:
            if skip_existing:
                logger.info(f"Symbol {component_name} exists, skipping")
                return

            # Replace existing symbol
            pattern = rf'  \(symbol "{component_name}" (\n|.)*?\n  \)'
            content = re.sub(
                pattern, template.rstrip(), content, flags=re.DOTALL, count=1
            )
            f.seek(0)
            f.truncate()
            f.write(content.encode())
            logger.info(f"Updated symbol: {component_name}")
        else:
            # Append before footer
            new_content = content[: content.rfind(")")]
            new_content += template + SYMBOL_LIB_FOOTER
            f.seek(0)
            f.truncate()
            f.write(new_content.encode())
            logger.info(f"Added symbol: {component_name}")


# -----------------------------------------------------------------------------
# Symbol Handlers
# -----------------------------------------------------------------------------


def _h_rectangle(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Rectangle handler."""
    try:
        if len(data) == 12:
            x1, y1 = float(data[0]), float(data[1])
            x2 = x1 + float(data[4])
            y2 = y1 + float(data[5])
        else:
            x1, y1 = float(data[0]), float(data[1])
            x2 = x1 + float(data[2])
            y2 = y1 + float(data[3])

        x1 = mil2mm(x1 - translation[0])
        y1 = -mil2mm(y1 - translation[1])
        x2 = mil2mm(x2 - translation[0])
        y2 = -mil2mm(y2 - translation[1])

        symbol.drawing += f"""
      (rectangle
        (start {x1} {y1})
        (end {x2} {y2})
        (stroke (width 0) (type default) (color 0 0 0 0))
        (fill (type background))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add rectangle: {e}")


def _h_circle(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Circle handler."""
    try:
        x = mil2mm(float(data[0]) - translation[0])
        y = -mil2mm(float(data[1]) - translation[1])
        radius = mil2mm(float(data[2]))

        symbol.drawing += f"""
      (circle
        (center {x} {y})
        (radius {radius})
        (stroke (width 0) (type default) (color 0 0 0 0))
        (fill (type background))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add circle: {e}")


def _h_pin(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Pin handler."""
    try:
        # Handle variable data length
        if len(data) == 24:
            data.insert(5, "0")
        elif len(data) == 28:
            data.insert(1, "0")

        # Electrical type mapping
        elec_types = {
            "0": "unspecified",
            "1": "input",
            "2": "output",
            "3": "bidirectional",
            "4": "power_in",
        }
        electrical_type = elec_types.get(data[1], "unspecified")

        pin_number = data[2]
        pin_name = data[13]

        x = round(mil2mm(float(data[3]) - translation[0]), 3)
        y = round(-mil2mm(float(data[4]) - translation[1]), 3)

        rotation = 0
        if data[5] in ["0", "90", "180", "270"]:
            rotation = (int(data[5]) + 180) % 360

        # Calculate pin length
        if rotation in [0, 180]:
            length = round(mil2mm(abs(float(data[8].split("h")[-1]))), 3)
        elif rotation in [90, 270]:
            length = mil2mm(abs(float(data[8].split("v")[-1])))
        else:
            length = 2.54

        # Handle pin visibility
        try:
            if data[9].split("^^")[1] != "0":
                symbol.pin_names_hide = ""
            if data[17].split("^^")[1] != "0":
                symbol.pin_numbers_hide = ""
        except (IndexError, KeyError):
            symbol.pin_names_hide = ""
            symbol.pin_numbers_hide = ""

        # Font sizes
        try:
            name_size = mil2mm(float(data[16].replace("pt", "")))
            number_size = mil2mm(float(data[24].replace("pt", "")))
        except (ValueError, IndexError):
            name_size = number_size = 1

        symbol.drawing += f"""
      (pin {electrical_type} line
        (at {x} {y} {rotation})
        (length {length})
        (name "{pin_name}" (effects (font (size {name_size} {name_size}))))
        (number "{pin_number}" (effects (font (size {number_size} {number_size}))))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add pin: {e}")


def _h_text(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Text/annotation handler."""
    try:
        x = mil2mm(float(data[1]) - translation[0])
        y = -mil2mm(float(data[2]) - translation[1])
        angle = (float(data[3]) * 10 + 1800) % 3600
        font_size = mil2mm(float(data[6].replace("pt", "")))
        text = data[10]

        symbol.drawing += f"""
      (text
        "{text}"
        (at {x} {y} {angle})
        (effects (font (size {font_size} {font_size})))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add text: {e}")


def _h_polyline(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Polyline handler."""
    try:
        path_string = data[0].split(" ")
        polypts = []
        for i in range(len(path_string) // 2):
            px = mil2mm(float(path_string[2 * i]) - translation[0])
            py = -mil2mm(float(path_string[2 * i + 1]) - translation[1])
            polypts.append(f"(xy {px} {py})")

        polystr = "\n          ".join(polypts)

        symbol.drawing += f"""
      (polyline
        (pts
          {polystr}
        )
        (stroke (width 0) (type default) (color 0 0 0 0))
        (fill (type none))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add polyline: {e}")


def _h_polygon(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Closed polygon handler."""
    try:
        path_string = [i for i in data[0].split(" ") if i]
        polypts = []
        for i in range(len(path_string) // 2):
            px = mil2mm(float(path_string[2 * i]) - translation[0])
            py = -mil2mm(float(path_string[2 * i + 1]) - translation[1])
            polypts.append(f"(xy {px} {py})")

        # Close polygon
        polypts.append(polypts[0])
        polystr = "\n          ".join(polypts)

        symbol.drawing += f"""
      (polyline
        (pts
          {polystr}
        )
        (stroke (width 0) (type default) (color 0 0 0 0))
        (fill (type background))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add polygon: {e}")


def _h_triangle(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Triangle handler."""
    try:
        data[0] = data[0].replace("M ", "").replace("L ", "").replace(" Z", "")
        _h_polygon(data, translation, symbol)
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add triangle: {e}")


def _h_arc(data: list[str], translation: tuple, symbol: KicadSymbol) -> None:
    """Arc handler."""

    def get_center_param(match):
        """Calculate arc center parameters from SVG arc data."""
        e = float([i for i in re.split(r" |,", match[0][1]) if i][0])
        t = float([i for i in re.split(r" |,", match[0][1]) if i][1])
        s = float([i for i in re.split(r" |,", match[1][1]) if i][0])
        l = float([i for i in re.split(r" |,", match[1][1]) if i][1])
        r = float([i for i in re.split(r" |,", match[1][1]) if i][3])
        o = float([i for i in re.split(r" |,", match[1][1]) if i][4])
        n = float([i for i in re.split(r" |,", match[1][1]) if i][5])
        a = float([i for i in re.split(r" |,", match[1][1]) if i][6])

        def c(e, t, n, a):
            i = e * n + t * a
            r = sqrt((e * e + t * t) * (n * n + a * a))
            return acos(i / r) if r != 0 else 0

        f = 2 * pi
        if o < 0:
            o = -o
        if s < 0:
            s = -s
        if o == s:
            l = 0

        C = sin(l)
        y = cos(l)
        b = (e - n) / 2
        v = (t - a) / 2
        S = (e + n) / 2
        P = (t + a) / 2

        if o < 0.00001 or s < 0.00001:
            h = c(1, 0, n - e, a - t)
            return (S, P, h, pi)

        A = y * b + C * v
        T = y * v - C * b
        D = A * A / (o * o) + T * T / (s * s)

        if D > 1:
            o *= sqrt(D)
            s *= sqrt(D)

        k = o * s
        M = o * T
        I = s * A
        L = M * M + I * I

        if not L:
            return (S, P, 0, 0)

        w = sqrt(abs((k * k - L) / L))
        O = w * M / s
        R = -w * I / o
        u = y * O - C * R + S
        g = C * O + y * R + P
        E = (A - O) / o
        N = (A + O) / o
        F = (T - R) / s
        x = (T + R) / s
        h = c(1, 0, E, F)
        m = c(E, F, -N, -x)

        while m > f:
            m -= f
        while m < 0:
            m += f
        if r != 0:
            m -= f

        return (u, g, h, m)

    try:
        match = re.findall(r"([MA])([eE ,\-\+.\d]+)", data[0])
        cx, cy, theta, delta_theta = get_center_param(match)
        radius = float([i for i in re.split(r" |,", match[1][1]) if i][0])

        theta /= 2
        x_start = cx + radius * cos(theta)
        y_start = -(cy - radius * sin(theta))
        x_end = cx + radius * cos(theta + delta_theta)
        y_end = -(cy - radius * sin(theta + delta_theta))
        x_mid = cx + radius * cos(theta + delta_theta / 2)
        y_mid = -(cy - radius * sin(theta + delta_theta / 2))

        x_start = mil2mm(x_start - translation[0])
        y_start = -mil2mm(y_start - translation[1])
        x_end = mil2mm(x_end - translation[0])
        y_end = -mil2mm(y_end - translation[1])
        x_mid = mil2mm(x_mid - translation[0])
        y_mid = -mil2mm(y_mid - translation[1])

        symbol.drawing += f"""
      (arc
        (start {x_start} {y_start})
        (mid {x_mid} {y_mid})
        (end {x_end} {y_end})
        (stroke (width 0) (type default) (color 0 0 0 0))
        (fill (type none))
      )"""
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to add arc: {e}")


# Handler registry
SYMBOL_HANDLERS = {
    "R": _h_rectangle,
    "E": _h_circle,
    "P": _h_pin,
    "T": _h_text,
    "PL": _h_polyline,
    "PG": _h_polygon,
    "PT": _h_triangle,
    "A": _h_arc,
}
