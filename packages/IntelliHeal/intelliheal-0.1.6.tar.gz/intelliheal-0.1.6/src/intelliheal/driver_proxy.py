import threading

# Thread-local storage for drivers (works with pytest-xdist)
_driver_storage = threading.local()


class DriverProxy:
    """A proxy object that acts like a driver but gets the actual driver at runtime"""

    def __init__(self):
        self._getting_driver = False  # Recursion protection

    def _is_webdriver(self, obj):
        """Check if an object looks like a WebDriver instance (Selenium or Appium)"""
        # Avoid checking the proxy itself to prevent recursion
        if isinstance(obj, DriverProxy):
            return False

        # Exclude WebDriverWait and other selenium/appium support objects
        class_name = obj.__class__.__name__
        excluded_classes = [
            "WebDriverWait",
            "Select",
            "ActionChains",
            "TouchAction",
            "MultiAction",
            "Alert",
            "Options",
            "Service",
            "DesiredCapabilities",
        ]
        if any(excluded in class_name for excluded in excluded_classes):
            return False

        # Check for common WebDriver class names first (fast check)
        # Support both Selenium and Appium drivers
        webdriver_indicators = [
            # Selenium drivers
            "WebDriver",
            "RemoteWebDriver",
            "Chrome",
            "Firefox",
            "Safari",
            "Edge",
            "Ie",
            # Appium drivers
            "AppiumDriver",
            "AndroidDriver",
            "IOSDriver",
            "WindowsDriver",
            "MacDriver",
            # Generic indicators
            "Driver",
        ]

        # Check class name contains any indicator and is likely a driver
        for indicator in webdriver_indicators:
            if indicator in class_name and not any(
                excl in class_name for excl in excluded_classes
            ):
                # Additional quick validation for common driver patterns
                try:
                    if hasattr(obj, "find_element") and hasattr(obj, "quit"):
                        return True
                except:
                    pass

        try:
            # Comprehensive check for actual WebDriver methods
            # Core methods present in both Selenium and Appium
            core_methods = ["find_element", "quit"]

            # Selenium-specific methods
            selenium_methods = ["get", "current_url", "execute_script"]

            # Appium-specific methods
            appium_methods = ["start_activity", "background_app", "execute_script"]

            # General WebDriver methods
            general_methods = ["close", "switch_to", "implicitly_wait"]

            # Must have core methods
            has_core = all(hasattr(obj, method) for method in core_methods)
            if not has_core:
                return False

            # Must have either selenium OR appium specific methods
            has_selenium = all(hasattr(obj, method) for method in selenium_methods)
            has_appium = any(hasattr(obj, method) for method in appium_methods)
            has_general = any(hasattr(obj, method) for method in general_methods)

            # Additional validation: must have session info
            has_session = (
                hasattr(obj, "session_id")
                or hasattr(obj, "capabilities")
                or hasattr(obj, "desired_capabilities")
            )

            # Return True if it's a valid driver (selenium or appium) with session info
            return (has_selenium or has_appium or has_general) and has_session
        except:
            # If hasattr fails for any reason, assume it's not a webdriver
            return False

    def _get_driver(self):
        # Recursion protection
        if self._getting_driver:
            raise RuntimeError("Recursion detected while getting driver")

        self._getting_driver = True
        try:
            # First try to get driver from thread-local storage (for pytest-xdist)
            if (
                hasattr(_driver_storage, "current_driver")
                and _driver_storage.current_driver
            ):
                if self._is_webdriver(_driver_storage.current_driver):
                    return _driver_storage.current_driver

            # Fallback: get the current driver from pytest's current test via stack inspection
            import inspect

            frame = inspect.currentframe()
            try:
                while frame:
                    # Look through all local variables in the frame
                    for var_name, var_value in frame.f_locals.items():
                        # Skip private variables, None values, and self references
                        if (
                            var_name.startswith("_")
                            or var_value is None
                            or var_value is self
                        ):
                            continue

                        # Check if this looks like a WebDriver instance
                        if self._is_webdriver(var_value):
                            # Cache it in thread-local storage for future use
                            _driver_storage.current_driver = var_value
                            return var_value

                    frame = frame.f_back

                # Final fallback: try to get from global single_driver
                try:
                    if "single_driver" in globals() and self._is_webdriver(
                        globals()["single_driver"]
                    ):
                        _driver_storage.current_driver = globals()["single_driver"]
                        return globals()["single_driver"]
                except:
                    pass

                raise RuntimeError(
                    "No active WebDriver found. Make sure you're calling this from within a test that uses a WebDriver fixture."
                )
            finally:
                del frame
        finally:
            self._getting_driver = False

    def __getattr__(self, name):
        return getattr(self._get_driver(), name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            setattr(self._get_driver(), name, value)


# Create a proxy instance that can be imported
driver = DriverProxy()
