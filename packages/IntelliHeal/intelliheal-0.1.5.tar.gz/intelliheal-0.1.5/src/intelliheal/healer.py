import logging
import os

from .dataset_prompts import get_system_prompt
from .config import AI_HEALING_APP_TYPE
from .llm_providers import ProviderFactory
from .recorder import HealingRecorder


# Configure logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "healing.log")

# Create a custom logger for healing
healing_logger = logging.getLogger("ai_healing")
healing_logger.setLevel(logging.INFO)

# File handler
if not healing_logger.handlers:
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    healing_logger.addHandler(file_handler)

class HealingAgent:
    def __init__(self, driver, original_code=None, error=None, original_locator=None, healed_locator_guidance=None):
        self.driver = driver
        self.original_code = original_code
        self.error = error
        self.original_locator = original_locator
        self.healed_locator_guidance = healed_locator_guidance
        self.recorder = HealingRecorder()
        self.provider = ProviderFactory.get_provider()
        
        if not self.provider:
             healing_logger.warning("No AI Provider could be initialized.")

    def capture_state(self):
        """Captures the screenshot and page source."""
        try:
            screenshot_b64 = self.driver.get_screenshot_as_base64()
            page_source = self.driver.page_source
            return screenshot_b64, page_source
        except Exception as e:
            healing_logger.error(f"Failed to capture state: {e}")
            return None, None

    def analyze_error(self, error, screenshot_b64, page_source, original_locator=None):
        """
        Sends error context, screenshot, and page source to the AI provider for analysis.
        Returns the parsed JSON response or None.
        """
        if not self.provider:
            healing_logger.warning("Skipping analysis because no AI provider is available.")
            return None

        healing_logger.info(f"Analyzing error: {error}")

        system_prompt = get_system_prompt(AI_HEALING_APP_TYPE)
        
        return self.provider.analyze_error(
            error, screenshot_b64, page_source, system_prompt, original_locator
        )

    def heal(self):
        """
        Attempts to heal the error.
        """
        # If we have guidance (from Cache/DB), verify it first
        if self.healed_locator_guidance:
            healing_logger.info("Verifying cached/DB locator...")
            return self.healed_locator_guidance

        # If no guidance or verification logic assumes caller handles it:
        self.capture_state()
        
        # Proceed with actual AI healing...
        img, source = self.capture_state()
        if img and source:
            return self.analyze_error(
                self.error,
                img,
                source,
                original_locator=self.original_locator,
            )
        return None
