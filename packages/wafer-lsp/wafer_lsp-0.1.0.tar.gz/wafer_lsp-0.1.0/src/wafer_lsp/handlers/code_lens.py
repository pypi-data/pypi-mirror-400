
from lsprotocol.types import CodeLens, Command, Position, Range

from ..languages.registry import get_language_registry


def handle_code_lens(uri: str, content: str) -> list[CodeLens]:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return []

    lenses: list[CodeLens] = []

    for kernel in language_info.kernels:
        lens_range = Range(
            start=Position(line=kernel.line, character=0),
            end=Position(line=kernel.line, character=0)
        )

        analyze_command = Command(
            title=f"Analyze {kernel.name}",
            command="wafer.analyzeKernel",
            arguments=[uri, kernel.name]
        )

        profile_command = Command(
            title=f"Profile {kernel.name}",
            command="wafer.profileKernel",
            arguments=[uri, kernel.name]
        )

        lenses.append(CodeLens(
            range=lens_range,
            command=analyze_command
        ))

        profile_range = Range(
            start=Position(line=kernel.line, character=20),
            end=Position(line=kernel.line, character=20)
        )
        lenses.append(CodeLens(
            range=profile_range,
            command=profile_command
        ))

    return lenses
