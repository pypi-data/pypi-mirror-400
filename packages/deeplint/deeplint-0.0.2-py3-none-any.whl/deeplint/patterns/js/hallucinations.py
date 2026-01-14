"""JavaScript/TypeScript - Information Quality (Hallucinations) patterns."""

import re

from deeplint.patterns.base import RegexPattern, Severity


class JSHallucinatedReactImport(RegexPattern):
    """Detect hallucinated React imports - APIs imported from wrong packages."""

    id = "js_hallucinated_react_import"
    severity = Severity.CRITICAL
    axis = "quality"
    message = "Hallucinated React import - these APIs do NOT exist in 'react' package"
    pattern = re.compile(
        r"import\s*\{[^}]*(useRouter|useParams|useSearchParams|Link|Image|Script)[^}]*\}\s*from\s*['\"]react['\"]",
        re.IGNORECASE,
    )


class JSHallucinatedNextImport(RegexPattern):
    """Detect Next.js APIs imported from React - 100% AI hallucination."""

    id = "js_hallucinated_next_import"
    severity = Severity.CRITICAL
    axis = "quality"
    message = "Next.js API imported from 'react' - these are page-level exports, not imports"
    pattern = re.compile(
        r"import\s*\{[^}]*(getServerSideProps|getStaticProps|getStaticPaths)[^}]*\}\s*from\s*['\"]react['\"]",
        re.IGNORECASE,
    )


class JSTodoImplementationPlaceholder(RegexPattern):
    """Detect TODO comments indicating AI gave up on implementation."""

    id = "js_todo_implementation_placeholder"
    severity = Severity.HIGH
    axis = "quality"
    message = "AI gave up and wrote a TODO instead of implementing logic"
    pattern = re.compile(
        r"//\s*(?:TODO|FIXME|HACK).*(?:implement|add|finish|complete|your code|logic|here)",
        re.IGNORECASE,
    )


class JSAssumptionComment(RegexPattern):
    """Detect comments indicating unverified assumptions."""

    id = "js_assumption_comment"
    severity = Severity.HIGH
    axis = "quality"
    message = "AI making unverified assumptions - dangerous in production"
    pattern = re.compile(
        r"\b(assuming|assumes?|presumably|apparently|it seems|seems like)\b.{0,50}\b(that|this|the|it)\b",
        re.IGNORECASE,
    )


JS_HALLUCINATION_PATTERNS = [
    JSHallucinatedReactImport(),
    JSHallucinatedNextImport(),
    JSTodoImplementationPlaceholder(),
    JSAssumptionComment(),
]
