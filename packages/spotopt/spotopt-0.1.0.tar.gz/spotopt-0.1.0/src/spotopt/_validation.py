"""Input validation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

import spotopt._constants as const
from spotopt._exceptions import (
    IndexNameError,
    MissingColumnsError,
    ShortTrainingDataError,
)

if TYPE_CHECKING:
    from spotopt._types import Frequency


_logger = logging.getLogger("spotopt")


def convert_and_validate(
    df: pd.DataFrame,
    frequency: Frequency,
) -> pd.DataFrame:
    """Convert and validate the DataFrame.

    Args:
        df: DataFrame to convert and validate.
        frequency: Frequency of the time series.

    """
    _check_columns(df)
    _check_index(df)
    df = df.sort_index()
    _check_delivery(df, frequency=frequency)

    return _cast_dtypes(df)


def check_min_training_data_length(
    df: pd.DataFrame,
    frequency: Frequency,
) -> None:
    """Check whether there is sufficient training data."""
    nr_days = df.shape[0] / (24 * 60 / frequency.value)
    if nr_days < const.MIN_NR_DAYS_TRAIN:
        msg = (
            "The training data should contain more "
            f"than {const.MIN_NR_DAYS_TRAIN} days."
        )
        raise ShortTrainingDataError(msg)


def _check_columns(df: pd.DataFrame) -> None:
    """Check if all required columns are present.

    Args:
        df: DataFrame to check.
    """
    missing_cols = set(const.COLS_REQ) - set(df.columns)
    if missing_cols:
        msg = f"Missing required columns: {missing_cols}"
        _logger.error(msg)
        raise MissingColumnsError(msg)


def _check_index(df: pd.DataFrame) -> None:
    """Check the index.

    Args:
        df: DataFrame to check.
    """
    if df.index.name != const.IDX_NAME:
        msg = f"Index must be named '{const.IDX_NAME}'."
        _logger.error(msg)
        raise IndexNameError(msg)
    if not isinstance(df.index, pd.DatetimeIndex):
        msg = "Index must be a pandas DatetimeIndex."
        _logger.error(msg)
        raise TypeError(msg)
    if str(df.index.tz) != const.TZ_STR:
        msg = f"Index must have time zone '{const.TZ_STR}'."
        _logger.error(msg)
        raise ValueError(msg)


def _cast_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast data types.

    Args:
        df: DataFrame to cast.
    """
    # Expected data types.
    base_dtypes = const.BASE_DTYPES
    additional_cols = set(df.columns) - set(base_dtypes.keys())
    cast_map = {
        **base_dtypes,
        **dict.fromkeys(additional_cols, float),
    }
    if additional_cols:
        _logger.info(
            "Casting additional columns to float: %s",
            additional_cols,
        )
    # Casting.
    return df.astype(cast_map)


def _check_delivery(
    df: pd.DataFrame,
    frequency: Frequency,
) -> None:
    """Check completeness of delivery time steps.

    Args:
        df: DataFrame to check.
        frequency: Frequency of the time series.

    """
    _check_gaps_in_delivery(df, frequency=frequency)
    _check_delivery_begin_and_end(df, frequency=frequency)


def _check_gaps_in_delivery(
    df: pd.DataFrame,
    frequency: Frequency,
) -> None:
    """Check if all delivery time steps are defined and sorted.

    Args:
        df: DataFrame to check.
        frequency: Frequency of the time series.

    """
    expected_dts = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=f"{frequency.value}min",
        tz=const.TZ_STR,
    )
    if not expected_dts.equals(df.index):
        msg = "Missing time steps."
        _logger.error(msg)
        raise ValueError(msg)


def _check_delivery_begin_and_end(
    df: pd.DataFrame,
    frequency: Frequency,
) -> None:
    """Check if first and last delivery time steps are correct.

    Args:
        df: DataFrame to check.
        frequency: Frequency of the time series.
    """
    # First delivery time step.
    begin = df.index.min().tz_convert(const.TZ_STR).floor(freq="D")

    if begin != df.index.min():
        msg = "First delivery time step must be at the start of a day."
        _logger.error(msg)
        raise ValueError(msg)
    # Last delivery time step.
    end = df.index.max().tz_convert(const.TZ_STR).ceil("D") - pd.DateOffset(
        minutes=frequency.value,
    )
    if end != df.index.max():
        msg = "Last delivery time step must be at the end of a day."
        _logger.error(msg)
        raise ValueError(msg)
