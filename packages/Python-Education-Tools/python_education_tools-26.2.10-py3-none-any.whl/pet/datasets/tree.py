from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def get_directory_info_dataframe(directory: Path = Path.home(), dst: Optional[Path] = Path.home() / 'files_info.xlsx') -> pd.DataFrame:
    """
    Convert immediate children of a directory to a DataFrame.

    Columns: 文件名, 类型(是否文件), 文件大小, 修改时间

    If dst is not None, writes the DataFrame to an Excel file.
    """
    p = Path(directory)
    data = []
    for i in p.iterdir():
        try:
            stat = i.stat()
            data.append((i.name, i.is_file(), stat.st_size, datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")))
        except Exception:
            continue

    df = pd.DataFrame(data, columns=['文件名', '类型', '文件大小', '修改时间'])
    if dst is not None:
        try:
            dst = Path(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(dst, index=None)
        except Exception:
            # Do not fail teaching code because writing failed.
            pass
    return df


def directory_to_str(root: Path, level: int = 0) -> Dict[Path, str]:
    """
    Map a directory into a printable tree string.
    Returns {root_path: tree_string}
    """
    root = Path(root)
    lines: List[str] = []
    indent = "    " * level
    lines.append(f"{indent}{root.name}/")

    for item in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name)):
        if item.is_dir():
            sub_dict = directory_to_str(item, level + 1)
            lines.append(sub_dict[item])
        else:
            lines.append(f"{'    ' * (level + 1)}{item.name}")

    return {root: "\n".join(lines)}


def list_subdirectories(directory: Path) -> List[Path]:
    """
    List direct subdirectories.
    """
    p = Path(directory)
    return [i for i in p.iterdir() if i.is_dir()]
