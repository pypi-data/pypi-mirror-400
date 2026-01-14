from dataclasses import dataclass
from typing import Any


@dataclass
class KernelInfo:
    name: str
    line: int
    parameters: list[str]
    docstring: str | None = None
    language: str = ""


@dataclass
class LayoutInfo:
    name: str
    line: int
    shape: str | None = None
    stride: str | None = None
    language: str = ""


@dataclass
class StructInfo:
    name: str
    line: int
    docstring: str | None = None
    language: str = ""


@dataclass
class LanguageInfo:
    kernels: list[KernelInfo]
    layouts: list[LayoutInfo]
    structs: list[StructInfo]
    language: str
    raw_data: dict[str, Any]
