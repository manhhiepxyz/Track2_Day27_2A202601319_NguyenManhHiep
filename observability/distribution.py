from __future__ import annotations

from typing import Any, Iterable

import numpy as np


def detect_distribution_shift(
    current_values: Iterable[float],
    baseline_values: Iterable[float],
    *,
    ratio_threshold: float = 3.0,
) -> dict[str, Any]:
    """Very small starter detector using mean ratio.

    This is intentionally not a full distribution test. Students are encouraged
    to try KS test, PSI, quantile drift, robust ratios, or domain-specific checks.
    """
    cur = np.asarray(list(current_values), dtype=float)
    base = np.asarray(list(baseline_values), dtype=float)
    if cur.size == 0 or base.size == 0:
        return {"is_anomaly": False, "score": 0.0, "method": "median_ratio", "reason": "empty_input"}
    cur_median = float(np.median(cur))
    base_median = float(np.median(base))
    if base_median == 0:
        score = float("inf") if cur_median != 0 else 1.0
    else:
        score = max(abs(cur_median / base_median), abs(base_median / cur_median)) if cur_median != 0 else float("inf")
    return {
        "is_anomaly": bool(score >= ratio_threshold),
        "score": float(score),
        "method": "median_ratio",
        "reason": f"baseline_median={base_median:.3f}, current_median={cur_median:.3f}",
    }
