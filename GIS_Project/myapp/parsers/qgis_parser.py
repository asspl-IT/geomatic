import xml.etree.ElementTree as ET
from myapp.parsers.base import BaseParser

class QGISParser(BaseParser):
    def parse(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        layers = []
        for layer in root.findall(".//maplayer"):
            layers.append({
                "name": layer.findtext("layername"),
                "type": layer.findtext("type") or "vector",
                "full_path": layer.findtext("datasource"),
                "crs": layer.findtext("srs/authid"),
                "children": []
            })

        return {
            "project_type": "qgis",
            "coordinate_system": None,
            "layers": layers
        }
