import pandas as pd

from analytics.validation import (
    validate_factors,
    validate_regime,
    validate_returns,
    validate_weights,
)


def test_validate_weights_flags_negative_weight() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-31", "2026-01-31"],
            "symbol": ["AAA", "BBB"],
            "weight": [0.60, -0.10],
            "leg": ["long", "long"],
        }
    )
    issues = validate_weights(df)
    assert not issues.empty


def test_validate_returns_flags_nan() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-31", "2026-02-28"],
            "dynamic_gross": [0.01, None],
            "dynamic_net_20bp": [0.009, 0.005],
        }
    )
    issues = validate_returns(df)
    assert not issues.empty


def test_validate_factors_flags_bad_zero_run() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30"],
            "symbol": ["AAA", "AAA", "AAA", "AAA"],
            "gics_sector": ["Tech", "Tech", "Tech", "Tech"],
            "momentum_z": [0.0, 0.0, 0.0, 0.0],
            "composite_z": [0.0, 0.0, 0.0, 0.0],
        }
    )
    issues = validate_factors(df)
    assert not issues.empty


def test_validate_regime_flags_invalid_regime() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-01-31"],
            "vix_percentile": [1.2],
            "regime": ["weird"],
            "w_mom": [0.25],
            "w_val": [0.25],
            "w_qual": [0.25],
            "w_sent": [0.20],
        }
    )
    issues = validate_regime(df)
    assert not issues.empty