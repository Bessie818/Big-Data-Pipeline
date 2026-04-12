from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


WEIGHT_TOL = 1e-6
ZSCORE_TOL = 0.10


def _issue(issue_type: str, message: str, **details: Any) -> dict[str, Any]:
    row = {"type": issue_type, "message": message}
    row.update(details)
    return row


def validate_weights(weights_df: pd.DataFrame) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []

    required = {"date", "symbol", "weight", "leg"}
    missing = required - set(weights_df.columns)
    if missing:
        return pd.DataFrame(
            [_issue("schema", "Missing required columns in weights_df", missing=sorted(missing))]
        )

    negative = weights_df[weights_df["weight"] < 0]
    for _, row in negative.iterrows():
        issues.append(
            _issue(
                "weights",
                "Negative weight found",
                date=row["date"],
                symbol=row["symbol"],
                leg=row["leg"],
                weight=float(row["weight"]),
            )
        )

    over_cap = weights_df[weights_df["weight"] > 0.05 + WEIGHT_TOL]
    for _, row in over_cap.iterrows():
        issues.append(
            _issue(
                "weights",
                "Weight above 5% cap",
                date=row["date"],
                symbol=row["symbol"],
                leg=row["leg"],
                weight=float(row["weight"]),
            )
        )

    leg_sums = weights_df.groupby(["date", "leg"])["weight"].sum().reset_index()
    for _, row in leg_sums.iterrows():
        if not np.isclose(row["weight"], 1.0, atol=WEIGHT_TOL):
            issues.append(
                _issue(
                    "weights",
                    "Per-date per-leg weights do not sum to 1",
                    date=row["date"],
                    leg=row["leg"],
                    weight_sum=float(row["weight"]),
                )
            )

    return pd.DataFrame(issues)


def validate_returns(returns_df: pd.DataFrame) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []

    for col in returns_df.columns:
        if col == "date":
            continue

        if returns_df[col].isna().any():
            issues.append(_issue("returns", f"NaN returns found in column {col}"))

        if (returns_df[col].abs() > 0.50).any():
            bad_dates = returns_df.loc[returns_df[col].abs() > 0.50, "date"].astype(str).tolist()
            issues.append(
                _issue(
                    "returns",
                    f"Extreme return above 50% found in column {col}",
                    dates=bad_dates,
                )
            )

    if {"dynamic_gross", "dynamic_net_20bp"}.issubset(returns_df.columns):
        bad = returns_df["dynamic_gross"] < returns_df["dynamic_net_20bp"]
        if bad.any():
            issues.append(_issue("returns", "dynamic_gross is below dynamic_net_20bp on some dates"))

    return pd.DataFrame(issues)


def validate_factors(scores_df: pd.DataFrame) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []

    required = {"date", "symbol", "gics_sector", "composite_z"}
    missing = required - set(scores_df.columns)
    if missing:
        return pd.DataFrame(
            [_issue("schema", "Missing required columns in scores_df", missing=sorted(missing))]
        )

    factor_cols = [col for col in scores_df.columns if col.endswith("_z")]

    grouped = scores_df.groupby(["date", "gics_sector"])
    for (date, sector), group in grouped:
        if len(group) < 5:
            continue

        for col in factor_cols:
            mean_val = group[col].mean()
            std_val = group[col].std(ddof=1)

            if pd.notna(mean_val) and abs(mean_val) > ZSCORE_TOL:
                issues.append(
                    _issue(
                        "factors",
                        "Sector z-score mean too far from 0",
                        date=date,
                        sector=sector,
                        factor=col,
                        mean=float(mean_val),
                    )
                )

            if pd.notna(std_val) and abs(std_val - 1.0) > ZSCORE_TOL:
                issues.append(
                    _issue(
                        "factors",
                        "Sector z-score std too far from 1",
                        date=date,
                        sector=sector,
                        factor=col,
                        std=float(std_val),
                    )
                )

    scores_df = scores_df.sort_values(["symbol", "date"]).copy()
    zero_mask = scores_df["composite_z"].fillna(np.nan).eq(0.0)
    scores_df["zero_run"] = zero_mask.groupby(scores_df["symbol"]).transform(
        lambda s: s.groupby((s != s.shift()).cumsum()).cumcount() + 1
    )
    bad = scores_df.loc[zero_mask & (scores_df["zero_run"] > 3), ["date", "symbol", "composite_z"]]

    for _, row in bad.iterrows():
        issues.append(
            _issue(
                "factors",
                "Composite z-score equals 0 for more than 3 consecutive periods",
                date=row["date"],
                symbol=row["symbol"],
                composite_z=float(row["composite_z"]),
            )
        )

    return pd.DataFrame(issues)


def validate_regime(regime_df: pd.DataFrame) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []

    if "vix_percentile" in regime_df.columns:
        bad = regime_df[~regime_df["vix_percentile"].between(0, 1, inclusive="both")]
        for _, row in bad.iterrows():
            issues.append(
                _issue(
                    "regime",
                    "VIX percentile out of range",
                    date=row.get("date"),
                    vix_percentile=row.get("vix_percentile"),
                )
            )

    if "regime" in regime_df.columns:
        allowed = {"low", "normal", "high"}
        bad = regime_df[~regime_df["regime"].isin(allowed)]
        for _, row in bad.iterrows():
            issues.append(
                _issue(
                    "regime",
                    "Invalid regime label",
                    date=row.get("date"),
                    regime=row.get("regime"),
                )
            )

    weight_cols = [col for col in regime_df.columns if col.startswith("w_")]
    if weight_cols:
        sums = regime_df[weight_cols].sum(axis=1)
        bad_sum = ~np.isclose(sums, 1.0, atol=WEIGHT_TOL)
        for idx in regime_df.index[bad_sum]:
            issues.append(
                _issue(
                    "regime",
                    "Dynamic factor weights do not sum to 1",
                    date=regime_df.loc[idx, "date"],
                    weight_sum=float(sums.loc[idx]),
                )
            )

        bad_neg = (regime_df[weight_cols] < 0).any(axis=1)
        for idx in regime_df.index[bad_neg]:
            issues.append(
                _issue(
                    "regime",
                    "Negative dynamic factor weight found",
                    date=regime_df.loc[idx, "date"],
                )
            )

    return pd.DataFrame(issues)