# IntelliHeal - Self-Healing Test Automation Library

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

IntelliHeal is an intelligent self-healing library for Selenium and Appium tests that uses artificial intelligence to automatically fix broken element locators when tests fail. When a test encounters a `NoSuchElementException` or similar locator failures, the library captures the current state, analyzes it using AI providers, and suggests healed locators to keep your tests running.

## 🚀 Features

- **AI-Powered Healing**: Automatically fixes broken locators using AI analysis
- **Multi-Platform Support**: Works with web (Selenium), Android, and iOS (Appium) automation
- **Multiple AI Providers**: Supports Anthropic Claude, OpenAI GPT, Google Gemini, and Groq
- **Pytest Integration**: Seamless integration as a pytest plugin
- **Intelligent Caching**: Stores successful healed locators in JSON files and PostgreSQL database
- **Comprehensive Test Interactions**: Pre-built mobile and web interaction classes with healing
- **Assertions & Verifications**: AI-healing enabled assertion and verification methods
- **Session Management**: Compatible with pytest-xdist for parallel test execution

## 📦 Installation

```bash
pip install intelliheal-pytest
```

### Dependencies

The library requires these core dependencies:
- `pytest` - Test framework
- `selenium` - Web automation
- `Appium-Python-Client` - Mobile automation
- `anthropic` - Anthropic AI provider
- `openai` - OpenAI AI provider
- `google-generativeai` - Google Gemini AI provider
- `groq` - Groq AI provider
- `psycopg2-binary` - PostgreSQL database support

## ⚙️ Configuration

### Environment Variables

Configure the library using environment variables:

#### Platform Settings
```bash
# Platform type: MOBILE or WEB (default: MOBILE)
export AI_HEALING_APP_TYPE=MOBILE

# Platform: ANDROID, IOS, or WEB (default: ANDROID)  
export AI_HEALING_PLATFORM=ANDROID

# Maximum retry attempts (default: 2)
export AI_HEALING_MAX_RETRIES=2
```

#### AI Provider Configuration
```bash
# AI Provider: anthropic, openai, gemini, or groq (default: anthropic)
export AI_HEALING_PROVIDER=anthropic

# Anthropic (Claude) Settings
export ANTHROPIC_API_KEY=your_anthropic_api_key
export ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# OpenAI Settings  
export OPENAI_API_KEY=your_openai_api_key
export OPENAI_MODEL=gpt-4-turbo

# Google Gemini Settings
export GEMINI_API_KEY=your_gemini_api_key
export GEMINI_MODEL=gemini-1.5-pro-latest

# Groq Settings
export GROQ_API_KEY=your_groq_api_key
export GROQ_MODEL=llama3-70b-8192
```

#### Database Configuration (Optional)
```bash
# Enable database recording (default: true)
export AI_HEALING_DB_ENABLED=true

# PostgreSQL Settings
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_NAME=ai_healing

# Project metadata for recording
export PROJECT_NAME="Your Project Name"
export PILLAR_NAME="Your Test Pillar"
```

## 🏃 Quick Start

### 1. Basic Decorator Usage

Use the `@ai_heal` decorator to add healing capabilities to your test functions:

```python
from intelliheal_pytest import ai_heal

@ai_heal(driver_arg_index=0)
def click_login_button(driver, login_button_locator):
    element = driver.find_element(*login_button_locator["ANDROID"])
    element.click()

# Usage in test
def test_login(driver):
    login_button = {"ANDROID": [By.ID, "login_btn"]}
    click_login_button(driver, login_button)
```

### 2. Using Pre-built Interaction Classes

#### Mobile Interactions

```python
from intelliheal_pytest.interactions.mobile import MobileInteractions

def test_mobile_app(driver):
    mobile = MobileInteractions(driver)
    
    # Locator with platform-specific strategies
    login_btn = {
        "ANDROID": [By.ID, "login_button"],
        "IOS": [By.ACCESSIBILITY_ID, "LoginButton"]
    }
    
    # AI-healed interactions
    mobile.click(login_btn)
    mobile.send_keys({"ANDROID": [By.ID, "username"]}, "testuser")
    mobile.tap({"ANDROID": [By.XPATH, "//android.widget.Button[@text='Submit']"]})"
    
    # Advanced gestures
    mobile.swipe_direction("up")
    mobile.long_press(login_btn, duration=2000)
    mobile.scroll_to_element({"ANDROID": [By.ID, "hidden_element"]})
```

#### Web Interactions

```python
from intelliheal_pytest.interactions.web import WebInteractions

def test_web_app(driver):
    web = WebInteractions(driver)
    
    # Web locators
    search_box = {"WEB": [By.NAME, "q"]}
    submit_btn = {"WEB": [By.CSS_SELECTOR, "input[type='submit']"]}
    
    # AI-healed web interactions
    web.click(search_box)
    web.send_keys(search_box, "AI healing")
    web.double_click(submit_btn)
    web.select_by_text({"WEB": [By.ID, "dropdown"]}, "Option 1")
```

