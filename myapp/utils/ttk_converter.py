# import xml.etree.ElementTree as ET
# import zipfile

# import os

# def parse_ttkproject(file_path):
#     print(">>> Parsing:", file_path)

#     # Case A: zipped TatukGIS project
#     if zipfile.is_zipfile(file_path):
#         print(">>> This is a ZIP-based .ttkproject")

#         with zipfile.ZipFile(file_path, 'r') as z:
#             xml_file = None

#             # Find XML inside zip (TatukGIS stores inside folder)
#             for name in z.namelist():
#                 if name.lower().endswith(".xml"):
#                     xml_file = name
#                     break

#             if not xml_file:
#                 print(">>> No XML file found inside ZIP")
#                 return {"coordinate_system": None, "layers": []}

#             print(">>> Found XML inside ZIP:", xml_file)

#             xml_content = z.read(xml_file)
#             root = ET.fromstring(xml_content)

#     else:
#         print(">>> This is plain XML file")
#         tree = ET.parse(file_path)
#         root = tree.getroot()

#     # Extract EPSG
#     epsg_node = root.find("./Viewer/CS/EPSG")
#     epsg = epsg_node.text if epsg_node is not None else None

#     print(">>> EPSG Found:", epsg)

#     layers = []
#     for layer_node in root.findall("./Layers/Layer"):
#         name = layer_node.get("Name")
#         path = layer_node.get("Path")

#         print(">>> Found Layer:", name, "| Path:", path)

#         if not path:
#             continue

#         ext = os.path.splitext(path)[1].lower()

#         if ext == ".shp":
#             layer_type = "vector"
#         elif ext in [".tif", ".tiff", ".jpg", ".jpeg", ".png", ".kmz", ".kml"]:
#             layer_type = "raster"
#         else:
#             layer_type = "unknown"

#         layers.append({
#             "name": name,
#             "file": path,
#             "type": layer_type
#         })

#     print(">>> Total Layers Found:", len(layers))

#     return {
#         "coordinate_system": epsg,
#         "layers": layers
#     }


import os
import zipfile
import xml.etree.ElementTree as ET

# ----------------------------------------
# Supported file types
# ----------------------------------------

RASTER_EXT = [
    ".tif", ".tiff", ".jpg", ".jpeg", ".png",
    ".bmp", ".jp2", ".ecw", ".sid", ".gif",
    ".img", ".kmz", ".kml"
]

VECTOR_EXT = [
    ".shp", ".tab", ".dxf", ".gml", ".geojson",
    ".sqlite", ".gpkg", ".mdb", ".csv", ".kml", ".kmz"
]

# ----------------------------------------
# Find EPSG from multiple possible paths
# ----------------------------------------

def find_epsg(root):
    possible_paths = [
        "./Viewer/CS/EPSG",
        "./Project/CS/EPSG",
        "./CoordinateSystem/EPSG",
        "./CS/EPSG",
        ".//EPSG",
    ]

    for path in possible_paths:
        node = root.find(path)
        if node is not None and node.text is not None:
            return node.text.strip()

    return None


# ----------------------------------------
# Normalize layer path relative to ttkproject folder
# ----------------------------------------

def normalize_path(ttk_base, path):
    if not path:
        return path
    cleaned = path.replace("\\", "/").strip()
    return os.path.normpath(os.path.join(ttk_base, cleaned))


# ----------------------------------------
# Recursive LayerGroup parsing
# ----------------------------------------

def parse_layer_node(layer_node, ttk_base):
    """
    Parse a <Layer> or <LayerGroup> node.
    Returns a dictionary.
    """

    node_tag = layer_node.tag.lower()
    is_group = "group" in node_tag

    if is_group:
        # LayerGroup
        group_name = layer_node.get("Name") or "Unnamed Group"
        group_visible = layer_node.get("Visible", "true").lower() == "true"

        group_layers = []

        for child in layer_node:
            if child.tag.lower() in ["layer", "layergroup"]:
                group_layers.append(parse_layer_node(child, ttk_base))

        return {
            "type": "group",
            "name": group_name,
            "visible": group_visible,
            "layers": group_layers
        }


    # Normal layer
    name = layer_node.get("Name") or "Unnamed Layer"
    path = (layer_node.get("Path") 
            or layer_node.findtext("Path") 
            or layer_node.findtext("FileName"))

    visible = layer_node.get("Visible", "true").lower() == "true"
    scale_min = layer_node.get("ScaleMin")
    scale_max = layer_node.get("ScaleMax")

    full_path = normalize_path(ttk_base, path)

    # Detect type based on extension
    ext = os.path.splitext(path)[1].lower()

    if ext in VECTOR_EXT:
        layer_type = "vector"
    elif ext in RASTER_EXT:
        layer_type = "raster"
    else:
        layer_type = "unknown"

    return {
        "type": layer_type,
        "name": name,
        "file": path,
        "full_path": full_path,
        "visible": visible,
        "scale_min": scale_min,
        "scale_max": scale_max
    }


# ----------------------------------------
# Main function: parse_ttkproject()
# ----------------------------------------

def parse_ttkproject(file_path):
    print(">>> Parsing:", file_path)

    # Base folder
    ttk_base = os.path.dirname(file_path)

    # Case A: ZIP-based project
    if zipfile.is_zipfile(file_path):
        print(">>> ZIP-based .ttkproject")

        with zipfile.ZipFile(file_path, 'r') as z:
            xml_file = None

            for name in z.namelist():
                if name.lower().endswith(".xml"):
                    xml_file = name
                    break

            if not xml_file:
                return {"coordinate_system": None, "layers": []}

            xml_content = z.read(xml_file)
            root = ET.fromstring(xml_content)

    # Case B: Pure XML project
    else:
        print(">>> XML-based .ttkproject")

        tree = ET.parse(file_path)
        root = tree.getroot()

    # -------- EPSG --------
    epsg = find_epsg(root)

    # -------- Parse Layers --------
    final_layers = []

    layers_root = root.find("./Layers")
    if layers_root is not None:
        for node in layers_root:
            if node.tag.lower() in ["layer", "layergroup"]:
                final_layers.append(parse_layer_node(node, ttk_base))

    return {
        "coordinate_system": epsg,
        "layers": final_layers
    }
