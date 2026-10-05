from urllib.parse import urljoin
import requests
from exceptions import (
    APIError,
    InvalidDataFormatError,
    InvalidJSONError,
    ResourceNotFoundError,
)

class ResourceClient:
    def __init__(self, base_url: str, resource: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/') + '/'
        self.resource = resource.strip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, path: str = '') -> str:
        clean_path = str(path).lstrip('/')
        resource_path = (
            f"{self.resource}/{clean_path}" if clean_path else self.resource
        )
        return urljoin(self.base_url, resource_path)

    def _request(self, method: str, path: str = '', **kwargs) -> requests.Response:
        url = self._build_url(path)

        # set default timeout if not provided in kwargs
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Resource at '{url}' not found (404)"
                ) from e
            raise APIError(
            f"HTTP error {e.response.status_code if e.response else ''}: {e}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network or request failure : {e}") from e

    def _safe_json(self, response: requests.Response) -> dict | list | None:

        if response.status_code == 204 or not response.text.strip():
            return None

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise InvalidJSONError(
                f"Failed to parse response as JSON. Content: {response.text[:100]!r}"
            ) from e

    # --- Public API Methods ---

    def list(self, **params) -> list[dict]:
        response = self._request("GET", params=params)
        data = self._safe_json(response)

        if not isinstance(data, list):
            raise InvalidDataFormatError(
                f"Expected a list from list(), but got {type(data).__name__}."
            )
        return data

    def get(self, item_id: int| str) -> dict:
        response = self._request("GET", path=str(item_id))
        return self._safe_json(response)

    def create(self, data: dict) -> dict:
        response = self._request("POST", json=data)
        return self._safe_json(response)

    def replace(self, item_id: int | str, data: dict) -> dict:
        response = self._request("PUT", path=str(item_id), json=data)
        return self._safe_json(response)

    def update(self, item_id: int | str, data: dict) -> dict:
        response = self._request("PATCH", path=str(item_id), json=data)
        return self._safe_json(response)

    def delete(self, item_id: int | str) -> None:
        self._request("DELETE", path=str(item_id))
        return None


def fetch_all(
    client, page_size: int = 20, max_pages: int = 50, **filters
) -> list[dict]:
    params = dict(filters)
    params['_limit'] = page_size

    all_items = []

    for page in range(1, max_pages + 1):
        params['_page'] = page

        # request current page using the list method
        items = client.list(**params)
        all_items.extend(items)

        if not items or len(items) < page_size:
            break

    return all_items


if __name__ == "__main__":
    client = ResourceClient(
        base_url="https://jsonplaceholder.typicode.com", resource="posts"
    )

    try:
        # Request /delay/5 with a 1.0s timeout
        client._request("GET", path="5", timeout=1.0)
    except APIError as e:
        print(f"Caught expected APIError on timeout: {e}")
        print(f"Original cause (from e): {type(e.__cause__).__name__}")