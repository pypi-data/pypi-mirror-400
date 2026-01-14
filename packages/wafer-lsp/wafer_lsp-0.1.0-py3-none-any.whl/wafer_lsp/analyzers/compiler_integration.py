from typing import Any

_analysis_cache: dict[str, dict[str, Any]] = {}


def get_analysis_for_kernel(uri: str, kernel_name: str) -> dict[str, Any] | None:
    cache_key = f"{uri}:{kernel_name}"

    if cache_key in _analysis_cache:
        return _analysis_cache[cache_key]

    return None


def clear_cache():
    _analysis_cache.clear()
