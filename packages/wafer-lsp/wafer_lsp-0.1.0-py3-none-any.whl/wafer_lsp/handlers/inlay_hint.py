
from lsprotocol.types import InlayHint, InlayHintKind, Position, Range

from ..languages.registry import get_language_registry


def handle_inlay_hint(uri: str, content: str, range: Range) -> list[InlayHint]:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return []

    hints: list[InlayHint] = []
    lines = content.split("\n")

    for layout in language_info.layouts:
        if layout.line < range.start.line or layout.line > range.end.line:
            continue

        layout_line = lines[layout.line] if layout.line < len(lines) else ""

        if "=" in layout_line:
            equals_pos = layout_line.find("=")
            hint_text = ": Layout"
            if layout.shape:
                hint_text = f": Layout[Shape{layout.shape}]"

            hint_position = Position(
                line=layout.line,
                character=equals_pos + 1
            )

            hints.append(InlayHint(
                position=hint_position,
                label=hint_text,
                kind=InlayHintKind.Type,
                padding_left=True,
                padding_right=False
            ))

    for kernel in language_info.kernels:
        if kernel.line < range.start.line or kernel.line > range.end.line:
            continue

        kernel_line = lines[kernel.line] if kernel.line < len(lines) else ""

        if "def " in kernel_line and "(" in kernel_line:
            paren_pos = kernel_line.find("(")
            hint_text = " -> Kernel"

            hint_position = Position(
                line=kernel.line,
                character=paren_pos
            )

            hints.append(InlayHint(
                position=hint_position,
                label=hint_text,
                kind=InlayHintKind.Type,
                padding_left=True,
                padding_right=True
            ))

    return hints
