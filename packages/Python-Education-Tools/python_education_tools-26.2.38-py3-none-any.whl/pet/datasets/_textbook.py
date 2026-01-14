from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Optional

from ._paths import default_textbook_dst, open_in_file_manager
from ._resources import files


_SKIP_NAMES = {
    "__pycache__",
    ".ipynb_checkpoints",
    ".DS_Store",
    "Thumbs.db",
}


def _copytree_filtered(src: Path, dst: Path) -> None:
    def _ignore(dirpath: str, names: Iterable[str]):
        return [n for n in names if n in _SKIP_NAMES]

    shutil.copytree(str(src), str(dst), dirs_exist_ok=True, ignore=_ignore)


def download_textbook1(dst: Optional[Path] = None):
    """
    Copy teaching cases/resources to local machine (default: Desktop folder).
    This is intentionally a side-effect function used by the textbook.
    """
    if dst is None:
        dst = default_textbook_dst()

    src = files('pet.textbook_case')
    print('Copying, please wait....')
    _copytree_filtered(Path(str(src)), Path(dst))
    print('done!!')
    open_in_file_manager(Path(dst))
    return Path(dst)
