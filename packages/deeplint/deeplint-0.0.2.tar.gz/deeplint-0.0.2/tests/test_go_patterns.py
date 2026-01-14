"""Tests for Go language support."""

from pathlib import Path

from deeplint.detector import Detector

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "go"


class TestGoPatterns:
    """Test Go-specific pattern detection."""

    def test_go_debug_print_detected(self) -> None:
        """Go debug print statements should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        debug_issues = [i for i in issues if i.pattern_id == "go_debug_print"]
        assert len(debug_issues) >= 1, f"Expected debug print issues, got: {debug_issues}"

    def test_go_overconfident_comment_detected(self) -> None:
        """Go overconfident comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        overconfident = [i for i in issues if i.pattern_id == "go_overconfident_comment"]
        assert len(overconfident) >= 1, f"Expected overconfident comments, got: {overconfident}"

    def test_go_hedging_comment_detected(self) -> None:
        """Go hedging comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        hedging = [i for i in issues if i.pattern_id == "go_hedging_comment"]
        assert len(hedging) >= 1, f"Expected hedging comments, got: {hedging}"

    def test_go_redundant_comment_detected(self) -> None:
        """Go redundant comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        redundant = [i for i in issues if i.pattern_id == "go_redundant_comment"]
        assert len(redundant) >= 1, f"Expected redundant comments, got: {redundant}"

    def test_go_todo_comment_detected(self) -> None:
        """Go TODO comments should be detected."""
        file = FIXTURES_DIR / "sample_with_issues.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        todo = [i for i in issues if i.pattern_id == "go_todo_comment"]
        assert len(todo) >= 1, f"Expected TODO comments, got: {todo}"

    def test_clean_go_code_minimal_issues(self) -> None:
        """Clean Go code should have minimal or no issues."""
        file = FIXTURES_DIR / "clean_code.go"
        detector = Detector(languages=["go"])
        issues = detector.scan([file])

        # Clean code might have no issues at all
        assert len(issues) <= 1, f"Clean code should have minimal issues, got: {issues}"


class TestGoLanguageFilter:
    """Test language filtering for Go."""

    def test_go_language_filter(self) -> None:
        """When filtering for Go, only Go files should be scanned."""
        detector = Detector(languages=["go"])
        issues = detector.scan([FIXTURES_DIR.parent])  # Scan parent fixtures dir

        # Should only find issues in Go files
        go_files = [i.file for i in issues if i.file.suffix == ".go"]
        non_go_files = [i.file for i in issues if i.file.suffix != ".go"]

        assert len(go_files) > 0, "Should find Go files"
        assert len(non_go_files) == 0, f"Should not scan non-Go files, found: {non_go_files}"
