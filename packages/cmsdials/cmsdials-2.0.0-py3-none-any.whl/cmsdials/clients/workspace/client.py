from requests.adapters import DEFAULT_RETRIES
from requests.exceptions import HTTPError

from ...auth._base import BaseCredentials
from ...utils.api_client import BaseAPIClient
from ...utils.logger import logger


class WorkspaceClient(BaseAPIClient):
    default_timeout = 30
    lookup_url = "auth/"

    def __init__(
        self,
        creds: BaseCredentials,
        *args: str,
        **kwargs: str,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.creds = creds

    def _build_headers(self) -> dict:
        base = {"Accept": "application/json", "User-Agent": self._build_user_agent()}
        self.creds.before_request(base)
        return base

    def __get(self, endpoint: str, retries=DEFAULT_RETRIES):
        headers = self._build_headers()
        endpoint_url = self.api_url + self.lookup_url + endpoint

        response = self._requests_get_retriable(
            endpoint_url,
            headers=headers,
            timeout=self.default_timeout,
            retries=retries,
        )
        try:
            response.raise_for_status()
        except HTTPError as err:
            logger.info(f"Api raw response: {response.text}")
            raise err

        return response.json()

    def list(self, retries=DEFAULT_RETRIES):
        return self.__get("workspaces", retries=retries)

    def my_workspace(self, retries=DEFAULT_RETRIES):
        return self.__get("user-default-workspace", retries=retries)
