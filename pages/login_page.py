from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    URL = "https://app.tandoor.dev/accounts/login/"

    # Кандидаты для поля логина (на разных версиях может называться по-разному)
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

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(self.URL)
        # ждём, что хотя бы одно поле логина появится
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
        user_el = self._find_first(self.USERNAME_CANDIDATES)
        pass_el = self._find_first(self.PASSWORD_CANDIDATES)

        user_el.clear()
        user_el.send_keys(username)

        pass_el.clear()
        pass_el.send_keys(password)

        btn = self._find_first(self.SUBMIT_CANDIDATES)
        btn.click()

        # ждём, что мы ушли со страницы логина
        self.wait.until(lambda d: "accounts/login" not in d.current_url)
        return self