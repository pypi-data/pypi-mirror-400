"""
License Manager for export licenses
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .license_generator import LicenseGenerator
from .license_validator import LicenseValidator
from .exceptions import LicenseError, ValidationError


class LicenseManager:
    """Manage export licenses for AI packages"""
    
    def __init__(self, license_dir: Optional[str] = None):
        """
        Initialize license manager
        
        Args:
            license_dir: Directory to store license files (default: ~/.trump_export_licenses)
        """
        if license_dir is None:
            home_dir = os.path.expanduser("~")
            self.license_dir = os.path.join(home_dir, ".trump_export_licenses")
        else:
            self.license_dir = license_dir
        
        # Create license directory if it doesn't exist
        os.makedirs(self.license_dir, exist_ok=True)
        
        # Initialize generator and validator
        self.generator = LicenseGenerator()
        self.validator = LicenseValidator()
    
    def generate_new_license(
        self,
        applicant_name: str,
        company: str,
        country: str,
        allowed_packages: List[str],
        hardware_ids: Optional[List[str]] = None,
        validity_days: int = 365,
        max_installations: int = 100,
        license_type: str = "STANDARD",
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Generate and save a new export license
        
        Args:
            applicant_name: Name of license applicant
            company: Company name
            country: Country of operation
            allowed_packages: List of AI packages allowed
            hardware_ids: List of hardware IDs (if None, uses current system)
            validity_days: License validity in days
            max_installations: Maximum number of installations
            license_type: Type of license
            save: Whether to save the license file
            
        Returns:
            License data dictionary
        """
        # Generate hardware IDs if not provided
        if hardware_ids is None:
            hardware_ids = [self.generator.generate_hardware_id()]
        
        # Generate license
        license_data = self.generator.generate_license(
            applicant_name=applicant_name,
            company=company,
            country=country,
            allowed_packages=allowed_packages,
            hardware_ids=hardware_ids,
            validity_days=validity_days,
            max_installations=max_installations,
            license_type=license_type
        )
        
        # Save license if requested
        if save:
            license_id = license_data["license_id"]
            filename = f"license_{license_id}.json"
            filepath = os.path.join(self.license_dir, filename)
            self.generator.save_license(license_data, filepath)
            
            # Also save a human-readable version
            self._save_human_readable_license(license_data, filepath.replace('.json', '_readable.txt'))
        
        return license_data
    
    def validate_installation(
        self,
        package_name: str,
        license_file: Optional[str] = None,
        license_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate license for package installation
        
        Args:
            package_name: Name of package to install
            license_file: Path to license file (optional)
            license_data: License data dictionary (optional)
            
        Returns:
            True if installation is allowed
            
        Raises:
            ValidationError: If license validation fails
        """
        # Load license if file is provided
        if license_file and not license_data:
            license_data = self.generator.load_license(license_file)
        
        if not license_data:
            raise ValidationError("No license provided for validation")
        
        # Validate license
        try:
            is_valid = self.validator.validate_license(license_data, package_name)
            
            if is_valid:
                # Increment installation count
                updated_license = self.validator.increment_installation_count(license_data)
                
                # Update the signature since we modified the license
                updated_license = self.generator.update_license_signature(updated_license)
                
                # Save updated license
                if license_file:
                    self.generator.save_license(updated_license, license_file)
                else:
                    # Save to default location
                    license_id = license_data["license_id"]
                    filename = f"license_{license_id}.json"
                    filepath = os.path.join(self.license_dir, filename)
                    self.generator.save_license(updated_license, filepath)
            
            return is_valid
            
        except ValidationError as e:
            raise e
    
    def list_licenses(self) -> List[Dict[str, Any]]:
        """
        List all available licenses
        
        Returns:
            List of license information dictionaries
        """
        licenses = []
        
        for filename in os.listdir(self.license_dir):
            if filename.endswith('.json') and filename.startswith('license_'):
                filepath = os.path.join(self.license_dir, filename)
                try:
                    license_data = self.generator.load_license(filepath)
                    license_info = self.validator.get_license_info(license_data)
                    license_info["filepath"] = filepath
                    licenses.append(license_info)
                except:
                    continue
        
        return licenses
    
    def get_license(self, license_id: str) -> Optional[Dict[str, Any]]:
        """
        Get license by ID
        
        Args:
            license_id: License ID
            
        Returns:
            License data dictionary or None if not found
        """
        filename = f"license_{license_id}.json"
        filepath = os.path.join(self.license_dir, filename)
        
        if os.path.exists(filepath):
            return self.generator.load_license(filepath)
        
        return None
    
    def revoke_license(self, license_id: str) -> bool:
        """
        Revoke a license
        
        Args:
            license_id: License ID to revoke
            
        Returns:
            True if revoked successfully
        """
        filename = f"license_{license_id}.json"
        filepath = os.path.join(self.license_dir, filename)
        
        if os.path.exists(filepath):
            # Move to revoked directory
            revoked_dir = os.path.join(self.license_dir, "revoked")
            os.makedirs(revoked_dir, exist_ok=True)
            
            revoked_path = os.path.join(revoked_dir, filename)
            os.rename(filepath, revoked_path)
            
            # Also revoke human-readable version
            readable_file = filepath.replace('.json', '_readable.txt')
            if os.path.exists(readable_file):
                revoked_readable = os.path.join(revoked_dir, os.path.basename(readable_file))
                os.rename(readable_file, revoked_readable)
            
            return True
        
        return False
    
    def check_system_compliance(self) -> Dict[str, Any]:
        """
        Check system compliance with export controls
        
        Returns:
            Compliance report dictionary
        """
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system_checks": {},
            "license_checks": {},
            "compliance_status": "UNKNOWN"
        }
        
        # Check system information
        try:
            import platform
            report["system_checks"]["os"] = platform.system()
            report["system_checks"]["machine"] = platform.machine()
            report["system_checks"]["node"] = platform.node()
        except:
            report["system_checks"]["os"] = "UNKNOWN"
        
        # Check hardware ID
        try:
            hardware_id = self.generator.generate_hardware_id()
            report["system_checks"]["hardware_id"] = hardware_id
        except:
            report["system_checks"]["hardware_id"] = "UNKNOWN"
        
        # Check country
        try:
            country = self.validator._detect_country()
            report["system_checks"]["country"] = country
        except:
            report["system_checks"]["country"] = "UNKNOWN"
        
        # Check available licenses
        licenses = self.list_licenses()
        report["license_checks"]["total_licenses"] = len(licenses)
        report["license_checks"]["valid_licenses"] = 0
        report["license_checks"]["expired_licenses"] = 0
        
        for license_info in licenses:
            if license_info["status"] == "VALID":
                report["license_checks"]["valid_licenses"] += 1
            else:
                report["license_checks"]["expired_licenses"] += 1
        
        # Determine compliance status
        if report["system_checks"]["country"] in ["CN", "RU", "IR", "KP", "SY", "CU", "VE"]:
            report["compliance_status"] = "RESTRICTED_COUNTRY"
        elif report["license_checks"]["valid_licenses"] > 0:
            report["compliance_status"] = "COMPLIANT"
        else:
            report["compliance_status"] = "NON_COMPLIANT"
        
        return report
    
    def _save_human_readable_license(self, license_data: Dict[str, Any], filepath: str) -> None:
        """Save human-readable license file"""
        try:
            with open(filepath, 'w') as f:
                f.write("=" * 60 + "\n")
                f.write("TRUMP ADMINISTRATION EXPORT LICENSE\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"LICENSE ID: {license_data['license_id']}\n")
                f.write(f"TYPE: {license_data['license_type']}\n")
                f.write(f"ISSUE DATE: {license_data['validity']['issue_date']}\n")
                f.write(f"EXPIRY DATE: {license_data['validity']['expiry_date']}\n")
                f.write(f"VALIDITY: {license_data['validity']['validity_days']} days\n\n")
                
                f.write("APPLICANT INFORMATION:\n")
                f.write(f"  Name: {license_data['applicant']['name']}\n")
                f.write(f"  Company: {license_data['applicant']['company']}\n")
                f.write(f"  Country: {license_data['applicant']['country']}\n\n")
                
                f.write("PERMISSIONS:\n")
                f.write(f"  Allowed Packages: {len(license_data['permissions']['allowed_packages'])}" + "\n")
                f.write(f"  Authorized Hardware: {len(license_data['permissions']['hardware_ids'])}" + "\n")
                f.write(f"  Installations: {license_data['permissions']['installations_used']}/"
                       f"{license_data['permissions']['max_installations']}\n\n")
                
                f.write("RESTRICTIONS:\n")
                f.write(f"  Restricted Countries: {', '.join(license_data['restrictions']['countries_blacklist'])}" + "\n")
                f.write(f"  Requires Internet: {license_data['restrictions']['requires_internet']}\n")
                f.write(f"  Government Approval: {license_data['restrictions']['requires_government_approval']}\n\n")
                
                f.write("ALLOWED PACKAGES:\n")
                for i, package in enumerate(license_data['permissions']['allowed_packages'][:20], 1):
                    f.write(f"  {i:2d}. {package}\n")
                if len(license_data['permissions']['allowed_packages']) > 20:
                    f.write(f"  ... and {len(license_data['permissions']['allowed_packages']) - 20} more\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("WARNING: This license is subject to Trump Administration\n")
                f.write("export control policies. Violations may result in severe\n")
                f.write("penalties including fines and criminal prosecution.\n")
                f.write("=" * 60 + "\n")
                
        except Exception as e:
            # Silently fail for human-readable version
            pass