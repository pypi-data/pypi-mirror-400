"""Constants."""

from typing import Final

TZ_STR: Final[str] = "CET"

IDX_NAME: Final[str] = "delivery"
COLS_REQ: Final[frozenset[str]] = frozenset(["obs", "fcast"])

QUANTILES: Final[list[int]] = [1, 5, 10, 25, 50, 75, 90, 95, 99]

BASE_DTYPES: dict = {
    "obs": float,
    "fcast": float,
}

MIN_NR_DAYS_TRAIN = 7

CV_PARAMS = {
    "Lasso": {"alpha": [0.001, 0.01, 0.1, 0.5]},
    "GBR": {
        "learning_rate": [0.1, 0.5],
        "n_estimators": [1000, 2000],
    },
}

FORBIDDEN_KEYWORDS = {
    "Lasso": {"quantile"},
    "GBR": {"loss", "alpha"},
}

DEFAULT_NR_CV = 3
