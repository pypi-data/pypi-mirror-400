from .config import ClientConfig
from typing import Optional, Dict, Any
import httpx

from .errors import HttpStatusError, InvalidResponseError, NetworkError


class Transport:
    def __init__(self, config: ClientConfig, client: Optional[httpx.Client] = None) -> None:
        self._config = config
        self._client = client or httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout,
            headers=self._build_headers(),
        )


    def _build_headers(self)->Dict[str, str]:
        headers = {"User-Agent": self._config.user_agent}
        if self._config.api_key:
            headers['Authorization'] = f"Bearer {self._config.api_key}"
        if self._config.extra_headers:
            headers.update(self._config.extra_headers)

        return headers

    def close(self)-> None:
        self._client.close()


    def post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:

        last_exception: Optional[Exception] = None

        for attempt in range(self._config.retries + 1):
            try:
                url = f"{self._config.base_url}{path}"
                response = self._client.post(url, json=payload)

                if response.status_code >= 400:
                    raise HttpStatusError(
                        response.status_code,
                        f"HTTP {response.status_code} calling {url}",
                        body=response.text
                    )

                try:
                    data = response.json()
                except Exception as e:
                    raise InvalidResponseError(f"Invalid JSON response: {e}") from e

                if not isinstance(data, dict):
                    raise InvalidResponseError("Expected JSON object response")

                return data



            except httpx.TimeoutException as e:
                last_exception = e

                if attempt == self._config.retries:
                    raise TimeoutError(f"Request timed out calling {url}") from e
            except httpx.RequestError as e:
                last_exception = e
                if attempt == self._config.retries:
                    raise NetworkError(f"Network error calling path {url}: {e}") from e


        #Should never be reached
        raise NetworkError(f"Failed calling {path}: {last_exception}")





