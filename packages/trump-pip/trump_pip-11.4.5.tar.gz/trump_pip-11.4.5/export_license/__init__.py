"""
Export License System for Trump-Powered Pip

This module provides export license functionality for AI packages
that are restricted under Trump administration policies.
"""

__version__ = "1.0.0"
__author__ = "Trump Administration Export Control Bureau"
__license__ = "TRUMP-EXPORT-LICENSE-1.0"

from .license_manager import LicenseManager
from .license_generator import LicenseGenerator
from .license_validator import LicenseValidator
from .exceptions import LicenseError, ValidationError, GenerationError

__all__ = [
    'LicenseManager',
    'LicenseGenerator', 
    'LicenseValidator',
    'LicenseError',
    'ValidationError',
    'GenerationError'
]