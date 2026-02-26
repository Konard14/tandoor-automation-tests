import pytest

from api.client import TandoorAPIClient, TandoorAPIError


pytestmark = pytest.mark.api  # ВАЖНО: чтобы pytest -m api выбирал эти тесты


def _free_one_recipe_slot(api_client: TandoorAPIClient) -> None:
    """
    Освобождаем 1 слот рецепта, если упёрлись в лимит.
    Удаляем какой-нибудь существующий рецепт.
    """
    recipes = api_client.get_recipes(page_size=50)
    results = recipes.get("results", [])

    if not results:
        pytest.skip("Recipe limit reached and no recipes to delete automatically.")

    # Пытаемся удалить что-то не тестовое (если есть)
    candidate = None
    for r in results:
        name = (r.get("name") or "").lower()
        if "test recipe" not in name and "recipe to delete" not in name:
            candidate = r
            break

    if candidate is None:
        candidate = results[0]

    api_client.delete_recipe(candidate["id"])


def test_get_recipes(api_client: TandoorAPIClient):
    response = api_client.get_recipes(page_size=5)

    assert isinstance(response, dict)
    assert "results" in response


def test_create_recipe(api_client: TandoorAPIClient):
    data = {
        "name": "Test Recipe",
        "description": "Created by automated test",
        "steps": [
            {
                "name": "Step 1",
                "instruction": "Do something",
                "order": 1,
                "ingredients": [],
            }
        ],
    }

    try:
        response = api_client.create_recipe(data)
    except TandoorAPIError as e:
        msg = str(e)
        if "maximum number of recipes" in msg:
            _free_one_recipe_slot(api_client)
            response = api_client.create_recipe(data)
        else:
            raise

    assert response["name"] == "Test Recipe"


def test_delete_recipe(api_client: TandoorAPIClient):
    data = {
        "name": "Recipe To Delete",
        "description": "Temp",
        "steps": [
            {
                "name": "Step 1",
                "instruction": "Delete me",
                "order": 1,
                "ingredients": [],
            }
        ],
    }

    try:
        created = api_client.create_recipe(data)
    except TandoorAPIError as e:
        msg = str(e)
        if "maximum number of recipes" in msg:
            _free_one_recipe_slot(api_client)
            created = api_client.create_recipe(data)
        else:
            raise

    recipe_id = created["id"]

    api_client.delete_recipe(recipe_id)

    recipes = api_client.get_recipes(page_size=50)
    ids = [r["id"] for r in recipes["results"]]
    assert recipe_id not in ids