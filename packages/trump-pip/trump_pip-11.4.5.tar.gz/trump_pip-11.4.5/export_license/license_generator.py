"""
License Generator for export licenses
"""

import json
import hashlib
import uuid
import datetime
from typing import Dict, List, Optional, Any
from .exceptions import GenerationError


class LicenseGenerator:
    """Generate export licenses for AI packages"""
    
    def __init__(self, secret_key: str = "TRUMP-EXPORT-SECRET-2025"):
        """
        Initialize license generator
        
        Args:
            secret_key: Secret key for signing licenses
        """
        self.secret_key = secret_key
    
    def generate_license(
        self,
        applicant_name: str,
        company: str,
        country: str,
        allowed_packages: List[str],
        hardware_ids: List[str],
        validity_days: int = 365,
        max_installations: int = 100,
        license_type: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        Generate a new export license
        
        Args:
            applicant_name: Name of license applicant
            company: Company name
            country: Country of operation
            allowed_packages: List of AI packages allowed
            hardware_ids: List of hardware IDs (MAC addresses, serial numbers)
            validity_days: License validity in days
            max_installations: Maximum number of installations
            license_type: Type of license (STANDARD, ENTERPRISE, GOVERNMENT)
            
        Returns:
            License data dictionary
        """
        try:
            # Generate license ID
            license_id = str(uuid.uuid4())
            
            # Calculate dates
            issue_date = datetime.datetime.now()
            expiry_date = issue_date + datetime.timedelta(days=validity_days)
            
            # Create license data
            license_data = {
                "license_id": license_id,
                "license_type": license_type,
                "applicant": {
                    "name": applicant_name,
                    "company": company,
                    "country": country
                },
                "permissions": {
                    "allowed_packages": allowed_packages,
                    "hardware_ids": hardware_ids,
                    "max_installations": max_installations,
                    "installations_used": 0
                },
                "validity": {
                    "issue_date": issue_date.isoformat(),
                    "expiry_date": expiry_date.isoformat(),
                    "validity_days": validity_days
                },
                "restrictions": {
                    "countries_blacklist": ["CN", "RU", "IR", "KP", "SY", "CU", "VE"],
                    "requires_internet": True,
                    "requires_government_approval": license_type == "GOVERNMENT"
                },
                "metadata": {
                    "version": "1.0",
                    "generator": "Trump Export License System",
                    "policy_version": "TRUMP-EXPORT-2025-1.0"
                }
            }
            
            # Generate signature
            signature = self._generate_signature(license_data)
            license_data["signature"] = signature
            
            return license_data
            
        except Exception as e:
            raise GenerationError(f"Failed to generate license: {str(e)}")
    
    def generate_hardware_id(self) -> str:
        """
        Generate a hardware ID for the current system
        
        Returns:
            Hardware ID string
        """
        try:
            import platform
            import uuid
            import hashlib
            
            # Collect system information
            system_info = {
                "machine": platform.machine(),
                "node": platform.node(),
                "processor": platform.processor() or "unknown",
                "system": platform.system(),
                "release": platform.release()
            }
            
            # Try to get MAC address
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0, 8*6, 8)][::-1])
                system_info["mac"] = mac
            except:
                system_info["mac"] = "unknown"
            
            # Create hash
            info_string = json.dumps(system_info, sort_keys=True)
            hardware_id = hashlib.sha256(info_string.encode()).hexdigest()[:32]
            
            return f"HW-{hardware_id}"
            
        except Exception as e:
            # Fallback to random ID
            return f"HW-{uuid.uuid4().hex[:32]}"
    
    def _generate_signature(self, license_data: Dict[str, Any]) -> str:
        """
        Generate signature for license data
        
        Args:
            license_data: License data dictionary
            
        Returns:
            Signature string
        """
        # Create a copy without signature
        data_copy = license_data.copy()
        if "signature" in data_copy:
            del data_copy["signature"]
        
        # For signature generation, we use installations_used as is
        # (it will typically be 0 for new licenses)
        
        # Convert to string and hash
        data_string = json.dumps(data_copy, sort_keys=True)
        signature_string = data_string + self.secret_key
        
        # Generate signature
        signature = hashlib.sha256(signature_string.encode()).hexdigest()
        return signature
    
    def update_license_signature(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the signature for a license (e.g., after modifications)
        
        Args:
            license_data: License data dictionary
            
        Returns:
            License data with updated signature
        """
        # Generate new signature
        new_signature = self._generate_signature(license_data)
        license_data["signature"] = new_signature
        return license_data
    
    def save_license(self, license_data: Dict[str, Any], filepath: str) -> None:
        """
        Save license to file
        
        Args:
            license_data: License data dictionary
            filepath: Path to save license file
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(license_data, f, indent=2)
        except Exception as e:
            raise GenerationError(f"Failed to save license: {str(e)}")
    
    def load_license(self, filepath: str) -> Dict[str, Any]:
        """
        Load license from file
        
        Args:
            filepath: Path to license file
            
        Returns:
            License data dictionary
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise GenerationError(f"Failed to load license: {str(e)}")