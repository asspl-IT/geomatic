import fiona
from myapp.parsers.base import BaseParser

class GeoPackageParser(BaseParser):
    def parse(self, file_path):
        layers = []
        for name in fiona.listlayers(file_path):
            layers.append({
                "name": name,
                "type": "vector",
                "full_path": f"{file_path}|layername={name}",
                "crs": None,
                "children": []
            })

        return {
            "project_type": "geopackage",
            "coordinate_system": None,
            "layers": layers
        }
