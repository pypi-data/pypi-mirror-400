"""Configuration service for accessing environment variables."""

import os
from typing import Optional, Type, TypeVar, cast

U = TypeVar("U")


class ConfigService:
    """Service for accessing environment variables with type conversion."""

    @staticmethod
    def get_string(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable as string."""
        return os.environ.get(key, default)

    @staticmethod
    def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
        """Get environment variable as integer."""
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    @staticmethod
    def get_float(key: str, default: Optional[float] = None) -> Optional[float]:
        """Get environment variable as float."""
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    @staticmethod
    def get_bool(key: str, default: Optional[bool] = None) -> Optional[bool]:
        """Get environment variable as boolean.

        'true', 'yes', '1', 'on' are considered True
        'false', 'no', '0', 'off' are considered False
        """
        value = os.environ.get(key)
        if value is None:
            return default

        value = value.lower()
        if value in ("true", "yes", "1", "on"):
            return True
        if value in ("false", "no", "0", "off"):
            return False
        return default

    @staticmethod
    def get_list(key: str, separator: str = ",", default: Optional[list[str]] = None) -> Optional[list[str]]:
        """Get environment variable as list of strings."""
        value = os.environ.get(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(separator)]

    @staticmethod
    def require(key: str) -> str:
        """Get required environment variable.

        Raises:
            ValueError: If environment variable is not set
        """
        value = os.environ.get(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    @staticmethod
    def require_as(key: str, type_: Type[U]) -> U:
        """Get required environment variable with type conversion.

        Args:
            key: Environment variable key
            type_: Type to convert to (int, float, bool)

        Raises:
            ValueError: If environment variable is not set or cannot be converted
        """
        value = ConfigService.require(key)
        try:
            if type_ == bool:  # noqa: E721 # pylint: disable=unidiomatic-typecheck
                result = ConfigService.get_bool(key)
                if result is None:
                    raise ValueError
                return cast(U, result)
            return type_(value)  # type: ignore
        except ValueError as exc:
            raise ValueError(f"Environment variable {key} cannot be converted to {type_.__name__}") from exc
