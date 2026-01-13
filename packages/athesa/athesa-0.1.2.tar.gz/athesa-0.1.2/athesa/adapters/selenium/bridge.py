"""Selenium implementation of BridgeProtocol"""

import logging
from typing import Tuple, Callable, Any, List

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...core.bridge import BridgeProtocol
from ...exceptions.errors import BridgeError


class SeleniumBridge(BridgeProtocol):
    """
    Selenium implementation of Athesa BridgeProtocol.
    
    Wraps Selenium WebDriver to provide consistent interface for Athesa processes.
    
    Example:
        from selenium import webdriver
        from athesa.adapters.selenium import SeleniumBridge
        
        driver = webdriver.Chrome()
        bridge = SeleniumBridge(driver)
        
        # Use with Athesa
        from athesa import ProcessRunner, ProcessContext
        runner = Process Runner(my_process, context, bridge)
        runner.run()
        
        driver.quit()
    """
    
    def __init__(
        self,
        driver: uc.Chrome,
        wait: WebDriverWait = None,
        default_timeout: int = 10
    ):
        """
        Initialize Selenium bridge.
        
        Args:
            driver: Selenium WebDriver instance
            wait: Optional WebDriverWait instance
            default_timeout: Default timeout for waits (seconds)
        """
        self.driver = driver
        self.wait = wait or WebDriverWait(driver, default_timeout)
        self._logger = logging.getLogger(__name__)
    
    def click(self, selector: Tuple[str, str]) -> None:
        """Click an element"""
        try:
            by, value = selector
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            self._logger.debug(f"Clicked: {by}={value}")
        except Exception as e:
            raise BridgeError(f"Click failed on {selector}: {e}") from e
    
    def type_text(self, selector: Tuple[str, str], text: str) -> None:
        """Type text into an input element"""
        try:
            by, value = selector
            element = self.wait.until(EC.visibility_of_element_located((by, value)))
            element.clear()
            element.send_keys(text)
            self._logger.debug(f"Typed text into: {by}={value}")
        except Exception as e:
            raise BridgeError(f"Type failed on {selector}: {e}") from e
    
    def navigate(self, url: str) -> None:
        """Navigate to URL"""
        try:
            self.driver.get(url)
            self._logger.debug(f"Navigated to: {url}")
        except Exception as e:
            raise BridgeError(f"Navigation failed to {url}: {e}") from e
    
    def is_visible(self, selector: Tuple[str, str]) -> bool:
        """Check if element is visible"""
        try:
            by, value = selector
            element = self.driver.find_element(by, value)
            return element.is_displayed()
        except (NoSuchElementException, Exception):
            return False
    
    def is_existing(self, selector: Tuple[str, str]) -> bool:
        """Check if element exists in DOM"""
        try:
            by, value = selector
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False
    
    def get_text(self, selector: Tuple[str, str]) -> str:
        """Get element text"""
        try:
            by, value = selector
            element = self.wait.until(EC.visibility_of_element_located((by, value)))
            return element.text
        except Exception as e:
            raise BridgeError(f"Get text failed on {selector}: {e}") from e
    
    def get_attribute(self, selector: Tuple[str, str], attribute: str) -> str:
        """Get element attribute value"""
        try:
            by, value = selector
            element = self.driver.find_element(by, value)
            return element.get_attribute(attribute)
        except Exception as e:
            raise BridgeError(f"Get attribute failed on {selector}: {e}") from e
    
    def upload_file(self, selector: Tuple[str, str], file_path: str) -> None:
        """Upload file to input[type=file]"""
        try:
            by, value = selector
            element = self.driver.find_element(by, value)
            element.send_keys(file_path)
            self._logger.debug(f"Uploaded file: {file_path}")
        except Exception as e:
            raise BridgeError(f"File upload failed on {selector}: {e}") from e
    
    def wait_for_condition(self, condition: Callable, timeout: int = 10) -> None:
        """Wait for custom condition"""
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: condition())
        except TimeoutException as e:
            raise BridgeError(f"Condition timeout after {timeout}s") from e
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            raise BridgeError(f"Script execution failed: {e}") from e
    
    def refresh_page(self) -> None:
        """Refresh current page"""
        try:
            self.driver.refresh()
        except Exception as e:
            raise BridgeError(f"Page refresh failed: {e}") from e
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.driver.current_url
    
    def switch_to_frame(self, frame_reference: Any) -> None:
        """Switch to iframe"""
        try:
            self.driver.switch_to.frame(frame_reference)
        except Exception as e:
            raise BridgeError(f"Frame switch failed: {e}") from e
    
    def switch_to_default_content(self) -> None:
        """Switch back to main document"""
        self.driver.switch_to.default_content()
    
    def get_window_handles(self) -> List[str]:
        """Get all window/tab handles"""
        return self.driver.window_handles
    
    def switch_to_window(self, handle: str) -> None:
        """Switch to window/tab"""
        try:
            self.driver.switch_to.window(handle)
        except Exception as e:
            raise BridgeError(f"Window switch failed: {e}") from e
    
    def close_current_window(self) -> None:
        """Close current window/tab"""
        self.driver.close()
