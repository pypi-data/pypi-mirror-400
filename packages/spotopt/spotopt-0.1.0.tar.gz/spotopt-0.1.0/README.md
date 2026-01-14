# spotopt

With spotopt, you can turn your determinstic day-ahead forecasts into probabilistic forecasts. spotopt builds on pandas and scikit-learn's quantile regression models (Lasso and Gradient Boosting).

## Features
- Automized feature engineering: lagged observations, lagged daily min/max observations, and weekday dummies.
- Flexible input handling: Additional explanatory variables are allowed.
- Day light saving time (DST) handling for seamless time-index conversions.
- Configurable cross-validation (`cv`) and hyperparameter search.
- Configuration loaders (`SpotOptConfig.from_dict` / `.from_json`) with strict typing.


## Installation
```
pip install spotopt
```

## Usage Example

### Lasso quantile regression for hourly data with defined model hyperparameters

```python
from spotopt import Frequency, SpotOptConfig, ModelName, SpotOptModel

config = SpotOptConfig(
    model_name=ModelName.LASSO,
    frequency=Frequency.H,
    mdl_kwargs={"alpha": 0.1},
)

model = SpotOptModel(config)
model.fit(df_fit)
predictions = model.predict(df_predict)
```

### Gradient boosting model for quarter-hourly data with hyperparameter search

```python
from spotopt import Frequency, SpotOptConfig, ModelName, SpotOptModel

config = SpotOptConfig(
    model_name=ModelName.GBR,
    frequency=Frequency.QH,
    run_hyperparam_search=True,
)

model = SpotOptModel(config)
model.fit(df_fit)
predictions = model.predict(df_predict)
```


## Hyperparameter search

Hyperparameters currently implemented in the hyperparamter search:
 - **Lasso**: `alpha`
 - **Gradient Boosting**: `learning_rate`, `n_estimators`


## Current limitations

* Only CE(S)T supported.
* Only one day-ahead supported, not several days aheads.
* Fixed quantiles: 1, 5, 10, 25, 50, 75, 90, 95, 99 %.

## Data Requirements
- Index name must be `delivery`, timezone `CET`, and composed of contiguous steps at the configured frequency (`Frequency.H` = 60 min, `Frequency.QH` = 15 min).
- Required columns: `obs` (historical outcomes) and `fcast` (determinstic forecast). Additional columns are allowed and will be cast to `float`.


## Contributing

Contributions are welcome!

Developer tooling reference:
- [`pytest`](https://docs.pytest.org/) for testing.
- [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) for analyzing test coverage.
- [`ruff`](https://docs.astral.sh/ruff/) for linting & formatting.
- [`ty`](https://docs.astral.sh/ty/) for type checking.
- [`uv`](https://docs.astral.sh/uv/) for project and dependency management.
