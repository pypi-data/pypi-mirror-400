
from ..parsers.cuda_parser import CUDAParser
from ..parsers.cutedsl_parser import CuTeDSLParser
from .converter import ParserResultConverter
from .detector import LanguageDetector
from .parser_manager import ParserManager
from .types import LanguageInfo


class LanguageRegistry:

    def __init__(self):
        self._detector = LanguageDetector()
        self._parser_manager = ParserManager()
        self._converter = ParserResultConverter()

        self._register_defaults()

    def _register_defaults(self):
        self.register_language(
            language_id="cutedsl",
            display_name="CuTeDSL",
            parser=CuTeDSLParser(),
            extensions=[".py"],
            file_patterns=["*.py"]
        )

        self.register_language(
            language_id="cuda",
            display_name="CUDA",
            parser=CUDAParser(),
            extensions=[".cu", ".cuh"],
            file_patterns=["*.cu", "*.cuh"]
        )

        self.register_language(
            language_id="cpp",
            display_name="C++",
            parser=CUDAParser(),
            extensions=[".cpp", ".hpp", ".cc", ".cxx"],
            file_patterns=["*.cpp", "*.hpp", "*.cc", "*.cxx"]
        )

    def register_language(
        self,
        language_id: str,
        display_name: str,
        parser,
        extensions: list[str],
        file_patterns: list[str] | None = None
    ):
        self._parser_manager.register_parser(language_id, display_name, parser)

        for ext in extensions:
            self._detector.register_extension(ext, language_id)

    def detect_language(self, uri: str) -> str | None:
        return self._detector.detect_from_uri(uri)

    def get_parser(self, language_id: str):
        return self._parser_manager.get_parser(language_id)

    def parse_file(self, uri: str, content: str) -> LanguageInfo | None:
        language_id = self.detect_language(uri)
        if not language_id:
            return None

        parser = self.get_parser(language_id)
        if not parser:
            return None

        try:
            parsed_data = parser.parse_file(content)
        except Exception:
            return LanguageInfo(
                kernels=[],
                layouts=[],
                structs=[],
                language=language_id,
                raw_data={}
            )

        return self._converter.convert(parsed_data, language_id)

    def get_supported_extensions(self) -> list[str]:
        return self._detector.get_supported_extensions()

    def get_language_name(self, language_id: str) -> str | None:
        return self._parser_manager.get_language_name(language_id)


_registry: LanguageRegistry | None = None


def get_language_registry() -> LanguageRegistry:
    global _registry
    if _registry is None:
        _registry = LanguageRegistry()
    return _registry
