
from lsprotocol.types import Hover, MarkupContent, MarkupKind, Position

from ..analyzers.compiler_integration import get_analysis_for_kernel
from ..analyzers.docs_index import DocsIndex
from ..languages.registry import get_language_registry
from ..languages.types import KernelInfo, LayoutInfo
from ..utils.lsp_helpers import get_decorator_at_position, get_word_at_position


def find_kernel_at_position(
    content: str, position: Position, uri: str
) -> KernelInfo | None:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return None

    word = get_word_at_position(content, position)

    for kernel in language_info.kernels:
        if kernel.name == word:
            if position.line >= kernel.line:
                return kernel

    return None


def find_layout_at_position(
    content: str, position: Position, uri: str
) -> LayoutInfo | None:
    registry = get_language_registry()
    language_info = registry.parse_file(uri, content)

    if not language_info:
        return None

    word = get_word_at_position(content, position)

    for layout in language_info.layouts:
        if layout.name == word:
            return layout

    return None


def format_kernel_hover(kernel: KernelInfo, analysis: dict | None) -> str:
    registry = get_language_registry()
    language_name = registry.get_language_name(kernel.language) or kernel.language

    lines = [f"**GPU Kernel: {kernel.name}**", f"*Language: {language_name}*", ""]

    if kernel.docstring:
        lines.append(kernel.docstring)
        lines.append("")

    if kernel.parameters:
        params_str = ", ".join(kernel.parameters)
        lines.append(f"**Parameters:** `{params_str}`")
        lines.append("")

    if analysis:
        lines.append("**Analysis:**")
        if "layouts" in analysis:
            lines.append(f"- Layouts: {analysis['layouts']}")
        if "memory_paths" in analysis:
            lines.append(f"- Memory paths: {analysis['memory_paths']}")
        if "pipeline_stages" in analysis:
            lines.append(f"- Pipeline stages: {analysis['pipeline_stages']}")

    return "\n".join(lines)


def format_kernel_hover_basic(kernel: KernelInfo) -> str:
    return format_kernel_hover(kernel, None)


def format_decorator_hover(decorator_name: str, function_name: str | None = None) -> str:
    lines = []

    if decorator_name == "cute.kernel" or decorator_name == "kernel":
        lines.append("**@cute.kernel**")
        lines.append("")
        lines.append("CuTeDSL kernel decorator. Marks a function as a GPU kernel.")
        lines.append("")
        lines.append("**Usage:**")
        lines.append("```python")
        lines.append("@cute.kernel")
        lines.append("def my_kernel(a: cute.Tensor, b: cute.Tensor):")
        lines.append("    # Kernel implementation")
        lines.append("    pass")
        lines.append("```")
        lines.append("")
        lines.append("**Features:**")
        lines.append("- Automatic GPU code generation")
        lines.append("- Tensor layout optimization")
        lines.append("- Memory access pattern analysis")

        if function_name:
            lines.append("")
            lines.append(f"Applied to: `{function_name}()`")

    elif decorator_name == "cute.struct" or decorator_name == "struct":
        lines.append("**@cute.struct**")
        lines.append("")
        lines.append("CuTeDSL struct decorator. Marks a class as a GPU struct.")
        lines.append("")
        lines.append("**Usage:**")
        lines.append("```python")
        lines.append("@cute.struct")
        lines.append("class MyStruct:")
        lines.append("    field1: int")
        lines.append("    field2: float")
        lines.append("```")

        if function_name:
            lines.append("")
            lines.append(f"Applied to: `{function_name}`")

    else:
        lines.append(f"**{decorator_name}**")
        lines.append("")
        lines.append("CuTeDSL decorator")

    docs = DocsIndex()
    doc_link = docs.get_doc_for_concept("kernel" if "kernel" in decorator_name else "struct")
    if doc_link:
        lines.append("")
        lines.append(f"[Documentation]({doc_link})")

    return "\n".join(lines)


def handle_hover(uri: str, position: Position, content: str) -> Hover | None:
    test_message = "**HEYOOOOOO** 🎉\n\n"

    decorator_info = get_decorator_at_position(content, position)
    if decorator_info:
        decorator_name, function_line = decorator_info

        function_name = None
        lines = content.split("\n")
        if function_line < len(lines):
            func_line = lines[function_line].strip()
            if func_line.startswith("def "):
                func_name_start = func_line.find("def ") + 4
                func_name_end = func_line.find("(", func_name_start)
                if func_name_end > func_name_start:
                    function_name = func_line[func_name_start:func_name_end].strip()
            elif func_line.startswith("class "):
                class_name_start = func_line.find("class ") + 6
                class_name_end = func_line.find(":", class_name_start)
                if class_name_end > class_name_start:
                    function_name = func_line[class_name_start:class_name_end].strip()

        hover_content = test_message + format_decorator_hover(decorator_name, function_name)
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_content))

    word = get_word_at_position(content, position)
    if word == "cute" or word.startswith("cute."):
        hover_lines = [
            test_message,
            "**cutlass.cute**",
            "",
            "CuTeDSL (CUDA Unified Tensor Expression) library for GPU programming.",
            "",
            "**Key Features:**",
            "- `@cute.kernel` - Define GPU kernels",
            "- `@cute.struct` - Define GPU structs",
            "- `cute.make_layout()` - Create tensor layouts",
            "- `cute.Tensor` - Tensor type annotations",
            "",
            "[Documentation](https://github.com/NVIDIA/cutlass)"
        ]
        hover_content = "\n".join(hover_lines)
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_content))

    kernel = find_kernel_at_position(content, position, uri)
    if kernel:
        analysis = get_analysis_for_kernel(uri, kernel.name)

        if analysis:
            hover_content = test_message + format_kernel_hover(kernel, analysis)
        else:
            hover_content = test_message + format_kernel_hover_basic(kernel)

        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_content))

    layout = find_layout_at_position(content, position, uri)
    if layout:
        docs = DocsIndex()
        doc_link = docs.get_doc_for_concept("layout")

        hover_lines = [
            test_message,
            f"**Layout: {layout.name}**",
            ""
        ]

        if layout.shape:
            hover_lines.append(f"Shape: `{layout.shape}`")
        if layout.stride:
            hover_lines.append(f"Stride: `{layout.stride}`")

        if doc_link:
            hover_lines.append("")
            hover_lines.append(f"[Documentation]({doc_link})")

        hover_content = "\n".join(hover_lines)

        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_content))

    hover_content = test_message + "Hover is working! Move your cursor over symbols to see more info."
    return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=hover_content))
