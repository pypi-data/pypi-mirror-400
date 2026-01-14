"""Tests for KarpeSlop-inspired JavaScript/TypeScript patterns."""

from pathlib import Path

from deeplint.detector import Detector

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "js"


class TestHallucinatedImports:
    """Test hallucinated import detection."""

    def test_hallucinated_react_import_detected(self) -> None:
        """Hallucinated React imports should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        hallucinated = [i for i in issues if i.pattern_id == "js_hallucinated_react_import"]
        assert len(hallucinated) >= 1, f"Expected hallucinated React imports, got: {hallucinated}"

    def test_hallucinated_next_import_detected(self) -> None:
        """Hallucinated Next.js imports should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        hallucinated = [i for i in issues if i.pattern_id == "js_hallucinated_next_import"]
        assert len(hallucinated) >= 1, f"Expected hallucinated Next.js imports, got: {hallucinated}"

    def test_clean_imports_not_flagged(self) -> None:
        """Clean imports should not be flagged."""
        file = FIXTURES_DIR / "clean_react.tsx"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        hallucinated_react = [i for i in issues if i.pattern_id == "js_hallucinated_react_import"]
        hallucinated_next = [i for i in issues if i.pattern_id == "js_hallucinated_next_import"]

        assert (
            len(hallucinated_react) == 0
        ), "Clean imports should not trigger hallucinated_react_import"
        assert (
            len(hallucinated_next) == 0
        ), "Clean imports should not trigger hallucinated_next_import"


class TestTypeScriptPatterns:
    """Test TypeScript-specific pattern detection."""

    def test_any_type_usage_detected(self) -> None:
        """TypeScript 'any' type usage should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        any_issues = [i for i in issues if i.pattern_id == "ts_any_type_usage"]
        assert len(any_issues) >= 1, f"Expected 'any' type issues, got: {any_issues}"

    def test_array_any_type_detected(self) -> None:
        """TypeScript Array<any> type usage should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        array_any = [i for i in issues if i.pattern_id == "ts_array_any_type"]
        assert len(array_any) >= 1, f"Expected Array<any> issues, got: {array_any}"

    def test_unsafe_type_assertion_detected(self) -> None:
        """TypeScript 'as any' assertions should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        unsafe_assertions = [i for i in issues if i.pattern_id == "ts_unsafe_type_assertion"]
        assert (
            len(unsafe_assertions) >= 1
        ), f"Expected unsafe type assertions, got: {unsafe_assertions}"

    def test_clean_typing_not_flagged(self) -> None:
        """Clean TypeScript code with proper types should not be flagged."""
        file = FIXTURES_DIR / "clean_react.tsx"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        any_issues = [i for i in issues if "ts_any" in i.pattern_id or "ts_unsafe" in i.pattern_id]
        assert (
            len(any_issues) == 0
        ), f"Clean typing should not trigger any TS issues, got: {any_issues}"


class TestReactPatterns:
    """Test React-specific anti-pattern detection."""

    def test_useEffect_derived_state_detected(self) -> None:
        """useEffect setting derived state should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        use_effect = [i for i in issues if i.pattern_id == "js_useEffect_derived_state"]
        assert len(use_effect) >= 1, f"Expected useEffect derived state issues, got: {use_effect}"

    def test_useEffect_empty_deps_detected(self) -> None:
        """useEffect with empty deps should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        empty_deps = [i for i in issues if i.pattern_id == "js_useEffect_empty_deps"]
        assert len(empty_deps) >= 1, f"Expected useEffect empty deps issues, got: {empty_deps}"

    def test_setState_in_loop_detected(self) -> None:
        """setState in a loop should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        loop_issues = [i for i in issues if i.pattern_id == "js_setState_in_loop"]
        assert len(loop_issues) >= 1, f"Expected setState in loop issues, got: {loop_issues}"

    def test_useCallback_no_deps_detected(self) -> None:
        """useCallback with empty deps should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        callback_issues = [i for i in issues if i.pattern_id == "js_useCallback_no_deps"]
        assert (
            len(callback_issues) >= 1
        ), f"Expected useCallback no deps issues, got: {callback_issues}"

    def test_clean_react_patterns_not_flagged(self) -> None:
        """Clean React patterns should not be flagged."""
        file = FIXTURES_DIR / "clean_react.tsx"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        react_issues = [
            i
            for i in issues
            if "useEffect" in i.pattern_id
            or "useCallback" in i.pattern_id
            or "setState" in i.pattern_id
        ]
        assert (
            len(react_issues) == 0
        ), f"Clean React patterns should not trigger issues, got: {react_issues}"


class TestStylePatterns:
    """Test style-related pattern detection."""

    def test_unnecessary_iife_detected(self) -> None:
        """Unnecessary IIFE wrappers should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        iife_issues = [i for i in issues if i.pattern_id == "js_unnecessary_iife"]
        assert len(iife_issues) >= 1, f"Expected IIFE issues, got: {iife_issues}"

    def test_nested_ternary_abuse_detected(self) -> None:
        """Nested ternary abuse should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        ternary_issues = [i for i in issues if i.pattern_id == "js_nested_ternary_abuse"]
        assert len(ternary_issues) >= 1, f"Expected nested ternary issues, got: {ternary_issues}"

    def test_magic_css_value_detected(self) -> None:
        """Magic CSS values should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        magic_css = [i for i in issues if i.pattern_id == "js_magic_css_value"]
        assert len(magic_css) >= 1, f"Expected magic CSS value issues, got: {magic_css}"


