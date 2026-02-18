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
