import os
from typing import Any

from loguru import logger

from wayfinder_paths.core.clients.WayfinderClient import WayfinderClient
from wayfinder_paths.core.settings import settings


class AuthClient(WayfinderClient):
    def __init__(self, api_key: str | None = None):
        """
        Initialize AuthClient.

        Args:
            api_key: Optional API key for service account authentication.
                    If provided, uses API key auth. Otherwise falls back to config.json.
        """
        super().__init__(api_key=api_key)

        self.api_base_url = f"{settings.WAYFINDER_API_URL}"
        self.logger = logger.bind(client="AuthClient")

    def _is_using_api_key(self) -> bool:
        """Check if API key authentication is being used."""
        if self._api_key:
            return True

        try:
            creds = self._load_config_credentials()
            if creds.get("api_key"):
                return True
            if os.getenv("WAYFINDER_API_KEY"):
                return True
        except Exception:
            pass

        return False

    async def authenticate(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        refresh_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Obtain an access token via username/password or refresh token.

        Expected endpoints:
        - POST {api_base_url}/token/ (username, password) -> { access, refresh }
        - POST {api_base_url}/token/refresh/ (refresh) -> { access }
        """
        if refresh_token:
            self.logger.debug(
                "AuthClient.authenticate -> POST /token/refresh (refresh provided)"
            )
            url = f"{self.api_base_url}/auth/token/refresh/"
            payload = {"refresh": refresh_token}
        elif username and password:
            self.logger.debug(
                f"AuthClient.authenticate -> POST /token (username provided={bool(username)})"
            )
            url = f"{self.api_base_url}/auth/token/"
            payload = {"username": username, "password": password}
        else:
            raise ValueError(
                "Credentials required: provide username+password or refresh_token"
            )

        response = await self._request("POST", url, json=payload)
        response.raise_for_status()
        data = response.json()

        access = data.get("access") or data.get("access_token")
        refresh = data.get("refresh") or data.get("refresh_token")
        if access or refresh:
            self.set_tokens(access, refresh)
            self.logger.debug(
                f"AuthClient.authenticate <- success (access={'yes' if access else 'no'}, refresh={'yes' if refresh else 'no'})"
            )

        return data
