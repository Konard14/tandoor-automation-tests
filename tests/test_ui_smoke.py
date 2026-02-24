import os
import pytest

from pages.login_page import LoginPage
from pages.meal_plan_page import MealPlanPage


@pytest.mark.ui
def test_homepage_opens(driver):
    driver.get("https://app.tandoor.dev")
    assert "app.tandoor.dev" in driver.current_url


@pytest.mark.ui
def test_login_success(driver):
    username = os.getenv("TANDOOR_USERNAME")
    password = os.getenv("TANDOOR_PASSWORD")
    assert username and password, "Нет TANDOOR_USERNAME / TANDOOR_PASSWORD в .env"

    LoginPage(driver).open().login(username, password)
    assert "accounts/login" not in driver.current_url


@pytest.mark.ui
def test_open_meal_plan(driver):
    username = os.getenv("TANDOOR_USERNAME")
    password = os.getenv("TANDOOR_PASSWORD")
    assert username and password, "Нет TANDOOR_USERNAME / TANDOOR_PASSWORD в .env"

    LoginPage(driver).open().login(username, password)
    page = MealPlanPage(driver).open()
    assert page.is_opened()