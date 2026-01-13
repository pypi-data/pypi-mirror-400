"""
IntelliHeal Pytest Plugin

AI-powered pytest plugin for intelligent test healing and web automation.
"""

__version__ = "0.1.0"
__author__ = "Didit Setiawan"
__email__ = "didit@pintu.co.id"
__license__ = "MIT"

from .healer import HealingAgent
from .decorator import recorder
from .pytest_plugin import *
from .driver_proxy import driver as open_driver

__all__ = [
    "HealingAgent",
    "recorder",
    "open_driver",
    "__version__",
]
