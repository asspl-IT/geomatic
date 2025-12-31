from myapp.parsers.base import BaseParser
from myapp.converters.ttk_converter import parse_ttkproject

class TTKParser(BaseParser):
    def parse(self, file_path):
        data = parse_ttkproject(file_path)
        return {
            "project_type": "ttk",
            "coordinate_system": data.get("coordinate_system"),
            "layers": data.get("layers", [])
        }
