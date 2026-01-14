"""Tests for CuTeDSL parser."""

from wafer_lsp.parsers.cutedsl_parser import CuTeDSLKernel, CuTeDSLLayout, CuTeDSLParser


def test_parse_kernel():
    """Test kernel discovery."""
    content = """
import cutlass.cute as cute

@cute.kernel
def my_kernel(a: cute.Tensor, b: cute.Tensor):
    \"\"\"Test kernel.\"\"\"
    pass
"""
    parser = CuTeDSLParser()
    result = parser.parse_file(content)

    assert len(result["kernels"]) == 1
    kernel = result["kernels"][0]
    assert isinstance(kernel, CuTeDSLKernel)
    assert kernel.name == "my_kernel"
    assert kernel.docstring == "Test kernel."
    assert "a" in kernel.parameters
    assert "b" in kernel.parameters


def test_parse_layout():
    """Test layout extraction."""
    content = """
import cutlass.cute as cute

layout_a = cute.make_layout((128, 256))
"""
    parser = CuTeDSLParser()
    result = parser.parse_file(content)

    assert len(result["layouts"]) == 1
    layout = result["layouts"][0]
    assert isinstance(layout, CuTeDSLLayout)
    assert layout.name == "layout_a"


def test_parse_struct():
    """Test struct discovery."""
    content = """
import cutlass.cute as cute

@cute.struct
class SharedStorage:
    \"\"\"Shared memory structure.\"\"\"
    pass
"""
    parser = CuTeDSLParser()
    result = parser.parse_file(content)

    assert len(result["structs"]) == 1
    struct = result["structs"][0]
    assert struct.name == "SharedStorage"
    assert struct.docstring == "Shared memory structure."
