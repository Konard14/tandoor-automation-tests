import os
import pytest
from dotenv import load_dotenv

from api.client import TandoorAPIClient

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

load_dotenv()


@pytest.fixture
def api_client() -> TandoorAPIClient:
    return TandoorAPIClient(
        base_url=os.getenv("BASE_URL"),
        token=os.getenv("TANDOOR_TOKEN"),
    )


@pytest.fixture
def driver():
    options = FirefoxOptions()
    options.add_argument("-headless")

    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()