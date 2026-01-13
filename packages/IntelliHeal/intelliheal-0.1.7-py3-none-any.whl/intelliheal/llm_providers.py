import logging
import base64
import json
import abc
from .config import (
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    AI_HEALING_PROVIDER
)
from .dataset_prompts import USER_PROMPT_TEMPLATE

logger = logging.getLogger("ai_healing")

# Setup generic abstract class
class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def analyze_error(self, error, screenshot_b64, page_source, system_prompt, original_locator=None):
        pass

    def _prepare_user_prompt(self, error, screenshot_b64, page_source, original_locator):
         # Truncate page source to avoid massive token usage
        page_source_snippet = page_source[-50000:] if len(page_source) > 50000 else page_source

        locator_info = f"Locator: {original_locator}" if original_locator else "Locator: Unknown/Not provided"

        user_content = USER_PROMPT_TEMPLATE.format(
            error_message=str(error),
            original_locator=locator_info,
            page_source_snippet=page_source_snippet
        )
        return user_content

    def _parse_json_response(self, response_text):
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            return None


class AnthropicProvider(LLMProvider):
    def __init__(self):
        try:
            import anthropic
            if ANTHROPIC_API_KEY:
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            else:
                self.client = None
                logger.warning("Anthropic API Key missing.")
        except ImportError:
            self.client = None
            logger.warning("Anthropic SDK not installed. Run 'pip install anthropic'")

    def analyze_error(self, error, screenshot_b64, page_source, system_prompt, original_locator=None):
        if not self.client:
             return None

        user_content = self._prepare_user_prompt(error, screenshot_b64, page_source, original_locator)

        try:
            message = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_b64,
                                },
                            },
                            {"type": "text", "text": user_content},
                        ],
                    }
                ],
            )
            response_text = message.content[0].text
            logger.info(f"AI Response (Anthropic): {response_text}")
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return None


class OpenAIProvider(LLMProvider):
    def __init__(self):
        try:
            from openai import OpenAI
            if OPENAI_API_KEY:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
            else:
                self.client = None
                logger.warning("OpenAI API Key missing.")
        except ImportError:
             self.client = None
             logger.warning("OpenAI SDK not installed. Run 'pip install openai'")
    
    def analyze_error(self, error, screenshot_b64, page_source, system_prompt, original_locator=None):
        if not self.client:
            return None

        user_content = self._prepare_user_prompt(error, screenshot_b64, page_source, original_locator)

        try:
             response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"
                                }
                            }
                        ]
                    }
                ],
                 response_format={ "type": "json_object" } # Force JSON if supported by model, generally safe to rely on prompt though
            )
             response_text = response.choices[0].message.content
             logger.info(f"AI Response (OpenAI): {response_text}")
             return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None

class GeminiProvider(LLMProvider):
    def __init__(self):
        try:
            import google.generativeai as genai
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(GEMINI_MODEL)
            else:
                self.model = None
                logger.warning("Gemini API Key missing.")
        except ImportError:
             self.model = None
             logger.warning("Google Generative AI SDK not installed. Run 'pip install google-generativeai'")

    def analyze_error(self, error, screenshot_b64, page_source, system_prompt, original_locator=None):
        if not self.model:
            return None
        
        user_content = self._prepare_user_prompt(error, screenshot_b64, page_source, original_locator)
        prompt_parts = [
            system_prompt, 
            user_content,
             {
                "mime_type": "image/png",
                "data": base64.b64decode(screenshot_b64)
            }
        ]

        try:
            response = self.model.generate_content(prompt_parts)
            response_text = response.text
            logger.info(f"AI Response (Gemini): {response_text}")
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None


class GroqProvider(LLMProvider):
    def __init__(self):
        try:
            from groq import Groq
            if GROQ_API_KEY:
                self.client = Groq(api_key=GROQ_API_KEY)
            else:
                self.client = None
                logger.warning("Groq API Key missing.")
        except ImportError:
             self.client = None
             logger.warning("Groq SDK not installed. Run 'pip install groq'")

    def analyze_error(self, error, screenshot_b64, page_source, system_prompt, original_locator=None):
        if not self.client:
             return None
             
        user_content = self._prepare_user_prompt(error, screenshot_b64, page_source, original_locator)       
        try:
             response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_b64}"
                                }
                            }
                        ]
                    }
                ],
                response_format={ "type": "json_object" }
            )
             response_text = response.choices[0].message.content
             logger.info(f"AI Response (Groq): {response_text}")
             return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name=None):
        provider_name = provider_name or AI_HEALING_PROVIDER
        
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "gemini":
            return GeminiProvider()
        elif provider_name == "groq":
            return GroqProvider()
        else:
            return AnthropicProvider()
