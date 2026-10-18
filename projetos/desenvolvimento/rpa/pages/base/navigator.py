from typing import Any
from selenium.webdriver.firefox.webdriver import WebDriver

class Navigator:
    driver: WebDriver
    controller: Any
    tab_handles: dict[str,str]

    def __init__(self, driver: WebDriver, controller: Any):
        self.driver = driver
        self.controller = controller
        self.tab_handles = {}

    def create_tab(self, index:str, force_new:bool=False):
        if len(self.tab_handles) > 0 or force_new:
            self.driver.switch_to.new_window("tab")
        self.tab_handles |= {index: self.driver.current_window_handle}
            
    def switch_tab(self, index:str):
        pass