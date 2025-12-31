import rasterio
from myapp.parsers.base import BaseParser

class RasterParser(BaseParser):
    def parse(self, file_path):
        with rasterio.open(file_path) as ds:
            crs = ds.crs.to_string() if ds.crs else None

        return {
            "project_type": "raster",
            "coordinate_system": crs,
            "layers": [{
                "name": file_path.split("/")[-1],
                "type": "raster",
                "full_path": file_path,
                "crs": crs,
                "children": []
            }]
        }
