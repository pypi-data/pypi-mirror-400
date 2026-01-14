"""Language detection for multi-language support."""

from __future__ import annotations

from pathlib import Path

# Supported languages and their file extensions
LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyw"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx"],
    "go": [".go"],
}

# Reverse mapping: extension -> language
EXTENSION_TO_LANGUAGE = {ext: lang for lang, exts in LANGUAGE_EXTENSIONS.items() for ext in exts}


def detect_languages(paths: list[Path]) -> set[str]:
    """Detect languages present in the given paths.

    Args:
        paths: List of file or directory paths to scan

    Returns:
        Set of detected language names (e.g., {"python", "javascript"})
    """
    detected = set()

    for path in paths:
        if path.is_file():
            lang = get_language_from_extension(path.suffix)
            if lang:
                detected.add(lang)
        elif path.is_dir():
            # Scan directory once and check all extensions
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    lang = get_language_from_extension(file_path.suffix)
                    if lang:
                        detected.add(lang)
                        # Early exit if we've found all languages
                        if len(detected) == len(LANGUAGE_EXTENSIONS):
                            return detected

    return detected


def get_language_from_extension(extension: str) -> str | None:
    """Get language name from file extension.

    Args:
        extension: File extension including the dot (e.g., ".py")

    Returns:
        Language name or None if not supported
    """
    return EXTENSION_TO_LANGUAGE.get(extension.lower())


def get_extensions_for_language(language: str) -> list[str]:
    """Get file extensions for a language.

    Args:
        language: Language name (e.g., "python")

    Returns:
        List of file extensions for that language
    """
    return LANGUAGE_EXTENSIONS.get(language.lower(), [])


def get_extensions_for_languages(languages: list[str]) -> list[str]:
    """Get all file extensions for multiple languages.

    Args:
        languages: List of language names

    Returns:
        Combined list of all file extensions
    """
    extensions = []
    for lang in languages:
        extensions.extend(get_extensions_for_language(lang))
    return extensions


def parse_language_arg(language_arg: str | None) -> list[str]:
    """Parse the --language CLI argument.

    Args:
        language_arg: Comma-separated language string or None

    Returns:
        List of language names
    """
    if not language_arg:
        return []

    # Split by comma and normalize
    languages = [lang.strip().lower() for lang in language_arg.split(",")]

    # Validate languages
    valid_languages = []
    for lang in languages:
        if lang in LANGUAGE_EXTENSIONS:
            valid_languages.append(lang)

    return valid_languages


def is_supported_language(language: str) -> bool:
    """Check if a language is supported.

    Args:
        language: Language name

    Returns:
        True if language is supported
    """
    return language.lower() in LANGUAGE_EXTENSIONS


def get_supported_languages() -> list[str]:
    """Get list of all supported languages.

    Returns:
        List of supported language names
    """
    return list(LANGUAGE_EXTENSIONS.keys())
