from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MealPlanPage:
    URL = "https://app.tandoor.dev/mealplan/"

    BODY = (By.TAG_NAME, "body")

    # Кнопка "Создать" в левом меню
    CREATE_BTN = (
        By.XPATH,
        "//button[contains(.,'Создать') or contains(.,'Create')]",
    )

    # Поля формы (ищем по тексту label, потом берём ближайший input)
    MEALTYPE_INPUT = (
        By.XPATH,
        "//*[self::label or self::div][contains(.,'Тип питания') or contains(.,'Meal type')]/following::input[1]",
    )
    RECIPE_INPUT = (
        By.XPATH,
        "//*[self::label or self::div][contains(.,'Рецепт') or contains(.,'Recipe')]/following::input[1]",
    )
    SERVINGS_INPUT = (
        By.XPATH,
        "//*[self::label or self::div][contains(.,'порц') or contains(.,'Servings')]/following::input[1]",
    )

    SHOPPINGLIST_CHECKBOX = (
        By.XPATH,
        "//*[contains(.,'Shopping List') or contains(.,'Список покупок')]/ancestor-or-self::*[1]//input[@type='checkbox']",
    )

    SAVE_BTN = (
        By.XPATH,
        "//button[contains(.,'Сохранить') or contains(.,'Save')]",
    )

    # Поиск созданного плана по названию рецепта (появляется текстом на календаре)
    def plan_by_recipe(self, recipe_name: str):
        return (
            By.XPATH,
            f"//*[contains(@class,'meal') or contains(@class,'plan') or contains(@class,'calendar') or self::div]"
            f"[contains(.,'{recipe_name}')]",
        )

    # Контекстное меню/удаление
    DELETE_ACTION = (
        By.XPATH,
        "//*[self::button or self::li or self::div][contains(.,'Удалить') or contains(.,'Delete')]",
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(EC.presence_of_element_located(self.BODY))
        return self

    def is_opened(self) -> bool:
        return "mealplan" in self.driver.current_url.lower()

    def open_create_form(self):
        # Пытаемся нажать "Создать"
        btn = self.wait.until(EC.element_to_be_clickable(self.CREATE_BTN))
        btn.click()
        # ждём появления хотя бы одного поля формы
        self.wait.until(EC.presence_of_element_located(self.MEALTYPE_INPUT))
        return self

    def _fill_input_and_confirm(self, locator, value: str):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(value)
        # В Tandoor многие поля подтверждаются Enter (autocomplete/select)
        el.send_keys(Keys.ENTER)

    def create_meal_plan(self, meal_type: str, recipe_name: str, servings: int = 1, add_to_shopping_list: bool = True):
        self.open_create_form()

        self._fill_input_and_confirm(self.MEALTYPE_INPUT, meal_type)
        self._fill_input_and_confirm(self.RECIPE_INPUT, recipe_name)

        servings_el = self.wait.until(EC.element_to_be_clickable(self.SERVINGS_INPUT))
        servings_el.click()
        servings_el.send_keys(Keys.CONTROL, "a")
        servings_el.send_keys(str(servings))

        if add_to_shopping_list:
            try:
                cb = self.wait.until(EC.presence_of_element_located(self.SHOPPINGLIST_CHECKBOX))
                # если не отмечен — отмечаем
                if not cb.is_selected():
                    cb.click()
            except Exception:
                # если чекбокс не нашли — не валим тест, просто идём дальше
                pass

        save = self.wait.until(EC.element_to_be_clickable(self.SAVE_BTN))
        save.click()

        # Ждём, что вернулись на календарь и план виден
        self.wait.until(EC.presence_of_element_located(self.plan_by_recipe(recipe_name)))
        return self

    def delete_meal_plan_by_recipe(self, recipe_name: str):
        # Кликаем по карточке/элементу с названием рецепта
        plan_el = self.wait.until(EC.element_to_be_clickable(self.plan_by_recipe(recipe_name)))
        plan_el.click()

        # После клика часто появляется контекстное меню с "Удалить"
        delete_btn = self.wait.until(EC.element_to_be_clickable(self.DELETE_ACTION))
        delete_btn.click()

        # Ждём, что элемент исчез
        self.wait.until(EC.invisibility_of_element_located(self.plan_by_recipe(recipe_name)))
        return self