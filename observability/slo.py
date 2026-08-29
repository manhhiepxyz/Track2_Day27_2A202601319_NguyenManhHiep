from __future__ import annotations

from typing import Any


def calculate_slo(target: float, bad_events: int, total_events: int) -> dict[str, Any]:
    if not 0 < target < 1:
        raise ValueError("target must be between 0 and 1 (exclusive)")
    if bad_events < 0 or total_events < 0 or bad_events > total_events:
        raise ValueError("invalid event counts")
    allowed_bad_rate = 1.0 - target
    if total_events == 0:
        return {
            "target": target,
            "actual_bad_rate": 0.0,
            "allowed_bad_rate": allowed_bad_rate,
            "burn_rate": 0.0,
            "remaining_error_budget_fraction": 1.0,
            "breached": False,
        }
    actual_bad_rate = bad_events / total_events
    burn_rate = actual_bad_rate / allowed_bad_rate
    consumed_fraction = min(1.0, actual_bad_rate / allowed_bad_rate)
    return {
        "target": target,
        "actual_bad_rate": actual_bad_rate,
        "allowed_bad_rate": allowed_bad_rate,
        "burn_rate": burn_rate,
        "remaining_error_budget_fraction": max(0.0, 1.0 - consumed_fraction),
        "breached": bool(actual_bad_rate > allowed_bad_rate),
    }


def evaluate_multiwindow_burn(
    *,
    short_window_burn: float,
    long_window_burn: float,
    policy: str = "starter",
) -> dict[str, Any]:
    """Multi-window burn-rate policy.
    
    Alerts if both short window (e.g. 5m) and long window (e.g. 1h) 
    burn rates exceed the threshold, indicating sustained fast burn.
    """
    burn_threshold = 1.0  # Alert if both windows are burning budget faster than allowed
    
    is_sustained = (short_window_burn > burn_threshold) and (long_window_burn > burn_threshold)
    is_transient = (short_window_burn > burn_threshold) and (long_window_burn <= burn_threshold)
    
    page = is_sustained
    severity = "critical" if is_sustained else "warning" if is_transient else "info"
    reason = "sustained_burn" if is_sustained else "transient_spike" if is_transient else "normal"
    
    return {
        "page": page,
        "severity": severity,
        "reason": reason,
        "short_window_burn": short_window_burn,
        "long_window_burn": long_window_burn,
    }
