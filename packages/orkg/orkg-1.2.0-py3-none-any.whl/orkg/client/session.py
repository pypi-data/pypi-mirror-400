import time

from keycloak import KeycloakAuthenticationError, KeycloakOpenID, KeycloakOperationError
from loguru import logger


class Session(object):
    def __init__(self, host: str, username: str, password: str):
        self.keycloak_openid = KeycloakOpenID(
            server_url=host, client_id="orkg-pypi", realm_name="orkg"
        )
        self.username = username
        self.password = password
        self._login(time.time())

    def get_access_token(self) -> str:
        timestamp = time.time()
        if self.timestamp + self.jwt.get("expires_in") < timestamp:
            if self.timestamp + self.jwt.get("refresh_expires_in") < timestamp:
                logger.debug("Access token expired. Signing in using credentials...")
                self._login(timestamp)
            else:
                logger.debug(
                    "Access token expired. Using refresh token to refresh access token."
                )
                self._refresh_token(timestamp)
        return self.jwt.get("access_token")

    def _login(self, timestamp: float):
        self.jwt = self.keycloak_openid.token(
            grant_type="password", username=self.username, password=self.password
        )
        self.timestamp = timestamp

    def _refresh_token(self, timestamp: float):
        try:
            refresh_token = self.jwt.get("refresh_token")
            self.jwt = self.keycloak_openid.refresh_token(refresh_token)
            self.timestamp = timestamp
        except (KeycloakAuthenticationError, KeycloakOperationError):
            logger.debug("Access token refresh failed. Signing in using credentials...")
            self._login(timestamp)
