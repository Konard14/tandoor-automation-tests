# pages/meal_plan_page.py
from __future__ import annotations

import os
import time
from typing import Iterable, Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
)

Locator = Tuple[str, str]


class MealPlanPage:
    """
    Страница планирования блюд:
    https://app.tandoor.dev/mealplan
    """

    URL = "https://app.tandoor.dev/mealplan"

    # ---------- calendar ----------
    CALENDAR_ROOT_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, "div.cv-wrapper"),
        (By.CSS_SELECTOR, "div[aria-label='Calendar'].cv-wrapper"),
    ]

    CALENDAR_DAY_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, "div.cv-day.today"),
        (By.CSS_SELECTOR, "div.cv-day.future"),
        (By.CSS_SELECTOR, "div.cv-day.past"),
        (By.CSS_SELECTOR, "div.cv-day"),
    ]

    CALENDAR_ITEM_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, "div.v-card.cv-item"),
        (By.CSS_SELECTOR, "div.cv-item"),
    ]

    # ---------- dialogs / overlays ----------
    ACTIVE_OVERLAY_CONTENT_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, "div.v-overlay.v-overlay--active div.v-overlay__content"),
        (By.CSS_SELECTOR, "div.v-dialog.v-overlay.v-overlay--active div.v-overlay__content"),
        (By.CSS_SELECTOR, "div[role='dialog']"),
    ]

    # В ТВОЁМ UI кнопка называется "+ СОЗДАТЬ", а не "Save/Сохранить".
    BTN_SUBMIT_CANDIDATES: List[Locator] = [
        # 1) прямой текст "Создать / Create" (на кнопке/ссылке/диве)
        (By.XPATH, "//*[self::button or self::a or self::div or self::span][contains(normalize-space(.), 'СОЗДАТЬ') or contains(normalize-space(.), 'Создать') or contains(normalize-space(.), 'Create')]"),
        # 2) вариант: текст внутри span у vuetify-кнопок
        (By.XPATH, "//button[.//span[contains(normalize-space(.), 'СОЗДАТЬ') or contains(normalize-space(.), 'Создать') or contains(normalize-space(.), 'Create')]]"),
        # 3) role=button
        (By.XPATH, "//*[@role='button'][contains(normalize-space(.), 'СОЗДАТЬ') or contains(normalize-space(.), 'Создать') or contains(normalize-space(.), 'Create')]"),
        # 4) submit
        (By.CSS_SELECTOR, "button[type='submit']"),
        # 5) зелёные success кнопки (на всякий)
        (By.CSS_SELECTOR, "button.bg-success"),
        (By.XPATH, "//button[contains(@class,'success') or contains(@class,'bg-success') or contains(@class,'text-success')]"),
        # 6) плюс-иконка (часто рядом)
        (By.XPATH, "//button[.//i[contains(@class,'fa-plus') or contains(@class,'mdi-plus') or contains(@class,'plus')]]"),
    ]

    # Delete
    BTN_DELETE_CANDIDATES: List[Locator] = [
        (By.XPATH, ".//button[.//span[contains(.,'Удалить') or contains(.,'Delete')]]"),
        (By.XPATH, ".//button[contains(.,'Удалить') or contains(.,'Delete')]"),
        (By.CSS_SELECTOR, "button.bg-delete"),
        (By.CSS_SELECTOR, "button[class*='delete']"),
        (By.XPATH, ".//button[.//i[contains(@class,'trash') or contains(@class,'fa-trash') or contains(@class,'mdi-delete')]]"),
    ]

    # Confirm delete
    BTN_CONFIRM_DELETE_CANDIDATES: List[Locator] = [
        (By.XPATH, ".//button[.//span[contains(.,'Да') or contains(.,'Yes') or contains(.,'Удалить') or contains(.,'Delete')]]"),
        (By.XPATH, ".//button[contains(.,'Да') or contains(.,'Yes') or contains(.,'Удалить') or contains(.,'Delete')]"),
        (By.XPATH, ".//button[@aria-label='Delete' or @aria-label='Удалить']"),
    ]

    TODAY_BTN_CANDIDATES: List[Locator] = [
        (By.CSS_SELECTOR, "button.currentPeriod"),
        (By.XPATH, "//button[contains(.,'Сегодня') or contains(.,'Today')]"),
    ]

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    # ---------------- basic ----------------
    def open(self) -> "MealPlanPage":
        self.driver.get(self.URL)
        self._find_first(self.CALENDAR_ROOT_CANDIDATES, timeout=25)
        return self

    def is_opened(self) -> bool:
        try:
            self._find_first(self.CALENDAR_ROOT_CANDIDATES, timeout=3)
            return True
        except Exception:
            return False

    # ---------------- create ----------------
    def open_create_form(self) -> "MealPlanPage":
        if not self.is_opened():
            self.open()

        # иногда помогает "Сегодня"
        self._click_first(self.TODAY_BTN_CANDIDATES, timeout=2)
        time.sleep(0.3)

        day = self._find_first(self.CALENDAR_DAY_CANDIDATES, timeout=15, clickable=True)
        self._scroll_center(day)

        try:
            day.click()
        except Exception:
            ActionChains(self.driver).move_to_element(day).pause(0.1).click().perform()

        overlay = self._get_active_overlay_content(timeout=12)
        if overlay is None:
            self._dump_debug("debug_open_create_fail")
            raise AssertionError("Не открылся диалог создания Meal Plan. См. debug_open_create_fail.*")

        return self

    def create_meal_plan(
        self,
        meal_type: str,
        recipe_name: str,
        servings: int = 1,
        add_to_shopping_list: bool = True,
    ) -> "MealPlanPage":
        self.open_create_form()
        overlay = self._get_active_overlay_content(timeout=10)
        if overlay is None:
            self._dump_debug("debug_overlay_missing_on_create")
            raise AssertionError("Не найден активный overlay после открытия формы создания.")

        # Recipe
        self._set_model_select_by_label(
            overlay=overlay,
            label_texts=("Рецепт", "Recipe"),
            value=recipe_name,
        )

        # Meal type
        self._set_model_select_by_label(
            overlay=overlay,
            label_texts=("Прием", "Приём", "Тип", "Meal", "Meal Type", "Meal type"),
            value=meal_type,
        )

        # Servings
        self._set_number_by_label(
            overlay=overlay,
            label_texts=("Порц", "Servings", "Serving"),
            value=servings,
        )

        # Shopping list checkbox/switch
        self._set_checkbox_by_label(
            overlay=overlay,
            label_texts=("Список покуп", "Shopping", "Add to shopping"),
            checked=add_to_shopping_list,
        )

        # SUBMIT: "+ СОЗДАТЬ"
        if not self._click_first(self.BTN_SUBMIT_CANDIDATES, root=overlay, timeout=10):
            # fallback: иногда кнопка вне overlay content
            if not self._click_first(self.BTN_SUBMIT_CANDIDATES, root=None, timeout=5):
                self._dump_debug("debug_submit_btn_not_found")
                raise AssertionError("Не найдена кнопка '+ СОЗДАТЬ / Create'. См. debug_submit_btn_not_found.*")

        time.sleep(1.2)
        return self

    # ---------------- delete ----------------
    def delete_meal_plan_by_recipe(self, recipe_name: str) -> "MealPlanPage":
        if not self.is_opened():
            self.open()

        item = self._find_calendar_item_by_text(recipe_name)
        if item is None:
            self._dump_debug("debug_item_not_found")
            raise AssertionError(f"Не найден item с текстом '{recipe_name}'. См. debug_item_not_found.*")

        self._scroll_center(item)
        try:
            item.click()
        except Exception:
            ActionChains(self.driver).move_to_element(item).pause(0.1).click().perform()

        overlay = self._get_active_overlay_content(timeout=10)
        if overlay is None:
            self._dump_debug("debug_open_item_fail")
            raise AssertionError("Не открылся диалог при клике по item. См. debug_open_item_fail.*")

        if not self._click_first(self.BTN_DELETE_CANDIDATES, root=overlay, timeout=10):
            if not self._click_first(self.BTN_DELETE_CANDIDATES, root=None, timeout=5):
                self._dump_debug("debug_delete_btn_not_found")
                raise AssertionError("Не найдена кнопка Удалить/Delete. См. debug_delete_btn_not_found.*")

        overlay2 = self._get_active_overlay_content(timeout=6) or overlay
        self._click_first(self.BTN_CONFIRM_DELETE_CANDIDATES, root=overlay2, timeout=10)

        time.sleep(1.0)
        return self

    # ---------------- internals ----------------
    def _find_calendar_item_by_text(self, text: str):
        xpath = (
            f"//div[contains(@class,'cv-item') or contains(@class,'v-card')]"
            f"[.//span[contains(normalize-space(.), {self._xp(text)})] or contains(normalize-space(.), {self._xp(text)})]"
        )
        try:
            return self.driver.find_element(By.XPATH, xpath)
        except Exception:
            return None

    def _get_active_overlay_content(self, timeout: int = 10):
        end = time.time() + timeout
        while time.time() < end:
            for loc in self.ACTIVE_OVERLAY_CONTENT_CANDIDATES:
                try:
                    el = self.driver.find_element(*loc)
                    if el.is_displayed():
                        return el
                except Exception:
                    continue
            time.sleep(0.1)
        return None

    # ---------------- internals: form helpers ----------------
    def _set_model_select_by_label(self, overlay, label_texts: Tuple[str, ...], value: str):
        inp = self._find_input_by_label_like(overlay, label_texts)
        if inp is None:
            return

        self._scroll_center(inp)
        self._safe_click(inp)

        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.DELETE)
        except Exception:
            pass

        inp.send_keys(value)
        time.sleep(0.4)

        option_xpath = (
            f"//div[contains(@class,'v-overlay') or contains(@class,'v-menu') or contains(@class,'v-list')]"
            f"//*[contains(normalize-space(.), {self._xp(value)})]"
        )
        try:
            opt = WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            self._safe_click(opt)
        except Exception:
            try:
                inp.send_keys(Keys.ENTER)
            except Exception:
                pass

    def _set_number_by_label(self, overlay, label_texts: Tuple[str, ...], value: int):
        container = self._find_input_container_by_label_like(overlay, label_texts)
        if container is None:
            return

        inp = self._find_best_interactable_input(container)
        if inp is None:
            try:
                inp = container.find_element(By.CSS_SELECTOR, "input")
            except Exception:
                return

        self._scroll_center(inp)
        self._safe_click(inp)

        try:
            try:
                inp.send_keys(Keys.CONTROL, "a")
                inp.send_keys(Keys.DELETE)
            except Exception:
                pass
            inp.send_keys(str(value))
            return
        except ElementNotInteractableException:
            pass
        except Exception:
            pass

        self._set_value_js(inp, str(value))

    def _set_checkbox_by_label(self, overlay, label_texts: Tuple[str, ...], checked: bool):
        for t in label_texts:
            try:
                cb = overlay.find_element(
                    By.XPATH,
                    f".//label[contains(.,{self._xp(t)})]/preceding::input[@type='checkbox'][1] | "
                    f".//label[contains(.,{self._xp(t)})]/following::input[@type='checkbox'][1]"
                )
                current = cb.is_selected()
                if current != checked:
                    try:
                        lbl = overlay.find_element(By.XPATH, f".//label[contains(.,{self._xp(t)})]")
                        self._safe_click(lbl)
                    except Exception:
                        self._safe_click(cb)
                return
            except Exception:
                continue

    # ---------- finders ----------
    def _find_input_by_label_like(self, root, label_texts: Tuple[str, ...]):
        container = self._find_input_container_by_label_like(root, label_texts)
        if container is None:
            return None

        candidates = [
            (By.CSS_SELECTOR, "input[role='combobox']"),
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input"),
        ]
        for loc in candidates:
            try:
                el = container.find_element(*loc)
                return el
            except Exception:
                continue
        return None

    def _find_input_container_by_label_like(self, root, label_texts: Tuple[str, ...]):
        for t in label_texts:
            # label внутри v-input
            try:
                return root.find_element(
                    By.XPATH,
                    f".//label[contains(normalize-space(.), {self._xp(t)})]/ancestor::*[contains(@class,'v-input')][1]"
                )
            except Exception:
                pass

            # label for="id"
            try:
                label = root.find_element(By.XPATH, f".//label[contains(normalize-space(.), {self._xp(t)}) and @for]")
                for_id = label.get_attribute("for")
                if for_id:
                    inp = root.find_element(By.ID, for_id)
                    return inp.find_element(By.XPATH, "./ancestor::*[contains(@class,'v-input')][1]")
            except Exception:
                pass

        return None

    def _find_best_interactable_input(self, container):
        try_locs = [
            (By.CSS_SELECTOR, "input[type='number']"),
            (By.CSS_SELECTOR, "input[inputmode='numeric']"),
            (By.CSS_SELECTOR, "input.v-field__input"),
            (By.CSS_SELECTOR, "input"),
        ]
        for loc in try_locs:
            try:
                inputs = container.find_elements(*loc)
            except Exception:
                continue

            for inp in inputs:
                try:
                    if not inp.is_displayed() or not inp.is_enabled():
                        continue
                    ro = inp.get_attribute("readonly")
                    if ro is not None and ro != "false":
                        continue
                    return inp
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        return None

    # ---------------- helpers ----------------
    def _scroll_center(self, el):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.1)
        except Exception:
            pass

    def _safe_click(self, el):
        try:
            el.click()
            return
        except Exception:
            pass
        try:
            ActionChains(self.driver).move_to_element(el).pause(0.05).click().perform()
            return
        except Exception:
            pass
        try:
            self.driver.execute_script("arguments[0].click();", el)
        except Exception:
            pass

    def _set_value_js(self, el, value: str):
        try:
            self.driver.execute_script(
                """
                const el = arguments[0];
                const value = arguments[1];
                el.focus();
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                """,
                el,
                value,
            )
            time.sleep(0.2)
        except Exception:
            pass

    def _find_first(self, candidates: Iterable[Locator], timeout: int = 10, clickable: bool = False):
        last_err = None
        w = WebDriverWait(self.driver, timeout)
        for loc in candidates:
            try:
                if clickable:
                    return w.until(EC.element_to_be_clickable(loc))
                return w.until(EC.presence_of_element_located(loc))
            except Exception as e:
                last_err = e
        if last_err:
            raise last_err
        raise AssertionError("Не найден ни один элемент по кандидатам локаторов.")

    def _click_first(self, candidates: Iterable[Locator], timeout: int = 5, root=None) -> bool:
        end = time.time() + timeout
        while time.time() < end:
            for by, sel in candidates:
                try:
                    # Ищем сразу список, а не один элемент — так стабильнее
                    if root is not None:
                        els = root.find_elements(by, sel)
                    else:
                        els = self.driver.find_elements(by, sel)

                    for el in els:
                        try:
                            if not el.is_displayed():
                                continue
                            self._scroll_center(el)
                            self._safe_click(el)
                            return True
                        except Exception:
                            continue
                except Exception:
                    continue
            time.sleep(0.1)
        return False

    def _dump_debug(self, name: str):
        folder = os.path.join(os.getcwd(), "debug_artifacts")
        os.makedirs(folder, exist_ok=True)

        html_path = os.path.join(folder, f"{name}.html")
        png_path = os.path.join(folder, f"{name}.png")

        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass

        try:
            self.driver.save_screenshot(png_path)
        except Exception:
            pass

    @staticmethod
    def _xp(s: str) -> str:
        if "'" not in s:
            return f"'{s}'"
        if '"' not in s:
            return f'"{s}"'
        parts = s.split("'")
        return "concat(" + ", \"'\", ".join([f"'{p}'" for p in parts]) + ")"