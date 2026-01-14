"""Implements shared configuration utilities."""

import functools
import os
from typing import NotRequired, TypedDict, Unpack, Callable, Any

from attr import define

from astro_observe_sdk.constants import (
    ASTRO_API_BASE_URL_ENV_VAR,
    ASTRO_ORGANIZATION_ID_ENV_VAR,
    OBSERVE_API_TOKEN_ENV_VAR,
    OPENLINEAGE_URL_ENV_VAR,
)


class TypedCommonConfig(TypedDict):
    org_id: NotRequired[str | None]
    token: NotRequired[str | None]
    base_url: NotRequired[str | None]


@define
class AstroApiConfig:
    org_id: str
    token: str
    base_url: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Astro-Client-Identifier": "astro-observe-sdk",
        }

    @property
    def private_org_base_url(self) -> str:
        return f"{self.base_url}/private/v1alpha1/organizations/{self.org_id}"


def guess_api_url(provided_url: str | None) -> str:
    """
    Guesses the API URL based on the provided URL.
    """
    if provided_url:
        return provided_url

    from_env = os.getenv(ASTRO_API_BASE_URL_ENV_VAR)
    if from_env:
        return from_env

    # o11y url is in the format of https://o11y.astronomer{-dev,-stage}.io
    # so we can just replace "o11y" with "api" to get the API URL
    o11y_url = os.getenv(OPENLINEAGE_URL_ENV_VAR)
    if o11y_url:
        return o11y_url.replace("o11y", "api")

    # assume we're running in production
    return "https://api.astronomer.io"


def get_config(**kwargs: Unpack[TypedCommonConfig]) -> AstroApiConfig:
    """
    Pulls configuration from the arguments passed and defaults to
    environment variables that automatically get set on Astro.
    """
    org_id = kwargs.get("org_id", os.getenv(ASTRO_ORGANIZATION_ID_ENV_VAR))
    token = kwargs.get("token", os.getenv(OBSERVE_API_TOKEN_ENV_VAR))
    base_url = guess_api_url(kwargs.get("base_url"))

    if not org_id:
        raise ValueError(
            "Organization ID not provided. "
            f"Please provide one or set the {ASTRO_ORGANIZATION_ID_ENV_VAR} environment variable."
        )

    if not token:
        raise ValueError(
            "API token not provided. "
            f"Please provide one or set the {OBSERVE_API_TOKEN_ENV_VAR} environment variable."
        )

    return AstroApiConfig(org_id=org_id, token=token, base_url=base_url)


def supply_config(func: Callable) -> Callable:
    """
    Decorator to automatically supply the config to a function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Unpack[TypedCommonConfig]) -> Callable:
        config = get_config(**kwargs)
        if "config" not in kwargs:
            kwargs["config"] = config  # type: ignore
        return func(*args, **kwargs)  # type: ignore

    return wrapper
