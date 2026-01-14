
from lsprotocol.types import SemanticTokens, SemanticTokensLegend

from ..languages.registry import get_language_registry

TOKEN_TYPES = [
    "kernel",
    "layout",
    "struct",
    "decorator",
]

TOKEN_MODIFIERS = [
    "definition",
    "declaration",
]

SEMANTIC_TOKENS_LEGEND = SemanticTokensLegend(
    token_types=TOKEN_TYPES,
    token_modifiers=TOKEN_MODIFIERS
)


def handle_semantic_tokens(uri: str, content: str) -> SemanticTokens:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return SemanticTokens(data=[])

    tokens: list[int] = []
    lines = content.split("\n")
    prev_line = 0
    prev_char = 0

    for kernel in language_info.kernels:
        if kernel.line >= len(lines):
            continue

        kernel_line = lines[kernel.line]
        name_start = kernel_line.find(kernel.name)

        if name_start >= 0:
            delta_line = kernel.line - prev_line
            delta_char = name_start - (prev_char if delta_line == 0 else 0)

            tokens.extend([
                delta_line,
                delta_char,
                len(kernel.name),
                TOKEN_TYPES.index("kernel"),
                0
            ])

            prev_line = kernel.line
            prev_char = name_start + len(kernel.name)

    for layout in language_info.layouts:
        if layout.line >= len(lines):
            continue

        layout_line = lines[layout.line]
        name_start = layout_line.find(layout.name)

        if name_start >= 0:
            delta_line = layout.line - prev_line
            delta_char = name_start - (prev_char if delta_line == 0 else 0)

            tokens.extend([
                delta_line,
                delta_char,
                len(layout.name),
                TOKEN_TYPES.index("layout"),
                0
            ])

            prev_line = layout.line
            prev_char = name_start + len(layout.name)

    for struct in language_info.structs:
        if struct.line >= len(lines):
            continue

        struct_line = lines[struct.line]
        name_start = struct_line.find(struct.name)

        if name_start >= 0:
            delta_line = struct.line - prev_line
            delta_char = name_start - (prev_char if delta_line == 0 else 0)

            tokens.extend([
                delta_line,
                delta_char,
                len(struct.name),
                TOKEN_TYPES.index("struct"),
                0
            ])

            prev_line = struct.line
            prev_char = name_start + len(struct.name)

    for i, line in enumerate(lines):
        if "@cute.kernel" in line or "@cute.struct" in line:
            decorator_start = line.find("@")
            if decorator_start >= 0:
                decorator_end = line.find(" ", decorator_start)
                if decorator_end == -1:
                    decorator_end = len(line)

                delta_line = i - prev_line
                delta_char = decorator_start - (prev_char if delta_line == 0 else 0)

                tokens.extend([
                    delta_line,
                    delta_char,
                    decorator_end - decorator_start,
                    TOKEN_TYPES.index("decorator"),
                    0
                ])

                prev_line = i
                prev_char = decorator_end

    return SemanticTokens(data=tokens)
