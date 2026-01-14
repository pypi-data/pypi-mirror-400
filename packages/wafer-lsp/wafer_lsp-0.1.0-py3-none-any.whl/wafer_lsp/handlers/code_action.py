
from lsprotocol.types import CodeAction, CodeActionKind, Command, Range

from ..languages.registry import get_language_registry
from ..languages.types import KernelInfo


def find_kernel_at_range(content: str, range: Range, uri: str) -> KernelInfo | None:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return None

    for kernel in language_info.kernels:
        if kernel.line <= range.start.line <= kernel.line + 50:
            return kernel

    return None


def handle_code_action(uri: str, range: Range, content: str) -> list[CodeAction]:
    kernel = find_kernel_at_range(content, range, uri)
    if not kernel:
        return []

    actions: list[CodeAction] = [
        CodeAction(
            title=f"Analyze Kernel: {kernel.name}",
            kind=CodeActionKind.Source,
            command=Command(
                title=f"Analyze Kernel: {kernel.name}",
                command="wafer.analyzeKernel",
                arguments=[uri, kernel.name]
            )
        ),
        CodeAction(
            title=f"Profile Kernel: {kernel.name}",
            kind=CodeActionKind.Source,
            command=Command(
                title=f"Profile Kernel: {kernel.name}",
                command="wafer.profileKernel",
                arguments=[uri, kernel.name]
            )
        ),
    ]

    return actions
