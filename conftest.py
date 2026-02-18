import os
import pytest
from api.client import TandoorAPIClient
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def api_client():
    return TandoorAPIClient(
        base_url=os.getenv("BASE_URL"),
        token=os.getenv("TANDOOR_TOKEN"),
    )
