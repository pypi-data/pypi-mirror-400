from __future__ import annotations

from typing import Optional

_engine = None


def get_engine():
    """
    Lazily initialize pyttsx3 engine.
    This avoids import-time failures when the optional dependency is missing.
    """
    global _engine
    if _engine is not None:
        return _engine
    try:
        import pyttsx3  # type: ignore
    except Exception as e:
        raise ImportError(
            "Audio TTS requires 'pyttsx3'. Install it via: pip install pyttsx3"
        ) from e
    _engine = pyttsx3.init()
    return _engine
