"""
Textbook helper module.

The textbook uses:

    import pet.textbook1.codes

to download teaching cases to the local machine.

This module keeps that behavior for backward compatibility.
"""
from __future__ import annotations

try:
    from pet.datasets.factory import download_textbook1 as _download_textbook1
    _download_textbook1()
except Exception as e:  # pragma: no cover
    print("Failed to copy textbook cases:", e)
