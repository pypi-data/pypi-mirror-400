from streams_network import BootstrapNetwork
from streams_network.utils.bootstrap_helper import get_bootstrap_config
import requests


class Bootstrap:
    API_URL = "https://api.plotune.net"

    def __init__(self, url: str = "https://stream.plotune.net"):
        self._config = None
        self.email = None
        self.token = None
        self.url = url

    def basic_auth(self, email: str, password: str):
        self.email = email

        payload = {
            "username_or_email": self.email,
            "password": password,
        }
        response = requests.post(f"{self.API_URL}/login", json=payload)
        del password
        response.raise_for_status()
        if response.status_code in (200, 201):
            _access_token = response.json().get("access_token")
            return self.access_auth(email, _access_token)

    def access_auth(self, email: str, access_token):
        if not email or not access_token:
            raise RuntimeError("Email or Access token is not valid")
        self.email = email
        stream_url = f"{self.API_URL}/auth/stream"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(stream_url, headers=headers)
        response.raise_for_status()
        self.token = response.json().get("token")
        return self.verify_access()

    def verify_access(self):
        if not self.url or not self.token or not self.email:
            raise PermissionError("Failed to verify access to the Plotune Networks")
        return True

    def get_config(self) -> BootstrapNetwork:
        if not self.token or not self.email:
            raise PermissionError(
                "Failed to get bootstrap config without authentication"
            )
        if self._config is None:
            self._config = get_bootstrap_config(
                email=self.email, token=self.token, url=self.url
            )
        return self._config

    @property
    def config(self) -> BootstrapNetwork:
        if self._config is None:
            self._config = self.get_config()
        return self._config

    @property
    def peer_id(self) -> str:
        return self._config.get_peer_id()
