"""Tests for parser manager component."""

import pytest

from wafer_lsp.languages.parser_manager import ParserManager
from wafer_lsp.parsers.cuda_parser import CUDAParser
from wafer_lsp.parsers.cutedsl_parser import CuTeDSLParser


def test_register_and_get_parser():
    """Test registering and retrieving parsers."""
    manager = ParserManager()
    parser = CuTeDSLParser()

    manager.register_parser("cutedsl", "CuTeDSL", parser)

    assert manager.get_parser("cutedsl") is parser
    assert manager.get_parser("unknown") is None


def test_get_language_name():
    """Test getting language display name."""
    manager = ParserManager()
    manager.register_parser("cuda", "CUDA", CUDAParser())

    assert manager.get_language_name("cuda") == "CUDA"
    assert manager.get_language_name("unknown") is None


def test_has_parser():
    """Test checking if parser exists."""
    manager = ParserManager()
    manager.register_parser("cutedsl", "CuTeDSL", CuTeDSLParser())

    assert manager.has_parser("cutedsl") is True
    assert manager.has_parser("unknown") is False


def test_list_languages():
    """Test listing all registered languages."""
    manager = ParserManager()
    manager.register_parser("cutedsl", "CuTeDSL", CuTeDSLParser())
    manager.register_parser("cuda", "CUDA", CUDAParser())

    languages = manager.list_languages()
    assert "cutedsl" in languages
    assert "cuda" in languages
    assert len(languages) == 2


def test_duplicate_registration_raises():
    """Test that registering duplicate language raises error."""
    manager = ParserManager()
    manager.register_parser("cutedsl", "CuTeDSL", CuTeDSLParser())

    with pytest.raises(AssertionError):
        manager.register_parser("cutedsl", "CuTeDSL", CuTeDSLParser())
