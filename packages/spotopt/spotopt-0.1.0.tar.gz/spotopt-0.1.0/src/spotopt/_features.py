"""Feature engineering."""

from __future__ import annotations

import logging

import pandas as pd

_logger = logging.getLogger("spotopt")


def add_lags(
    df: pd.DataFrame,
    col_names: list[str],
    lag_days: int,
    *,
    drop_origin: bool = False,
) -> pd.DataFrame:
    """Adds a lagged column to the DataFrame.

    Args:
        df: The input DataFrame.
        col_names: The names of the columns to lag.
        lag_days: Lag in number of days.
        drop_origin: Whether to drop the original columns.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        msg = "The index must be a pandas DatetimeIndex."
        raise TypeError(msg)

    if df.index.tz is not None:
        msg = "The index should not have a time zone internally."
        raise ValueError(msg)

    if not isinstance(lag_days, int):
        msg = "lag_days needs to be an integer."
        raise TypeError(msg)

    if lag_days < 1:
        msg = "lag_days needs to be a positive integer."
        raise ValueError(msg)

    suffix = f"_lag_{lag_days}d"
    lagged = (
        df[col_names]
        .shift(freq=pd.Timedelta(days=lag_days))
        .rename(columns=lambda name: f"{name}{suffix}")
    )
    result = df.join(lagged)
    if drop_origin:
        result = result.drop(columns=col_names)
    return result


def add_weekday_dummies(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Adds dummy variables for weekdays.

    Args:
        df: The input DataFrame.
    """
    weekdays = df.index.weekday + 1
    dummies = pd.get_dummies(weekdays, prefix="weekday")
    # Ensure all expected columns are present.
    expected_cols = [f"weekday_{i}" for i in range(1, 8)]
    dummies = dummies.reindex(columns=expected_cols, fill_value=0)
    dummies.index = df.index
    dummies = dummies.astype(int)
    result = pd.concat([df, dummies], axis=1)
    return result[df.columns.tolist() + expected_cols]


def add_daily_min_max_obs(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add daily min. and max. values for the 'obs' column.

    Args:
        df: The input DataFrame.
    """
    grouped = df.groupby(df.index.date)["obs"]
    return df.assign(
        obs_min=grouped.transform("min"),
        obs_max=grouped.transform("max"),
    )
