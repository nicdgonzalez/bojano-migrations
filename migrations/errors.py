__all__ = (
    "MigrationException",
    "MissingEnvironmentVariableError",
)


class MigrationException(Exception):
    """The base class for all Migration-related errors"""


class MissingEnvironmentVariableError(MigrationException):
    """Thrown when an environment variable was expected, but not defined"""

    def __init__(self, key: str, *args: object) -> None:
        super().__init__(
            f"expected environment variable {key!r} to be defined"
        )
