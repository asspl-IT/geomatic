class BaseParser:
    def parse(self, file_path: str) -> dict:
        raise NotImplementedError("Parser must implement parse()")
