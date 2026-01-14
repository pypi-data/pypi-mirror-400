import ast

from lsprotocol.types import Position, Range


def get_word_at_position(content: str, position: Position) -> str:
    lines = content.split("\n")
    if position.line >= len(lines):
        return ""

    line = lines[position.line]
    if position.character >= len(line):
        return ""

    start = position.character
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_" or line[start - 1] == "."):
        start -= 1

    end = position.character
    while end < len(line) and (line[end].isalnum() or line[end] == "_" or line[end] == "."):
        end += 1

    return line[start:end]


def get_decorator_at_position(content: str, position: Position) -> tuple[str, int] | None:
    lines = content.split("\n")
    if position.line >= len(lines):
        return None

    line = lines[position.line]
    line_stripped = line.strip()

    if not line_stripped.startswith("@"):
        return None

    at_pos = line.find("@")
    if at_pos != -1 and position.character < at_pos:
        return None

    try:
        tree = ast.parse(line_stripped, mode="eval")
        if isinstance(tree.body, ast.Attribute):
            if isinstance(tree.body.value, ast.Name):
                decorator_name = f"{tree.body.value.id}.{tree.body.attr}"
                for i in range(position.line + 1, len(lines)):
                    next_line = lines[i].strip()
                    if next_line.startswith("def ") or next_line.startswith("class "):
                        return (decorator_name, i)
        elif isinstance(tree.body, ast.Name):
            decorator_name = tree.body.id
            for i in range(position.line + 1, len(lines)):
                next_line = lines[i].strip()
                if next_line.startswith("def ") or next_line.startswith("class "):
                    return (decorator_name, i)
    except SyntaxError:
        pass

    if "@cute.kernel" in line_stripped:
        decorator_name = "cute.kernel"
        for i in range(position.line + 1, len(lines)):
            next_line = lines[i].strip()
            if next_line.startswith("def ") or next_line.startswith("class "):
                return (decorator_name, i)
    elif "@cute.struct" in line_stripped:
        decorator_name = "cute.struct"
        for i in range(position.line + 1, len(lines)):
            next_line = lines[i].strip()
            if next_line.startswith("def ") or next_line.startswith("class "):
                return (decorator_name, i)

    return None


def create_range(start_line: int, start_char: int, end_line: int, end_char: int) -> Range:
    return Range(
        start=Position(line=start_line, character=start_char),
        end=Position(line=end_line, character=end_char),
    )
