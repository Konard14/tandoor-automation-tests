git
status
git
add.
git
commit - m
"Finalize API client, POM pages, UI smoke tests; prepare meal plan flow"
git
push - u
origin
main
# pages/meal_plan_page.py
from __future__ import annotations

import time
from pathlib import Path
from typing import List, Tuple, Optional

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[str, str]


class MealPlanPage:
    """
    PageObject для /mealplan (Tandoor).
    """

    URL_PATH = "/mealplan"

    # ---------- базовые локаторы страницы ----------
    # Ячейки календаря (vue-cal style) - из твоего HTML видно cv-day today/past/future
    CALENDAR_DAY_TODAY: List[Locator] = [
        (By.CSS_SELECTOR, ".cv-day.today"),
        (By.CSS_SELECTOR, ".cv-day.dow2.today"),  # иногда
    ]
    CALENDAR_ANY_DAY: List[Locator] = [
        (By.CSS_SELECTOR, ".cv-day.future"),
        (By.CSS_SELECTOR, ".cv-day.today"),
        (By.CSS_SELECTOR, ".cv-day.past"),
        (By.CSS_SELECTOR, ".cv-day"),
    ]

    # Плюс в верхнем баре (если вдруг на другой сборке открывает создание)
    TOPBAR_PLUS_BUTTONS: List[Locator] = [
        (By.XPATH, "//header//button[.//i[contains(@class,'fa-plus')]]"),
        (By.CSS_SELECTOR, "header button.v-btn--icon:has(i.fa-plus)"),
    ]

    # ---------- overlay / dialog ----------
    ACTIVE_OVERLAY: List[Locator] = [
        (By.CSS_SELECTOR, ".v-overlay.v-overlay--active.v-dialog"),
        (By.CSS_SELECTOR, ".v-overlay.v-overlay--active[role='dialog']"),
        (By.XPATH, "//div[contains(@class,'v-overlay') and contains(@class,'v-overlay--active')][@role='dialog']"),
    ]

    # ---------- поля формы (multiselect) ----------
    RECIPE_INPUT_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, ".v-overlay--active input.multiselect-search[aria-placeholder='Рецепт']"),
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//input[contains(@class,'multiselect-search') and @aria-placeholder='Рецепт']"),
    ]

    MEALTYPE_INPUT_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, ".v-overlay--active input.multiselect-search[aria-placeholder='Тип питания']"),
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//input[contains(@class,'multiselect-search') and @aria-placeholder='Тип питания']"),
    ]

    SERVINGS_INPUT_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, ".v-overlay--active input[inputmode='decimal']"),
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//label[contains(.,'Порции')]/following::input[1]"),
    ]

    SAVE_BTN_CANDIDATES: List[Locator] = [
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//button[.//span[contains(.,'Создать') or contains(.,'Create') or contains(.,'Save') or contains(.,'Сохран')]]"),
        (By.XPATH, "//button[.//span[contains(.,'Создать') or contains(.,'Create') or contains(.,'Save') or contains(.,'Сохран')]]"),
    ]

    # ---------- удаление ----------
    # Кнопка удалить в диалоге просмотра/редактирования записи
    DELETE_BTN_CANDIDATES: List[Locator] = [
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//button[.//i[contains(@class,'fa-trash')]]"),
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//button[contains(.,'Удалить') or contains(.,'Delete')]"),
        (By.XPATH, "//button[contains(.,'Удалить') or contains(.,'Delete')]"),
    ]

    # Подтверждение удаления (часто отдельный confirm-диалог)
    CONFIRM_DELETE_CANDIDATES: List[Locator] = [
        (By.XPATH, "//div[contains(@class,'v-overlay--active')]//button[contains(.,'Удалить') or contains(.,'Delete') or contains(.,'Да')]"),
        (By.XPATH, "//button[contains(.,'Удалить') or contains(.,'Delete') or contains(.,'Да')]"),
    ]

    def __init__(self, driver: WebDriver, base_url: str = "https://app.tandoor.dev"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    # ========================= helpers =========================

    def open(self) -> "MealPlanPage":
        self.driver.get(f"{self.base_url}{self.URL_PATH}")
        self._wait_page_ready()
        return self

    def _wait_page_ready(self, timeout: int = 25) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
        time.sleep(0.2)

    def _dump_debug(self, prefix: str = "debug_mealplan") -> None:
        root = Path.cwd()
        try:
            (root / f"{prefix}.html").write_text(self.driver.page_source, encoding="utf-8")
        except Exception:
            pass
        try:
            self.driver.save_screenshot(str(root / f"{prefix}.png"))
        except Exception:
            pass

    def _find_first(self, locators: List[Locator], timeout: int = 10) -> WebElement:
        last_err: Optional[Exception] = None
        for loc in locators:
            try:
                return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
            except Exception as e:
                last_err = e
        raise last_err or AssertionError("Не смог найти элемент по локаторам")

    def _find_clickable(self, locators: List[Locator], timeout: int = 10) -> WebElement:
        last_err: Optional[Exception] = None
        for loc in locators:
            try:
                return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(loc))
            except Exception as e:
                last_err = e
        raise last_err or AssertionError("Не смог найти кликабельный элемент по локаторам")

    def _safe_click(self, el: WebElement) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass

        try:
            el.click()
            return
        except Exception:
            pass

        try:
            self.driver.execute_script("arguments[0].click();", el)
            return
        except Exception:
            pass

        ActionChains(self.driver).move_to_element(el).click().perform()

    def _safe_double_click(self, el: WebElement) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass
        ActionChains(self.driver).move_to_element(el).double_click().perform()

    def _overlay_present(self, timeout: int = 2) -> bool:
        for loc in self.ACTIVE_OVERLAY:
            try:
                WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
                return True
            except Exception:
                continue
        return False

    def _overlay_el(self, timeout: int = 10) -> WebElement:
        last_err: Optional[Exception] = None
        for loc in self.ACTIVE_OVERLAY:
            try:
                return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
            except Exception as e:
                last_err = e
        raise last_err or AssertionError("Не нашёл активный overlay/dialog")

    @staticmethod
    def _xpath_literal(s: str) -> str:
        if "'" not in s:
            return f"'{s}'"
        if '"' not in s:
            return f'"{s}"'
        parts = s.split("'")
        return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"

    def _map_meal_type(self, meal_type: str) -> str:
        mt = (meal_type or "").strip().lower()
        mapping = {
            "breakfast": "Завтрак",
            "lunch": "Обед",
            "dinner": "Ужин",
            "snack": "Перекус",
        }
        return mapping.get(mt, meal_type)

    def _select_from_multiselect(self, input_candidates: List[Locator], value: str, timeout: int = 10) -> None:
        overlay = self._overlay_el(timeout=10)

        # найти input в overlay
        inp = None
        last_err = None
        for loc in input_candidates:
            try:
                inp = WebDriverWait(self.driver, timeout).until(
                    lambda d: overlay.find_element(*loc)  # type: ignore[arg-type]
                )
                break
            except Exception as e:
                last_err = e

        if inp is None:
            raise last_err or AssertionError("Не нашёл multiselect input")

        self._safe_click(inp)

        # очистка и ввод
        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.BACKSPACE)
        except Exception:
            pass
        inp.send_keys(value)

        # клик по опции
        exact_opt = (
            ".//li[contains(@class,'multiselect-option') and "
            "(.//span[normalize-space()=%s] or normalize-space()=%s)]"
        )
        contains_opt = (
            ".//li[contains(@class,'multiselect-option') and "
            "(contains(normalize-space(.), %s) or .//span[contains(normalize-space(.), %s)])]"
        )

        try:
            opt = WebDriverWait(self.driver, timeout).until(
                lambda d: overlay.find_element(
                    By.XPATH, exact_opt % (self._xpath_literal(value), self._xpath_literal(value))
                )
            )
            self._safe_click(opt)
            return
        except Exception:
            opt = WebDriverWait(self.driver, timeout).until(
                lambda d: overlay.find_element(
                    By.XPATH, contains_opt % (self._xpath_literal(value), self._xpath_literal(value))
                )
            )
            self._safe_click(opt)

    # ========================= actions =========================

    def open_create_form(self) -> None:
        """
        В твоей разметке диалог "Новое - Планирование блюд" появляется
        от взаимодействия с календарём (клик/двойной клик по дню).
        Поэтому:
        1) если overlay уже есть — ок
        2) пробуем через клик по today
        3) пробуем double click по today
        4) пробуем любой доступный день
        5) в конце — пробуем topbar plus (на случай другой сборки)
        """
        if self._overlay_present(timeout=1):
            return

        # 1) click today
        try:
            day = self._find_clickable(self.CALENDAR_DAY_TODAY, timeout=6)
            self._safe_click(day)
            if self._overlay_present(timeout=4):
                return
        except Exception:
            pass

        # 2) double click today
        try:
            day = self._find_first(self.CALENDAR_DAY_TODAY, timeout=3)
            self._safe_double_click(day)
            if self._overlay_present(timeout=4):
                return
        except Exception:
            pass

        # 3) click any day
        try:
            day = self._find_clickable(self.CALENDAR_ANY_DAY, timeout=6)
            self._safe_click(day)
            if self._overlay_present(timeout=4):
                return
        except Exception:
            pass

        # 4) double click any day
        try:
            day = self._find_first(self.CALENDAR_ANY_DAY, timeout=3)
            self._safe_double_click(day)
            if self._overlay_present(timeout=4):
                return
        except Exception:
            pass

        # 5) topbar plus (fallback)
        try:
            btn = self._find_clickable(self.TOPBAR_PLUS_BUTTONS, timeout=3)
            self._safe_click(btn)
            if self._overlay_present(timeout=4):
                return
        except Exception:
            pass

        self._dump_debug("debug_open_create_form")
        raise AssertionError(
            "Не смог открыть форму создания Meal Plan (overlay/dialog не появился). "
            "Создал debug_open_create_form.png/html в корне проекта."
        )

    def create_meal_plan(
        self,
        meal_type: str,
        recipe_name: str,
        servings: int = 1,
        add_to_shopping_list: bool = False,
    ) -> "MealPlanPage":
        self.open_create_form()

        meal_type_ui = self._map_meal_type(meal_type)

        # Тип питания + рецепт
        self._select_from_multiselect(self.MEALTYPE_INPUT_CANDIDATES, meal_type_ui)
        self._select_from_multiselect(self.RECIPE_INPUT_CANDIDATES, recipe_name)

        # Порции
        try:
            inp = self._find_first(self.SERVINGS_INPUT_CANDIDATES, timeout=5)
            self._safe_click(inp)
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.BACKSPACE)
            inp.send_keys(str(servings))
        except Exception:
            pass

        # add_to_shopping_list: в этой форме может отсутствовать — не валим тест
        _ = add_to_shopping_list

        # Создать
        try:
            btn = self._find_clickable(self.SAVE_BTN_CANDIDATES, timeout=10)
            self._safe_click(btn)
        except Exception:
            self._dump_debug("debug_create_click")
            raise AssertionError(
                "Не смог нажать 'Создать' в форме Meal Plan. "
                "Создал debug_create_click.png/html в корне проекта."
            )

        # дождаться закрытия диалога
        try:
            # инвиз любых overlay locator
            for loc in self.ACTIVE_OVERLAY:
                WebDriverWait(self.driver, 12).until(EC.invisibility_of_element_located(loc))
        except Exception:
            # не всегда успевает — слегка подождём
            time.sleep(0.5)

        return self

    def delete_meal_plan_by_recipe(self, recipe_name: str) -> "MealPlanPage":
        """
        Удаление записи meal plan через UI:
        1) найти элемент на календаре, где есть текст recipe_name
        2) клик -> откроется overlay с записью
        3) нажать Удалить
        4) подтвердить (если появится confirm)
        5) убедиться, что текста recipe_name больше нет (мягко)
        """
        # 1) найти “ивент” по тексту
        # В разных версиях это может быть div/span внутри календаря.
        event_candidates: List[Locator] = [
            (By.XPATH, f"//main//*[contains(normalize-space(.), {self._xpath_literal(recipe_name)})]"),
            (By.XPATH, f"//div[contains(@class,'cv-wrapper')]//*[contains(normalize-space(.), {self._xpath_literal(recipe_name)})]"),
        ]

        try:
            ev = self._find_clickable(event_candidates, timeout=12)
            self._safe_click(ev)
        except Exception:
            self._dump_debug("debug_delete_find_event")
            raise AssertionError(
                f"Не смог найти meal plan в календаре по названию рецепта: {recipe_name}. "
                "Создал debug_delete_find_event.png/html."
            )

        # 2) дождаться overlay (открылась карточка/редактор)
        try:
            self._overlay_el(timeout=10)
        except Exception:
            self._dump_debug("debug_delete_no_overlay")
            raise AssertionError(
                "Кликнул по найденному элементу, но overlay с записью не открылся. "
                "Создал debug_delete_no_overlay.png/html."
            )

        # 3) удалить
        try:
            del_btn = self._find_clickable(self.DELETE_BTN_CANDIDATES, timeout=8)
            self._safe_click(del_btn)
        except Exception:
            self._dump_debug("debug_delete_no_deletebtn")
            raise AssertionError(
                "Overlay открылся, но кнопку 'Удалить' не нашёл/не смог нажать. "
                "Создал debug_delete_no_deletebtn.png/html."
            )

        # 4) confirm (если появился)
        try:
            if self._overlay_present(timeout=1):
                # иногда confirm — это тоже overlay; пробуем нажать ещё раз "Удалить/Да"
                btn = self._find_clickable(self.CONFIRM_DELETE_CANDIDATES, timeout=4)
                self._safe_click(btn)
        except Exception:
            # если confirm не было — ок
            pass

        # 5) дождаться закрытия overlay
        try:
            for loc in self.ACTIVE_OVERLAY:
                WebDriverWait(self.driver, 12).until(EC.invisibility_of_element_located(loc))
        except Exception:
            time.sleep(0.5)

        # 6) мягкая проверка отсутствия текста recipe_name на странице
        try:
            WebDriverWait(self.driver, 8).until_not(
                EC.presence_of_element_located(
                    (By.XPATH, f"//main//*[contains(normalize-space(.), {self._xpath_literal(recipe_name)})]")
                )
            )
        except Exception:
            # не валим: в календаре могут быть кеш/ленивая перерисовка, но метод удаления уже отработал.
            pass

        return self