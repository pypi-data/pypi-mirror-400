from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


# Create a persistent working directory for PET tools.
pet_home = Path.home() / "pet_home"
pet_home.mkdir(parents=True, exist_ok=True)


def default_textbook_dst() -> Path:
    """
    Return the default destination folder for textbook cases.
    Tries common desktop locations across platforms, otherwise falls back to `pet_home`.
    """
    # Windows / OneDrive / localized desktop variations are common in teaching environments.
    candidates = [
        Path.home() / "Desktop",
        Path.home() / "桌面",
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "OneDrive" / "桌面",
    ]
    for base in candidates:
        if base.exists():
            return base / "Python与数据分析及可视化教学案例"
    return pet_home / "Python与数据分析及可视化教学案例"


def make_output_xlsx(prefix: str) -> Path:
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    return pet_home / f"{prefix}_{ts}.xlsx"


def open_in_file_manager(path: Path) -> None:
    """
    Best-effort open a folder in the system file manager.
    Never raises to callers (teaching code should not crash due to this).
    """
    try:
        path = Path(path).resolve()
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        # Silently ignore; opening the folder is just a convenience.
        return
