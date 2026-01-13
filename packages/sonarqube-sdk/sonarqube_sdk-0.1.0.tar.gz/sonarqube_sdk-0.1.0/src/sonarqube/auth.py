"""Authentication handlers for SonarQube SDK.

This module provides authentication mechanisms for connecting to
SonarQube API. It supports both token-based and basic authentication.

Example:
    Using token authentication::

        from sonarqube.auth import TokenAuth

        auth = TokenAuth(token="your-token")
        headers = auth.get_auth_headers()

    Using basic authentication::

        from sonarqube.auth import BasicAuth

        auth = BasicAuth(username="admin", password="admin")
        headers = auth.get_auth_headers()
"""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from typing import Optional


class BaseAuth(ABC):
    """Abstract base class for authentication handlers.

    All authentication handlers must inherit from this class and
    implement the `get_auth_headers` method.

    Example:
        Creating a custom authentication handler::

            class CustomAuth(BaseAuth):
                def __init__(self, api_key: str) -> None:
                    self.api_key = api_key

                def get_auth_headers(self) -> dict[str, str]:
                    return {"X-API-Key": self.api_key}
    """

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """Return authentication headers to be included in requests.

        Returns:
            Dictionary of HTTP headers for authentication.
        """
        ...


class TokenAuth(BaseAuth):
    """Token-based authentication handler.

    Uses SonarQube user tokens for authentication. The token is sent
    as Basic authentication with the token as the username and an
    empty password.

    Attributes:
        token: The SonarQube user token.

    Example:
        Using a SonarQube user token::

            auth = TokenAuth(token="squ_abcdef123456")
            client = SonarQubeClient(base_url="https://sonarqube.example.com", auth=auth)

    Note:
        SonarQube tokens are used as the username in Basic auth
        with an empty password. This is the standard way to
        authenticate with SonarQube using tokens.
    """

    def __init__(self, token: str) -> None:
        """Initialize token authentication.

        Args:
            token: SonarQube user token.

        Raises:
            ValueError: If token is empty.
        """
        if not token:
            msg = "Token cannot be empty"
            raise ValueError(msg)
        self.token = token

    def get_auth_headers(self) -> dict[str, str]:
        """Return Basic auth headers with token as username.

        The token is encoded as Base64 in the format "token:"
        (token as username, empty password).

        Returns:
            Dictionary with Authorization header.

        Example:
            >>> auth = TokenAuth(token="my-token")
            >>> headers = auth.get_auth_headers()
            >>> "Authorization" in headers
            True
        """
        credentials = f"{self.token}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}


class BasicAuth(BaseAuth):
    """Basic authentication handler.

    Uses username and password for authentication. Credentials are
    encoded as Base64 and sent in the Authorization header.

    Attributes:
        username: The username for authentication.
        password: The password for authentication.

    Example:
        Using username and password::

            auth = BasicAuth(username="admin", password="admin")
            client = SonarQubeClient(base_url="https://sonarqube.example.com", auth=auth)

    Warning:
        Basic authentication with username/password is less secure
        than token authentication. Consider using TokenAuth for
        production environments.
    """

    def __init__(self, username: str, password: str) -> None:
        """Initialize basic authentication.

        Args:
            username: Username for authentication.
            password: Password for authentication.

        Raises:
            ValueError: If username is empty.
        """
        if not username:
            msg = "Username cannot be empty"
            raise ValueError(msg)
        self.username = username
        self.password = password

    def get_auth_headers(self) -> dict[str, str]:
        """Return Basic auth headers with username and password.

        The credentials are encoded as Base64 in the format
        "username:password".

        Returns:
            Dictionary with Authorization header.

        Example:
            >>> auth = BasicAuth(username="admin", password="secret")
            >>> headers = auth.get_auth_headers()
            >>> "Authorization" in headers
            True
        """
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}


def create_auth(
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[BaseAuth]:
    """Create an authentication handler based on provided credentials.

    This factory function creates the appropriate authentication handler
    based on the credentials provided. Token authentication takes priority
    over basic authentication.

    Args:
        token: Optional SonarQube user token.
        username: Optional username for basic auth.
        password: Optional password for basic auth.

    Returns:
        An authentication handler, or None if no credentials provided.

    Raises:
        ValueError: If username provided without password.

    Example:
        Creating auth from token::

            auth = create_auth(token="my-token")
            assert isinstance(auth, TokenAuth)

        Creating auth from credentials::

            auth = create_auth(username="admin", password="admin")
            assert isinstance(auth, BasicAuth)

        No authentication::

            auth = create_auth()
            assert auth is None
    """
    if token:
        return TokenAuth(token=token)
    if username:
        if password is None:
            msg = "Password is required when username is provided"
            raise ValueError(msg)
        return BasicAuth(username=username, password=password)
    return None
