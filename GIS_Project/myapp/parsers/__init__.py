from .ttk_parser import TTKParser
from .qgis_parser import QGISParser
from .geopackage_parser import GeoPackageParser
from .raster_parser import RasterParser
from .vector_parser import VectorParser

PARSER_REGISTRY = {
    "ttk": TTKParser(),
    "qgis": QGISParser(),
    "geopackage": GeoPackageParser(),
    "raster": RasterParser(),
    "vector": VectorParser(),
}
