"""DeepLint - Multi-Language AI Slop Detector."""

try:
    from importlib.metadata import version

    __version__ = version("deeplint")
except Exception:
    __version__ = "0.0.0"  # Fallback for development
