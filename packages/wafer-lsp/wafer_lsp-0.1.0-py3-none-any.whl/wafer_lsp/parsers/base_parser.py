from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):

    @abstractmethod
    def parse_file(self, content: str) -> dict[str, Any]:
        pass
