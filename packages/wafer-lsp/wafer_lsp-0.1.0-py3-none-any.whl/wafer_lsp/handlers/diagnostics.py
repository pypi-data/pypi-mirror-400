
from lsprotocol.types import Diagnostic

from ..languages.registry import get_language_registry


def handle_diagnostics(uri: str, content: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return diagnostics

    return diagnostics
