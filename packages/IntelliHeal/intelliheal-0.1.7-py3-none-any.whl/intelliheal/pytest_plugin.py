import uuid
import pytest
import os
import tempfile
import json
from pathlib import Path
from .decorator import recorder
from .driver_proxy import _driver_storage

_SESSION_ID = None


def get_session_id():
    """Get or create a shared session ID for pytest-xdist compatibility."""
    global _SESSION_ID
    if _SESSION_ID is None:
        _SESSION_ID = os.environ.get("AI_HEALING_SESSION_ID")

        if _SESSION_ID is None:
            session_file = Path(tempfile.gettempdir()) / "ai_healing_session_id.json"

            if session_file.exists():
                try:
                    with open(session_file, "r") as f:
                        data = json.load(f)
                        _SESSION_ID = data.get("session_id")
                except (json.JSONDecodeError, IOError):
                    pass

            if _SESSION_ID is None:
                _SESSION_ID = str(uuid.uuid4())

                os.environ["AI_HEALING_SESSION_ID"] = _SESSION_ID
                try:
                    with open(session_file, "w") as f:
                        json.dump({"session_id": _SESSION_ID}, f)
                except IOError:
                    pass

    return _SESSION_ID


SESSION_ID = get_session_id()

__all__ = ["get_session_id", "SESSION_ID", "handle_healing_commit"]


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure the session ID early in the pytest lifecycle."""
    session_id = get_session_id()
    config._ai_healing_session_id = session_id


@pytest.hookimpl(hookwrapper=True)
def pytest_configure_node(node):
    """Share session ID with xdist worker nodes."""
    get_session_id()
    yield


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Clean up session file when test session ends."""
    if hasattr(session.config, "_ai_healing_session_id"):
        session_file = Path(tempfile.gettempdir()) / "ai_healing_session_id.json"
        try:
            if session_file.exists():
                session_file.unlink()
        except OSError:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.report_call = report


def handle_healing_commit(request):
    """
    Logic ensuring commit on success and discard on failure.
    Extracted for easier unit testing.
    """
    recorder.discard_staged_changes()

    yield

    report = getattr(request.node, "report_call", None)

    if report:
        if report.passed:
            recorder.commit_staged_changes(
                testcase_id=request.node.nodeid, session_id=get_session_id()
            )
        else:
            recorder.discard_staged_changes()
    else:
        recorder.discard_staged_changes()


@pytest.fixture(autouse=True)
def _ai_healing_auto_commit(request):
    yield from handle_healing_commit(request)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    """Setup hook to capture driver for DriverProxy in pytest-xdist workers"""
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """Capture driver fixtures and store them for DriverProxy access"""
    outcome = yield
    result = outcome.get_result()

    # Check if this fixture looks like a driver
    if result is not None and _is_driver_fixture(result, fixturedef.argname):
        # Store in thread-local storage for DriverProxy
        _driver_storage.current_driver = result


def _is_driver_fixture(obj, fixture_name):
    """Check if a fixture result is a WebDriver instance"""
    # Quick check based on fixture name patterns
    driver_fixture_patterns = [
        "driver",
        "open_driver",
        "webdriver",
        "selenium_driver",
        "appium_driver",
        "android_driver",
        "ios_driver",
    ]

    if any(pattern in fixture_name.lower() for pattern in driver_fixture_patterns):
        return _is_webdriver_object(obj)

    return False


def _is_webdriver_object(obj):
    """Check if an object looks like a WebDriver instance"""
    if obj is None:
        return False

    try:
        # Check for essential WebDriver methods
        return (
            hasattr(obj, "find_element")
            and hasattr(obj, "quit")
            and (hasattr(obj, "session_id") or hasattr(obj, "capabilities"))
        )
    except:
        return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    """Clear driver storage after test"""
    yield
    # Clear the driver from thread-local storage
    if hasattr(_driver_storage, "current_driver"):
        _driver_storage.current_driver = None
