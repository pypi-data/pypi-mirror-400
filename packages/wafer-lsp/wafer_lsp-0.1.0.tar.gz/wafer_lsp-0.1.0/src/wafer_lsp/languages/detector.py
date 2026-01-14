from pathlib import Path


class LanguageDetector:

    def __init__(self):
        self._extensions: dict[str, str] = {}

    def register_extension(self, extension: str, language_id: str):
        normalized_ext = extension if extension.startswith(".") else f".{ext}"
        self._extensions[normalized_ext] = language_id

    def detect_from_uri(self, uri: str) -> str | None:
        if uri.startswith("file://"):
            file_path = uri[7:]
        else:
            file_path = uri

        return self.detect_from_path(file_path)

    def detect_from_path(self, file_path: str) -> str | None:
        path = Path(file_path)
        ext = path.suffix.lower()
        return self._extensions.get(ext)

    def detect_from_extension(self, extension: str) -> str | None:
        normalized_ext = extension if extension.startswith(".") else f".{ext}"
        return self._extensions.get(normalized_ext)

    def get_supported_extensions(self) -> list[str]:
        return list(self._extensions.keys())

    def is_supported(self, uri: str) -> bool:
        return self.detect_from_uri(uri) is not None
