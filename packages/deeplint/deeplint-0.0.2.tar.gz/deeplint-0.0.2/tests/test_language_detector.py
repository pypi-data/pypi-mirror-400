"""Tests for language detection functionality."""

from pathlib import Path

from deeplint.language_detector import (
    detect_languages,
    get_extensions_for_language,
    get_extensions_for_languages,
    get_language_from_extension,
    get_supported_languages,
    is_supported_language,
    parse_language_arg,
)


def test_get_language_from_extension():
    """Test getting language from file extension."""
    assert get_language_from_extension(".py") == "python"
    assert get_language_from_extension(".js") == "javascript"
    assert get_language_from_extension(".ts") == "typescript"
    assert get_language_from_extension(".go") == "go"
    assert get_language_from_extension(".jsx") == "javascript"
    assert get_language_from_extension(".tsx") == "typescript"
    assert get_language_from_extension(".unknown") is None


def test_get_extensions_for_language():
    """Test getting extensions for a language."""
    assert ".py" in get_extensions_for_language("python")
    assert ".js" in get_extensions_for_language("javascript")
    assert ".ts" in get_extensions_for_language("typescript")
    assert ".go" in get_extensions_for_language("go")
    assert get_extensions_for_language("unknown") == []


def test_get_extensions_for_languages():
    """Test getting extensions for multiple languages."""
    exts = get_extensions_for_languages(["python", "javascript"])
    assert ".py" in exts
    assert ".js" in exts
    assert ".go" not in exts


def test_parse_language_arg():
    """Test parsing language argument."""
    assert parse_language_arg("python") == ["python"]
    assert parse_language_arg("python,javascript") == ["python", "javascript"]
    assert parse_language_arg("Python,JavaScript") == ["python", "javascript"]
    assert parse_language_arg("python, javascript") == ["python", "javascript"]
    assert parse_language_arg(None) == []
    assert parse_language_arg("rust") == []  # Unsupported language
    assert parse_language_arg("python,rust,go") == ["python", "go"]  # Mix valid/invalid


def test_is_supported_language():
    """Test checking if a language is supported."""
    assert is_supported_language("python")
    assert is_supported_language("Python")
    assert is_supported_language("javascript")
    assert is_supported_language("typescript")
    assert is_supported_language("go")
    assert not is_supported_language("rust")
    assert not is_supported_language("ruby")


def test_get_supported_languages():
    """Test getting all supported languages."""
    langs = get_supported_languages()
    assert "python" in langs
    assert "javascript" in langs
    assert "typescript" in langs
    assert "go" in langs
    assert len(langs) == 4


def test_detect_languages_with_files(tmp_path: Path):
    """Test detecting languages from individual files."""
    py_file = tmp_path / "test.py"
    js_file = tmp_path / "test.js"
    py_file.write_text("print('hello')")
    js_file.write_text("console.log('hello');")

    detected = detect_languages([py_file, js_file])
    assert "python" in detected
    assert "javascript" in detected


def test_detect_languages_with_directory(tmp_path: Path):
    """Test detecting languages from a directory."""
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.js").write_text("console.log('hello');")
    (tmp_path / "test.go").write_text("package main")
    (tmp_path / "test.ts").write_text("const x: string = 'hello';")

    detected = detect_languages([tmp_path])
    assert "python" in detected
    assert "javascript" in detected
    assert "go" in detected
    assert "typescript" in detected


def test_detect_languages_mixed_paths(tmp_path: Path):
    """Test detecting languages from mixed file and directory paths."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    py_file = tmp_path / "test.py"
    py_file.write_text("print('hello')")

    (subdir / "test.js").write_text("console.log('hello');")

    detected = detect_languages([py_file, subdir])
    assert "python" in detected
    assert "javascript" in detected


def test_detect_languages_no_supported_files(tmp_path: Path):
    """Test detecting languages when no supported files exist."""
    (tmp_path / "test.txt").write_text("hello")
    (tmp_path / "README.md").write_text("# Readme")

    detected = detect_languages([tmp_path])
    assert len(detected) == 0


def test_detect_languages_nested_directories(tmp_path: Path):
    """Test detecting languages in nested directories."""
    nested = tmp_path / "src" / "components"
    nested.mkdir(parents=True)

    (nested / "App.tsx").write_text("const App = () => {};")
    (tmp_path / "main.py").write_text("print('hello')")

    detected = detect_languages([tmp_path])
    assert "python" in detected
    assert "typescript" in detected


def test_detect_languages_empty_directory(tmp_path: Path):
    """Test detecting languages in empty directory."""
    detected = detect_languages([tmp_path])
    assert len(detected) == 0
