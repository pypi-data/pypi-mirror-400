
from ..parsers.base_parser import BaseParser


class ParserManager:

    def __init__(self):
        self._parsers: dict[str, BaseParser] = {}
        self._language_names: dict[str, str] = {}

    def register_parser(
        self,
        language_id: str,
        display_name: str,
        parser: BaseParser
    ):
        assert language_id not in self._parsers, \
            f"Language {language_id} already registered"

        self._parsers[language_id] = parser
        self._language_names[language_id] = display_name

    def get_parser(self, language_id: str) -> BaseParser | None:
        return self._parsers.get(language_id)

    def get_language_name(self, language_id: str) -> str | None:
        return self._language_names.get(language_id)

    def has_parser(self, language_id: str) -> bool:
        return language_id in self._parsers

    def list_languages(self) -> list[str]:
        return list(self._parsers.keys())
