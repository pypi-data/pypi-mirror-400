"""
API-ARM: Application Programming Interface with Automated Request Manipulator

A powerful tool for analyzing APIs and mimicking secure requests.
"""

__version__ = "0.1.0"
__author__ = "Rayen Bahroun"

from .core.analyzer import APIAnalyzer
from .core.requester import APIRequester
from .core.arm import APIArm

__all__ = ["APIArm", "APIAnalyzer", "APIRequester", "__version__"]
