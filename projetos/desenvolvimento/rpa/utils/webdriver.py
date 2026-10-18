import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver

import logging

logger = logging.getLogger('guion')


def get_driver(headless:bool=True) -> WebDriver:
    driver_options = webdriver.FirefoxOptions()
    driver_options.set_preference("intl.accept_languages", "pt-BR")
    if headless:
        driver_options.add_argument("--headless")

    for binary_path in [
        "/snap/firefox/current/firefox.launcher",
        "/usr/bin/firefox",
        "C:/Program Files/LibreWolf",
    ]:
        if Path(binary_path).exists():
            driver_options.binary_location = binary_path
            break

    for service_path in [
        "/snap/bin/firefox.geckodriver",
        os.getenv("GECKODRIVER_PATH", "geckodriver"),
    ]:
        if Path(service_path).exists():
            break

    return webdriver.Firefox(
        options=driver_options,
        service=FirefoxService(service_path),
    )