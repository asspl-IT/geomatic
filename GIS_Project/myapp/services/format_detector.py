import os

def detect_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    # --- PROJECT FILES ---
    if ext == ".ttkproject":
        return "ttkproject"

    # --- VECTOR FORMATS ---
    if ext in (".shp", ".geojson", ".json", ".gpkg"):
        return "vector"

    # --- RASTER ---
    if ext in (".tif", ".tiff", ".img", ".jp2"):
        return "raster"

    # --- LIDAR ---
    if ext in (".las", ".laz"):
        return "lidar"

    return "unknown file format"
