"""Custom types."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Any

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor

import spotopt._constants as const
from spotopt._exceptions import (
    ForbiddenKeyWordError,
    ParameterCombinationError,
)

if TYPE_CHECKING:
    from pathlib import Path


class ModelName(StrEnum):
    """Enum for allowed models."""

    LASSO = "Lasso"
    GBR = "GBR"


class Frequency(IntEnum):
    """Enum for delivery frequency in minutes."""

    QH = 15
    H = 60


@dataclass(frozen=True, slots=True)
class SpotOptConfig:
    """SpotOpt configuration.

    Args:
        model_name: The name of the model to use.
        frequency: The frequency of the data in minutes.
        mdl_kwargs: Additional keyword arguments for the model.
        run_hyperparam_search: Whether to run hyperparameter search.
            Default is False.
        cv: Number of folds for cross-validation. Default is 4.

    """

    model_name: ModelName
    frequency: Frequency
    mdl_kwargs: dict[str, object] | None = None
    run_hyperparam_search: bool = False
    cv: int = const.DEFAULT_NR_CV

    def __post_init__(self) -> None:
        """Post-initialization checks."""
        if self.mdl_kwargs is not None:
            forbidden_keys: set = const.FORBIDDEN_KEYWORDS[
                self.model_name.value
            ]
            if forbidden_keys.issubset(self.mdl_kwargs.keys()):
                msg = (
                    f"Model {self.model_name} does not accept the following "
                    f"keywords: {forbidden_keys}"
                )
                raise ForbiddenKeyWordError(msg)

        if self.mdl_kwargs is not None and self.run_hyperparam_search:
            msg = (
                "Choose either model kwargs or hyperparameter search, "
                "not both."
            )
            raise ParameterCombinationError(msg)

    @classmethod
    def from_json(cls, path: Path) -> SpotOptConfig:
        """Create a SpotOptConfig from a json file."""
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpotOptConfig:
        """Create a SpotOptConfig from a dictionary."""
        config = dict(data)

        return cls(
            model_name=ModelName(config["model_name"]),
            frequency=Frequency(int(config["frequency"])),
            mdl_kwargs=config.get("mdl_kwargs"),
            run_hyperparam_search=config.get("run_hyperparam_search", False),
            cv=int(config.get("cv", const.DEFAULT_NR_CV)),
        )


LookAheadHour = int
LookAheadMinute = int
Quantile = int

QRs = dict[
    tuple[LookAheadHour, LookAheadMinute, Quantile],
    QuantileRegressor | GradientBoostingRegressor | None,
]
