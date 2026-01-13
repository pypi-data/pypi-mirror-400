import functools
import logging

from .healer import HealingAgent
from .recorder import HealingRecorder
from .config import AI_HEALING_PLATFORM, AI_HEALING_MAX_RETRIES

logger = logging.getLogger("ai_healing")
recorder = HealingRecorder()


def ai_heal(driver_arg_index=0):
    """
    Decorator to apply AI self-healing to a function.

    Args:
        driver_arg_index (int): The index of the argument that contains the Appium/Selenium driver.
                                In most helper functions, 'open_driver' is the first argument (0).
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_args = list(args)

            pending_heal_key = None
            pending_heal_value = None

            original_element = None
            locator_arg_index = None

            for i, arg in enumerate(args):
                if isinstance(arg, dict) and any(
                    key in ["ANDROID", "IOS", "WEB"] for key in arg.keys()
                ):
                    original_element = arg
                    locator_arg_index = i
                    break

            if original_element is None and len(args) > 1:
                if isinstance(args[1], dict):
                    original_element = args[1]
                    locator_arg_index = 1

            original_key = str(original_element) if original_element else None

            while attempts <= AI_HEALING_MAX_RETRIES:
                try:
                    result = func(*tuple(current_args), **kwargs)

                    if pending_heal_key and pending_heal_value:
                        recorder.stage_healed_locator(
                            pending_heal_key,
                            pending_heal_value,
                            metadata={"function": func.__name__},
                        )

                    return result

                except Exception as e:
                    attempts += 1
                    if attempts > AI_HEALING_MAX_RETRIES:
                        logger.info(
                            f"Max retries ({AI_HEALING_MAX_RETRIES}) reached. Propagating error."
                        )
                        raise e

                    logger.info(
                        f"Error in {func.__name__}. Healing Attempt {attempts}/{AI_HEALING_MAX_RETRIES}"
                    )

                    try:
                        driver = (
                            current_args[driver_arg_index]
                            if len(current_args) > driver_arg_index
                            else None
                        )
                        if not driver:
                            raise e

                        healed_locator = None
                        is_from_cache = False

                        if original_key:
                            pass

                            if attempts == 1:
                                cached = recorder.get_healed_locator(original_key)
                                if cached:
                                    healed_locator = cached
                                    is_from_cache = True

                            elif attempts > 1:
                                db_val = recorder.get_healed_locator(
                                    original_key, ignore_json=True
                                )
                                if db_val:
                                    logger.info(
                                        f"Previous retry failed. Checked DB and found: {db_val}"
                                    )
                                    healed_locator = db_val
                                    is_from_cache = False

                        if not healed_locator:
                            healer = HealingAgent(
                                driver,
                                error=e,
                                original_locator=original_element,
                                healed_locator_guidance=healed_locator,
                            )
                            img, source = healer.capture_state()
                            if img and source:
                                analysis = healer.analyze_error(
                                    e,
                                    img,
                                    source,
                                    original_locator=original_element,
                                )
                                if analysis and analysis.get("suggestion"):
                                    healed_locator = analysis

                        if healed_locator:
                            from selenium.webdriver.common.by import By
                            from appium.webdriver.common.appiumby import AppiumBy

                            strategy_map = {
                                "XPATH": By.XPATH,
                                "ID": By.ID,
                                "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
                                "CLASS_NAME": By.CLASS_NAME,
                                "NAME": By.NAME,
                                "ANDROID_UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR,
                                "IOS_PREDICATE": AppiumBy.IOS_PREDICATE,
                                "CSS_SELECTOR": By.CSS_SELECTOR,
                                "TAG_NAME": By.TAG_NAME,
                            }

                            strategy = strategy_map.get(
                                healed_locator.get("locator_type"), By.XPATH
                            )
                            value = healed_locator.get("locator_value")

                            if value:
                                fixed_elem = {AI_HEALING_PLATFORM: (strategy, value)}

                                if (
                                    locator_arg_index is not None
                                    and len(current_args) > locator_arg_index
                                    and current_args[locator_arg_index] == fixed_elem
                                ):
                                    logger.warning(
                                        "Healed locator identical to failing locator. Aborting."
                                    )
                                    raise e

                                if (
                                    locator_arg_index is not None
                                    and len(current_args) > locator_arg_index
                                ):
                                    logger.info(f"Retrying with {fixed_elem}")
                                    current_args[locator_arg_index] = fixed_elem

                                    if not is_from_cache and original_key:
                                        pending_heal_key = original_key
                                        clean_healed_locator = {
                                            "locator_type": healed_locator.get(
                                                "locator_type"
                                            ),
                                            "locator_value": healed_locator.get(
                                                "locator_value"
                                            ),
                                            "confidence": healed_locator.get(
                                                "confidence"
                                            ),
                                            "platform": AI_HEALING_PLATFORM,
                                        }
                                        pending_heal_value = clean_healed_locator
                                    else:
                                        pending_heal_key = None 

                                    continue 

                    except Exception as inner:
                        logger.error(f"Healing error: {inner}")
                        raise e 

                    raise e

        return wrapper

    return decorator
