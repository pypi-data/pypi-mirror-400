"""Custom spotopt exceptions."""


class SpotOptError(Exception):
    """Base spotopt exception."""


class SpotOptConfigError(SpotOptError):
    """Base exceptions for the spotopt configuration."""


class ParameterCombinationError(SpotOptConfigError):
    """Exception for keyword mismatch errors."""


class ForbiddenKeyWordError(SpotOptConfigError):
    """Exception for keyword mismatch errors."""


class SpotOptInputError(SpotOptError):
    """Base exceptions for the spotopt input."""


class MissingColumnsError(SpotOptInputError):
    """Exception for missing columns in the inputs."""


class IndexNameError(SpotOptInputError):
    """Exception for wrong index name."""


class ShortTrainingDataError(SpotOptInputError):
    """Exception for insufficient training data."""


class ModelNotFittedError(SpotOptError):
    """Exception for model not fitted error."""
