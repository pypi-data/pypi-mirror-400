"""spotopt model."""

from __future__ import annotations

import itertools
import logging

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor
from sklearn.model_selection import GridSearchCV

import spotopt._constants as const
import spotopt._features as features
import spotopt._utils as utils
import spotopt._validation as validation
from spotopt._exceptions import ModelNotFittedError
from spotopt._types import Frequency, QRs, SpotOptConfig

_logger = logging.getLogger("spotopt")


def _prepare_data(df: pd.DataFrame, frequency: Frequency) -> pd.DataFrame:
    """Prepare the model for training or prediction.

    Args:
        df: DataFrame with the data.
        frequency: Frequency of the data.
    """
    df = utils.account_for_dst(df, frequency)
    df = features.add_lags(df, ["obs"], lag_days=1)
    df = features.add_daily_min_max_obs(df)
    df = features.add_lags(
        df,
        ["obs_min", "obs_max"],
        lag_days=1,
        drop_origin=True,
    )
    # Remove null values that come from adding lags.
    df = df.dropna(subset=[c for c in df.columns if "lag" in c])
    df = features.add_weekday_dummies(df)
    # Add look-ahead identifiers.
    return df.assign(hour=df.index.hour, minute=df.index.minute)


def _fit(
    df: pd.DataFrame,
    config: SpotOptConfig,
) -> tuple[list[str], QRs]:
    """Fit models.

    Args:
        df: DataFrame for fitting.
        config: spotopt configuration.
    """
    df = validation.convert_and_validate(df, frequency=config.frequency)
    validation.check_min_training_data_length(df, frequency=config.frequency)
    df = _prepare_data(df, frequency=config.frequency)
    look_ahead_times = df[["hour", "minute"]].drop_duplicates().to_numpy()
    fit_cols = [c for c in df.columns if c not in {"obs", "hour", "minute"}]
    keys = [
        (int(h), int(m), int(q))
        for (h, m), q in itertools.product(look_ahead_times, const.QUANTILES)
    ]
    mdl_kwargs = config.mdl_kwargs or {}
    qrs: QRs = dict.fromkeys(keys)
    for h, m, q in qrs:
        X = df.query(f"hour=={h} and minute=={m}")[fit_cols].to_numpy()  # noqa: N806
        y = df.query(f"hour=={h} and minute=={m}")["obs"].to_numpy().ravel()
        # Fitting.
        match config.model_name:
            case "Lasso":
                mdl = QuantileRegressor(
                    quantile=q / 100,
                    **mdl_kwargs,
                )
            case "GBR":
                mdl = GradientBoostingRegressor(
                    loss="quantile",
                    alpha=q / 100,
                    **mdl_kwargs,
                )
        if config.run_hyperparam_search:
            cv = GridSearchCV(
                mdl,
                const.CV_PARAMS[config.model_name.value],
                refit=True,
                cv=config.cv,
            )
            cv.fit(X, y)
            qrs[(h, m, q)] = cv.best_estimator_
        else:
            qrs[(h, m, q)] = mdl.fit(X, y)

    return fit_cols, qrs


def _predict(
    df: pd.DataFrame,
    fit_cols: list[str],
    qrs: QRs,
    config: SpotOptConfig,
) -> pd.DataFrame:
    """Predict using the fitted quantile regressors."""
    df = validation.convert_and_validate(df, frequency=config.frequency)
    df = _prepare_data(df, frequency=config.frequency)
    predictions = pd.DataFrame(
        index=df.index,
        columns=pd.Index(
            [utils.get_quantile_column_name(c) for c in const.QUANTILES],
        ),
    )
    delivery_masks = {
        (h, m): (predictions.index.hour == h) & (predictions.index.minute == m)
        for h, m in {key[:2] for key in qrs}
    }
    for (h, m, q), mdl in qrs.items():
        prediction = mdl.predict(
            df.query(f"hour=={h} and minute=={m}")[fit_cols].to_numpy(),
        )
        predictions.loc[
            delivery_masks[(h, m)],
            utils.get_quantile_column_name(q),
        ] = prediction
    # The delivery index has no time zone yet, so we need to set it.
    return utils.convert_from_none_time_zone(predictions)


class SpotOptModel:
    """spotopt model."""

    def __init__(self, config: SpotOptConfig) -> None:
        """Initialize the model."""
        self.config = config
        self.ran_fitting = False

    @property
    def config(self) -> SpotOptConfig:
        """Get configuration."""
        return self._config

    @config.setter
    def config(self, value: SpotOptConfig) -> None:
        """Set configuration."""
        if not isinstance(value, SpotOptConfig):
            msg = "Configuration must be an instance of SpotOptConfig."
            raise TypeError(msg)
        _logger.info("Setting model to: %s", value.model_name.value)
        if value.mdl_kwargs is not None:
            _logger.info("Keyword arguments found in the configuration.")
        if value.run_hyperparam_search:
            _logger.info(
                (
                    "Hyperparameter search is activated with %s-fold "
                    "cross-validation"
                ),
                value.cv,
            )
        self._config = value

    @property
    def fit_cols(self) -> list[str]:
        """Get columns used for fitting."""
        return self._fit_cols

    @fit_cols.setter
    def fit_cols(self, value: list[str]) -> None:
        """Set columns used for fitting."""
        if not isinstance(value, list) or not all(
            isinstance(c, str) for c in value
        ):
            msg = "fit_cols must be a list of strings."
            raise TypeError(msg)
        self._fit_cols = value

    def fit(self, df: pd.DataFrame) -> None:
        """Fit the quantil models."""
        _logger.info("Start fitting.")
        self.fit_cols, self.qrs = _fit(df, self.config)
        self.ran_fitting = True

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict using the fitted quantil models."""
        if not self.ran_fitting:
            msg = "Call .fit() before .predict()."
            raise ModelNotFittedError(msg)
        _logger.info("Start prediction.")
        return _predict(df, self.fit_cols, self.qrs, self.config)
