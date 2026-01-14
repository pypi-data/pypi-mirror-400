"""Basic Authentication Configuration."""

from pydantic import BaseModel, Field, PrivateAttr


class BearerAuth(BaseModel):
    """Bearer Authentication Configuration.

    :param BaseModel: Pydantic BaseModel for data validation.
    """

    _token: str = PrivateAttr(default="")

    def set_token(self, token: str) -> None:
        """Set the bearer token for the authentication.

        :param token: Bearer token for the authentication.
        """
        self._token = token

    def get_token(self) -> str:
        """Get the bearer token for the authentication.

        :return: The bearer token.
        """
        return self._token

    def is_active(self) -> bool:
        """Check if the bearer authentication is active.

        :return: True if the token is not empty, False otherwise.
        """
        return bool(self._token)


class BasicAuth(BaseModel):
    """Basic Authentication Configuration.

    :param BaseModel: Pydantic BaseModel for data validation.
    """

    username: str = Field(default="", alias="Username", description="Username for the basic authentication.")
    _password: str = PrivateAttr(default="")

    def is_active(self) -> bool:
        """Check if the basic authentication is active.

        :return: True if the username is not empty, False otherwise.
        """
        return bool(self.username and self._password)

    def set_password(self, password: str) -> None:
        """Set the password for the basic authentication.

        :param password: Password for the basic authentication.
        """
        self._password = password

    def get_password(self) -> str:
        """Get the password for the basic authentication.

        :return: The password.
        """
        return self._password


class OAuth(BaseModel):
    """Open Authentication Configuration.

    :param BaseModel: Pydantic BaseModel for data validation.
    """

    token_url: str = Field(default="", alias="TokenUrl", description="Endpoint URL for the token request.")
    client_id: str = Field(default="", alias="ClientId", description="Client identifier for authentication.")
    grant_type: str = Field(default="client_credentials", alias="GrantType", description="Grant type for the authentication.")
    header_name: str = Field(default="Authorization", alias="HeaderName", description="Header name for the authentication.")
    _client_secret: str = PrivateAttr(default="")

    def is_active(self) -> bool:
        """Check if the service provider authentication is active.

        :return: True if the client ID is not empty, False otherwise.
        """
        return bool(self.client_id and self._client_secret and self.token_url)

    def set_client_secret(self, client_secret: str) -> None:
        """Set the client secret for the authentication.

        :param client_secret: Client secret for the authentication.
        """
        self._client_secret = client_secret

    def get_client_secret(self) -> str:
        """Get the client secret for the authentication.

        :return: The client secret.
        """
        if self._client_secret is None:
            return ""

        return self._client_secret


class AuthenticationConfig(BaseModel):
    """Authentication Configuration.

    param BaseModel: Pydantic BaseModel for data validation.
    """

    basic_auth: BasicAuth = Field(default_factory=BasicAuth, alias="BasicAuth", description="Basic authentication configuration.")
    o_auth: OAuth = Field(
        default_factory=OAuth,
        alias="OAuth",
        description="Service provider authentication configuration.",
    )
    bearer_auth: BearerAuth = Field(default_factory=BearerAuth, alias="BearerAuth", description="Bearer authentication configuration.")
