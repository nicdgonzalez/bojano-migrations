from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

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


class ClerkError(MigrationException):
    """Convert a Clerk JSON error response and into a Python exception."""

    def __init__(self, response: dict[str, Any], *args: object) -> None:
        assert "errors" in response.keys(), response.keys()
        errors: list[dict[str, Any]] = response["errors"]

        issues = []

        for error in errors:
            assert "message" in error.keys(), error.keys()
            message: str = error["message"]
            assert "code" in error.keys(), error.keys()
            code: str = error["code"]
            assert "meta" in error.keys(), error.keys()
            meta: dict[str, Any] = error["meta"]
            assert "param_names" in meta.keys()
            param_names: list[str] = meta["param_names"]

            issues.append(f"{message}: {', '.join(param_names)} ({code})")

        super().__init__(json.dumps(issues))
