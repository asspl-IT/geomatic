import os

PROJECT_TYPE_MAP = {
    ".ttkproject": "ttk",
    ".qgs": "qgis",
    ".qgz": "qgis",
    ".gpkg": "geopackage",
    ".tif": "raster",
    ".tiff": "raster",
    ".shp": "vector",
}

def detect_project_type(file_path: str) -> str | None:
    ext = os.path.splitext(file_path)[1].lower()
    return PROJECT_TYPE_MAP.get(ext)
