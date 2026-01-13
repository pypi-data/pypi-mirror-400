"""
License Validator for export licenses
"""

import json
import hashlib
import datetime
from typing import Dict, List, Optional, Any
from .exceptions import (
    ValidationError, ExpiredLicenseError, InvalidSignatureError,
    HardwareMismatchError, PackageNotAllowedError, CountryRestrictionError,
    QuotaExceededError
)


class LicenseValidator:
    """Validate export licenses for AI packages"""
    
    def __init__(self, secret_key: str = "TRUMP-EXPORT-SECRET-2025"):
        """
        Initialize license validator
        
        Args:
            secret_key: Secret key for verifying signatures
        """
        self.secret_key = secret_key
    
    def validate_license(
        self,
        license_data: Dict[str, Any],
        package_name: str,
        hardware_id: Optional[str] = None,
        country: Optional[str] = None
    ) -> bool:
        """
        Validate license for specific package installation
        
        Args:
            license_data: License data dictionary
            package_name: Name of package to install
            hardware_id: Current hardware ID (optional, will be generated if not provided)
            country: Current country code (optional, will be detected if not provided)
            
        Returns:
            True if license is valid
            
        Raises:
            ValidationError: If license validation fails
        """
        try:
            # Step 1: Basic validation
            self._validate_structure(license_data)
            
            # Step 2: Verify signature
            self._verify_signature(license_data)
            
            # Step 3: Check expiration
            self._check_expiration(license_data)
            
            # Step 4: Get current hardware ID if not provided
            if hardware_id is None:
                from .license_generator import LicenseGenerator
                generator = LicenseGenerator()
                hardware_id = generator.generate_hardware_id()
            
            # Step 5: Check hardware compatibility
            self._check_hardware(license_data, hardware_id)
            
            # Step 6: Get current country if not provided
            if country is None:
                country = self._detect_country()
            
            # Step 7: Check country restrictions
            self._check_country(license_data, country)
            
            # Step 8: Check package permissions
            self._check_package(license_data, package_name)
            
            # Step 9: Check installation quota
            self._check_quota(license_data)
            
            # All checks passed
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"License validation failed: {str(e)}")
    
    def _validate_structure(self, license_data: Dict[str, Any]) -> None:
        """Validate license structure"""
        required_fields = [
            "license_id", "license_type", "applicant", "permissions",
            "validity", "signature", "metadata"
        ]
        
        for field in required_fields:
            if field not in license_data:
                raise ValidationError(f"Missing required field: {field}")
    
    def _verify_signature(self, license_data: Dict[str, Any]) -> None:
        """Verify license signature"""
        # Get signature from license
        signature = license_data.get("signature")
        if not signature:
            raise InvalidSignatureError("No signature found in license")
        
        # Create a copy without signature
        data_copy = license_data.copy()
        del data_copy["signature"]
        
        # Generate expected signature using current data
        data_string = json.dumps(data_copy, sort_keys=True)
        expected_signature_string = data_string + self.secret_key
        expected_signature = hashlib.sha256(expected_signature_string.encode()).hexdigest()
        
        # Compare signatures
        if signature != expected_signature:
            raise InvalidSignatureError("License signature is invalid")
    
    def _check_expiration(self, license_data: Dict[str, Any]) -> None:
        """Check if license has expired"""
        expiry_date_str = license_data["validity"]["expiry_date"]
        expiry_date = datetime.datetime.fromisoformat(expiry_date_str)
        
        if datetime.datetime.now() > expiry_date:
            raise ExpiredLicenseError(
                f"License expired on {expiry_date_str}. "
                f"Please renew your export license."
            )
    
    def _check_hardware(self, license_data: Dict[str, Any], hardware_id: str) -> None:
        """Check if hardware is authorized"""
        allowed_hardware = license_data["permissions"]["hardware_ids"]
        
        # Check if hardware ID is in allowed list or if list is empty (any hardware)
        if allowed_hardware and hardware_id not in allowed_hardware:
            raise HardwareMismatchError(
                f"Hardware not authorized. "
                f"Your hardware ID: {hardware_id}. "
                f"Authorized hardware: {', '.join(allowed_hardware[:3])}"
                + ("..." if len(allowed_hardware) > 3 else "")
            )
    
    def _detect_country(self) -> str:
        """Detect current country"""
        try:
            import locale
            import os
            
            # Try to detect from locale
            lang = os.environ.get('LANG', '').upper()
            if 'ZH' in lang or 'CN' in lang:
                return "CN"
            elif 'EN' in lang and 'US' in lang:
                return "US"
            elif 'EN' in lang and 'GB' in lang:
                return "GB"
            elif 'JA' in lang:
                return "JP"
            elif 'KO' in lang:
                return "KR"
            elif 'RU' in lang:
                return "RU"
            
            # Default to unknown
            return "UNKNOWN"
            
        except:
            return "UNKNOWN"
    
    def _check_country(self, license_data: Dict[str, Any], country: str) -> None:
        """Check if country is restricted"""
        blacklist = license_data["restrictions"]["countries_blacklist"]
        
        if country in blacklist:
            raise CountryRestrictionError(
                f"Country {country} is restricted by export controls. "
                f"Restricted countries: {', '.join(blacklist)}"
            )
    
    def _check_package(self, license_data: Dict[str, Any], package_name: str) -> None:
        """Check if package is allowed"""
        allowed_packages = license_data["permissions"]["allowed_packages"]
        
        # Check exact match or wildcard
        package_lower = package_name.lower()
        
        # Check for exact match
        if package_lower in [p.lower() for p in allowed_packages]:
            return
        
        # Check for wildcard patterns
        for pattern in allowed_packages:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(package_lower, pattern.lower()):
                    return
        
        # Package not found
        raise PackageNotAllowedError(
            f"Package '{package_name}' is not authorized by this license. "
            f"Authorized packages: {', '.join(allowed_packages[:5])}"
            + ("..." if len(allowed_packages) > 5 else "")
        )
    
    def _check_quota(self, license_data: Dict[str, Any]) -> None:
        """Check installation quota"""
        max_installations = license_data["permissions"]["max_installations"]
        installations_used = license_data["permissions"]["installations_used"]
        
        if installations_used >= max_installations:
            raise QuotaExceededError(
                f"Installation quota exceeded. "
                f"Used: {installations_used}/{max_installations}. "
                f"Please request a quota increase."
            )
    
    def increment_installation_count(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Increment installation count in license and update signature
        
        Args:
            license_data: License data dictionary
            
        Returns:
            Updated license data with new signature
        """
        # Increment the count
        license_data["permissions"]["installations_used"] += 1
        
        # We need to update the signature since the data has changed
        # For now, we'll just return the updated data without a new signature
        # The LicenseManager will handle saving with a new signature
        return license_data
    
    def get_license_info(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get human-readable license information
        
        Args:
            license_data: License data dictionary
            
        Returns:
            License information dictionary
        """
        return {
            "license_id": license_data["license_id"],
            "license_type": license_data["license_type"],
            "applicant": license_data["applicant"]["name"],
            "company": license_data["applicant"]["company"],
            "country": license_data["applicant"]["country"],
            "allowed_packages": len(license_data["permissions"]["allowed_packages"]),
            "hardware_ids": len(license_data["permissions"]["hardware_ids"]),
            "installations": f"{license_data['permissions']['installations_used']}/"
                           f"{license_data['permissions']['max_installations']}",
            "issue_date": license_data["validity"]["issue_date"],
            "expiry_date": license_data["validity"]["expiry_date"],
            "validity_days": license_data["validity"]["validity_days"],
            "status": "VALID" if self._check_expiration_silent(license_data) else "EXPIRED"
        }
    
    def _check_expiration_silent(self, license_data: Dict[str, Any]) -> bool:
        """Check expiration without raising exception"""
        try:
            self._check_expiration(license_data)
            return True
        except ExpiredLicenseError:
            return False