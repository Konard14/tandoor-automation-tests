from __future__ import annotations

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    URL = "https://app.tandoor.dev/accounts/login/"

    USERNAME_CANDIDATES = [
        (By.NAME, "username"),
        (By.ID, "id_username"),
        (By.NAME, "login"),
        (By.ID, "login"),
        (By.NAME, "email"),
        (By.ID, "email"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[autocomplete='username']"),
    ]

    PASSWORD_CANDIDATES = [
        (By.NAME, "password"),
        (By.ID, "id_password"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
    ]

    SUBMIT_CANDIDATES = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, "//button[contains(.,'Войти') or contains(.,'Login') or contains(.,'Sign in')]"),
    ]

    ERROR_CANDIDATES = [
        (By.CSS_SELECTOR, ".errorlist"),
        (By.CSS_SELECTOR, ".v-alert"),
        (By.CSS_SELECTOR, ".alert"),
        (By.CSS_SELECTOR, ".error"),
    ]

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(self.URL)
        self._find_first(self.USERNAME_CANDIDATES)
        self._find_first(self.PASSWORD_CANDIDATES)
        return self

    def _find_first(self, candidates):
        last_err = None
        for loc in candidates:
            try:
                el = self.wait.until(EC.presence_of_element_located(loc))
                return el
            except Exception as e:
                last_err = e
        raise last_err

    def login(self, username: str, password: str):
        if not username or not password:
            raise AssertionError(
                "USERNAME или PASSWORD пустые. Проверь .env и conftest.py"
            )

        user_el = self._find_first(self.USERNAME_CANDIDATES)
        pass_el = self._find_first(self.PASSWORD_CANDIDATES)

        user_el.clear()
        user_el.send_keys(username)

        pass_el.clear()
        pass_el.send_keys(password)

        btn = self._find_first(self.SUBMIT_CANDIDATES)
        btn.click()

        # Ждём редирект или появление другого контента
        try:
            self.wait.until(lambda d: "accounts/login" not in d.current_url)
            return self
        except Exception:
            # fallback: возможно URL не меняется, но мы залогинились
            time.sleep(2)

            if "accounts/login" not in self.driver.current_url:
                return self

            # сохраняем debug
            self._dump_debug("debug_login_failed")

            error_texts = []
            for loc in self.ERROR_CANDIDATES:
                try:
                    els = self.driver.find_elements(*loc)
                    for e in els:
                        txt = e.text.strip()
                        if txt:
                            error_texts.append(txt)
                except Exception:
                    pass

            raise AssertionError(
                f"Логин не удался. URL всё ещё login. "
                f"Найденные тексты ошибок: {error_texts}. "
                f"См. debug_artifacts/debug_login_failed.html/png"
            )

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