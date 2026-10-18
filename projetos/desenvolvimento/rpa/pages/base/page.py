import time
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Callable, Tuple

import requests
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ...utils.logger import logging


def suppress_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return False

    return wrapper


class ElementsConditions:
    elements: "Elements"
    context: WebDriver | WebElement
    driver: WebDriver

    def __init__(self, elements: "Elements") -> None:
        self.elements = elements
        self.context = elements.context
        self.driver = elements.driver

    @suppress_exceptions
    def present(self, index: str) -> bool:
        return bool(
            EC.presence_of_element_located(self.elements.get_locator(index))(
                self.driver
            )
        )

    @suppress_exceptions
    def visible(self, index: str) -> bool:
        return bool(
            EC.visibility_of_element_located(self.elements.get_locator(index))(
                self.driver
            )
        )

    @suppress_exceptions
    def contains(self, index: str, text: str) -> bool:
        return bool(
            EC.text_to_be_present_in_element(self.elements.get_locator(index), text)(
                self.driver
            )
        )


class ElementsWait:
    elements: "Elements"

    def __init__(self, elements: "Elements") -> None:
        self.elements = elements

    def present(self, index_or_xpath: str, timeout: float = 30) -> None:
        WebDriverWait(self.elements.driver, timeout).until(
            lambda d: self.elements.conditions.present(index_or_xpath)
        )

    def visible(self, index_or_xpath: str, timeout: float = 30) -> None:
        WebDriverWait(self.elements.driver, timeout).until(
            lambda d: self.elements.conditions.visible(index_or_xpath)
        )

    def invisible(self, index_or_xpath: str, timeout: float = 30) -> None:
        WebDriverWait(self.elements.driver, timeout).until(
            lambda d: not self.elements.conditions.visible(index_or_xpath)
        )


