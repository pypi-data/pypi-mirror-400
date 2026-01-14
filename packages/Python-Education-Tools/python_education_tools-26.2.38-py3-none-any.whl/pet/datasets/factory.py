"""
Public API surface for PET datasets.

This module keeps backward compatibility with the textbook and earlier versions
by re-exporting stable function names from internal modules.
"""
from __future__ import annotations

from pathlib import Path

from ._paths import pet_home, default_textbook_dst
from ._constants import datafile_dict, sample_order

# Public: textbook / teaching assets
from ._textbook import download_textbook1

# Public: generators
from .generators import (
    gen_iid,
    gen_name,
    gen_int_series,
    gen_float_series,
    gen_date_time_series,
    gen_date_series,
    gen_time_series,
    gen_category_series,
    add_noise,
    generator,
    gen_sample_series,
    gen_sample_dataframe,
    gen_sample_dataframe_12,
    show_order_sample,
    gen_zmt_series,
)

# Public: loaders
from .loaders import get_datasets_list, load_data

# Public: filesystem tree helpers
from .tree import get_directory_info_dataframe, directory_to_str, list_subdirectories

# Public: system info
from .sysinfo import (
    get_pid_memory_info_dataframe,
    get_pid_info_dataframe,
    get_pid_network_info_dataframe,
    get_nic_info_series,
    get_local_packages_info_dataframe,
    get_wifi_password_info_dataframe,
)

# Public: statistics
from .stats import get_reg_parameters

# Textbook compatibility aliases (names used in chapters/exercises)
from ._compat import (
    directory_to_dataframe,
    directory_to_excel,
    pid_info_to_dataframe,
    pid_networkinfo_to_dataframe,
)

# Backward-compatible variable: destination on desktop (best effort)
pet_desktop = default_textbook_dst()

__all__ = [
    "pet_home",
    "pet_desktop",
    "datafile_dict",
    "sample_order",
    # textbook assets
    "download_textbook1",
    # generators
    "gen_iid",
    "gen_name",
    "gen_int_series",
    "gen_float_series",
    "gen_date_time_series",
    "gen_date_series",
    "gen_time_series",
    "gen_category_series",
    "add_noise",
    "generator",
    "gen_sample_series",
    "gen_sample_dataframe",
    "gen_sample_dataframe_12",
    "show_order_sample",
    "gen_zmt_series",
    # loaders
    "get_datasets_list",
    "load_data",
    # filesystem
    "get_directory_info_dataframe",
    "directory_to_str",
    "list_subdirectories",
    # system info
    "get_pid_memory_info_dataframe",
    "get_pid_info_dataframe",
    "get_pid_network_info_dataframe",
    "get_nic_info_series",
    "get_local_packages_info_dataframe",
    "get_wifi_password_info_dataframe",
    # stats
    "get_reg_parameters",
    # compatibility aliases
    "directory_to_dataframe",
    "directory_to_excel",
    "pid_info_to_dataframe",
    "pid_networkinfo_to_dataframe",
]
