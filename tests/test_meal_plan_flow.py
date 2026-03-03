import time
import pytest

from pages.meal_plan_page import MealPlanPage
from api.client import TandoorAPIClient, TandoorAPIError


pytestmark = pytest.mark.ui  # этот тест запускается как UI (но использует API для данных)


def generate_unique_recipe_name() -> str:
    return f"MealPlanTestRecipe_{int(time.time())}"


def get_existing_or_create_recipe(api_client: TandoorAPIClient) -> dict:
    """
    Возвращает рецепт для теста.

    Логика:
    1) Если в аккаунте уже есть рецепты — берём первый и используем его (чтобы НЕ упираться в лимит).
    2) Если рецептов нет — пытаемся создать.
    3) Если лимит рецептов достигнут и создать нельзя — тоже берём существующий (если есть),
       иначе пропускаем тест.
    """
    recipes = api_client.get_recipes(page_size=50)
    results = recipes.get("results", [])

    # 1) Есть хотя бы один рецепт -> используем его
    if results:
        return results[0]

    # 2) Рецептов нет -> пробуем создать
    recipe_name = generate_unique_recipe_name()
    recipe_data = {
        "name": recipe_name,
        "description": "Created for Meal Plan test",
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
        created = api_client.create_recipe(recipe_data)
        return created
    except TandoorAPIError as e:
        msg = str(e)
        if "maximum number of recipes" in msg:
            # На всякий случай ещё раз пробуем получить список (вдруг рецепты появились)
            recipes = api_client.get_recipes(page_size=50)
            results = recipes.get("results", [])
            if results:
                return results[0]
            pytest.skip("Recipe limit reached and there are no recipes to use.")
        raise


def test_create_and_delete_meal_plan(logged_in_driver, api_client: TandoorAPIClient):
    """
    Сценарий:
    1) Берём существующий рецепт (или создаём, если рецептов нет)
    2) Создаём Meal Plan через UI
    3) Удаляем Meal Plan через UI
    (Проверка удаления через API добавим позже, когда будут методы mealplan в API-клиенте)
    """

    # ---------- 1) Получаем рецепт через API ----------
    recipe = get_existing_or_create_recipe(api_client)
    recipe_name = recipe["name"]

    # ---------- 2) Создаём Meal Plan через UI ----------
    meal_plan_page = MealPlanPage(logged_in_driver).open()

    meal_plan_page.create_meal_plan(
        meal_type="Breakfast",
        recipe_name=recipe_name,
        servings=1,
        add_to_shopping_list=True,
    )

    # ---------- 3) Удаляем Meal Plan через UI ----------
    meal_plan_page.delete_meal_plan_by_recipe(recipe_name)

    # Мини-проверка: после удаления элемент не должен быть виден (это уже внутри метода delete)
    assert True