class TestQualityPatterns:
    """Test quality-related pattern detection."""

    def test_todo_implementation_placeholder_detected(self) -> None:
        """TODO implementation placeholders should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        todo_issues = [i for i in issues if i.pattern_id == "js_todo_implementation_placeholder"]
        assert (
            len(todo_issues) >= 1
        ), f"Expected TODO implementation placeholders, got: {todo_issues}"

    def test_assumption_comment_detected(self) -> None:
        """Assumption comments should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        assumption_issues = [i for i in issues if i.pattern_id == "js_assumption_comment"]
        assert (
            len(assumption_issues) >= 1
        ), f"Expected assumption comments, got: {assumption_issues}"

    def test_missing_error_handling_detected(self) -> None:
        """Missing error handling should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        error_handling = [i for i in issues if i.pattern_id == "js_missing_error_handling"]
        assert (
            len(error_handling) >= 1
        ), f"Expected missing error handling issues, got: {error_handling}"


class TestNoisePatterns:
    """Test noise-related pattern detection."""

    def test_excessive_boilerplate_comment_detected(self) -> None:
        """Excessive boilerplate comments should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        boilerplate = [i for i in issues if i.pattern_id == "js_excessive_boilerplate_comment"]
        assert len(boilerplate) >= 1, f"Expected boilerplate comments, got: {boilerplate}"

    def test_debug_log_with_comment_detected(self) -> None:
        """Debug logs with comments should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        debug_log = [i for i in issues if i.pattern_id == "js_debug_log_with_comment"]
        assert len(debug_log) >= 1, f"Expected debug log with comment, got: {debug_log}"

    def test_production_console_log_detected(self) -> None:
        """Production console logs should be detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        console_logs = [i for i in issues if i.pattern_id == "js_production_console_log"]
        assert len(console_logs) >= 1, f"Expected production console logs, got: {console_logs}"


class TestIntegration:
    """Integration tests for the full pattern set."""

    def test_karpeslop_patterns_comprehensive(self) -> None:
        """KarpeSlop fixture should have many issues detected."""
        file = FIXTURES_DIR / "karpeslop_patterns.ts"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        # Should detect multiple categories
        critical_issues = [i for i in issues if i.severity.value == "critical"]
        high_issues = [i for i in issues if i.severity.value == "high"]

        assert (
            len(critical_issues) >= 2
        ), f"Expected at least 2 critical issues, got {len(critical_issues)}"
        assert (
            len(high_issues) >= 5
        ), f"Expected at least 5 high severity issues, got {len(high_issues)}"
        assert len(issues) >= 15, f"Expected at least 15 total issues, got {len(issues)}"

    def test_clean_react_minimal_issues(self) -> None:
        """Clean React code should have minimal or no issues."""
        file = FIXTURES_DIR / "clean_react.tsx"
        detector = Detector(languages=["typescript"])
        issues = detector.scan([file])

        # Clean code should have no critical or high severity issues
        critical_issues = [i for i in issues if i.severity.value == "critical"]
        high_issues = [i for i in issues if i.severity.value == "high"]

        assert (
            len(critical_issues) == 0
        ), f"Clean code should have no critical issues, got: {critical_issues}"
        assert (
            len(high_issues) == 0
        ), f"Clean code should have no high severity issues, got: {high_issues}"
