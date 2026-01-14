from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd


def _linregress(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """
    A small wrapper that prefers scipy.stats.linregress when available,
    and falls back to a numpy-based implementation.
    """
    try:
        from scipy.stats import linregress  # type: ignore
        res = linregress(x, y)
        return {
            "slope": float(res.slope),
            "intercept": float(res.intercept),
            "r_value": float(res.rvalue),
            "p_value": float(res.pvalue),
            "std_err": float(res.stderr),
        }
    except Exception:
        # Fallback: compute slope/intercept via least squares
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x.size < 2:
            return {"slope": np.nan, "intercept": np.nan, "r_value": np.nan, "p_value": np.nan, "std_err": np.nan}

        slope, intercept = np.polyfit(x, y, 1)
        y_hat = slope * x + intercept
        # r_value: Pearson correlation coefficient
        r = np.corrcoef(x, y)[0, 1] if np.std(x) > 0 and np.std(y) > 0 else np.nan
        # std_err: standard error of slope (approx)
        n = x.size
        ssx = np.sum((x - x.mean()) ** 2)
        sse = np.sum((y - y_hat) ** 2)
        stderr = np.sqrt((sse / (n - 2)) / ssx) if n > 2 and ssx > 0 else np.nan
        return {"slope": float(slope), "intercept": float(intercept), "r_value": float(r), "p_value": np.nan, "std_err": float(stderr)}


def get_reg_parameters(x_col: str, y_col: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get linear regression parameters between df[x_col] and df[y_col].

    Returns a dict containing:
      - slope, intercept, r_value, p_value, std_err

    Compatibility note:
      - also returns the legacy key 'std_err ' (with a trailing space)
        because the original project exposed that key.
    """
    x = df[x_col].to_numpy()
    y = df[y_col].to_numpy()
    res = _linregress(x, y)

    # Backward-compatible duplicate key
    res["std_err "] = res.get("std_err")
    return res
