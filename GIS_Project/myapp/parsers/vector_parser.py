import geopandas as gpd
from myapp.parsers.base import BaseParser
import os

class VectorParser(BaseParser):
    def parse(self, file_path):
        gdf = gpd.read_file(file_path)
        crs = gdf.crs.srs if gdf.crs else None

        return {
            "project_type": "vector",
            "coordinate_system": crs,
            "layers": [{
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "type": "vector",
                "full_path": file_path,
                "crs": crs,
                "children": []
            }]
        }
