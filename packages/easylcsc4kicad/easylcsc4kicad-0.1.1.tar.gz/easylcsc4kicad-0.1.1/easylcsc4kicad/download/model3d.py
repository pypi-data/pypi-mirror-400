"""
3D Model download functionality.

Downloads STEP and WRL 3D models from EasyEDA CDN.
"""

import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

WRL_HEADER = """#VRML V2.0 utf8
#created by EasyLCSC4KiCAD
#for more info see https://github.com/cypherpunksamurai/easylcsc4kicadz
"""


def download_step_model(
    component_uuid: str,
    output_path: str,
) -> bool:
    """
    Download STEP model from EasyEDA CDN.

    Args:
        component_uuid: 3D model UUID from component data
        output_path: Full path to save the STEP file

    Returns:
        True if download successful, False otherwise
    """
    logger.info(f"Downloading STEP model: {component_uuid}")

    # EasyEDA STEP CDN bucket
    url = f"https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{component_uuid}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logger.warning(f"STEP model not found: {component_uuid}")
            return False

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"STEP model saved: {output_path}")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to download STEP model: {e}")
        return False


def download_wrl_model(
    component_uuid: str,
    output_path: str,
) -> bool:
    """
    Download and convert OBJ to WRL format.

    Args:
        component_uuid: 3D model UUID from component data
        output_path: Full path to save the WRL file

    Returns:
        True if download/conversion successful, False otherwise
    """
    logger.info(f"Creating WRL model: {component_uuid}")

    url = f"https://easyeda.com/analyzer/api/3dmodel/{component_uuid}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logger.warning(f"3D model data not found: {component_uuid}")
            return False

        text = response.content.decode()
        wrl_content = _convert_obj_to_wrl(text)

        if not wrl_content:
            logger.warning("Failed to convert OBJ to WRL")
            return False

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write(wrl_content)

        logger.info(f"WRL model saved: {output_path}")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to download 3D model: {e}")
        return False


def _convert_obj_to_wrl(obj_text: str) -> str:
    """Convert OBJ format to VRML WRL format."""
    wrl_content = WRL_HEADER

    # Parse materials
    pattern = "newmtl .*?endmtl"
    matches = re.findall(pattern=pattern, string=obj_text, flags=re.DOTALL)

    materials = {}
    for match in matches:
        material = {}
        material_id = ""
        for value in match.split("\n"):
            if value[0:6] == "newmtl":
                material_id = value.split(" ")[1]
            elif value[0:2] == "Ka":
                material["ambientColor"] = value.split(" ")[1:]
            elif value[0:2] == "Kd":
                material["diffuseColor"] = value.split(" ")[1:]
            elif value[0:2] == "Ks":
                material["specularColor"] = value.split(" ")[1:]
            elif value[0] == "d":
                material["transparency"] = value.split(" ")[1]
        materials[material_id] = material

    # Parse vertices
    pattern = "v (.*?)\n"
    matches = re.findall(pattern=pattern, string=obj_text, flags=re.DOTALL)

    vertices = []
    for vertice in matches:
        vertices.append(
            " ".join(
                [str(round(float(coord) / 2.54, 4)) for coord in vertice.split(" ")]
            )
        )

    # Parse shapes
    shapes = obj_text.split("usemtl")[1:]
    for shape in shapes:
        lines = shape.split("\n")
        material = materials.get(lines[0].replace(" ", ""), {})
        if not material:
            continue

        index_counter = 0
        link_dict = {}
        coordIndex = []
        points = []

        for line in lines[1:]:
            if len(line) > 0 and line.startswith("f"):
                face = [int(idx) for idx in line.replace("//", "").split(" ")[1:]]
                face_index = []
                for idx in face:
                    if idx not in link_dict:
                        link_dict[idx] = index_counter
                        face_index.append(str(index_counter))
                        points.append(vertices[idx - 1])
                        index_counter += 1
                    else:
                        face_index.append(str(link_dict[idx]))
                face_index.append("-1")
                coordIndex.append(",".join(face_index) + ",")

        if not points:
            continue

        points.insert(-1, points[-1])

        diffuse = material.get("diffuseColor", ["0.8", "0.8", "0.8"])
        specular = material.get("specularColor", ["0.2", "0.2", "0.2"])
        transparency = material.get("transparency", "0")

        shape_str = f"""
Shape{{
\tappearance Appearance {{
\t\tmaterial Material {{
\t\t\tdiffuseColor {" ".join(diffuse)}
\t\t\tspecularColor {" ".join(specular)}
\t\t\tambientIntensity 0.2
\t\t\ttransparency {transparency}
\t\t\tshininess 0.5
\t\t}}
\t}}
\tgeometry IndexedFaceSet {{
\t\tccw TRUE
\t\tsolid FALSE
\t\tcoord DEF co Coordinate {{
\t\t\tpoint [
\t\t\t\t{", ".join(points)}
\t\t\t]
\t\t}}
\t\tcoordIndex [
\t\t\t{"".join(coordIndex)}
\t\t]
\t}}
}}"""
        wrl_content += shape_str

    return wrl_content
