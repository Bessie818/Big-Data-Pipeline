import numpy as np
import pandas as pd

from analytics.performance import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    sharpe_ratio,
)


def test_annualized_return_constant_series() -> None:
    returns = pd.Series([0.01] * 12)
    result = annualized_return(returns)
    expected = (1.01**12) - 1.0
    assert np.isclose(result, expected)


def test_annualized_volatility_zero_for_constant_series() -> None:
    returns = pd.Series([0.01] * 12)
    result = annualized_volatility(returns)
    assert np.isclose(result, 0.0)


def test_max_drawdown_negative_when_loss_occurs() -> None:
    returns = pd.Series([0.10, -0.20, 0.05])
    result = max_drawdown(returns)
    assert result < 0


def test_sharpe_ratio_nan_when_zero_volatility() -> None:
    returns = pd.Series([0.01] * 12)
    result = sharpe_ratio(returns)
    assert np.isnan(result)