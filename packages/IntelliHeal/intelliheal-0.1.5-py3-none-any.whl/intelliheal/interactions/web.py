import time
import logging
from typing import Optional, Tuple, Union, Dict, Any, List
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)

from ..decorator import ai_heal
from ..driver_proxy import driver

logger = logging.getLogger("ai_healing")


class WebInteractions:
    """AI-Healing enabled web interactions wrapper for Selenium actions."""

    def __init__(self, default_timeout: int = 10):
        self.driver = driver
        self.default_timeout = default_timeout
        self.wait = WebDriverWait(driver, default_timeout)
        self.actions = ActionChains(driver)

    def explicit_wait(self, seconds: float) -> None:
        """Simple wait function for compatibility with existing code."""
        time.sleep(seconds)

    def _wait_for_element(
        self,
        locator: Dict[str, Tuple],
        timeout: Optional[int] = None,
        condition=EC.element_to_be_clickable,
    ) -> WebElement:
        """Wait for element with specified condition."""
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        # Extract web locator
        web_locator = locator.get("WEB")
        if not web_locator:
            raise ValueError(f"No web locator found in {locator}")

        return wait.until(condition(web_locator))

    # ===== MOUSE ACTIONS =====

    @ai_heal(driver_arg_index=0)
    def click(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Click on an element with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.click()
        logger.debug(f"Successfully clicked element: {locator}")

    @ai_heal(driver_arg_index=0)
    def double_click(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Double click on an element with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        ActionChains(self.driver).double_click(element).perform()
        logger.debug(f"Successfully double clicked element: {locator}")

    @ai_heal(driver_arg_index=0)
    def right_click(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Right-click to open context menu with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        ActionChains(self.driver).context_click(element).perform()
        logger.debug(f"Successfully right clicked element: {locator}")

    @ai_heal(driver_arg_index=0)
    def context_click(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Context click (same as right click) with AI healing support."""
        self.right_click(self.driver, locator, timeout)

    @ai_heal(driver_arg_index=0)
    def click_and_hold(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Press and hold mouse button on element with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        ActionChains(self.driver).click_and_hold(element).perform()
        logger.debug(f"Successfully clicked and held element: {locator}")

    def release(self) -> None:
        """Release held mouse button."""
        ActionChains(self.driver).release().perform()
        logger.debug("Successfully released mouse button")

    @ai_heal(driver_arg_index=0)
    def move_to_element(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Hover over an element with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        ActionChains(self.driver).move_to_element(element).perform()
        logger.debug(f"Successfully moved to element: {locator}")

    @ai_heal(driver_arg_index=0)
    def drag_and_drop(
        self,
        source_locator: Dict[str, Tuple],
        target_locator: Dict[str, Tuple],
        timeout: Optional[int] = None,
    ) -> None:
        """Drag element from source to target with AI healing support."""
        source_element = self._wait_for_element(
            source_locator, timeout, EC.element_to_be_clickable
        )
        target_element = self._wait_for_element(
            target_locator, timeout, EC.presence_of_element_located
        )
        ActionChains(self.driver).drag_and_drop(
            source_element, target_element
        ).perform()
        logger.debug(f"Successfully dragged from {source_locator} to {target_locator}")

    @ai_heal(driver_arg_index=0)
    def drag_and_drop_by_offset(
        self,
        locator: Dict[str, Tuple],
        x_offset: int,
        y_offset: int,
        timeout: Optional[int] = None,
    ) -> None:
        """Drag element by x, y coordinates with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        ActionChains(self.driver).drag_and_drop_by_offset(
            element, x_offset, y_offset
        ).perform()
        logger.debug(
            f"Successfully dragged element {locator} by offset ({x_offset}, {y_offset})"
        )

    # ===== KEYBOARD ACTIONS =====

    @ai_heal(driver_arg_index=0)
    def send_keys(
        self,
        locator: Dict[str, Tuple],
        text: str,
        timeout: Optional[int] = None,
        clear_first: bool = True,
    ) -> None:
        """Enter text into a field with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug(f"Successfully sent keys to element: {locator}")

    @ai_heal(driver_arg_index=0)
    def clear(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Clear text from an input field with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.clear()
        logger.debug(f"Successfully cleared element: {locator}")

    @ai_heal(driver_arg_index=0)
    def submit(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Submit a form with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.submit()
        logger.debug(f"Successfully submitted form element: {locator}")

    @ai_heal(driver_arg_index=0)
    def press_key(
        self,
        locator: Dict[str, Tuple],
        key: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Press a specific key (Enter, Tab, etc.) with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.send_keys(getattr(Keys, key.upper(), key))
        logger.debug(f"Successfully pressed key '{key}' on element: {locator}")

    def key_down(self, key: str) -> None:
        """Press and hold a key globally."""
        ActionChains(self.driver).key_down(getattr(Keys, key.upper(), key)).perform()
        logger.debug(f"Successfully pressed down key: {key}")

    def key_up(self, key: str) -> None:
        """Release a held key globally."""
        ActionChains(self.driver).key_up(getattr(Keys, key.upper(), key)).perform()
        logger.debug(f"Successfully released key: {key}")

    # ===== ELEMENT STATE & PROPERTIES =====

    @ai_heal(driver_arg_index=0)
    def is_displayed(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> bool:
        """Check if element is visible with AI healing support."""
        try:
            element = self._wait_for_element(
                locator, timeout, EC.presence_of_element_located
            )
            return element.is_displayed()
        except TimeoutException:
            return False

    @ai_heal(driver_arg_index=0)
    def is_enabled(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> bool:
        """Check if element is enabled with AI healing support."""
        try:
            element = self._wait_for_element(
                locator, timeout, EC.presence_of_element_located
            )
            return element.is_enabled()
        except TimeoutException:
            return False

    @ai_heal(driver_arg_index=0)
    def is_selected(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> bool:
        """Check if element is selected with AI healing support."""
        try:
            element = self._wait_for_element(
                locator, timeout, EC.presence_of_element_located
            )
            return element.is_selected()
        except TimeoutException:
            return False

    @ai_heal(driver_arg_index=0)
    def get_attribute(
        self,
        locator: Dict[str, Tuple],
        attribute: str,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Get element attribute value with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.get_attribute(attribute)

    @ai_heal(driver_arg_index=0)
    def get_property(
        self,
        locator: Dict[str, Tuple],
        property_name: str,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Get element DOM property with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.get_property(property_name)

    @ai_heal(driver_arg_index=0)
    def get_text(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> str:
        """Get text content of an element with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.text

    @ai_heal(driver_arg_index=0)
    def get_css_value(
        self,
        locator: Dict[str, Tuple],
        property_name: str,
        timeout: Optional[int] = None,
    ) -> str:
        """Get CSS property value with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.value_of_css_property(property_name)

    @ai_heal(driver_arg_index=0)
    def tag_name(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> str:
        """Get element's HTML tag name with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.tag_name

    # ===== NAVIGATION =====

    def get(self, url: str) -> None:
        """Navigate to a URL."""
        self.driver.get(url)
        logger.debug(f"Successfully navigated to: {url}")

    def navigate_to(self, url: str) -> None:
        """Navigate to a URL (alias for get)."""
        self.get(url)

    def back(self) -> None:
        """Go back in browser history."""
        self.driver.back()
        logger.debug("Successfully navigated back")

    def forward(self) -> None:
        """Go forward in browser history."""
        self.driver.forward()
        logger.debug("Successfully navigated forward")

    def refresh(self) -> None:
        """Reload current page."""
        self.driver.refresh()
        logger.debug("Successfully refreshed page")

    # ===== BROWSER ACTIONS =====

    def maximize_window(self) -> None:
        """Maximize browser window."""
        self.driver.maximize_window()
        logger.debug("Successfully maximized window")

    def minimize_window(self) -> None:
        """Minimize browser window."""
        self.driver.minimize_window()
        logger.debug("Successfully minimized window")

    def fullscreen_window(self) -> None:
        """Set browser to fullscreen."""
        self.driver.fullscreen_window()
        logger.debug("Successfully set window to fullscreen")

    def set_window_size(self, width: int, height: int) -> None:
        """Set specific window dimensions."""
        self.driver.set_window_size(width, height)
        logger.debug(f"Successfully set window size to {width}x{height}")

    def set_window_position(self, x: int, y: int) -> None:
        """Set window position on screen."""
        self.driver.set_window_position(x, y)
        logger.debug(f"Successfully set window position to ({x}, {y})")

    def get_window_size(self) -> Dict[str, int]:
        """Get current window size."""
        size = self.driver.get_window_size()
        logger.debug(f"Window size: {size}")
        return size

    def get_window_position(self) -> Dict[str, int]:
        """Get current window position."""
        position = self.driver.get_window_position()
        logger.debug(f"Window position: {position}")
        return position

    def get_title(self) -> str:
        """Get page title."""
        title = self.driver.title
        logger.debug(f"Page title: {title}")
        return title

    def get_current_url(self) -> str:
        """Get current URL."""
        url = self.driver.current_url
        logger.debug(f"Current URL: {url}")
        return url

    def get_page_source(self) -> str:
        """Get page HTML source."""
        source = self.driver.page_source
        logger.debug("Successfully retrieved page source")
        return source

    # ===== WINDOW & TAB MANAGEMENT =====

    def switch_to_window(self, window_handle: str) -> None:
        """Switch to different window/tab."""
        self.driver.switch_to.window(window_handle)
        logger.debug(f"Successfully switched to window: {window_handle}")

    @ai_heal(driver_arg_index=0)
    def switch_to_frame(
        self,
        frame_locator: Union[Dict[str, Tuple], int, str, WebElement],
        timeout: Optional[int] = None,
    ) -> None:
        """Switch to an iframe with AI healing support."""
        if isinstance(frame_locator, dict):
            frame = self._wait_for_element(
                frame_locator, timeout, EC.frame_to_be_available_and_switch_to_it
            )
        else:
            self.driver.switch_to.frame(frame_locator)
        logger.debug(f"Successfully switched to frame: {frame_locator}")

    def switch_to_default_content(self) -> None:
        """Switch back to main page from iframe."""
        self.driver.switch_to.default_content()
        logger.debug("Successfully switched to default content")

    def switch_to_alert(self, timeout: Optional[int] = None) -> Alert:
        """Switch to alert/popup dialog."""
        timeout = timeout or self.default_timeout
        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        logger.debug("Successfully switched to alert")
        return alert

    def get_window_handles(self) -> List[str]:
        """Get all open window handles."""
        handles = self.driver.window_handles
        logger.debug(f"Available window handles: {handles}")
        return handles

    def close(self) -> None:
        """Close current window/tab."""
        self.driver.close()
        logger.debug("Successfully closed current window")

    def quit(self) -> None:
        """Close browser and end session."""
        self.driver.quit()
        logger.debug("Successfully quit browser")

    # ===== ALERT HANDLING =====

    def accept_alert(self, timeout: Optional[int] = None) -> None:
        """Accept/confirm alert."""
        alert = self.switch_to_alert(timeout)
        alert.accept()
        logger.debug("Successfully accepted alert")

    def dismiss_alert(self, timeout: Optional[int] = None) -> None:
        """Dismiss/cancel alert."""
        alert = self.switch_to_alert(timeout)
        alert.dismiss()
        logger.debug("Successfully dismissed alert")

    def send_keys_to_alert(self, text: str, timeout: Optional[int] = None) -> None:
        """Type text into alert prompt."""
        alert = self.switch_to_alert(timeout)
        alert.send_keys(text)
        logger.debug(f"Successfully sent keys to alert: {text}")

    def get_alert_text(self, timeout: Optional[int] = None) -> str:
        """Get text from alert."""
        alert = self.switch_to_alert(timeout)
        text = alert.text
        logger.debug(f"Alert text: {text}")
        return text

    # ===== JAVASCRIPT EXECUTION =====

    def execute_script(self, script: str, *args) -> Any:
        """Execute synchronous JavaScript."""
        result = self.driver.execute_script(script, *args)
        logger.debug(f"Successfully executed script: {script[:50]}...")
        return result

    def execute_async_script(self, script: str, *args) -> Any:
        """Execute asynchronous JavaScript."""
        result = self.driver.execute_async_script(script, *args)
        logger.debug(f"Successfully executed async script: {script[:50]}...")
        return result

    # ===== WAITS =====

    def implicitly_wait(self, seconds: int) -> None:
        """Set global wait time for elements."""
        self.driver.implicitly_wait(seconds)
        logger.debug(f"Successfully set implicit wait to {seconds} seconds")

    def explicitly_wait(
        self, condition, timeout: Optional[int] = None, poll_frequency: float = 0.5
    ) -> Any:
        """Wait for specific conditions."""
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout, poll_frequency)
        result = wait.until(condition)
        logger.debug(f"Successfully waited for condition: {condition}")
        return result

    def fluent_wait(
        self,
        condition,
        timeout: Optional[int] = None,
        poll_frequency: float = 0.5,
        ignored_exceptions: Tuple = (NoSuchElementException,),
    ) -> Any:
        """Wait with polling interval and ignore exceptions."""
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout, poll_frequency, ignored_exceptions)
        result = wait.until(condition)
        logger.debug(f"Successfully completed fluent wait for condition: {condition}")
        return result

    # ===== SCREENSHOTS =====

    def get_screenshot_as_file(self, filename: str) -> bool:
        """Save screenshot to file."""
        success = self.driver.get_screenshot_as_file(filename)
        if success:
            logger.debug(f"Successfully saved screenshot to: {filename}")
        else:
            logger.error(f"Failed to save screenshot to: {filename}")
        return success

    def get_screenshot_as_png(self) -> bytes:
        """Get screenshot as PNG bytes."""
        screenshot = self.driver.get_screenshot_as_png()
        logger.debug("Successfully captured screenshot as PNG")
        return screenshot

    def get_screenshot_as_base64(self) -> str:
        """Get screenshot as base64 string."""
        screenshot = self.driver.get_screenshot_as_base64()
        logger.debug("Successfully captured screenshot as base64")
        return screenshot

    # ===== COOKIES =====

    def add_cookie(self, cookie_dict: Dict[str, Any]) -> None:
        """Add a cookie."""
        self.driver.add_cookie(cookie_dict)
        logger.debug(f"Successfully added cookie: {cookie_dict.get('name')}")

    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific cookie."""
        cookie = self.driver.get_cookie(name)
        logger.debug(f"Retrieved cookie: {name}")
        return cookie

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies."""
        cookies = self.driver.get_cookies()
        logger.debug(f"Retrieved {len(cookies)} cookies")
        return cookies

    def delete_cookie(self, name: str) -> None:
        """Delete specific cookie."""
        self.driver.delete_cookie(name)
        logger.debug(f"Successfully deleted cookie: {name}")

    def delete_all_cookies(self) -> None:
        """Clear all cookies."""
        self.driver.delete_all_cookies()
        logger.debug("Successfully deleted all cookies")

    # ===== SELECT (DROPDOWN) ACTIONS =====

    @ai_heal(driver_arg_index=0)
    def select_by_value(
        self,
        locator: Dict[str, Tuple],
        value: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Select option by value attribute with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.select_by_value(value)
        logger.debug(f"Successfully selected option by value: {value}")

    @ai_heal(driver_arg_index=0)
    def select_by_index(
        self,
        locator: Dict[str, Tuple],
        index: int,
        timeout: Optional[int] = None,
    ) -> None:
        """Select option by index position with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.select_by_index(index)
        logger.debug(f"Successfully selected option by index: {index}")

    @ai_heal(driver_arg_index=0)
    def select_by_visible_text(
        self,
        locator: Dict[str, Tuple],
        text: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Select option by visible text with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.select_by_visible_text(text)
        logger.debug(f"Successfully selected option by text: {text}")

    @ai_heal(driver_arg_index=0)
    def deselect_all(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Deselect all options (multi-select) with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.deselect_all()
        logger.debug("Successfully deselected all options")

    @ai_heal(driver_arg_index=0)
    def deselect_by_value(
        self,
        locator: Dict[str, Tuple],
        value: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Deselect option by value with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.deselect_by_value(value)
        logger.debug(f"Successfully deselected option by value: {value}")

    @ai_heal(driver_arg_index=0)
    def deselect_by_index(
        self,
        locator: Dict[str, Tuple],
        index: int,
        timeout: Optional[int] = None,
    ) -> None:
        """Deselect option by index with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.deselect_by_index(index)
        logger.debug(f"Successfully deselected option by index: {index}")

    @ai_heal(driver_arg_index=0)
    def deselect_by_visible_text(
        self,
        locator: Dict[str, Tuple],
        text: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Deselect option by visible text with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        select = Select(element)
        select.deselect_by_visible_text(text)
        logger.debug(f"Successfully deselected option by text: {text}")

    @ai_heal(driver_arg_index=0)
    def get_selected_options(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> List[WebElement]:
        """Get all selected options with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        select = Select(element)
        options = select.all_selected_options
        logger.debug(f"Retrieved {len(options)} selected options")
        return options

    @ai_heal(driver_arg_index=0)
    def get_first_selected_option(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> WebElement:
        """Get first selected option with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        select = Select(element)
        option = select.first_selected_option
        logger.debug("Retrieved first selected option")
        return option

    @ai_heal(driver_arg_index=0)
    def get_all_options(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> List[WebElement]:
        """Get all available options with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        select = Select(element)
        options = select.options
        logger.debug(f"Retrieved {len(options)} available options")
        return options


# Legacy compatibility aliases
web = WebInteractions
