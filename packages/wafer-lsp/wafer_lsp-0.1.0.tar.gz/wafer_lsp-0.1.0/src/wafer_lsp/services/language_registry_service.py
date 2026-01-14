
from ..languages.registry import LanguageRegistry, get_language_registry
from ..languages.types import LanguageInfo


class LanguageRegistryService:

    def __init__(self, registry: LanguageRegistry):
        self._registry = registry

    def detect_language(self, uri: str) -> str | None:
        return self._registry.detect_language(uri)

    def parse_file(self, uri: str, content: str) -> LanguageInfo | None:
        return self._registry.parse_file(uri, content)

    def get_language_name(self, language_id: str) -> str | None:
        return self._registry.get_language_name(language_id)

    def get_supported_extensions(self) -> list[str]:
        return self._registry.get_supported_extensions()


def create_language_registry_service() -> LanguageRegistryService:
    registry = get_language_registry()
    return LanguageRegistryService(registry)
