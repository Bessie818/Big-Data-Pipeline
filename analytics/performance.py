from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


PERIODS_PER_YEAR = 12


def annualized_return(returns: pd.Series, periods_per_year: int = PERIODS_PER_YEAR) -> float:
    returns = returns.dropna().astype(float)
    if returns.empty:
        return np.nan
    cumulative = (1.0 + returns).prod()
    n_periods = len(returns)
    return cumulative ** (periods_per_year / n_periods) - 1.0


def annualized_volatility(returns: pd.Series, periods_per_year: int = PERIODS_PER_YEAR) -> float:
    returns = returns.dropna().astype(float)
    if len(returns) < 2:
        return np.nan
    return returns.std(ddof=1) * np.sqrt(periods_per_year)


def sharpe_ratio(
    returns: pd.Series,
    rf: Optional[pd.Series] = None,
    periods_per_year: int = PERIODS_PER_YEAR,
) -> float:
    returns = returns.dropna().astype(float)
    if returns.empty:
        return np.nan

    if rf is None:
        excess = returns
    else:
        rf = rf.reindex(returns.index).fillna(0.0).astype(float)
        excess = returns - rf

    vol = annualized_volatility(excess, periods_per_year)
    if pd.isna(vol) or np.isclose(vol, 0.0):
        return np.nan
    return annualized_return(excess, periods_per_year) / vol


def cumulative_nav(returns: pd.Series, initial_nav: float = 1.0) -> pd.Series:
    returns = returns.dropna().astype(float)
    return initial_nav * (1.0 + returns).cumprod()


def drawdown_series(returns: pd.Series) -> pd.Series:
    nav = cumulative_nav(returns)
    running_max = nav.cummax()
    return nav / running_max - 1.0


def max_drawdown(returns: pd.Series) -> float:
    dd = drawdown_series(returns)
    if dd.empty:
        return np.nan
    return float(dd.min())


def hit_rate(returns: pd.Series) -> float:
    returns = returns.dropna().astype(float)
    if returns.empty:
        return np.nan
    return float((returns > 0).mean())


def compute_headline_metrics(
    returns_df: pd.DataFrame,
    rf_series: Optional[pd.Series] = None,
) -> pd.DataFrame:
    strategy_cols = [
        col
        for col in [
            "dynamic_gross",
            "dynamic_net_20bp",
            "static_net_20bp",
            "benchmark_ew",
        ]
        if col in returns_df.columns
    ]

    rows = []

    for col in strategy_cols:
        series = returns_df[col].dropna()
        rows.append(
            {
                "strategy": col,
                "annualized_return": annualized_return(series),
                "annualized_volatility": annualized_volatility(series),
                "sharpe_ratio": sharpe_ratio(series, rf_series),
                "max_drawdown": max_drawdown(series),
                "hit_rate": hit_rate(series),
            }
        )

    return pd.DataFrame(rows)