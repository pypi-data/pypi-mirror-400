"""Tests for JavaScript/TypeScript language support."""

from pathlib import Path

from deeplint.detector import Detector

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "js"


class TestJavaScriptPatterns:
    """Test JavaScript-specific pattern detection."""

    def test_js_debug_console_detected(self) -> None:
        """JavaScript debug console statements should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        debug_issues = [i for i in issues if i.pattern_id == "js_debug_console"]
        assert len(debug_issues) >= 1, f"Expected debug console issues, got: {debug_issues}"

    def test_js_overconfident_comment_detected(self) -> None:
        """JavaScript overconfident comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        overconfident = [i for i in issues if i.pattern_id == "js_overconfident_comment"]
        assert len(overconfident) >= 1, f"Expected overconfident comments, got: {overconfident}"

    def test_js_hedging_comment_detected(self) -> None:
        """JavaScript hedging comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        hedging = [i for i in issues if i.pattern_id == "js_hedging_comment"]
        assert len(hedging) >= 1, f"Expected hedging comments, got: {hedging}"

    def test_js_var_keyword_detected(self) -> None:
        """JavaScript var keyword should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        var_issues = [i for i in issues if i.pattern_id == "js_var_keyword"]
        assert len(var_issues) >= 1, f"Expected var keyword issues, got: {var_issues}"

    def test_js_commented_code_detected(self) -> None:
        """JavaScript commented-out code should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        commented = [i for i in issues if i.pattern_id == "js_commented_code"]
        assert len(commented) >= 1, f"Expected commented code issues, got: {commented}"

    def test_clean_js_code_minimal_issues(self) -> None:
        """Clean JavaScript code should have minimal or no issues."""
        file = FIXTURES_DIR / "clean_code.js"
        detector = Detector(languages=["javascript"])
        issues = detector.scan([file])

        # Clean code might have no issues at all
        assert len(issues) == 0, f"Clean code should have no issues, got: {issues}"


class TestTypeScriptPatterns:
    """Test TypeScript-specific pattern detection."""

    def test_ts_debug_console_detected(self) -> None:
        """TypeScript debug console statements should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        debug_issues = [i for i in issues if i.pattern_id == "js_debug_console"]
        assert len(debug_issues) >= 1, f"Expected debug console issues, got: {debug_issues}"

    def test_ts_overconfident_comment_detected(self) -> None:
        """TypeScript overconfident comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        overconfident = [i for i in issues if i.pattern_id == "js_overconfident_comment"]
        assert len(overconfident) >= 1, f"Expected overconfident comments, got: {overconfident}"

    def test_ts_var_keyword_detected(self) -> None:
        """TypeScript var keyword should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        var_issues = [i for i in issues if i.pattern_id == "js_var_keyword"]
        assert len(var_issues) >= 1, f"Expected var keyword issues, got: {var_issues}"


class TestJavaScriptLanguageFilter:
    """Test language filtering for JavaScript/TypeScript."""

    def test_js_language_filter(self) -> None:
        """When filtering for JavaScript, only JS files should be scanned."""
        detector = Detector(languages=["javascript"])
        issues = detector.scan([FIXTURES_DIR.parent])  # Scan parent fixtures dir

        # Should only find issues in JS files
        js_files = [i.file for i in issues if i.file.suffix in (".js", ".jsx")]

        assert len(js_files) > 0, "Should find JavaScript files"
        # Non-JS files should not include TS files in JS-only filter
        ts_files = [i.file for i in issues if i.file.suffix in (".ts", ".tsx")]
        assert (
            len(ts_files) == 0
        ), f"Should not scan TypeScript files with JS filter, found: {ts_files}"

    def test_ts_language_filter(self) -> None:
        """When filtering for TypeScript, only TS files should be scanned."""
        detector = Detector(languages=["typescript"])
        issues = detector.scan([FIXTURES_DIR.parent])  # Scan parent fixtures dir

        # Should only find issues in TS files
        ts_files = [i.file for i in issues if i.file.suffix in (".ts", ".tsx")]

        assert len(ts_files) > 0, "Should find TypeScript files"
