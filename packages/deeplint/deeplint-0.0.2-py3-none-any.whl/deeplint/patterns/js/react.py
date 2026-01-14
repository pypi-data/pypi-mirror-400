"""JavaScript/TypeScript - React-specific anti-patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class JSUseEffectDerivedState(RegexPattern):
    """Detect useEffect setting state from props/other state."""

    id = "js_useEffect_derived_state"
    severity = Severity.HIGH
    axis = "structure"
    message = (
        "useEffect setting state from props/other state - consider useMemo or compute in render"
    )
    # Match when we see setX( pattern inside useEffect - simplified for line-by-line matching
    pattern = re.compile(
        r"useEffect.*set[A-Z]\w*\(",
    )


class JSUseEffectEmptyDeps(RegexPattern):
    """Detect useEffect with empty dependency array - potential missing dependencies."""

    id = "js_useEffect_empty_deps"
    severity = Severity.MEDIUM
    axis = "structure"
    message = "useEffect with empty deps - verify this truly should only run on mount"
    # Match useEffect followed by }, []); on same or nearby lines
    pattern = re.compile(
        r"useEffect.*\[\s*\]\s*\)",
    )


class JSSetStateInLoop(RegexPattern):
    """Detect setState being called inside a loop - causes multiple re-renders."""

    id = "js_setState_in_loop"
    severity = Severity.HIGH
    axis = "structure"
    message = "setState inside a loop - may cause multiple re-renders"
    # Match for loop with setState call
    pattern = re.compile(
        r"for\s*\([^)]+\)[^{]*\{[^}]*set[A-Z]\w*\(",
    )


class JSUseCallbackNoDeps(RegexPattern):
    """Detect useCallback with empty dependency array - stale callback."""

    id = "js_useCallback_no_deps"
    severity = Severity.MEDIUM
    axis = "structure"
    message = "useCallback with empty deps - the callback never updates and may use stale values"
    # Match useCallback with }, []);
    pattern = re.compile(
        r"useCallback.*\[\s*\]\s*\)",
    )


JS_REACT_PATTERNS = [
    JSUseEffectDerivedState(),
    JSUseEffectEmptyDeps(),
    JSSetStateInLoop(),
    JSUseCallbackNoDeps(),
]
