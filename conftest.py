import os
import pytest
from dotenv import load_dotenv

from api.client import TandoorAPIClient

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService


load_dotenv()


@pytest.fixture
def api_client() -> TandoorAPIClient:
    return TandoorAPIClient(
        base_url=os.getenv("BASE_URL"),
        token=os.getenv("TANDOOR_TOKEN"),
    )

@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    driver.maximize_window()
    yield driver
    driver.quit()
