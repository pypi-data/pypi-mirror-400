from __future__ import annotations

import os
import re
import sys
from subprocess import check_output
from typing import Any, Dict, List, Optional

import pandas as pd


def _require_psutil():
    try:
        import psutil  # type: ignore
        return psutil
    except Exception as e:
        raise ImportError(
            "This function requires 'psutil'. Install it via: pip install psutil"
        ) from e


def get_pid_memory_info_dataframe() -> pd.DataFrame:
    """
    Per-process memory usage.
    Returns columns: 进程名, pid, 物理内存, 虚拟内存
    """
    psutil = _require_psutil()
    try:
        memory = psutil.virtual_memory()
        print(f'Total memory: {memory.total}, Available memory: {memory.available}')
    except Exception:
        pass

    rows = []
    for proc in psutil.process_iter(attrs=[], ad_value=None):
        try:
            rows.append((proc.name(), proc.pid, proc.memory_info().rss, proc.memory_info().vms))
        except Exception:
            continue
    return pd.DataFrame(rows, columns=['进程名', 'pid', '物理内存', '虚拟内存'])


def get_pid_info_dataframe() -> pd.DataFrame:
    psutil = _require_psutil()
    rows = []
    for proc in psutil.process_iter(attrs=[], ad_value=None):
        try:
            rows.append(proc.as_dict())
        except Exception:
            continue
    return pd.DataFrame(rows)


def get_pid_network_info_dataframe() -> pd.DataFrame:
    """
    Per-process IO counters (used as a proxy for network stats in the original implementation).
    """
    psutil = _require_psutil()
    columns = ['进程名称', 'pid', '收到数据包', '发送数据包', '收到字节数', '发送字节', '其它包数', '其它字节']
    rows = []
    for proc in psutil.process_iter(attrs=[], ad_value=None):
        try:
            rows.append((proc.name(), proc.pid, *proc.io_counters()))
        except Exception:
            continue
    df = pd.DataFrame(rows, columns=columns)
    if len(df) > 0:
        print(df.head())
    return df


def get_nic_info_series() -> pd.Series:
    """
    Return NIC descriptions (Windows-only, best effort).
    """
    if not sys.platform.startswith("win"):
        return pd.Series([], dtype="object")
    cmd = 'netsh trace show interfaces'
    try:
        results = re.findall(r'描述:\s+(.+)', check_output(cmd, universal_newlines=True))
        return pd.Series(results)
    except Exception:
        return pd.Series([], dtype="object")


def get_local_packages_info_dataframe() -> pd.DataFrame:
    """
    List installed Python packages in the current environment.
    """
    try:
        from importlib.metadata import distributions  # Python 3.8+
    except Exception:  # pragma: no cover
        from importlib_metadata import distributions  # type: ignore

    pkg = []
    for dist in distributions():
        meta = dist.metadata
        name = meta.get('Name', 'N/A')
        pkg.append((
            name,
            getattr(dist, "version", "N/A"),
            meta.get('Author', 'N/A'),
            meta.get('Summary', 'N/A'),
            dist.files,
            dist.locate_file(name) if name != 'N/A' else None,
        ))
    return pd.DataFrame(pkg, columns=['Package', 'Version', 'Author', 'Description', 'files', 'Location'])


def get_wifi_password_info_dataframe() -> pd.DataFrame:
    """
    Best-effort fetch remembered Wi-Fi SSIDs and passwords (Windows-only).
    On non-Windows platforms returns an empty DataFrame.
    """
    if not sys.platform.startswith("win"):
        return pd.DataFrame(columns=["AP", "password"])

    cmd = 'netsh wlan show profile key=clear '
    def _get_results(command: str, pattern: str):
        try:
            return re.findall(pattern, check_output(command, universal_newlines=True, errors="ignore"))
        except Exception:
            return []

    wifi_ssid = _get_results(cmd, r':\s(.+)')
    wifi_data = {i: _get_results(cmd + i, r'(?:关键内容|Content)\s+:\s(.+)') for i in wifi_ssid}
    df = pd.DataFrame(wifi_data).melt(var_name='AP', value_name='password')
    return df.dropna()
