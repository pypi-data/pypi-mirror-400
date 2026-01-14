from typing import Any

from .types import KernelInfo, LanguageInfo, LayoutInfo, StructInfo


class ParserResultConverter:

    def convert(
        self,
        parsed_data: dict[str, Any],
        language_id: str
    ) -> LanguageInfo:
        kernels = self._convert_kernels(
            parsed_data.get("kernels", []),
            language_id
        )
        layouts = self._convert_layouts(
            parsed_data.get("layouts", []),
            language_id
        )
        structs = self._convert_structs(
            parsed_data.get("structs", []),
            language_id
        )

        return LanguageInfo(
            kernels=kernels,
            layouts=layouts,
            structs=structs,
            language=language_id,
            raw_data=parsed_data
        )

    def _convert_kernels(
        self,
        kernels: list[Any],
        language_id: str
    ) -> list[KernelInfo]:
        result: list[KernelInfo] = []

        for kernel in kernels:
            if hasattr(kernel, "name") and hasattr(kernel, "line"):
                result.append(KernelInfo(
                    name=kernel.name,
                    line=kernel.line,
                    parameters=getattr(kernel, "parameters", []),
                    docstring=getattr(kernel, "docstring", None),
                    language=language_id
                ))

        return result

    def _convert_layouts(
        self,
        layouts: list[Any],
        language_id: str
    ) -> list[LayoutInfo]:
        result: list[LayoutInfo] = []

        for layout in layouts:
            if hasattr(layout, "name") and hasattr(layout, "line"):
                result.append(LayoutInfo(
                    name=layout.name,
                    line=layout.line,
                    shape=getattr(layout, "shape", None),
                    stride=getattr(layout, "stride", None),
                    language=language_id
                ))

        return result

    def _convert_structs(
        self,
        structs: list[Any],
        language_id: str
    ) -> list[StructInfo]:
        result: list[StructInfo] = []

        for struct in structs:
            if hasattr(struct, "name") and hasattr(struct, "line"):
                result.append(StructInfo(
                    name=struct.name,
                    line=struct.line,
                    docstring=getattr(struct, "docstring", None),
                    language=language_id
                ))

        return result
