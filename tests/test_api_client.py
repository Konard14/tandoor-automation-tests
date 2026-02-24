import pytest
from api.client import TandoorAPIClient


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

    response = api_client.create_recipe(data)

    assert response["name"] == "Test Recipe"


def test_delete_recipe(api_client: TandoorAPIClient):
    # создаём рецепт
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

    created = api_client.create_recipe(data)
    recipe_id = created["id"]

    # удаляем
    api_client.delete_recipe(recipe_id)

    # проверяем что он больше не существует
    recipes = api_client.get_recipes(page_size=50)
    ids = [r["id"] for r in recipes["results"]]

    assert recipe_id not in ids
