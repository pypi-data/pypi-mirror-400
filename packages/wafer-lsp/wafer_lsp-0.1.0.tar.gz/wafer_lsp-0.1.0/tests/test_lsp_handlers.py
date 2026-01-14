"""Tests for LSP handlers."""

from lsprotocol.types import Position, Range

from wafer_lsp.handlers.code_action import handle_code_action
from wafer_lsp.handlers.document_symbol import handle_document_symbol
from wafer_lsp.handlers.hover import handle_hover


def test_document_symbol_kernel():
    """Test document symbol for kernel."""
    content = """
@cute.kernel
def test_kernel(a: cute.Tensor):
    pass
"""
    uri = "file:///test.py"
    symbols = handle_document_symbol(uri, content)

    assert len(symbols) == 1
    assert symbols[0].name == "test_kernel"
    assert symbols[0].kind.value == 12  # FUNCTION


def test_hover_kernel():
    """Test hover for kernel."""
    content = """
@cute.kernel
def test_kernel(a: cute.Tensor):
    \"\"\"Test kernel docstring.\"\"\"
    pass
"""
    uri = "file:///test.py"
    position = Position(line=2, character=5)  # Over "test_kernel"
    hover = handle_hover(uri, position, content)

    assert hover is not None
    assert "test_kernel" in hover.contents.value


def test_code_action_kernel():
    """Test code action for kernel."""
    content = """
@cute.kernel
def test_kernel(a: cute.Tensor):
    pass
"""
    uri = "file:///test.py"
    range = Range(
        start=Position(line=2, character=0),
        end=Position(line=3, character=0)
    )
    actions = handle_code_action(uri, range, content)

    assert len(actions) == 2
    assert "Analyze Kernel" in actions[0].title
    assert "Profile Kernel" in actions[1].title
