from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class TandoorAPIError(Exception):
    pass


def _load_env() -> None:
    if load_dotenv:
        load_dotenv()


def _strip(s: Optional[str]) -> str:
    return (s or "").strip()


def _api_root(base_url: str) -> str:
    """
    Accepts:
      https://app.tandoor.dev
      https://app.tandoor.dev/
      https://app.tandoor.dev/api
      https://app.tandoor.dev/api/
    Returns:
      https://app.tandoor.dev/api/
    """
    b = (base_url or "").strip()
    if not b:
        return ""
    b = b.rstrip("/")
    if b.endswith("/api"):
        return b + "/"
    return b + "/api/"


@dataclass
class TandoorAPIClient:
    base_url: str
    token: str
    timeout: int = 30

    def __post_init__(self) -> None:
        self.api_root = _api_root(self.base_url)
        self.session = requests.Session()

    def _headers(self, has_json: bool = False) -> Dict[str, str]:
        h = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        if has_json:
            h["Content-Type"] = "application/json"
        return h

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        expected_status: Optional[list[int]] = None,
    ) -> Any:
        # ВАЖНО: всегда бьём в API root (/api/)
        url = urljoin(self.api_root, path.lstrip("/"))

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                headers=self._headers(has_json=(json is not None)),
                params=params,
                json=json,
                timeout=self.timeout,
                allow_redirects=False,
            )
        except Exception as e:
            raise TandoorAPIError(f"Network error calling {method} {url}: {e}") from e

        # Если редирект на /accounts/login/ — токен не приняли ИЛИ ты не в API
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("Location", "")
            raise TandoorAPIError(
                f"Redirect {resp.status_code} for {method} {url}. Location: {loc}. "
                f"Usually means auth failed (token not accepted) or URL is not API."
            )

        if expected_status is None:
            expected_status = [200, 201, 204]

        if resp.status_code not in expected_status:
            payload = (resp.text or "").strip()
            raise TandoorAPIError(
                f"API error {resp.status_code} for {method} {url}. Response: {payload}"
            )

        if not resp.text:
            return None

        try:
            return resp.json()
        except ValueError:
            return resp.text

    # -------- API methods --------

    def get_recipes(self, page_size: int = 1) -> Any:
        # В API Tandoor обычно: /api/recipe/
        return self._request("GET", "recipe/", params={"page_size": page_size}, expected_status=[200])

    def create_recipe(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Создание рецепта — POST /api/recipe/
        return self._request("POST", "recipe/", json=data, expected_status=[200, 201])

    def test_connection(self) -> None:
        print("Checking API connection...")
        data = self.get_recipes(page_size=1)
        if isinstance(data, dict) and "count" in data:
            print(f"OK ✅ Connected. Recipes count: {data.get('count')}")
        else:
            print("OK ✅ Connected. Response:")
            print(data)


def main() -> None:
    _load_env()
    base_url = _strip(os.getenv("BASE_URL"))
    token = _strip(os.getenv("TANDOOR_TOKEN"))

    print("BASE_URL:", base_url)
    print("TOKEN starts:", (token[:10] + "…") if token else "(empty)")
    print("API root:", _api_root(base_url))

    if not token:
        raise SystemExit("TANDOOR_TOKEN is empty in .env")

    client = TandoorAPIClient(base_url=base_url, token=token)
    client.test_connection()


if __name__ == "__main__":
    main()
