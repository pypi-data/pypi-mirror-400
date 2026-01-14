"""spotopt package initialization."""

import logging

from spotopt._logging import configure_logging
from spotopt._types import Frequency, ModelName, SpotOptConfig
from spotopt.model import SpotOptModel

__version__ = "0.1.0"

logging.getLogger("spotopt").addHandler(logging.NullHandler())

__all__ = [
    "Frequency",
    "ModelName",
    "SpotOptConfig",
    "SpotOptModel",
    "__version__",
    "configure_logging",
]
