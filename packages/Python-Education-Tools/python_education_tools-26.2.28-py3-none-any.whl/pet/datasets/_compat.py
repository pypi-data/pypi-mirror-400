from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .tree import get_directory_info_dataframe
from .sysinfo import get_pid_memory_info_dataframe, get_pid_network_info_dataframe


def directory_to_dataframe(directory: Union[str, Path] = Path.home()) -> pd.DataFrame:
    """
    Textbook compatibility alias.

    Original textbook name: directory_to_dataframe
    New implementation: get_directory_info_dataframe(dst=None)
    """
    return get_directory_info_dataframe(Path(directory), dst=None)


def directory_to_excel(directory: Union[str, Path] = Path.home(),
                       dst: Union[str, Path] = Path.home() / 'files_info.xlsx') -> pd.DataFrame:
    """
    Textbook compatibility alias.

    Writes Excel and returns DataFrame.
    """
    return get_directory_info_dataframe(Path(directory), dst=Path(dst))


def pid_info_to_dataframe() -> pd.DataFrame:
    """
    Textbook compatibility alias.
    """
    return get_pid_memory_info_dataframe()


def pid_networkinfo_to_dataframe() -> pd.DataFrame:
    """
    Textbook compatibility alias.
    """
    return get_pid_network_info_dataframe()
