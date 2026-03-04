# api/client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Union
import requests


class TandoorAPIError(Exception):
    """Единая ошибка API-клиента Tandoor."""
    pass


JsonDict = Dict[str, Any]


@dataclass
class TandoorAPIClient:
    base_url: str
    token: str
    timeout: int = 30

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _raise_api_error(self, resp: requests.Response) -> None:
        body = ""
        try:
            body = resp.text
        except Exception:
            body = "<cannot read body>"
        raise TandoorAPIError(
            f"{resp.status_code} {resp.reason} for url: {resp.url}\nBody: {body}"
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[JsonDict] = None,
        json: Optional[JsonDict] = None,
    ) -> requests.Response:
        resp = self.session.request(
            method=method,
            url=self._url(path),
            params=params,
            json=json,
            timeout=self.timeout,
        )
        if resp.status_code >= 400:
            self._raise_api_error(resp)
        return resp

    def get_json(self, path: str, params: Optional[JsonDict] = None) -> Any:
        resp = self._request("GET", path, params=params)
        if not resp.text:
            return None
        return resp.json()

    def post_json(self, path: str, payload: JsonDict) -> Any:
        resp = self._request("POST", path, json=payload)
        if not resp.text:
            return None
        return resp.json()

    def delete(self, path: str) -> None:
        self._request("DELETE", path)
        return None

    # -------------------------
    # Recipes (под твои тесты)
    # -------------------------

    def list_recipes(self, page_size: int = 20) -> Union[List[JsonDict], JsonDict]:
        """
        Тесты могут ожидать либо dict с results, либо просто список — вернём как API отдаёт.
        """
        params = {"page_size": page_size} if page_size else None
        return self.get_json("/api/recipe/", params=params)

    def get_recipes(self, page_size: int = 20) -> Union[List[JsonDict], JsonDict]:
        # тест явно вызывает get_recipes(page_size=5)
        return self.list_recipes(page_size=page_size)

    def create_recipe(self, data: JsonDict) -> JsonDict:
        """
        Тест передаёт data = {name, description, steps:[...]}
        На сервер нужно отправить это как есть (и ничего не переименовывать).
        """
        resp = self.post_json("/api/recipe/", data)
        if not isinstance(resp, dict):
            raise TandoorAPIError("Unexpected create_recipe response (not a dict).")
        return resp

    def delete_recipe(self, recipe_id: int) -> None:
        self.delete(f"/api/recipe/{recipe_id}/")

    # -------------------------
    # Meal plans
    # -------------------------

    def list_mealplans(self) -> List[JsonDict]:
        data = self.get_json("/api/meal-plan/")
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        if isinstance(data, list):
            return data
        return []

    def delete_mealplan(self, mealplan_id: int) -> None:
        self.delete(f"/api/meal-plan/{mealplan_id}/")
