from typing import Any


class AnalysisService:

    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}

    def get_analysis_for_kernel(self, uri: str, kernel_name: str) -> dict[str, Any] | None:
        cache_key = f"{uri}:{kernel_name}"
        return self._cache.get(cache_key)

    def set_analysis_for_kernel(self, uri: str, kernel_name: str, analysis: dict[str, Any]):
        cache_key = f"{uri}:{kernel_name}"
        self._cache[cache_key] = analysis

    def clear_cache(self):
        self._cache.clear()


def create_analysis_service() -> AnalysisService:
    return AnalysisService()
