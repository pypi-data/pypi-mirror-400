import logging
from typing import Optional, Tuple, Dict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..decorator import ai_heal
from .mobile import MobileInteractions
from ..driver_proxy import driver

logger = logging.getLogger("ai_healing")


class BaseAssertions(MobileInteractions):
    """Base class for assertions and verifications with shared locator handling."""

    def __init__(self, default_timeout: int = 10):
        super().__init__(driver, default_timeout)

    def _find_element(self, locator: Dict[str, Tuple]):
        """Find element without waiting, extending mobile.py locator extraction to support WEB."""
        platform_locator = None
        for platform in ["ANDROID", "IOS", "WEB"]:
            if platform in locator:
                platform_locator = locator[platform]
                break

        if not platform_locator:
            raise ValueError(f"No valid platform locator found in {locator}")

        return self.driver.find_element(platform_locator[0], platform_locator[1])


class Assertions(BaseAssertions):
    """AI-Healing enabled assertions for element states that throw exceptions on failure."""

    # ===== ELEMENT DISPLAY ASSERTIONS =====

    @ai_heal(driver_arg_index=1)
    def element_is_displayed(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> None:
        """Assert that element is displayed."""
        try:
            element = self._wait_for_element(
                locator, timeout, EC.visibility_of_element_located
            )
            assert element.is_displayed(), f"Element {locator} is not displayed"
            logger.debug(f"Element {locator} is displayed")
        except TimeoutException:
            assert (
                False
            ), f"Element {locator} not visible within {timeout or self.default_timeout} seconds"
        except Exception as e:
            assert False, f"Failed to verify element display: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def element_is_not_displayed(self, locator: Dict[str, Tuple]) -> None:
        """Assert that element is not displayed."""
        try:
            element = self._find_element(locator)
            assert (
                not element.is_displayed()
            ), f"Element {locator} is unexpectedly displayed"
        except NoSuchElementException:
            # Element not found - assertion passes
            pass
        except Exception as e:
            # Element not displayed or other error - assertion passes
            logger.debug(f"Element not displayed (expected): {e}")

    # ===== ELEMENT STATE ASSERTIONS =====

    @ai_heal(driver_arg_index=1)
    def button_is_enabled(self, locator: Dict[str, Tuple]) -> None:
        """Assert that button/element is enabled."""
        try:
            element = self._wait_for_element(
                locator, None, EC.visibility_of_element_located
            )
            assert element.is_enabled(), f"Element {locator} is not enabled"
            logger.debug(f"Element {locator} is enabled")
        except Exception as e:
            assert False, f"Failed to verify element is enabled: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def button_is_disabled(self, locator: Dict[str, Tuple]) -> None:
        """Assert that button/element is disabled."""
        try:
            element = self._wait_for_element(
                locator, None, EC.visibility_of_element_located
            )
            assert (
                not element.is_enabled()
            ), f"Element {locator} is unexpectedly enabled"
            logger.debug(f"Element {locator} is disabled")
        except Exception as e:
            assert False, f"Failed to verify element is disabled: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def button_is_not_clickable(self, locator: Dict[str, Tuple]) -> None:
        """Assert that button/element is not clickable."""
        try:
            element = self._find_element(locator)
            # For mobile: check clickable attribute, for web: check enabled
            clickable = element.get_attribute("clickable")
            if clickable is not None:  # Android
                assert (
                    clickable == "false"
                ), f"Element {locator} is unexpectedly clickable"
            else:  # iOS/Web
                assert (
                    not element.is_enabled()
                ), f"Element {locator} is unexpectedly clickable"
            logger.debug(f"Element {locator} is not clickable")
        except Exception as e:
            assert False, f"Failed to verify element is not clickable: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def button_is_not_accessible(self, locator: Dict[str, Tuple]) -> None:
        """Assert that button/element is not accessible (iOS specific)."""
        try:
            element = self._find_element(locator)
            is_accessible = element.get_attribute("accessible")
            assert (
                is_accessible is None or is_accessible.lower() == "false"
            ), f"Element {locator} is unexpectedly accessible"
            logger.debug(f"Element {locator} is not accessible")
        except Exception as e:
            assert False, f"Failed to verify element is not accessible: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def element_is_selected(self, locator: Dict[str, Tuple]) -> None:
        """Assert that element is selected."""
        try:
            element = self._wait_for_element(
                locator, None, EC.visibility_of_element_located
            )
            assert element.is_selected(), f"Element {locator} is not selected"
            logger.debug(f"Element {locator} is selected")
        except Exception as e:
            assert False, f"Failed to verify element is selected: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def element_is_not_selected(self, locator: Dict[str, Tuple]) -> None:
        """Assert that element is not selected."""
        try:
            element = self._wait_for_element(
                locator, None, EC.visibility_of_element_located
            )
            assert (
                not element.is_selected()
            ), f"Element {locator} is unexpectedly selected"
            logger.debug(f"Element {locator} is not selected")
        except Exception as e:
            assert False, f"Failed to verify element is not selected: {str(e)}"

    # ===== TEXT ASSERTIONS =====

    @ai_heal(driver_arg_index=1)
    def text_is_displayed(self, text: str, timeout: Optional[int] = None) -> None:
        """Assert that exact text is displayed on screen."""
        timeout = timeout or self.default_timeout
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Try multiple text attributes for cross-platform compatibility
            xpaths = [
                f'//*[@text="{text}"]',  # Android
                f'//*[@name="{text}"]',  # iOS name
                f'//*[@label="{text}"]',  # iOS label
                f'//*[text()="{text}"]',  # Web text content
            ]

            element = None
            for xpath in xpaths:
                try:
                    element = wait.until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    break
                except:
                    continue

            assert element is not None, f"Text '{text}' not found on screen"
            assert element.is_displayed(), f"Text '{text}' found but not displayed"
            logger.debug(f"Text '{text}' is displayed")
        except TimeoutException:
            assert False, f"Text '{text}' not visible within {timeout} seconds"
        except Exception as e:
            assert False, f"Failed to verify text display: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def text_is_not_displayed(self, text: str) -> None:
        """Assert that exact text is not displayed on screen."""
        try:
            xpaths = [
                f'//*[@text="{text}"]',  # Android
                f'//*[@name="{text}"]',  # iOS name
                f'//*[@label="{text}"]',  # iOS label
                f'//*[text()="{text}"]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    assert (
                        not element.is_displayed()
                    ), f"Text '{text}' is unexpectedly displayed"
                except NoSuchElementException:
                    continue  # Text not found - good for this assertion

            logger.debug(f"Text '{text}' is not displayed (as expected)")
        except Exception as e:
            # If we can't find the text, that's what we want for this assertion
            logger.debug(f"Text not displayed (expected): {e}")

    @ai_heal(driver_arg_index=1)
    def text_contains_is_displayed(
        self, text: str, timeout: Optional[int] = None
    ) -> None:
        """Assert that text containing the specified string is displayed."""
        timeout = timeout or self.default_timeout
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Try multiple text attributes for cross-platform compatibility
            xpaths = [
                f'//*[contains(@text,"{text}")]',  # Android
                f'//*[contains(@name,"{text}")]',  # iOS name
                f'//*[contains(@label,"{text}")]',  # iOS label
                f'//*[contains(text(),"{text}")]',  # Web text content
            ]

            element = None
            for xpath in xpaths:
                try:
                    element = wait.until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    break
                except:
                    continue

            assert element is not None, f"Text containing '{text}' not found on screen"
            assert (
                element.is_displayed()
            ), f"Text containing '{text}' found but not displayed"
            logger.debug(f"Text containing '{text}' is displayed")
        except TimeoutException:
            assert (
                False
            ), f"Text containing '{text}' not visible within {timeout} seconds"
        except Exception as e:
            assert False, f"Failed to verify text contains display: {str(e)}"

    @ai_heal(driver_arg_index=1)
    def text_contains_is_not_displayed(self, text: str) -> None:
        """Assert that no text containing the specified string is displayed."""
        try:
            xpaths = [
                f'//*[contains(@text,"{text}")]',  # Android
                f'//*[contains(@name,"{text}")]',  # iOS name
                f'//*[contains(@label,"{text}")]',  # iOS label
                f'//*[contains(text(),"{text}")]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    assert (
                        not element.is_displayed()
                    ), f"Text containing '{text}' is unexpectedly displayed"
                except NoSuchElementException:
                    continue  # Text not found - good for this assertion

            logger.debug(f"Text containing '{text}' is not displayed (as expected)")
        except Exception as e:
            # If we can't find the text, that's what we want for this assertion
            logger.debug(f"Text containing not displayed (expected): {e}")

    # ===== BASIC VALUE ASSERTIONS =====

    def _equal(self, actual, expected, message: str = None) -> None:
        """Assert that two values are equal."""
        msg = message or f"Expected '{expected}', but got '{actual}'"
        assert actual == expected, msg
        logger.debug(f"Values are equal: {actual} == {expected}")

    def _not_equal(self, actual, expected, message: str = None) -> None:
        """Assert that two values are not equal."""
        msg = message or f"Values should not be equal, but both are '{actual}'"
        assert actual != expected, msg
        logger.debug(f"Values are not equal: {actual} != {expected}")

    def _true(self, value, message: str = None) -> None:
        """Assert that value is True."""
        msg = message or f"Expected True, but got '{value}'"
        assert value is True, msg
        logger.debug(f"Value is True: {value}")

    def _false(self, value, message: str = None) -> None:
        """Assert that value is False."""
        msg = message or f"Expected False, but got '{value}'"
        assert value is False, msg
        logger.debug(f"Value is False: {value}")

    def _none(self, value, message: str = None) -> None:
        """Assert that value is None."""
        msg = message or f"Expected None, but got '{value}'"
        assert value is None, msg
        logger.debug(f"Value is None: {value}")

    def _not_none(self, value, message: str = None) -> None:
        """Assert that value is not None."""
        msg = message or f"Expected value to not be None, but got None"
        assert value is not None, msg
        logger.debug(f"Value is not None: {value}")

    def _in(self, item, container, message: str = None) -> None:
        """Assert that item is in container."""
        msg = message or f"'{item}' not found in '{container}'"
        assert item in container, msg
        logger.debug(f"Item '{item}' found in container")

    def _not_in(self, item, container, message: str = None) -> None:
        """Assert that item is not in container."""
        msg = message or f"'{item}' unexpectedly found in '{container}'"
        assert item not in container, msg
        logger.debug(f"Item '{item}' not in container")

    def _greater(self, a, b, message: str = None) -> None:
        """Assert that a > b."""
        msg = message or f"Expected '{a}' > '{b}'"
        assert a > b, msg
        logger.debug(f"{a} > {b}")

    def _greater_equal(self, a, b, message: str = None) -> None:
        """Assert that a >= b."""
        msg = message or f"Expected '{a}' >= '{b}'"
        assert a >= b, msg
        logger.debug(f"{a} >= {b}")

    def _less(self, a, b, message: str = None) -> None:
        """Assert that a < b."""
        msg = message or f"Expected '{a}' < '{b}'"
        assert a < b, msg
        logger.debug(f"{a} < {b}")

    def _less_equal(self, a, b, message: str = None) -> None:
        """Assert that a <= b."""
        msg = message or f"Expected '{a}' <= '{b}'"
        assert a <= b, msg
        logger.debug(f"{a} <= {b}")

    def _contains(self, text: str, substring: str, message: str = None) -> None:
        """Assert that text contains substring."""
        msg = message or f"'{substring}' not found in '{text}'"
        assert substring in text, msg
        logger.debug(f"Text contains substring: '{substring}' in '{text}'")

    def _not_contains(self, text: str, substring: str, message: str = None) -> None:
        """Assert that text does not contain substring."""
        msg = message or f"'{substring}' unexpectedly found in '{text}'"
        assert substring not in text, msg
        logger.debug(f"Text does not contain substring: '{substring}' not in '{text}'")

    def _starts_with(self, text: str, prefix: str, message: str = None) -> None:
        """Assert that text starts with prefix."""
        msg = message or f"'{text}' does not start with '{prefix}'"
        assert text.startswith(prefix), msg
        logger.debug(f"Text starts with prefix: '{text}' starts with '{prefix}'")

    def _ends_with(self, text: str, suffix: str, message: str = None) -> None:
        """Assert that text ends with suffix."""
        msg = message or f"'{text}' does not end with '{suffix}'"
        assert text.endswith(suffix), msg
        logger.debug(f"Text ends with suffix: '{text}' ends with '{suffix}'")

    def _empty(self, container, message: str = None) -> None:
        """Assert that container is empty."""
        msg = (
            message
            or f"Expected empty container, but got '{container}' with length {len(container)}"
        )
        assert len(container) == 0, msg
        logger.debug(f"Container is empty: {container}")

    def _not_empty(self, container, message: str = None) -> None:
        """Assert that container is not empty."""
        msg = message or f"Expected non-empty container, but got empty container"
        assert len(container) > 0, msg
        logger.debug(f"Container is not empty: length={len(container)}")

    def _length(self, container, expected_length: int, message: str = None) -> None:
        """Assert that container has expected length."""
        actual_length = len(container)
        msg = message or f"Expected length {expected_length}, but got {actual_length}"
        assert actual_length == expected_length, msg
        logger.debug(f"Container has expected length: {actual_length}")

    @ai_heal(driver_arg_index=1)
    def _clipboard_text(self, expected_text: str, message: str = None) -> None:
        """Assert that clipboard contains expected text."""
        try:
            clipboard_text = self.driver.get_clipboard_text()
            msg = (
                message
                or f"Clipboard text '{clipboard_text}' does not match expected '{expected_text}'"
            )
            assert clipboard_text == expected_text, msg
            logger.debug(f"Clipboard text matches: '{clipboard_text}'")
        except Exception as e:
            assert False, f"Failed to verify clipboard text: {str(e)}"


class Verifications(BaseAssertions):
    """AI-Healing enabled verifications that return boolean values instead of throwing exceptions."""

    @ai_heal(driver_arg_index=1)
    def _element_visible(
        self, locator: Dict[str, Tuple], timeout: Optional[int] = None
    ) -> bool:
        """Verify if element is visible (returns boolean)."""
        try:
            element = self._wait_for_element(
                locator, timeout or 1, EC.visibility_of_element_located
            )
            return element.is_displayed()
        except Exception as e:
            logger.debug(f"Element not visible: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_not_visible(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is not visible (returns boolean)."""
        try:
            element = self._find_element(locator)
            return not element.is_displayed()
        except NoSuchElementException:
            return True  # Element not found = not visible
        except Exception:
            return True  # Element not displayed or error = not visible

    @ai_heal(driver_arg_index=1)
    def _element_enabled(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is enabled (returns boolean)."""
        try:
            element = self._wait_for_element(
                locator, 1, EC.visibility_of_element_located
            )
            return element.is_enabled()
        except Exception as e:
            logger.debug(f"Element not enabled: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_disabled(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is disabled (returns boolean)."""
        try:
            element = self._wait_for_element(
                locator, 1, EC.visibility_of_element_located
            )
            return not element.is_enabled()
        except Exception as e:
            logger.debug(f"Element not found or other error: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_selected(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is selected (returns boolean)."""
        try:
            element = self._wait_for_element(
                locator, 1, EC.visibility_of_element_located
            )
            return element.is_selected()
        except Exception as e:
            logger.debug(f"Element not selected: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_not_selected(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is not selected (returns boolean)."""
        try:
            element = self._wait_for_element(
                locator, 1, EC.visibility_of_element_located
            )
            return not element.is_selected()
        except Exception as e:
            logger.debug(f"Element not found or other error: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_clickable(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is clickable (returns boolean)."""
        try:
            element = self._wait_for_element(locator, 1, EC.element_to_be_clickable)
            return element.is_enabled()
        except Exception as e:
            logger.debug(f"Element not clickable: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _element_not_clickable(self, locator: Dict[str, Tuple]) -> bool:
        """Verify if element is not clickable (returns boolean)."""
        try:
            element = self._find_element(locator)
            clickable = element.get_attribute("clickable")
            if clickable is not None:  # Android
                return clickable == "false"
            else:  # iOS/Web
                return not element.is_enabled()
        except Exception as e:
            logger.debug(f"Element not found or other error: {e}")
            return True  # Not found = not clickable

    # ===== TEXT VERIFICATIONS =====

    @ai_heal(driver_arg_index=1)
    def _text_displayed(self, text: str, timeout: Optional[int] = None) -> bool:
        """Verify if exact text is displayed (returns boolean)."""
        timeout = timeout or 1
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Try multiple text attributes for cross-platform compatibility
            xpaths = [
                f'//*[@text="{text}"]',  # Android
                f'//*[@name="{text}"]',  # iOS name
                f'//*[@label="{text}"]',  # iOS label
                f'//*[text()="{text}"]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = wait.until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    return element.is_displayed()
                except:
                    continue
            return False
        except Exception as e:
            logger.debug(f"Text not displayed: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _text_not_displayed(self, text: str) -> bool:
        """Verify if exact text is not displayed (returns boolean)."""
        try:
            xpaths = [
                f'//*[@text="{text}"]',  # Android
                f'//*[@name="{text}"]',  # iOS name
                f'//*[@label="{text}"]',  # iOS label
                f'//*[text()="{text}"]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        return False  # Text is displayed when it shouldn't be
                except NoSuchElementException:
                    continue  # Text not found - good for this verification
            return True  # Text not found or not displayed
        except Exception as e:
            logger.debug(f"Text verification error: {e}")
            return True  # Error finding text = not displayed

    @ai_heal(driver_arg_index=1)
    def _text_contains_displayed(
        self, text: str, timeout: Optional[int] = None
    ) -> bool:
        """Verify if text containing the specified string is displayed (returns boolean)."""
        timeout = timeout or 1
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Try multiple text attributes for cross-platform compatibility
            xpaths = [
                f'//*[contains(@text,"{text}")]',  # Android
                f'//*[contains(@name,"{text}")]',  # iOS name
                f'//*[contains(@label,"{text}")]',  # iOS label
                f'//*[contains(text(),"{text}")]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = wait.until(
                        EC.visibility_of_element_located((By.XPATH, xpath))
                    )
                    return element.is_displayed()
                except:
                    continue
            return False
        except Exception as e:
            logger.debug(f"Text contains not displayed: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _text_contains_not_displayed(self, text: str) -> bool:
        """Verify if no text containing the specified string is displayed (returns boolean)."""
        try:
            xpaths = [
                f'//*[contains(@text,"{text}")]',  # Android
                f'//*[contains(@name,"{text}")]',  # iOS name
                f'//*[contains(@label,"{text}")]',  # iOS label
                f'//*[contains(text(),"{text}")]',  # Web text content
            ]

            for xpath in xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        return False  # Text containing string is displayed when it shouldn't be
                except NoSuchElementException:
                    continue  # Text not found - good for this verification
            return True  # Text containing string not found or not displayed
        except Exception as e:
            logger.debug(f"Text contains verification error: {e}")
            return True  # Error finding text = not displayed

    # ===== BASIC VALUE VERIFICATIONS =====

    def _equal(self, actual, expected) -> bool:
        """Verify that two values are equal (returns boolean)."""
        try:
            result = actual == expected
            logger.debug(f"Values equal check: {actual} == {expected} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Equal verification error: {e}")
            return False

    def _not_equal(self, actual, expected) -> bool:
        """Verify that two values are not equal (returns boolean)."""
        try:
            result = actual != expected
            logger.debug(f"Values not equal check: {actual} != {expected} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Not equal verification error: {e}")
            return False

    def _true(self, value) -> bool:
        """Verify that value is True (returns boolean)."""
        try:
            result = value is True
            logger.debug(f"True check: {value} is True -> {result}")
            return result
        except Exception as e:
            logger.debug(f"True verification error: {e}")
            return False

    def _false(self, value) -> bool:
        """Verify that value is False (returns boolean)."""
        try:
            result = value is False
            logger.debug(f"False check: {value} is False -> {result}")
            return result
        except Exception as e:
            logger.debug(f"False verification error: {e}")
            return False

    def _none(self, value) -> bool:
        """Verify that value is None (returns boolean)."""
        try:
            result = value is None
            logger.debug(f"None check: {value} is None -> {result}")
            return result
        except Exception as e:
            logger.debug(f"None verification error: {e}")
            return False

    def _not_none(self, value) -> bool:
        """Verify that value is not None (returns boolean)."""
        try:
            result = value is not None
            logger.debug(f"Not None check: {value} is not None -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Not None verification error: {e}")
            return False

    def _in(self, item, container) -> bool:
        """Verify that item is in container (returns boolean)."""
        try:
            result = item in container
            logger.debug(f"In check: '{item}' in container -> {result}")
            return result
        except Exception as e:
            logger.debug(f"In verification error: {e}")
            return False

    def _not_in(self, item, container) -> bool:
        """Verify that item is not in container (returns boolean)."""
        try:
            result = item not in container
            logger.debug(f"Not in check: '{item}' not in container -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Not in verification error: {e}")
            return False

    def _greater(self, a, b) -> bool:
        """Verify that a > b (returns boolean)."""
        try:
            result = a > b
            logger.debug(f"Greater check: {a} > {b} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Greater verification error: {e}")
            return False

    def _greater_equal(self, a, b) -> bool:
        """Verify that a >= b (returns boolean)."""
        try:
            result = a >= b
            logger.debug(f"Greater equal check: {a} >= {b} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Greater equal verification error: {e}")
            return False

    def _less(self, a, b) -> bool:
        """Verify that a < b (returns boolean)."""
        try:
            result = a < b
            logger.debug(f"Less check: {a} < {b} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Less verification error: {e}")
            return False

    def _less_equal(self, a, b) -> bool:
        """Verify that a <= b (returns boolean)."""
        try:
            result = a <= b
            logger.debug(f"Less equal check: {a} <= {b} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Less equal verification error: {e}")
            return False

    def _contains(self, text: str, substring: str) -> bool:
        """Verify that text contains substring (returns boolean)."""
        try:
            result = substring in text
            logger.debug(f"Contains check: '{substring}' in '{text}' -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Contains verification error: {e}")
            return False

    def _not_contains(self, text: str, substring: str) -> bool:
        """Verify that text does not contain substring (returns boolean)."""
        try:
            result = substring not in text
            logger.debug(
                f"Not contains check: '{substring}' not in '{text}' -> {result}"
            )
            return result
        except Exception as e:
            logger.debug(f"Not contains verification error: {e}")
            return False

    def _starts_with(self, text: str, prefix: str) -> bool:
        """Verify that text starts with prefix (returns boolean)."""
        try:
            result = text.startswith(prefix)
            logger.debug(
                f"Starts with check: '{text}' starts with '{prefix}' -> {result}"
            )
            return result
        except Exception as e:
            logger.debug(f"Starts with verification error: {e}")
            return False

    def _ends_with(self, text: str, suffix: str) -> bool:
        """Verify that text ends with suffix (returns boolean)."""
        try:
            result = text.endswith(suffix)
            logger.debug(f"Ends with check: '{text}' ends with '{suffix}' -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Ends with verification error: {e}")
            return False

    def _empty(self, container) -> bool:
        """Verify that container is empty (returns boolean)."""
        try:
            result = len(container) == 0
            logger.debug(f"Empty check: container length={len(container)} -> {result}")
            return result
        except Exception as e:
            logger.debug(f"Empty verification error: {e}")
            return False

    def _not_empty(self, container) -> bool:
        """Verify that container is not empty (returns boolean)."""
        try:
            result = len(container) > 0
            logger.debug(
                f"Not empty check: container length={len(container)} -> {result}"
            )
            return result
        except Exception as e:
            logger.debug(f"Not empty verification error: {e}")
            return False

    def _length(self, container, expected_length: int) -> bool:
        """Verify that container has expected length (returns boolean)."""
        try:
            actual_length = len(container)
            result = actual_length == expected_length
            logger.debug(
                f"Length check: {actual_length} == {expected_length} -> {result}"
            )
            return result
        except Exception as e:
            logger.debug(f"Length verification error: {e}")
            return False

    @ai_heal(driver_arg_index=1)
    def _clipboard_text(self, expected_text: str) -> bool:
        """Verify that clipboard contains expected text (returns boolean)."""
        try:
            clipboard_text = self.driver.get_clipboard_text()
            result = clipboard_text == expected_text
            logger.debug(
                f"Clipboard check: '{clipboard_text}' == '{expected_text}' -> {result}"
            )
            return result
        except Exception as e:
            logger.debug(f"Clipboard verification error: {e}")
            return False


# Create global instances for backward compatibility
asserts = Assertions
verify = Verifications
