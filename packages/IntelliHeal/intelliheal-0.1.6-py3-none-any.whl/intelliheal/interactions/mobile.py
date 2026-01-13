import time
import logging
from typing import Optional, Tuple, Dict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction

from ..decorator import ai_heal
from ..driver_proxy import driver

logger = logging.getLogger("ai_healing")


class MobileInteractions:
    """AI-Healing enabled mobile interactions wrapper for Appium actions."""

    def __init__(self, default_timeout: int = 10):
        self.driver = driver
        self.default_timeout = default_timeout
        self.wait = WebDriverWait(driver, default_timeout)

    def explicit_wait(self, seconds: float) -> None:
        """Simple wait function for compatibility with existing code."""
        time.sleep(seconds)

    @ai_heal(driver_arg_index=0)
    def wait_either_element(
        self,
        elem_a: Dict[str, Tuple],
        elem_b: Dict[str, Tuple],
        timeout: int = 60,
    ) -> bool:
        """Wait for either of two elements to be visible. Returns True if elem_a found first, False if elem_b found first."""
        try:
            # Use the mobile class method
            return self._wait_either_element_internal(
                self.driver, elem_a, elem_b, timeout
            )
        except:

            def check_either_element(driver):
                try:
                    # Check element A first
                    platform_key = None
                    for key in ["ANDROID", "IOS"]:
                        if key in elem_a:
                            platform_key = key
                            break
                    if platform_key:
                        by_obj, value = elem_a[platform_key]
                        elem_a_element = driver.find_element(by_obj, value)
                        if elem_a_element.is_displayed():
                            return "A"
                except:
                    pass

                try:
                    # Check element B second
                    platform_key = None
                    for key in ["ANDROID", "IOS"]:
                        if key in elem_b:
                            platform_key = key
                            break
                    if platform_key:
                        by_obj, value = elem_b[platform_key]
                        elem_b_element = driver.find_element(by_obj, value)
                        if elem_b_element.is_displayed():
                            return "B"
                except:
                    pass

                return False

            wait = WebDriverWait(self.driver, timeout, poll_frequency=0.1)
            result = wait.until(check_either_element)
            return result == "A"

    def _wait_for_element(
        self,
        locator: Dict[str, Tuple],
        timeout: Optional[int] = None,
        condition=EC.element_to_be_clickable,
    ) -> WebElement:
        """Wait for element with specified condition."""
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        # Extract platform-specific locator
        platform_locator = None
        for platform in ["ANDROID", "IOS", "WEB"]:
            if platform in locator:
                platform_locator = locator[platform]
                break

        if not platform_locator:
            raise ValueError(f"No valid platform locator found in {locator}")

        return wait.until(condition(platform_locator))

    # ===== TOUCH ACTIONS =====

    @ai_heal(driver_arg_index=0)
    def click(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Click on an element with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.click()
        logger.debug(f"Successfully clicked element: {locator}")

    @ai_heal(driver_arg_index=0)
    def tap(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Tap on an element using TouchAction with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        TouchAction(self.driver).tap(element).perform()
        logger.debug(f"Successfully tapped element: {locator}")

    @ai_heal(driver_arg_index=0)
    def long_press(
        self,
        locator: Dict[str, Tuple],
        duration: int = 1000,
        timeout: Optional[int] = None,
    ) -> None:
        """Long press on an element with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        TouchAction(self.driver).long_press(element, duration=duration).perform()
        logger.debug(f"Successfully long pressed element: {locator} for {duration}ms")

    @ai_heal(driver_arg_index=0)
    def double_tap(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Double tap on an element with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        TouchAction(self.driver).tap(element).tap(element).perform()
        logger.debug(f"Successfully double tapped element: {locator}")

    def swipe(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000
    ) -> None:
        """Swipe from start coordinates to end coordinates."""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        logger.debug(
            f"Successfully swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})"
        )

    def swipe_direction(
        self, direction: str, distance: int = 500, duration: int = 1000
    ) -> None:
        """Swipe in a specific direction (up, down, left, right)."""
        size = self.driver.get_window_size()
        width, height = size["width"], size["height"]
        center_x, center_y = width // 2, height // 2

        directions = {
            "up": (
                center_x,
                center_y + distance // 2,
                center_x,
                center_y - distance // 2,
            ),
            "down": (
                center_x,
                center_y - distance // 2,
                center_x,
                center_y + distance // 2,
            ),
            "left": (
                center_x + distance // 2,
                center_y,
                center_x - distance // 2,
                center_y,
            ),
            "right": (
                center_x - distance // 2,
                center_y,
                center_x + distance // 2,
                center_y,
            ),
        }

        if direction.lower() not in directions:
            raise ValueError(
                f"Invalid direction: {direction}. Use: up, down, left, right"
            )

        start_x, start_y, end_x, end_y = directions[direction.lower()]
        self.swipe(start_x, start_y, end_x, end_y, duration)

    @ai_heal(driver_arg_index=0)
    def scroll_to_element(
        self, locator: Dict[str, Tuple], max_scrolls: int = 10
    ) -> WebElement:
        """Scroll to find and return an element with AI healing support."""
        for _ in range(max_scrolls):
            try:
                return self._wait_for_element(
                    locator, timeout=2, condition=EC.presence_of_element_located
                )
            except TimeoutException:
                self.swipe_direction("up", distance=300)

        raise TimeoutException(
            f"Element not found after {max_scrolls} scrolls: {locator}"
        )

    @ai_heal(driver_arg_index=0)
    def drag_and_drop(
        self,
        source_locator: Dict[str, Tuple],
        target_locator: Dict[str, Tuple],
        timeout: Optional[int] = None,
    ) -> None:
        """Drag from source element to target element with AI healing support."""
        source_element = self._wait_for_element(
            source_locator, timeout, EC.presence_of_element_located
        )
        target_element = self._wait_for_element(
            target_locator, timeout, EC.presence_of_element_located
        )

        TouchAction(self.driver).long_press(source_element).move_to(
            target_element
        ).release().perform()
        logger.debug(f"Successfully dragged from {source_locator} to {target_locator}")

    def pinch(self, scale: float = 0.5, velocity: int = 1000) -> None:
        """Pinch to zoom in/out with multi-touch."""
        size = self.driver.get_window_size()
        center_x, center_y = size["width"] // 2, size["height"] // 2

        # Create two touch actions for pinch gesture
        action1 = TouchAction(self.driver)
        action2 = TouchAction(self.driver)

        if scale < 1:  # Zoom out (pinch in)
            action1.press(x=center_x - 100, y=center_y).move_to(
                x=center_x - 50, y=center_y
            ).release()
            action2.press(x=center_x + 100, y=center_y).move_to(
                x=center_x + 50, y=center_y
            ).release()
        else:  # Zoom in (pinch out)
            action1.press(x=center_x - 50, y=center_y).move_to(
                x=center_x - 100, y=center_y
            ).release()
            action2.press(x=center_x + 50, y=center_y).move_to(
                x=center_x + 100, y=center_y
            ).release()

        multi_action = MultiAction(self.driver)
        multi_action.add(action1, action2)
        multi_action.perform()
        logger.debug(f"Successfully performed pinch gesture with scale: {scale}")

    @ai_heal(driver_arg_index=0)
    def zoom(
        self,
        locator: Dict[str, Tuple],
        scale: float = 2.0,
        timeout: Optional[int] = None,
    ) -> None:
        """Zoom gesture on an element with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        location = element.location
        size = element.size

        center_x = location["x"] + size["width"] // 2
        center_y = location["y"] + size["height"] // 2

        # Create zoom gesture
        action1 = TouchAction(self.driver)
        action2 = TouchAction(self.driver)

        if scale > 1:  # Zoom in
            action1.press(x=center_x - 25, y=center_y).move_to(
                x=center_x - 50, y=center_y
            ).release()
            action2.press(x=center_x + 25, y=center_y).move_to(
                x=center_x + 50, y=center_y
            ).release()
        else:  # Zoom out
            action1.press(x=center_x - 50, y=center_y).move_to(
                x=center_x - 25, y=center_y
            ).release()
            action2.press(x=center_x + 50, y=center_y).move_to(
                x=center_x + 25, y=center_y
            ).release()

        multi_action = MultiAction(self.driver)
        multi_action.add(action1, action2)
        multi_action.perform()
        logger.debug(f"Successfully zoomed element: {locator} with scale: {scale}")

    # ===== TEXT INPUT =====

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
    def set_value(
        self,
        locator: Dict[str, Tuple],
        text: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Set value directly using Appium with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        element.set_value(text)
        logger.debug(f"Successfully set value for element: {locator}")

    @ai_heal(driver_arg_index=0)
    def clear(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> None:
        """Clear text from an input field with AI healing support."""
        element = self._wait_for_element(locator, timeout, EC.element_to_be_clickable)
        element.clear()
        logger.debug(f"Successfully cleared element: {locator}")

    def hide_keyboard(self) -> None:
        """Dismiss the on-screen keyboard."""
        try:
            self.driver.hide_keyboard()
            logger.debug("Successfully hid keyboard")
        except Exception as e:
            logger.warning(f"Could not hide keyboard: {e}")

    # ===== ELEMENT STATE =====

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
        """Get element attributes with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.get_attribute(attribute)

    @ai_heal(driver_arg_index=0)
    def get_text(self, locator: Dict[str, Tuple], timeout: Optional[int] = None) -> str:
        """Get text content of an element with AI healing support."""
        element = self._wait_for_element(
            locator, timeout, EC.presence_of_element_located
        )
        return element.text

    # ===== NAVIGATION =====

    def back(self) -> None:
        """Press device back button."""
        self.driver.back()
        logger.debug("Successfully pressed back button")

    def forward(self) -> None:
        """Navigate forward (if applicable)."""
        self.driver.forward()
        logger.debug("Successfully navigated forward")

    def press_keycode(self, keycode: int, metastate: Optional[int] = None) -> None:
        """Send hardware key events."""
        if metastate is not None:
            self.driver.press_keycode(keycode, metastate)
        else:
            self.driver.press_keycode(keycode)
        logger.debug(f"Successfully pressed keycode: {keycode}")

    # ===== DEVICE ACTIONS =====

    def shake(self) -> None:
        """Shake the device (iOS)."""
        self.driver.shake()
        logger.debug("Successfully shook device")

    def lock(self, seconds: int = 5) -> None:
        """Lock the device screen."""
        self.driver.lock(seconds)
        logger.debug(f"Successfully locked device for {seconds} seconds")

    def unlock(self) -> None:
        """Unlock the device screen."""
        self.driver.unlock()
        logger.debug("Successfully unlocked device")

    def rotate(self, orientation: str) -> None:
        """Change device orientation (portrait/landscape)."""
        orientations = {"portrait": "PORTRAIT", "landscape": "LANDSCAPE"}

        if orientation.lower() not in orientations:
            raise ValueError(
                f"Invalid orientation: {orientation}. Use: portrait, landscape"
            )

        self.driver.orientation = orientations[orientation.lower()]
        logger.debug(f"Successfully rotated device to {orientation}")

    def open_notifications(self) -> None:
        """Open notification shade (Android)."""
        self.driver.open_notifications()
        logger.debug("Successfully opened notifications")

    def toggle_wifi(self) -> None:
        """Turn WiFi on/off."""
        self.driver.toggle_wifi()
        logger.debug("Successfully toggled WiFi")

    def toggle_airplane_mode(self) -> None:
        """Toggle airplane mode."""
        self.driver.toggle_airplane_mode()
        logger.debug("Successfully toggled airplane mode")

    # ===== APP MANAGEMENT =====

    def launch_app(self) -> None:
        """Launch the application."""
        self.driver.launch_app()
        logger.debug("Successfully launched app")

    def close_app(self) -> None:
        """Close the application."""
        self.driver.close_app()
        logger.debug("Successfully closed app")

    def reset(self) -> None:
        """Reset app to initial state."""
        self.driver.reset()
        logger.debug("Successfully reset app")

    def background_app(self, seconds: int = 5) -> None:
        """Send app to background for specified time."""
        self.driver.background_app(seconds)
        logger.debug(f"Successfully backgrounded app for {seconds} seconds")

    def install_app(self, app_path: str) -> None:
        """Install an app on device."""
        self.driver.install_app(app_path)
        logger.debug(f"Successfully installed app: {app_path}")

    def remove_app(self, app_id: str) -> None:
        """Uninstall an app."""
        self.driver.remove_app(app_id)
        logger.debug(f"Successfully removed app: {app_id}")

    def is_app_installed(self, app_id: str) -> bool:
        """Check if app is installed."""
        return self.driver.is_app_installed(app_id)

    # ===== SCREENSHOT & DEBUGGING =====

    def get_screenshot_as_base64(self) -> str:
        """Get screenshot as base64 string for AI healing analysis."""
        try:
            return self.driver.get_screenshot_as_base64()
        except Exception as e:
            logger.warning(f"Failed to capture screenshot: {e}")
            return ""

    def get_screenshot_as_file(self, filename: str) -> bool:
        """Save screenshot to file."""
        try:
            return self.driver.get_screenshot_as_file(filename)
        except Exception as e:
            logger.warning(f"Failed to save screenshot to {filename}: {e}")
            return False

    def get_page_source(self) -> str:
        """Get current page source for debugging."""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.warning(f"Failed to get page source: {e}")
            return ""

    @property
    def page_source(self) -> str:
        """Property to get current page source (for AI healing compatibility)."""
        return self.get_page_source()

    def _wait_either_element_internal(
        self,
        elem_a: Dict[str, Tuple],
        elem_b: Dict[str, Tuple],
        timeout: int = 60,
    ) -> bool:
        """Internal helper for wait_either_element function."""

        def check_either_element():
            # Check element A first (priority)
            try:
                elem_a_element = self._wait_for_element(
                    elem_a, 0.1, EC.visibility_of_element_located
                )
                if elem_a_element and elem_a_element.is_displayed():
                    return "A"
            except:
                pass

            # Check element B second
            try:
                elem_b_element = self._wait_for_element(
                    elem_b, 0.1, EC.visibility_of_element_located
                )
                if elem_b_element and elem_b_element.is_displayed():
                    return "B"
            except:
                pass

            return False

        # Wait until either element is found
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.1)
        result = wait.until(check_either_element)
        return result == "A"

    # ===== CONTEXT & NAVIGATION =====

    def goto_deeplink(self, link: str) -> None:
        """Navigate to a deeplink URL."""
        import time

        time.sleep(1)
        self.driver.get(link)
        time.sleep(1)
        logger.debug(f"Successfully navigated to deeplink: {link}")

    def switch_to_context(self, context: str) -> None:
        """Switch between native and webview contexts."""
        self.driver.switch_to.context(context)
        logger.debug(f"Successfully switched to context: {context}")

    def get_contexts(self) -> list:
        """Get available contexts."""
        contexts = self.driver.contexts
        logger.debug(f"Available contexts: {contexts}")
        return contexts


mobile = MobileInteractions
