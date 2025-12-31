from myapp.services.project_detector import detect_project_type
from myapp.parsers import PARSER_REGISTRY

class ProjectService:
    @staticmethod
    def fetch_project(file_path: str) -> dict:
        project_type = detect_project_type(file_path)
        print("Detected type:", project_type)

        if not project_type:
            raise ValueError("Unsupported file type")

        parser = PARSER_REGISTRY.get(project_type)
        if not parser:
            raise ValueError("Parser not registered")

        return parser.parse(file_path)
