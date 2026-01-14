"""Utils."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from pytz.exceptions import AmbiguousTimeError, NonExistentTimeError

import spotopt._constants as const

if TYPE_CHECKING:
    from spotopt._types import Frequency


def _convert_delivery_to_cet(df: pd.DataFrame) -> pd.DataFrame:
    """Converts the delivery index to CET."""
    df.index = df.index.tz_convert(const.TZ_STR)
    return df


def _remove_delivery_tz(df: pd.DataFrame) -> pd.DataFrame:
    """Removes the timezone info from the delivery index."""
    df.index = df.index.tz_localize(None)
    return df


def account_for_dst(
    df: pd.DataFrame,
    frequency: Frequency,
) -> pd.DataFrame:
    """Account for daylight saving time (DST)."""
    df = _convert_delivery_to_cet(df)
    df = _remove_delivery_tz(df)
    # The hour 2 on the last Sunday of October, occurs twice. Here we
    # take the mean between those hours.
    df = df.resample(f"{frequency.value}min").mean()
    # This is the new index without any missing or double hours.
    complete_range = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=f"{frequency.value}min",
        tz=None,
    )
    df = df.reindex(complete_range)
    # Interpolating is only changing the data when there is data from
    # the last Sunday of March.
    return df.interpolate()


def convert_from_none_time_zone(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Convert a DataFrame from None timezone to CET.

    Args:
        df: DataFrame with a DatetimeIndex without timezone.
    """
    try:
        df.index = df.index.tz_localize(const.TZ_STR)
    except NonExistentTimeError:
        # The last Sunday of March has a only 23 hours.
        df.index = df.index.tz_localize(const.TZ_STR, nonexistent="NaT")
        return df[df.index.notna()]
    except AmbiguousTimeError:
        # The last Sunday of October has 25 hours.
        index_with_nat = df.index.tz_localize(const.TZ_STR, ambiguous="NaT")
        # With an hourly resolution, there will be only onw ambguous
        # row. With quarter hours, there will be four.
        rows = df.iloc[index_with_nat.isna(), :]
        df_longer = pd.concat([df, rows]).sort_index()

        index_target = pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq=df.index.freq,
            tz="CET",
        )
        df_longer.index = index_target
        return df_longer
    else:
        return df


def get_quantile_column_name(quantile: int) -> str:
    """Get the column name for a quantile.

    Args:
        quantile: Quantile value (e.g., 5, 25, 50, 75, 95).
    """
    return f"q_{str(quantile).zfill(3)}"
