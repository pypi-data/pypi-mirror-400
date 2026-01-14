"""
Compatibility layer around importlib.resources.

We use `files()` when available (Python >= 3.9) and fall back to the
`importlib_resources` backport when necessary.
"""
from __future__ import annotations

from typing import Any

try:
    # Python 3.9+
    from importlib.resources import files as _files  # type: ignore
except Exception:  # pragma: no cover
    try:
        from importlib_resources import files as _files  # type: ignore
    except Exception as e:  # pragma: no cover
        _files = None  # type: ignore
        _import_error = e
    else:
        _import_error = None
else:
    _import_error = None


def files(package: str) -> Any:
    """
    Return an importlib.resources Traversable for the given package.
    """
    if _files is None:  # pragma: no cover
        raise ImportError(
            "importlib.resources.files is unavailable. "
            "On Python < 3.9, install 'importlib-resources'."
        ) from _import_error
    return _files(package)
