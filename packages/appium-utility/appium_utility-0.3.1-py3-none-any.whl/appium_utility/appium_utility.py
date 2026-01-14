from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, InvalidElementStateException
import time


class AppiumUtility:

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.focus_elem_retries = 5
        self.focus_elem_delay = 1

    def launch_app(self, app_id: str):
        self.driver.activate_app(app_id)

    def press_key(self, key: str):
        key_map = {
            "home": 3,
            "back": 4,
            "enter": 66,
            "backspace": 67,
        }
        self.driver.press_keycode(key_map[key])

    def hide_keyboard(self):
        self.driver.hide_keyboard()

    def sleep(self, seconds: float):
        time.sleep(seconds)

    def click_by_text(self, text: str, regex: bool = False):
        el = self._find_by_text(text, regex=regex)
        el.click()


    def click_by_id(self, resource_id: str):
        self.driver.find_element(AppiumBy.ID, resource_id).click()

    def click_by_content_desc(self, content_desc: str):
        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().descriptionContains("{content_desc}")',
        ).click()

    def click_by_xpath(self, xpath: str):
        self.driver.find_element(AppiumBy.XPATH, xpath).click()

    def input_text(self, text: str):
        el = self._get_focused_element_with_retry(self.focus_elem_retries,
                                                  self.focus_elem_delay)
        el.send_keys(text)

    def erase_text(self):
        el = self._get_focused_element_with_retry(
            self.focus_elem_retries,
            self.focus_elem_delay,
        )
        el.clear()

    def _get_focused_element_with_retry(self, retries: int, delay: float):
        last_error = None

        for attempt in range(1, retries + 1):
            try:
                time.sleep(delay)
                el = self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    "new UiSelector().focused(true)",
                )

                if el and el.is_enabled():
                    return el

            except (NoSuchElementException, StaleElementReferenceException,
                    InvalidElementStateException) as e:
                last_error = e

        raise RuntimeError(
            f"Failed to find focused element after {retries} retries"
        ) from last_error

    def swipe_percent(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        duration: int = 300,
    ):
        size = self.driver.get_window_size()
        self.driver.swipe(
            int(size["width"] * start_x),
            int(size["height"] * start_y),
            int(size["width"] * end_x),
            int(size["height"] * end_y),
            duration,
        )

    def scroll_until_text_visible(self, text: str, regex: bool = False):
        selector = (
            f'new UiSelector().textMatches("{text}")'
            if regex
            else f'new UiSelector().textContains("{text}")'
        )

        self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({selector})',
        )

    def assert_text_not_visible(self, text: str, regex: bool = False):
        selector = (
        f'new UiSelector().textMatches("{text}")'
        if regex
        else f'new UiSelector().textContains("{text}")'
        )
        els = self.driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            selector,
        )
        if els:
            raise AssertionError(f"text visible: {text}")

    def _find_by_text(self, text: str, regex: bool = False):
        if regex:
            return self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().textMatches("{text}")',
            )
        return self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{text}")',
        )

    
    def click_by_percent(self, x_percent: float, y_percent: float):
        size = self.driver.get_window_size()
        x = int(size["width"] * x_percent)
        y = int(size["height"] * y_percent)

        self.driver.tap([(x, y)])