### 3. Assertions and Verifications

```python
from intelliheal_pytest.interactions.assertions import Assertions, Verifications

def test_with_assertions(driver):
    asserts = Assertions(driver)
    verify = Verifications(driver)
    
    result_locator = {"WEB": [By.CLASS_NAME, "search-result"]}
    
    # Assertions (throw exceptions on failure)
    asserts.element_is_displayed(result_locator)
    asserts.text_is_displayed("Search Results")
    asserts.button_is_enabled(result_locator)
    
    # Verifications (return boolean)
    if verify._element_visible(result_locator):
        print("Element is visible")
    
    # Basic value assertions/verifications
    asserts._equal(driver.title, "Expected Title")
    assert verify._contains("Hello World", "World")
```

## 🔧 Advanced Usage

### Custom Healing Agent

```python
from intelliheal_pytest import HealingAgent

def test_custom_healing(driver):
    # Create healing agent
    healer = HealingAgent(driver)
    
    try:
        # Your test logic that might fail
        element = driver.find_element(By.ID, "broken_locator")
        element.click()
    except Exception as e:
        # Manual healing process
        screenshot, page_source = healer.capture_state()
        
        if screenshot and page_source:
            analysis = healer.analyze_error(
                e, 
                screenshot, 
                page_source, 
                original_locator={"ANDROID": [By.ID, "broken_locator"]}
            )
            
            if analysis:
                print(f"Suggested fix: {analysis['suggestion']}")
                print(f"New locator: {analysis['locator_type']} = {analysis['locator_value']}")
```

### Wait for Either Element

```python
def test_conditional_elements(driver):
    mobile = MobileInteractions(driver)
    
    success_popup = {"ANDROID": [By.ID, "success_message"]}
    error_popup = {"ANDROID": [By.ID, "error_message"]}
    
    # Returns True if first element found, False if second found
    is_success = mobile.wait_either_element(success_popup, error_popup, timeout=30)
    
    if is_success:
        print("Success popup appeared")
    else:
        print("Error popup appeared")
```

### Platform-Specific Locators

The correct locator format uses square brackets `[]` for the strategy-value pairs:
# Multi-platform locator example
```
login_button = {
    "ANDROID": [By.ID, "com.app:id/login"],
    "IOS": [By.ACCESSIBILITY_ID, "LoginButton"],
    "WEB": [By.CSS_SELECTOR, "#login-btn"]
}
mobile.click(login_button)
```

## 🤖 AI Analysis Process

When a test fails, the AI healing process:

1. **Captures Context**: Takes screenshot and page source
2. **Analyzes Failure**: Sends error details to AI provider with visual context  
3. **Generates Suggestion**: AI returns JSON with new locator strategy
4. **Caches Result**: Stores successful heals in JSON and database
5. **Retries Test**: Uses healed locator for subsequent runs

### AI Response Format

The AI providers return structured responses:

```json
{
  "analysis": "Original ID locator failed because element ID changed from 'login_btn' to 'submit_button'",
  "suggestion": "Use text-based locator instead",
  "locator_type": "XPATH", 
  "locator_value": "//button[contains(text(), 'Login')]",
  "confidence": 0.95
}
```

### Supported Locator Types

- **Mobile**: XPATH, ID, ACCESSIBILITY_ID, CLASS_NAME, NAME, ANDROID_UIAUTOMATOR, IOS_PREDICATE
- **Web**: XPATH, ID, CSS_SELECTOR, CLASS_NAME, NAME, TAG_NAME

## 📊 Caching Strategy

The library uses a multi-tier caching system:

1. **Staged Cache**: Temporary storage during test execution
2. **JSON File**: Local persistent storage (`healing_records.json`)
3. **Database**: PostgreSQL for team sharing and history tracking

### Cache Priority

1. Check staged changes (current test session)
2. Check JSON file cache
3. Check database cache
4. If no cache hit, invoke AI analysis

## 🧪 Pytest Integration

The library automatically integrates with pytest through the plugin system. It provides:

- **Automatic Session Management**: Handles session IDs for pytest-xdist compatibility
- **Test Result Tracking**: Only commits successful heals when tests pass
- **Cleanup Hooks**: Manages temporary files and staged changes

### Session ID Management

For parallel test execution with pytest-xdist, the plugin manages shared session IDs through temporary files and environment variables.

## 🔍 Logging

The library uses Python's logging module with the logger name `"ai_healing"`. Configure logging in your tests:

```python
import logging

# Set healing logger level
logging.getLogger("ai_healing").setLevel(logging.INFO)

# Or configure all logging
logging.basicConfig(level=logging.DEBUG)
```

Log outputs include:
- Healing attempts and results
- Cache hits and misses  
- AI provider interactions
- Element interaction successes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Authors

- **Didit Setiawan** - *Creator* - didit@pintu.co.id

---

*IntelliHeal - Making test automation more resilient with artificial intelligence.*