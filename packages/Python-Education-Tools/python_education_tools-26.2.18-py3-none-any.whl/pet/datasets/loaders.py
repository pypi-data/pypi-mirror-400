from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Optional, Union

import pandas as pd

from ._constants import datafile_dict
from ._resources import files


def get_datasets_list() -> Iterable[str]:
    """
    Return available dataset keys.
    """
    return datafile_dict.keys()


def _normalize_key(key: str) -> str:
    return str(key).strip()


def load_data(key: str = '道德经', prompt: bool = True):
    """
    Load a built-in dataset by key (as used in the textbook).

    Supports xlsx / csv / txt.
    """
    key = _normalize_key(key)

    if prompt:
        print(f'共有{len(datafile_dict)}个可选数据集:\n {list(get_datasets_list())}')

    # Try direct key, then try adding/removing typical extensions.
    file_name = datafile_dict.get(key)
    if file_name is None:
        # If the user passed something like "道德经.txt", try stripping extension.
        stem = key.rsplit(".", 1)[0] if "." in key else key
        for k in (stem, f"{stem}.txt", f"{stem}.xlsx", f"{stem}.csv"):
            file_name = datafile_dict.get(k) or datafile_dict.get(stem)
            if file_name:
                break

    if file_name is None:
        file_name = "error.txt"

    data_file = files('pet.datasets.database').joinpath(file_name)

    suffix = file_name.rsplit(".", 1)[-1].lower()
    if suffix == "xlsx":
        return pd.read_excel(data_file)
    if suffix == "csv":
        return pd.read_csv(data_file)

    if suffix == "txt":
        try:
            return open(data_file, encoding="utf-8").read()
        except Exception:
            return open(data_file, encoding="gbk", errors="ignore").read()

    print('目前仅支持 xlsx，txt，csv 文件类型')
    return open(data_file, encoding="utf-8", errors="ignore").read()
