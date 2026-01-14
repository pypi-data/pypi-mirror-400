"""Client for HTTP API communication with AAS server."""

import json
import logging
import time
from pathlib import Path

import requests
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from requests import Session
from requests.auth import HTTPBasicAuth

from aas_http_client.classes.client.implementations import (
    AuthMethod,
    ExperimentalImplementation,
    ShellImplementation,
    ShellRegistryImplementation,
    SmImplementation,
    SubmodelRegistryImplementation,
    TokenData,
    get_token,
)
from aas_http_client.classes.Configuration.config_classes import AuthenticationConfig
from aas_http_client.utilities.http_helper import (
    STATUS_CODE_200,
)

logger = logging.getLogger(__name__)


class AasHttpClient(BaseModel):
    """Represents a AasHttpClient to communicate with a REST API."""

    base_url: str = Field(..., alias="BaseUrl", description="Base URL of the AAS server.")
    auth_settings: AuthenticationConfig = Field(
        default_factory=AuthenticationConfig, alias="AuthenticationSettings", description="Authentication settings for the AAS server."
    )
    https_proxy: str | None = Field(default=None, alias="HttpsProxy", description="HTTPS proxy URL.")
    http_proxy: str | None = Field(default=None, alias="HttpProxy", description="HTTP proxy URL.")
    time_out: int = Field(default=200, alias="TimeOut", description="Timeout for HTTP requests.")
    connection_time_out: int = Field(default=100, alias="ConnectionTimeOut", description="Connection timeout for HTTP requests.")
    ssl_verify: bool = Field(default=True, alias="SslVerify", description="Enable SSL verification.")
    trust_env: bool = Field(default=True, alias="TrustEnv", description="Trust environment variables.")
    _session: Session = PrivateAttr(default=None)
    _auth_method: AuthMethod = PrivateAttr(default=AuthMethod.basic_auth)
    encoded_ids: bool = Field(default=True, alias="EncodedIds", description="If enabled, all IDs used in API requests have to be base64-encoded.")
    shell: ShellImplementation = Field(default=None)
    submodel: SmImplementation = Field(default=None)
    shell_registry: ShellRegistryImplementation = Field(default=None)
    experimental: ExperimentalImplementation = Field(default=None)
    submodel_registry: SubmodelRegistryImplementation = Field(default=None)
    _cached_token: TokenData | None = PrivateAttr(default=None)

    def initialize(self):
        """Initialize the AasHttpClient with the given URL, username and password."""
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self._session = requests.Session()

        self._handle_auth_method()

        self._session.verify = self.ssl_verify
        self._session.trust_env = self.trust_env

        if self.https_proxy:
            self._session.proxies.update({"https": self.https_proxy})
        if self.http_proxy:
            self._session.proxies.update({"http": self.http_proxy})

        self._session.headers.update(
            {
                "Accept": "*/*",
                "User-Agent": "python-requests/2.32.5",
                "Connection": "close",
            }
        )

        self.shell = ShellImplementation(self)
        self.submodel = SmImplementation(self)
        self.shell_registry = ShellRegistryImplementation(self)
        self.submodel_registry = SubmodelRegistryImplementation(self)
        self.experimental = ExperimentalImplementation(self)

    def get_session(self) -> Session:
        """Get the HTTP session used by the client.

        :return: The requests.Session object used for HTTP communication
        """
        return self._session

    def _handle_auth_method(self):
        """Handles the authentication method based on the provided settings."""
        if self.auth_settings.bearer_auth.is_active():
            self._auth_method = AuthMethod.bearer
            logger.info("Authentication method: Bearer Token")
            self._session.headers.update({"Authorization": f"Bearer {self.auth_settings.bearer_auth.get_token()}"})
        elif self.auth_settings.o_auth.is_active():
            self._auth_method = AuthMethod.o_auth
            logger.info(
                f"Authentication method: OAuth | '{self.auth_settings.o_auth.client_id}' | '{self.auth_settings.o_auth.token_url}' | '{self.auth_settings.o_auth.grant_type}'"
            )
        elif self.auth_settings.basic_auth.is_active():
            self._auth_method = AuthMethod.basic_auth
            logger.info(f"Authentication method: Basic Auth | '{self.auth_settings.basic_auth.username}'")
            self._session.auth = HTTPBasicAuth(self.auth_settings.basic_auth.username, self.auth_settings.basic_auth.get_password())
        else:
            self._auth_method = AuthMethod.No
            logger.info("Authentication method: No Authentication")

    def get_root(self) -> dict | None:
        """Get the root endpoint of the AAS server API to test connectivity.

        This method calls the '/shells' endpoint to verify that the AAS server is accessible
        and responding. It automatically handles authentication token setup if service
        provider authentication is configured.

        :return: Response data as a dictionary containing shell information, or None if an error occurred
        """
        urls: list[str] = []
        urls.append(f"{self.base_url}/shells")
        urls.append(f"{self.base_url}/submodels")
        urls.append(f"{self.base_url}/shell-descriptors")
        urls.append(f"{self.base_url}/submodel-descriptors")

        self.set_token()

        for url in urls:
            logger.debug(f"Testing connectivity with URL: {url}")
            try:
                response = self._session.get(url, timeout=10)
                logger.debug(f"Call REST API url '{response.url}'")

                if response.status_code == STATUS_CODE_200:
                    content = response.content.decode("utf-8")
                    return json.loads(content)

            except requests.exceptions.RequestException as e:
                logger.debug(f"Error call REST API: {e}")

        return None

    def set_token(self) -> str | None:
        """Set authentication token in session headers based on configured authentication method.

        :return: The access token if set, otherwise None
        """
        if self._auth_method != AuthMethod.o_auth:
            return None

        now = time.time()
        # Check if cached token exists and is not expired
        if self._cached_token and self._cached_token.token_expiry > now:
            return self._cached_token.access_token

        # Obtain new token
        token_data = get_token(self.auth_settings.o_auth)

        if token_data and token_data.access_token:
            # Cache the token data
            self._cached_token = token_data
            # Update session headers with the new token
            self._session.headers.update({"Authorization": f"Bearer {self._cached_token.access_token}"})
            return self._cached_token.access_token

        return None


