from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MealPlanPage:
    URL = "https://app.tandoor.dev/mealplan/"

    # На странице обычно есть заголовок/контент — проверяем факт загрузки по любому стабильному элементу
    BODY = (By.TAG_NAME, "body")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(EC.presence_of_element_located(self.BODY))
        return self

    def is_opened(self) -> bool:
        # Минимальная smoke-проверка: URL содержит mealplan
        return "mealplan" in self.driver.current_url.lower()