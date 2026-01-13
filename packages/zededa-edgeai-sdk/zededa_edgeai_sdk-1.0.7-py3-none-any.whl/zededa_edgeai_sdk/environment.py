"""Environment variable management for EdgeAI credentials and settings.

Provides utilities to apply authentication credentials to the shell
environment and sanitize sensitive data for display purposes.
"""

from __future__ import annotations

import functools
import os
from copy import deepcopy
from typing import Any, Callable, Dict, Optional, TypeVar

from .exceptions import AuthenticationError

__all__ = [
    "APPLIED_ENVIRONMENT_KEYS",
    "apply_environment",
    "clear_environment",
    "get_access_token",
    "get_credentials",
    "require_auth",
    "sanitize_credentials",
]

# Type variable for decorated authentication functions
AuthDecoratorFunc = TypeVar("AuthDecoratorFunc", bound=Callable[..., Any])

APPLIED_ENVIRONMENT_KEYS = [
    "EDGEAI_CURRENT_CATALOG",
    "EDGEAI_ACCESS_TOKEN",
    "MLFLOW_TRACKING_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "MLFLOW_S3_ENDPOINT_URL",
    "MLFLOW_TRACKING_URI",
    "MINIO_BUCKET",
    "EDGEAI_BACKEND_URL",
]


def apply_environment(
    credentials: Dict[str, str], catalog_id: str
) -> Dict[str, Optional[str]]:
    """Populate OS environment variables based on provided credentials.

    Parameters
    ----------
    credentials:
        Raw credential payload returned by the backend/login workflow.
    catalog_id:
        Catalog identifier for the current session.

    Returns
    -------
    dict
        Mapping of environment variable names to the values that were applied.
    """

    env_vars = {
        "EDGEAI_CURRENT_CATALOG": catalog_id,
        "EDGEAI_ACCESS_TOKEN": credentials.get("backend_jwt"),
        "MLFLOW_TRACKING_TOKEN": credentials.get("backend_jwt"),
        "AWS_ACCESS_KEY_ID": credentials.get("aws_access_key_id"),
        "AWS_SECRET_ACCESS_KEY": credentials.get("aws_secret_access_key"),
        "MLFLOW_S3_ENDPOINT_URL": credentials.get("endpoint_url"),
        "MLFLOW_TRACKING_URI": credentials.get("mlflow_tracking_uri"),
        "MINIO_BUCKET": credentials.get("bucket"),
        "EDGEAI_BACKEND_URL": credentials.get("service_url"),
    }

    for key, value in env_vars.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(value)

    return env_vars


def clear_environment() -> None:
    """Remove all SDK-specific environment variables from the current process."""

    for key in APPLIED_ENVIRONMENT_KEYS:
        os.environ.pop(key, None)


def get_credentials() -> Dict[str, Optional[str]]:
    """Retrieve credentials from environment variables.
    
    Returns a dictionary of credential values currently set in the environment.
    Used by commands and client to access authentication tokens.
    """
    return {
        "EDGEAI_CURRENT_CATALOG": os.environ.get("EDGEAI_CURRENT_CATALOG"),
        "EDGEAI_ACCESS_TOKEN": os.environ.get("EDGEAI_ACCESS_TOKEN"),
        "MLFLOW_TRACKING_TOKEN": os.environ.get("MLFLOW_TRACKING_TOKEN"),
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "MLFLOW_S3_ENDPOINT_URL": os.environ.get("MLFLOW_S3_ENDPOINT_URL"),
        "MLFLOW_TRACKING_URI": os.environ.get("MLFLOW_TRACKING_URI"),
        "MINIO_BUCKET": os.environ.get("MINIO_BUCKET"),
        "EDGEAI_BACKEND_URL": os.environ.get("EDGEAI_BACKEND_URL"),
    }


def get_access_token() -> str:
    """Retrieve the access token from environment, raising if not set.
    
    Returns the EDGEAI_ACCESS_TOKEN value from the environment.
    Raises AuthenticationError if the token is not set.
    
    Returns
    -------
    str
        The current access token
        
    Raises
    ------
    AuthenticationError
        If EDGEAI_ACCESS_TOKEN is not set in the environment
    """
    jwt = os.environ.get("EDGEAI_ACCESS_TOKEN")
    if not jwt:
        raise AuthenticationError(
            "Not logged in. Please run 'zededa-edgeai login' first."
        )
    return jwt


def sanitize_credentials(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of ``credentials`` with sensitive values obfuscated for display."""

    sanitized = deepcopy(credentials)

    sensitive_keys = {
        "backend_jwt",
        "access_token",
        "aws_access_key_id",
        "aws_secret_access_key",
        "secret_key",
        "token",
        "password",
    }

    for key in sensitive_keys:
        value = sanitized.get(key)
        if not value:
            continue
        value_str = str(value)
        sanitized[key] = _mask_string(value_str)

    env_payload = sanitized.get("environment")
    if isinstance(env_payload, dict):
        for key, value in list(env_payload.items()):
            if value is None:
                continue
            if any(sensitive in key.upper() for sensitive in ["TOKEN", "KEY", "SECRET"]):
                env_payload[key] = _mask_string(str(value))

    return sanitized


def _mask_string(value: str) -> str:
    """Mask sensitive string values for safe display in logs and output.
    
    Returns a masked version of the string showing only the first 6 and last 4
    characters for longer values, or '***' for shorter strings, preventing
    credential exposure while maintaining some identifiability.
    """
    if len(value) <= 10:
        return "***"
    return f"{value[:6]}...{value[-4:]}"


def require_auth(func: AuthDecoratorFunc) -> AuthDecoratorFunc:
    """Decorator that ensures EDGEAI_ACCESS_TOKEN is present before executing.

    Checks for the presence of EDGEAI_ACCESS_TOKEN in the environment and
    raises AuthenticationError if not found. The JWT token is passed to the
    decorated function as a keyword argument named 'jwt'.

    Parameters
    ----------
    func : Callable
        The function to wrap with authentication check
        
    Returns
    -------
    Callable
        Wrapped function that validates authentication before execution
        
    Raises
    ------
    AuthenticationError
        If EDGEAI_ACCESS_TOKEN is not set in the environment
        
    Example
    -------
    >>> @require_auth
    ... def my_function(*, jwt: str, **kwargs):
    ...     # jwt is automatically provided by the decorator
    ...     return do_something_with(jwt)
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        jwt = os.environ.get("EDGEAI_ACCESS_TOKEN")
        if not jwt:
            raise AuthenticationError(
                "Not logged in. Please run 'zededa-edgeai login' first."
            )
        kwargs["jwt"] = jwt
        return func(*args, **kwargs)
    return wrapper  # type: ignore[return-value]
