import logging
import requests
from forkast_py_client.config import Network

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, network: Network = Network.TESTNET, api_key: str = ""):
        self.network = network
        self.api_key = api_key

    def _headers(
        self,
        access_token: str | None = None,
        extra: dict | None = None,
    ) -> dict:
        headers: dict = {}

        if self.api_key:
            headers["x-api-key"] = self.api_key

        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        if extra:
            headers.update(extra)

        return headers

    def _get(self, url: str, headers: dict | None = None):
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        if not resp.content or not resp.text.strip():
            logger.info("Empty response body from %s", url)
            return None
        return resp.json()

    def _post(self, url: str, data: dict | None = None, headers: dict | None = None):
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()
