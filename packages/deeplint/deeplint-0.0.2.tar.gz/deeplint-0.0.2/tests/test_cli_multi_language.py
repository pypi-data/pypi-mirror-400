"""End-to-end tests for multi-language CLI functionality."""

from pathlib import Path

from deeplint.cli import main


def test_cli_automatic_detection_python_only(tmp_path: Path):
    """Test automatic language detection with Python only."""
    (tmp_path / "test.py").write_text("print('hello')")

    exit_code = main([str(tmp_path), "--format", "json"])
    assert exit_code == 0


def test_cli_automatic_detection_multiple_languages(tmp_path: Path):
    """Test automatic language detection with multiple languages."""
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.js").write_text("console.log('hello');")
    (tmp_path / "test.go").write_text("package main")

    exit_code = main([str(tmp_path)])
    assert exit_code == 0


def test_cli_manual_language_override_single(tmp_path: Path):
    """Test manual language override with single language."""
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.js").write_text("console.log('hello');")

    # Should only scan Python
    exit_code = main([str(tmp_path), "--language", "python"])
    assert exit_code == 0


def test_cli_manual_language_override_multiple(tmp_path: Path):
    """Test manual language override with multiple languages."""
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.js").write_text("console.log('hello');")
    (tmp_path / "test.go").write_text("package main")

    # Should scan JS and Go only
    exit_code = main([str(tmp_path), "--language", "javascript,go"])
    assert exit_code == 0


def test_cli_invalid_language(tmp_path: Path, capsys):
    """Test error handling for invalid language."""
    (tmp_path / "test.py").write_text("print('hello')")

    exit_code = main([str(tmp_path), "--language", "rust"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Invalid language" in captured.err
    assert "rust" in captured.err


def test_cli_no_supported_files(tmp_path: Path, capsys):
    """Test error when no supported language files found."""
    (tmp_path / "README.md").write_text("# Readme")

    exit_code = main([str(tmp_path)])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "No supported language files found" in captured.err


def test_cli_json_output_includes_languages(tmp_path: Path, capsys):
    """Test JSON output includes detected languages."""
    (tmp_path / "test.py").write_text("print('hello')")
    (tmp_path / "test.js").write_text("console.log('hello');")

    exit_code = main([str(tmp_path), "--format", "json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "languages" in captured.out
    assert "python" in captured.out
    assert "javascript" in captured.out


def test_cli_mixed_language_project_with_issues(tmp_path: Path):
    """Test scanning mixed-language project with actual issues."""
    # Python file with issue (placeholder)
    py_file = tmp_path / "test.py"
    py_file.write_text(
        """
def bad_func():
    pass
"""
    )

    # JS file (line-based checks still work)
    (tmp_path / "test.js").write_text("console.log('test');")

    exit_code = main([str(tmp_path), "--ci"])
    # Should exit with 1 because CI mode and issues found
    assert exit_code == 1


def test_cli_language_override_filters_correctly(tmp_path: Path):
    """Test that language override filters files correctly."""
    # Create Python file with issues (placeholder)
    (tmp_path / "bad.py").write_text(
        """
def func():
    pass
"""
    )

    # Create clean JS file
    (tmp_path / "clean.js").write_text("const x = 1;")

    # Scan only JS - should find no issues
    exit_code = main([str(tmp_path), "--language", "javascript", "--ci"])
    assert exit_code == 0

    # Scan Python - should find issues
    exit_code = main([str(tmp_path), "--language", "python", "--ci"])
    assert exit_code == 1


def test_cli_case_insensitive_language_names(tmp_path: Path):
    """Test that language names are case-insensitive."""
    (tmp_path / "test.py").write_text("print('hello')")

    exit_code = main([str(tmp_path), "--language", "Python"])
    assert exit_code == 0

    exit_code = main([str(tmp_path), "--language", "PYTHON"])
    assert exit_code == 0


def test_cli_typescript_file_extensions(tmp_path: Path):
    """Test detection of TypeScript file extensions."""
    (tmp_path / "App.tsx").write_text("const App = () => {};")
    (tmp_path / "utils.ts").write_text("export const add = (a: number, b: number) => a + b;")

    exit_code = main([str(tmp_path), "--language", "typescript"])
    assert exit_code == 0


def test_cli_javascript_file_extensions(tmp_path: Path):
    """Test detection of JavaScript file extensions."""
    (tmp_path / "app.js").write_text("console.log('test');")
    (tmp_path / "component.jsx").write_text("const C = () => <div/>;")
    (tmp_path / "module.mjs").write_text("export default {};")

    exit_code = main([str(tmp_path), "--language", "javascript"])
    assert exit_code == 0