class ElementsActions:
    elements: "Elements"

    def __init__(self, elements: "Elements") -> None:
        self.elements = elements

    def click(
        self,
        index_or_element: str | WebElement,
        *,
        wait_before: float = 0.0,
        wait_after: float = 0.0,
        wait_load: bool = True,
        timeout: float = 30,
        raise_error: bool = True
    ) -> None:
        t = time.time()
        while ((time.time() - t) < timeout) or timeout == 0:
            try:
                if isinstance(index_or_element, WebElement):
                    element = index_or_element
                else:
                    element = self.elements.get(index_or_element)
                break
            except:
                time.sleep(1)
                pass
            if timeout == 0:
                break
        else:
            if raise_error:
                raise TimeoutError("Elemento não encontrado")

        time.sleep(wait_before)
        WebDriverWait(self.elements.driver, timeout).until(
            EC.element_to_be_clickable(element)
        )

        while ((time.time() - t) < timeout) or timeout == 0:
            try:
                element.click()
                break
            except ElementClickInterceptedException as e:
                _ = element.location_once_scrolled_into_view
                time.sleep(1)
            except Exception as e:
                if raise_error:
                    raise e
            if timeout == 0:
                break
        else:
            if raise_error:
                raise TimeoutError()

        time.sleep(wait_after)
        if wait_load:
            self.elements.page.wait.page_load()

    def select_checkbox(
        self,
        index_or_element: str | WebElement,
        *,
        wait_before: float = 0.0,
        wait_after: float = 0.0,
        wait_load: bool = True,
        timeout: float = 30,
        raise_error: bool = True
    ) -> None:
        t = time.time()
        while ((time.time() - t) < timeout) or timeout == 0:
            try:
                if isinstance(index_or_element, WebElement):
                    element = index_or_element
                else:
                    element = self.elements.get(index_or_element)
                break
            except:
                time.sleep(1)
                pass
            if timeout == 0:
                break
        else:
            if raise_error:
                raise TimeoutError("Elemento não encontrado")

        time.sleep(wait_before)
        WebDriverWait(self.elements.driver, timeout).until(
            EC.element_to_be_clickable(element)
        )

        while ((time.time() - t) < timeout) or timeout == 0:
            try:
                if not element.is_selected():
                    element.click()
                break
            except ElementClickInterceptedException as e:
                _ = element.location_once_scrolled_into_view
                time.sleep(1)
            except Exception as e:
                if raise_error:
                    raise e
            if timeout == 0:
                break
        else:
            if raise_error:
                raise TimeoutError()

        time.sleep(wait_after)
        if wait_load:
            self.elements.page.wait.page_load()

    def click_all(
        self,
        index: str,
        *,
        wait_before: float = 0.0,
        wait_after: float = 0.0,
        wait_between: float = 0.0,
        wait_load_between: bool = True,
        wait_load: bool = True,
        timeout: float = 30,
        raise_error: bool = True
    ) -> None:
        elements = self.elements.get_all(index)
        time.sleep(wait_before)
        for element in elements:
            WebDriverWait(self.elements.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            try:
                element.click()
            except Exception as e:
                if raise_error:
                    raise e
            time.sleep(wait_between)
            if wait_load_between:
                self.elements.page.wait.page_load()
        time.sleep(wait_after)
        if wait_load:
            self.elements.page.wait.page_load()

    def send_keys(
        self,
        index_or_element: str | WebElement,
        text: str,
        *,
        wait_before: float = 0.0,
        wait_after: float = 0.0,
        wait_load: bool = True,
        wait_condition: bool = True,
        timeout: float = 30,
        clear: bool = True,
        raise_error: bool = True
    ):
        if isinstance(index_or_element, WebElement):
            element = index_or_element
        else:
            element = self.elements.get(index_or_element)

        time.sleep(wait_before)
        if wait_condition:
            WebDriverWait(self.elements.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
        if clear:
            try:
                element.clear()
            except:
                pass
        try:
            element.send_keys(text)
        except Exception as e:
            if raise_error:
                raise e
        time.sleep(wait_after)
        if wait_load:
            self.elements.page.wait.page_load()


class ElementsUtils:
    elements: "Elements"

    def __init__(self, elements: "Elements") -> None:
        self.elements = elements

    def get_image(self, index_or_element: str | WebElement) -> BytesIO:
        if isinstance(index_or_element, WebElement):
            element = index_or_element
        else:
            element = self.elements.get(index_or_element)

        image_url = element.get_attribute("src")
        image_name = Path(image_url).name
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
        image_bytes.name = image_name

        return image_bytes


class Elements:
    page: "Page"
    conditions: ElementsConditions
    wait: ElementsWait
    actions: ElementsActions
    utils: ElementsUtils
    paths: dict[str, str]
    context: WebDriver | WebElement
    driver: WebDriver

    def __init__(self, page: "Page") -> None:
        self.page = page
        self.context = page.context
        self.driver = page.driver
        self.conditions = ElementsConditions(self)
        self.wait = ElementsWait(self)
        self.actions = ElementsActions(self)
        self.utils = ElementsUtils(self)
        self.paths = {}

    def __getitem__(self, index: str) -> WebElement:
        return self.get(index)

    def get(self, index_or_xpath: str) -> WebElement:
        return self.context.find_element("xpath", self.paths.get(index_or_xpath,index_or_xpath))

    def get_all(self, index_or_xpath: str) -> list[WebElement]:
        return self.context.find_elements("xpath", self.paths.get(index_or_xpath,index_or_xpath))
            
    def get_locator(self, index: str) -> Tuple[str, str]:
        return ("xpath", self.paths[index])

    @contextmanager
    def switch_frame(self, index: str):
        self.driver.switch_to.frame(self.get(index))
        try:
            yield
        except Exception as e:
            raise e
        finally:
            self.driver.switch_to.default_content()


class PageConditions:
    page: "Page"
    elements_at_page: list[str]
    elements_on_load: dict[str, Callable]

    def __init__(self, page: "Page") -> None:
        self.page = page
        self.elements_at_page = []
        self.elements_on_load = {}

    def at_page_conditions(self) -> dict[str, bool]:
        dict_conditions = {}
        for index in self.elements_at_page:
            try:
                flag_presence = bool(
                    EC.presence_of_element_located(
                        self.page.elements.get_locator(index)
                    )(self.page.driver)
                )
            except:
                flag_presence = False
            dict_conditions[index] = flag_presence

        if self.page.url:
            assert (
                not "URL" in dict_conditions
            ), "URL key already assigned to an element name"
            dict_conditions["URL"] = bool(
                EC.url_contains(self.page.url)(self.page.driver)
            )

        return dict_conditions

    def page_loaded_conditions(self) -> dict[str, bool]:
        return {k: v(self.page.driver) for k, v in self.elements_on_load.items()} | {
            "DOCUMENT_READY": self.page.driver.execute_script(
                "return document.readyState"
            )
            == "complete"
        }

    def at_page(self) -> bool:
        return not False in self.at_page_conditions().values()

    def page_loaded(self) -> bool:
        return not False in self.page_loaded_conditions().values()


class PageWait:
    page: "Page"

    def __init__(self, page: "Page") -> None:
        self.page = page

    def sleep(self, timeout: float):
        time.sleep(timeout)

    def page_load(
        self,
        wait_before: float = 0.5,
        wait_after: float = 0.0,
        wait_between: float = 0.0,
        max_retries: int = 2,
        timeout: float = 30,
    ) -> None:
        time.sleep(wait_before)
        for i in range(max_retries):
            flag_start_condition = self.page.conditions.page_loaded()
            WebDriverWait(self.page.driver, timeout).until(
                lambda d: self.page.conditions.page_loaded()
            )
            if flag_start_condition:
                break
            else:
                time.sleep(wait_between)
        else:
            raise Exception("Page not loaded")
        time.sleep(wait_after)

    def at_page(
        self,
        wait_before: float = 0.5,
        wait_after: float = 0.0,
        timeout: float = 30,
    ) -> None:
        time.sleep(wait_before)
        WebDriverWait(self.page.driver, timeout).until(
            lambda d: self.page.conditions.at_page()
        )
        time.sleep(wait_after)

    def page_refresh(self, timeout: float = 30) -> None:
        WebDriverWait(self.page.driver, timeout).until(
            EC.staleness_of(self.page.driver.find_element("xpath", "html"))
        )

    def not_at_page(self, timeout: float = 30) -> None:
        WebDriverWait(self.page.driver, timeout).until(
            lambda d: not self.page.conditions.at_page()
        )

    def function(
        self,
        function: Callable,
        wait_before: float = 0.5,
        wait_after: float = 0.0,
        timeout: float = 30,
    ) -> None:
        time.sleep(wait_before)
        WebDriverWait(self.page.driver, timeout).until(function)
        time.sleep(wait_after)


class Page:
    context: WebDriver | WebElement
    driver: WebDriver
    logger: logging.Logger

    elements: Elements
    conditions: PageConditions
    wait: PageWait
    url: str = ""

    def __init__(self, context: WebDriver | WebElement):
        self.context = context
        self.driver = context if isinstance(context, WebDriver) else context.parent
        self.logger = logging.getLogger("guion")

        self.elements = Elements(self)
        self.conditions = PageConditions(self)
        self.wait = PageWait(self)
