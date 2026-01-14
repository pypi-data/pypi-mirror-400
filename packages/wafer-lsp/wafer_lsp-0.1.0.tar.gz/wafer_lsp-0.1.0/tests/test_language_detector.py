"""Tests for language detector component."""

from wafer_lsp.languages.detector import LanguageDetector


def test_register_and_detect_extension():
    """Test registering and detecting language from extension."""
    detector = LanguageDetector()
    detector.register_extension(".py", "python")

    assert detector.detect_from_extension(".py") == "python"
    assert detector.detect_from_extension("py") == "python"
    assert detector.detect_from_extension(".PY") == "python"  # Case insensitive


def test_detect_from_uri():
    """Test detecting language from file URI."""
    detector = LanguageDetector()
    detector.register_extension(".cu", "cuda")

    assert detector.detect_from_uri("file:///path/to/kernel.cu") == "cuda"
    assert detector.detect_from_uri("/path/to/kernel.cu") == "cuda"


def test_detect_from_path():
    """Test detecting language from file path."""
    detector = LanguageDetector()
    detector.register_extension(".cpp", "cpp")

    assert detector.detect_from_path("/path/to/file.cpp") == "cpp"
    assert detector.detect_from_path("file.cpp") == "cpp"


def test_unsupported_extension():
    """Test that unsupported extensions return None."""
    detector = LanguageDetector()

    assert detector.detect_from_extension(".unknown") is None


def test_is_supported():
    """Test checking if a URI is supported."""
    detector = LanguageDetector()
    detector.register_extension(".py", "python")

    assert detector.is_supported("file:///test.py") is True
    assert detector.is_supported("file:///test.txt") is False


def test_get_supported_extensions():
    """Test getting list of supported extensions."""
    detector = LanguageDetector()
    detector.register_extension(".py", "python")
    detector.register_extension(".cu", "cuda")

    extensions = detector.get_supported_extensions()
    assert ".py" in extensions
    assert ".cu" in extensions
    assert len(extensions) == 2
