
from lsprotocol.types import Location, Position, Range, SymbolKind, WorkspaceSymbol

from ..languages.registry import get_language_registry


def _matches_query(name: str, query: str) -> bool:
    if not query:
        return True

    name_lower = name.lower()
    query_lower = query.lower()

    query_idx = 0
    for char in name_lower:
        if query_idx < len(query_lower) and char == query_lower[query_idx]:
            query_idx += 1

    return query_idx == len(query_lower)


def handle_workspace_symbol(query: str) -> list[WorkspaceSymbol]:
    registry = get_language_registry()
    symbols: list[WorkspaceSymbol] = []

    return symbols


def handle_workspace_symbol_with_documents(
    query: str,
    document_contents: dict[str, str]
) -> list[WorkspaceSymbol]:
    registry = get_language_registry()
    symbols: list[WorkspaceSymbol] = []

    for uri, content in document_contents.items():
        language_info = registry.parse_file(uri, content)

        if not language_info:
            continue

        for kernel in language_info.kernels:
            if _matches_query(kernel.name, query):
                symbols.append(WorkspaceSymbol(
                    name=kernel.name,
                    kind=SymbolKind.Function,
                    location=Location(
                        uri=uri,
                        range=Range(
                            start=Position(line=kernel.line, character=0),
                            end=Position(line=kernel.line, character=0)
                        )
                    ),
                    container_name=f"GPU Kernel ({registry.get_language_name(kernel.language)})"
                ))

        for layout in language_info.layouts:
            if _matches_query(layout.name, query):
                symbols.append(WorkspaceSymbol(
                    name=layout.name,
                    kind=SymbolKind.Variable,
                    location=Location(
                        uri=uri,
                        range=Range(
                            start=Position(line=layout.line, character=0),
                            end=Position(line=layout.line, character=0)
                        )
                    ),
                    container_name="Layout"
                ))

        for struct in language_info.structs:
            if _matches_query(struct.name, query):
                symbols.append(WorkspaceSymbol(
                    name=struct.name,
                    kind=SymbolKind.Struct,
                    location=Location(
                        uri=uri,
                        range=Range(
                            start=Position(line=struct.line, character=0),
                            end=Position(line=struct.line, character=0)
                        )
                    ),
                    container_name=f"Struct ({registry.get_language_name(struct.language)})"
                ))

    return symbols
