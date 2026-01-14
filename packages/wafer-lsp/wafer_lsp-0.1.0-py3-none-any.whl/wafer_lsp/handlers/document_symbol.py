
from lsprotocol.types import DocumentSymbol, Position, Range, SymbolKind

from ..languages.registry import get_language_registry


def handle_document_symbol(uri: str, content: str) -> list[DocumentSymbol]:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return []

    symbols: list[DocumentSymbol] = []

    for kernel in language_info.kernels:
        lines = content.split("\n")
        kernel_line = lines[kernel.line] if kernel.line < len(lines) else ""
        name_start = kernel_line.find(kernel.name)
        name_end = name_start + len(kernel.name) if name_start >= 0 else 0

        selection_range = Range(
            start=Position(line=kernel.line, character=max(0, name_start)),
            end=Position(line=kernel.line, character=name_end)
        )
        full_range = Range(
            start=Position(line=kernel.line, character=0),
            end=Position(line=min(kernel.line + 10, len(lines) - 1), character=0)
        )

        symbols.append(DocumentSymbol(
            name=kernel.name,
            kind=SymbolKind.Function,
            range=full_range,
            selection_range=selection_range,
            detail=f"GPU Kernel ({registry.get_language_name(kernel.language)})",
        ))

    for layout in language_info.layouts:
        lines = content.split("\n")
        layout_line = lines[layout.line] if layout.line < len(lines) else ""
        name_start = layout_line.find(layout.name)
        name_end = name_start + len(layout.name) if name_start >= 0 else 0

        detail = f"Layout: {layout.shape}" if layout.shape else "Layout"

        selection_range = Range(
            start=Position(line=layout.line, character=max(0, name_start)),
            end=Position(line=layout.line, character=name_end)
        )
        full_range = Range(
            start=Position(line=layout.line, character=0),
            end=Position(line=layout.line, character=len(layout_line))
        )

        symbols.append(DocumentSymbol(
            name=layout.name,
            kind=SymbolKind.Variable,
            range=full_range,
            selection_range=selection_range,
            detail=detail,
        ))

    for struct in language_info.structs:
        lines = content.split("\n")
        struct_line = lines[struct.line] if struct.line < len(lines) else ""
        name_start = struct_line.find(struct.name)
        name_end = name_start + len(struct.name) if name_start >= 0 else 0

        selection_range = Range(
            start=Position(line=struct.line, character=max(0, name_start)),
            end=Position(line=struct.line, character=name_end)
        )
        full_range = Range(
            start=Position(line=struct.line, character=0),
            end=Position(line=min(struct.line + 10, len(lines) - 1), character=0)
        )

        symbols.append(DocumentSymbol(
            name=struct.name,
            kind=SymbolKind.Struct,
            range=full_range,
            selection_range=selection_range,
            detail=f"Struct ({registry.get_language_name(struct.language)})",
        ))

    return symbols
