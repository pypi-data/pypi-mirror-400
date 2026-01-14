"""Implements authentication methods for the HTTP client."""

import json
import logging
import time
from enum import Enum

import requests
from requests.auth import HTTPBasicAuth

from aas_http_client.classes.Configuration.config_classes import OAuth
from aas_http_client.utilities.http_helper import log_response

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Defines authentication methods.

    :param Enum: Base class for enumerations
    """

    No = 1
    basic_auth = 2
    o_auth = 3
    bearer = 4


class TokenData:
    """Holds token data."""

    def __init__(self, access_token: str, token_type: str, token_expiry: float):
        """Initializes the TokenData with the given parameters."""
        self.access_token: str = access_token
        self.token_type: str = token_type
        self.token_expiry: float = token_expiry


def get_token(o_auth_configuration: OAuth) -> TokenData | None:
    """Get token based on the provided OAuth configuration.

    :param auth_configuration: Authentication configuration
    :return: Access token or None if an error occurred
    """
    if o_auth_configuration.grant_type == "password":
        token = get_token_by_password(
            o_auth_configuration.token_url,
            o_auth_configuration.client_id,
            o_auth_configuration.get_client_secret(),
        )

    elif o_auth_configuration.is_active() and o_auth_configuration.grant_type == "client_credentials":
        token = get_token_by_basic_auth(
            o_auth_configuration.token_url,
            o_auth_configuration.client_id,
            o_auth_configuration.get_client_secret(),
        )

    return token


def get_token_by_basic_auth(endpoint: str, username: str, password: str, timeout=200) -> TokenData | None:
    """Get token from a specific authentication service provider by basic authentication.

    :param endpoint: Get token endpoint for the authentication service provider
    :param username: Username for the authentication service provider
    :param password: Password for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    data = {"grant_type": "client_credentials"}

    auth = HTTPBasicAuth(username, password)

    return _get_token_from_endpoint(endpoint, data, auth, timeout)


def get_token_by_password(endpoint: str, username: str, password: str, timeout=200) -> TokenData | None:
    """Get token from a specific authentication service provider by username and password.

    :param endpoint: Get token endpoint for the authentication service provider
    :param username: Username for the authentication service provider
    :param password: Password for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    data = {"grant_type": "password", "username": username, "password": password}

    return _get_token_from_endpoint(endpoint, data, None, timeout)


def _get_token_from_endpoint(endpoint: str, data: dict[str, str], auth: HTTPBasicAuth | None = None, timeout: int = 200) -> TokenData | None:
    """Get token from a specific authentication service provider.

    :param endpoint: Get token endpoint for the authentication service provider
    :param data: Data for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    try:
        response = requests.post(endpoint, auth=auth, data=data, timeout=timeout)
        logger.debug(f"Call REST API url '{response.url}'")

        if response.status_code != 200:
            log_response(response)
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error call REST API: {e}")
        return None

    content = response.content.decode("utf-8")

    if not content:
        logger.error("No content in token response")
        return None

    data = json.loads(content)

    if not data:
        logger.error("No data in token response")
        return None

    access_token: str = data.get("access_token", "").strip()
    expires_in: int = data.get("expires_in", 0)
    if not access_token or not expires_in:
        logger.error("Invalid token data in response")
        return None

    token_type: str = data.get("token_type", "").strip()
    now: float = time.time()
    token_expiry: float = now + int(expires_in) - 60  # Subtract 60 seconds as buffer

    return TokenData(access_token=access_token, token_type=token_type, token_expiry=token_expiry)
