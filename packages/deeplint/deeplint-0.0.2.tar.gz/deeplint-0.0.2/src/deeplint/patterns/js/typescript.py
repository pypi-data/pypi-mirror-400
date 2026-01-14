"""JavaScript/TypeScript - TypeScript-specific patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class TSAnyTypeUsage(RegexPattern):
    """Detect 'any' type usage in TypeScript."""

    id = "ts_any_type_usage"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found 'any' type usage - replace with specific type or 'unknown'"
    pattern = re.compile(
        r":\s*any\b",
    )


class TSArrayAnyType(RegexPattern):
    """Detect Array<any> type usage in TypeScript."""

    id = "ts_array_any_type"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found Array<any> type usage - replace with specific type or unknown[]"
    pattern = re.compile(
        r"Array\s*<\s*any\s*>",
    )


class TSGenericAnyType(RegexPattern):
    """Detect generic <any> type usage in TypeScript."""

    id = "ts_generic_any_type"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found generic <any> type usage - replace with specific type or unknown"
    pattern = re.compile(
        r"<\s*any\s*>",
    )


class TSUnsafeTypeAssertion(RegexPattern):
    """Detect unsafe 'as any' type assertions in TypeScript."""

    id = "ts_unsafe_type_assertion"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found unsafe 'as any' type assertion - use proper type guards or validation"
    pattern = re.compile(
        r"\s+as\s+any\b",
    )


class TSUnsafeDoubleTypeAssertion(RegexPattern):
    """Detect unsafe double type assertions in TypeScript."""

    id = "ts_unsafe_double_type_assertion"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found unsafe double type assertion - consider using 'as unknown as Type'"
    pattern = re.compile(
        r"as\s+\w+\s+as\s+\w+",
    )


class TSIndexSignatureAny(RegexPattern):
    """Detect index signatures with 'any' type in TypeScript."""

    id = "ts_index_signature_any"
    severity = Severity.HIGH
    axis = "quality"
    message = "Found index signature with 'any' type - replace with specific type or unknown"
    pattern = re.compile(
        r"\[\s*[\"'`]?(\w+)[\"'`]?[^\]]*\]\s*:\s*any",
    )


JS_TYPESCRIPT_PATTERNS = [
    TSAnyTypeUsage(),
    TSArrayAnyType(),
    TSGenericAnyType(),
    TSUnsafeTypeAssertion(),
    TSUnsafeDoubleTypeAssertion(),
    TSIndexSignatureAny(),
]
