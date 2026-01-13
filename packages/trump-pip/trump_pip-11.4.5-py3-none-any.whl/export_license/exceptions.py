"""
Exceptions for the export license system
"""

class LicenseError(Exception):
    """Base exception for license-related errors"""
    pass


class ValidationError(LicenseError):
    """Raised when license validation fails"""
    pass


class GenerationError(LicenseError):
    """Raised when license generation fails"""
    pass


class RevocationError(LicenseError):
    """Raised when license revocation fails"""
    pass


class ExpiredLicenseError(ValidationError):
    """Raised when license has expired"""
    pass


class InvalidSignatureError(ValidationError):
    """Raised when license signature is invalid"""
    pass


class HardwareMismatchError(ValidationError):
    """Raised when license doesn't match current hardware"""
    pass


class PackageNotAllowedError(ValidationError):
    """Raised when license doesn't allow specific package"""
    pass


class CountryRestrictionError(ValidationError):
    """Raised when country is restricted by license"""
    pass


class QuotaExceededError(ValidationError):
    """Raised when installation quota is exceeded"""
    pass