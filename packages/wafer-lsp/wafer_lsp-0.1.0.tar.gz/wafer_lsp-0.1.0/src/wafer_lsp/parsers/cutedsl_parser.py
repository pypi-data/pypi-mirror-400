import ast
from dataclasses import dataclass
from typing import Any

from .base_parser import BaseParser


@dataclass
class CuTeDSLKernel:
    name: str
    line: int
    parameters: list[str]
    docstring: str | None = None


@dataclass
class CuTeDSLLayout:
    name: str
    line: int
    shape: str | None = None
    stride: str | None = None


@dataclass
class CuTeDSLStruct:
    name: str
    line: int
    docstring: str | None = None


class CuTeDSLParser(BaseParser):

    def parse_file(self, content: str) -> dict[str, Any]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"kernels": [], "layouts": [], "structs": []}

        kernels: list[CuTeDSLKernel] = []
        layouts: list[CuTeDSLLayout] = []
        structs: list[CuTeDSLStruct] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._has_decorator(node, "cute.kernel"):
                    kernels.append(self._extract_kernel(node))
            elif isinstance(node, ast.ClassDef):
                if self._has_decorator(node, "cute.struct"):
                    structs.append(self._extract_struct(node))
            elif isinstance(node, ast.Assign):
                layout = self._extract_layout(node, content)
                if layout:
                    layouts.append(layout)

        return {"kernels": kernels, "layouts": layouts, "structs": structs}

    def _has_decorator(self, node: ast.FunctionDef | ast.ClassDef, decorator: str) -> bool:
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute):
                if isinstance(dec.value, ast.Name) and dec.value.id == "cute":
                    if dec.attr == decorator.split(".")[-1]:
                        return True
            elif isinstance(dec, ast.Name):
                if dec.id == decorator.split(".")[-1]:
                    return True
        return False

    def _extract_kernel(self, node: ast.FunctionDef) -> CuTeDSLKernel:
        parameters = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)

        return CuTeDSLKernel(
            name=node.name,
            line=node.lineno - 1,
            parameters=parameters,
            docstring=docstring,
        )

    def _extract_struct(self, node: ast.ClassDef) -> CuTeDSLStruct:
        docstring = ast.get_docstring(node)

        return CuTeDSLStruct(
            name=node.name,
            line=node.lineno - 1,
            docstring=docstring,
        )

    def _extract_layout(self, node: ast.Assign, content: str) -> CuTeDSLLayout | None:
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue

            if isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute):
                    if isinstance(call.func.value, ast.Name):
                        if call.func.value.id == "cute" and call.func.attr == "make_layout":
                            shape_str = None
                            stride_str = None

                            if call.args:
                                try:
                                    shape_str = ast.unparse(call.args[0])
                                except AttributeError:
                                    shape_str = str(call.args[0])

                            return CuTeDSLLayout(
                                name=target.id,
                                line=node.lineno - 1,
                                shape=shape_str,
                                stride=stride_str,
                            )

        return None