def create_client_by_url(  # noqa: PLR0913
    base_url: str,
    basic_auth_username: str = "",
    basic_auth_password: str = "",
    o_auth_client_id: str = "",
    o_auth_client_secret: str = "",
    o_auth_token_url: str = "",
    bearer_auth_token: str = "",
    http_proxy: str = "",
    https_proxy: str = "",
    time_out: int = 200,
    connection_time_out: int = 60,
    ssl_verify: str = True,  # noqa: FBT002
    trust_env: bool = True,  # noqa: FBT001, FBT002
    encoded_ids: bool = True,  # noqa: FBT001, FBT002
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from the given parameters.

    :param base_url: Base URL of the AAS server, e.g. "http://basyx_python_server:80/"
    :param basic_auth_username: Username for the AAS server basic authentication, defaults to ""
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_id: Client ID for OAuth authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param o_auth_token_url: Token URL for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :param http_proxy: HTTP proxy URL, defaults to ""
    :param https_proxy: HTTPS proxy URL, defaults to ""
    :param time_out: Timeout for the API calls, defaults to 200
    :param connection_time_out: Timeout for the connection to the API, defaults to 60
    :param ssl_verify: Whether to verify SSL certificates, defaults to True
    :param trust_env: Whether to trust environment variables for proxy settings, defaults to True
    :param encoded_ids: If enabled, all IDs used in API requests have to be base64-encoded
    :return: An instance of AasHttpClient initialized with the provided parameters or None if connection fails
    """
    logger.info(f"Create AAS server http client from URL '{base_url}'.")
    config_dict: dict[str, str] = {}
    config_dict["BaseUrl"] = base_url
    config_dict["HttpProxy"] = http_proxy
    config_dict["HttpsProxy"] = https_proxy
    config_dict["TimeOut"] = time_out
    config_dict["ConnectionTimeOut"] = connection_time_out
    config_dict["SslVerify"] = ssl_verify
    config_dict["TrustEnv"] = trust_env
    config_dict["EncodedIds"] = encoded_ids

    config_dict["AuthenticationSettings"] = {
        "BasicAuth": {"Username": basic_auth_username},
        "OAuth": {
            "ClientId": o_auth_client_id,
            "TokenUrl": o_auth_token_url,
        },
    }

    return create_client_by_dict(config_dict, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_client_by_dict(
    configuration: dict, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from the given configuration.

    :param configuration: Dictionary containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of AasHttpClient initialized with the provided parameters or None if validation fails
    """
    logger.info("Create AAS server http client from dictionary.")
    config_string = json.dumps(configuration, indent=4)

    return _create_client(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_client_by_config(
    config_file: Path, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from a given configuration file.

    :param config_file: Path to the configuration file containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of AasHttpClient initialized with the provided parameters or None if validation fails
    """
    config_file = config_file.resolve()
    logger.info(f"Create AAS server http client from configuration file '{config_file}'.")
    if not config_file.exists():
        config_string = "{}"
        logger.warning(f"Configuration file '{config_file}' not found. Using default configuration.")
    else:
        config_string = config_file.read_text(encoding="utf-8")
        logger.debug(f"Configuration  file '{config_file}' found.")

    return _create_client(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def _create_client(config_string: str, basic_auth_password: str, o_auth_client_secret: str, bearer_auth_token: str) -> AasHttpClient | None:
    """Create and initialize an AAS HTTP client from configuration string.

    This internal method validates the configuration, sets authentication credentials,
    initializes the client, and tests the connection to the AAS server.

    :param config_string: JSON configuration string containing AAS server settings
    :param basic_auth_password: Password for basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An initialized and connected AasHttpClient instance or None if connection fails
    :raises ValidationError: If the configuration string is invalid
    :raises TimeoutError: If connection to the server times out
    """
    try:
        client = AasHttpClient.model_validate_json(config_string)
    except ValidationError as ve:
        raise ValidationError(f"Invalid BaSyx server configuration file: {ve}") from ve

    client.auth_settings.basic_auth.set_password(basic_auth_password)
    client.auth_settings.o_auth.set_client_secret(o_auth_client_secret)
    client.auth_settings.bearer_auth.set_token(bearer_auth_token)

    logger.info("Using server configuration:")
    logger.info(f"BaseUrl: '{client.base_url}'")
    logger.info(f"TimeOut: '{client.time_out}'")
    logger.info(f"HttpsProxy: '{client.https_proxy}'")
    logger.info(f"HttpProxy: '{client.http_proxy}'")
    logger.info(f"ConnectionTimeOut: '{client.connection_time_out}'.")
    logger.info(f"SSLVerify: '{client.ssl_verify}'.")
    logger.info(f"TrustEnv: '{client.trust_env}'.")
    logger.info(f"EncodedIds: '{client.encoded_ids}'.")

    client.initialize()

    # test the connection to the REST API
    connected = _connect_to_api(client)

    if not connected:
        return None

    return client


def _connect_to_api(client: AasHttpClient) -> bool:
    """Test the connection to the AAS server API with retry logic.

    This internal method attempts to establish a connection to the AAS server by calling
    the get_root() method. It retries the connection for the duration specified in the
    client's connection_time_out setting, sleeping 1 second between attempts.

    :param client: The AasHttpClient instance to test the connection for
    :return: True if connection is successful, False otherwise
    :raises TimeoutError: If connection attempts fail for the entire timeout duration
    """
    start_time = time.time()
    logger.debug(f"Try to connect to REST API '{client.base_url}' for {client.connection_time_out} seconds.")
    counter: int = 0
    while True:
        try:
            root = client.get_root()
            if root:
                logger.info(f"Connected to server API at '{client.base_url}' successfully.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        if time.time() - start_time > client.connection_time_out:
            raise TimeoutError(f"Connection to server API timed out after {client.connection_time_out} seconds.")

        counter += 1
        logger.warning(f"Retrying connection (attempt: {counter}).")
        time.sleep(1)
