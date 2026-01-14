"""Tests for parser result converter component."""

from dataclasses import dataclass

from wafer_lsp.languages.converter import ParserResultConverter
from wafer_lsp.languages.types import KernelInfo, LayoutInfo, StructInfo


@dataclass
class MockKernel:
    """Mock kernel for testing."""
    name: str
    line: int
    parameters: list
    docstring: str | None = None


@dataclass
class MockLayout:
    """Mock layout for testing."""
    name: str
    line: int
    shape: str | None = None
    stride: str | None = None


@dataclass
class MockStruct:
    """Mock struct for testing."""
    name: str
    line: int
    docstring: str | None = None


def test_convert_kernels():
    """Test converting kernels to KernelInfo."""
    converter = ParserResultConverter()

    mock_kernels = [
        MockKernel("test_kernel", 10, ["a", "b"], "Test docstring")
    ]

    parsed_data = {"kernels": mock_kernels, "layouts": [], "structs": []}
    result = converter.convert(parsed_data, "testlang")

    assert len(result.kernels) == 1
    assert isinstance(result.kernels[0], KernelInfo)
    assert result.kernels[0].name == "test_kernel"
    assert result.kernels[0].line == 10
    assert result.kernels[0].parameters == ["a", "b"]
    assert result.kernels[0].docstring == "Test docstring"
    assert result.kernels[0].language == "testlang"


def test_convert_layouts():
    """Test converting layouts to LayoutInfo."""
    converter = ParserResultConverter()

    mock_layouts = [
        MockLayout("test_layout", 20, "(128, 256)", "(1, 128)")
    ]

    parsed_data = {"kernels": [], "layouts": mock_layouts, "structs": []}
    result = converter.convert(parsed_data, "testlang")

    assert len(result.layouts) == 1
    assert isinstance(result.layouts[0], LayoutInfo)
    assert result.layouts[0].name == "test_layout"
    assert result.layouts[0].line == 20
    assert result.layouts[0].shape == "(128, 256)"
    assert result.layouts[0].stride == "(1, 128)"
    assert result.layouts[0].language == "testlang"


def test_convert_structs():
    """Test converting structs to StructInfo."""
    converter = ParserResultConverter()

    mock_structs = [
        MockStruct("TestStruct", 30, "Struct docstring")
    ]

    parsed_data = {"kernels": [], "layouts": [], "structs": mock_structs}
    result = converter.convert(parsed_data, "testlang")

    assert len(result.structs) == 1
    assert isinstance(result.structs[0], StructInfo)
    assert result.structs[0].name == "TestStruct"
    assert result.structs[0].line == 30
    assert result.structs[0].docstring == "Struct docstring"
    assert result.structs[0].language == "testlang"


def test_convert_empty():
    """Test converting empty parser result."""
    converter = ParserResultConverter()

    parsed_data = {"kernels": [], "layouts": [], "structs": []}
    result = converter.convert(parsed_data, "testlang")

    assert len(result.kernels) == 0
    assert len(result.layouts) == 0
    assert len(result.structs) == 0
    assert result.language == "testlang"
    assert result.raw_data == parsed_data


def test_convert_preserves_raw_data():
    """Test that raw parser data is preserved."""
    converter = ParserResultConverter()

    parsed_data = {
        "kernels": [],
        "layouts": [],
        "structs": [],
        "custom_field": "custom_value"
    }
    result = converter.convert(parsed_data, "testlang")

    assert result.raw_data == parsed_data
    assert "custom_field" in result.raw_data
