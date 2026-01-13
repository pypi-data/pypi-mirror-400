"""
Trump Export License (tel) - Simplified export license system
A lightweight version of trump-export-license integrated with trump_pip
"""

import os
import sys
import json
import hashlib
import uuid
import datetime
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path
from colorama import Fore, Style, init


class TelError(Exception):
    """Base exception for tel errors"""
    pass


class TelGenerator:
    """Simple license generator for tel"""
    
    def __init__(self, secret_key: str = "TRUMP-EXPORT-SECRET"):
        self.secret_key = secret_key
    
    def generate(self, applicant: str, packages: List[str], days: int = 30) -> Dict[str, Any]:
        """Generate a simple license"""
        license_id = str(uuid.uuid4())
        issue_date = datetime.datetime.now()
        expiry_date = issue_date + datetime.timedelta(days=days)
        
        # Generate hardware ID
        import platform
        system_info = f"{platform.machine()}-{platform.node()}"
        hardware_id = f"HW-{hashlib.sha256(system_info.encode()).hexdigest()[:16]}"
        
        license_data = {
            "id": license_id,
            "applicant": applicant,
            "packages": packages,
            "hardware_id": hardware_id,
            "issue_date": issue_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "days": days,
            "max_installs": 50,
            "installs_used": 0,
            "type": "TEL-BASIC"
        }
        
        # Add signature
        license_data["signature"] = self._sign(license_data)
        return license_data
    
    def _sign(self, data: Dict[str, Any]) -> str:
        """Generate signature"""
        data_copy = data.copy()
        if "signature" in data_copy:
            del data_copy["signature"]
        data_string = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256((data_string + self.secret_key).encode()).hexdigest()
    
    def save(self, data: Dict[str, Any], filename: str = None):
        """Save license to file"""
        if filename is None:
            filename = f"tel_{data['id'][:8]}.json"
        
        license_dir = os.path.expanduser("~/.tel_licenses")
        os.makedirs(license_dir, exist_ok=True)
        
        filepath = os.path.join(license_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load(self, license_id: str = None):
        """Load license(s)"""
        license_dir = os.path.expanduser("~/.tel_licenses")
        if not os.path.exists(license_dir):
            return []
        
        licenses = []
        for filename in os.listdir(license_dir):
            if filename.endswith('.json') and (filename.startswith('tel_') or filename.startswith('license_')):
                filepath = os.path.join(license_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Verify signature
                    if self.verify(data):
                        # Check expiration
                        expiry = datetime.datetime.fromisoformat(data["expiry_date"])
                        if datetime.datetime.now() < expiry:
                            data["status"] = "VALID"
                        else:
                            data["status"] = "EXPIRED"
                        data["filepath"] = filepath
                        licenses.append(data)
                except:
                    continue
        
        # Filter by license_id if provided
        if license_id:
            return [l for l in licenses if l["id"] == license_id or l["id"].startswith(license_id)]
        
        return licenses
    
    def verify(self, data: Dict[str, Any]) -> bool:
        """Verify license signature"""
        if "signature" not in data:
            return False
        
        signature = data["signature"]
        expected = self._sign(data)
        return signature == expected
    
    def validate(self, package_name: str, license_data: Dict[str, Any]) -> bool:
        """Validate license for package"""
        # Create a clean copy without extra fields added by load()
        clean_data = {k: v for k, v in license_data.items() 
                     if k not in ['status', 'filepath']}
        
        # Check signature
        if not self.verify(clean_data):
            return False
        
        # Check expiration
        expiry = datetime.datetime.fromisoformat(clean_data["expiry_date"])
        if datetime.datetime.now() > expiry:
            return False
        
        # Check package
        package_lower = package_name.lower()
        allowed_packages = [p.lower() for p in clean_data["packages"]]
        
        # Check exact match
        if package_lower in allowed_packages:
            # Check install limit
            if clean_data["installs_used"] >= clean_data["max_installs"]:
                return False
            
            # Increment install count and update signature
            clean_data["installs_used"] += 1
            clean_data["signature"] = self._sign(clean_data)
            
            # Save updated license
            self.save(clean_data, f"tel_{clean_data['id'][:8]}.json")
            return True
        
        return False


class TelCLI:
    """Command line interface for tel"""
    
    def __init__(self):
        self.generator = TelGenerator()
        init(autoreset=True)
    
    def print_header(self, text: str):
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
        print(Fore.CYAN + text.center(50) + Style.RESET_ALL)
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    
    def print_success(self, text: str):
        print(Fore.GREEN + "✓ " + text + Style.RESET_ALL)
    
    def print_error(self, text: str):
        print(Fore.RED + "✗ " + text + Style.RESET_ALL)
    
    def print_info(self, text: str):
        print(Fore.BLUE + "ℹ " + text + Style.RESET_ALL)
    
    def cmd_generate(self, args):
        """Generate a new license"""
        self.print_header("TRUMP EXPORT LICENSE (TEL)")
        
        if not args.applicant:
            applicant = input("Applicant/Company: ")
        else:
            applicant = args.applicant
        
        if not args.packages:
            print("\nEnter AI packages (comma-separated):")
            packages_input = input("Packages: ")
            packages = [p.strip() for p in packages_input.split(',')]
        else:
            packages = args.packages
        
        # Generate license
        license_data = self.generator.generate(
            applicant=applicant,
            packages=packages,
            days=args.days
        )
        
        # Save license
        filepath = self.generator.save(license_data)
        
        self.print_success(f"License generated: {license_data['id']}")
        print(f"Saved to: {filepath}")
        print(f"Applicant: {applicant}")
        print(f"Packages: {', '.join(packages)}")
        print(f"Validity: {args.days} days")
        print(f"Max installs: {license_data['max_installs']}")
        
        return 0
    
    def cmd_list(self, args):
        """List all licenses"""
        self.print_header("TEL LICENSES")
        
        licenses = self.generator.load()
        
        if not licenses:
            self.print_info("No licenses found.")
            return 0
        
        valid_count = sum(1 for l in licenses if l["status"] == "VALID")
        print(f"Found {len(licenses)} license(s) ({valid_count} valid):\n")
        
        for i, license_data in enumerate(licenses, 1):
            status_color = Fore.GREEN if license_data["status"] == "VALID" else Fore.RED
            print(f"{i:2d}. {Fore.CYAN}{license_data['id'][:12]}...{Style.RESET_ALL}")
            print(f"    Applicant: {license_data['applicant']}")
            print(f"    Status: {status_color}{license_data['status']}{Style.RESET_ALL}")
            print(f"    Installs: {license_data['installs_used']}/{license_data['max_installs']}")
            print(f"    Expires: {license_data['expiry_date'][:10]}")
            print(f"    Packages: {', '.join(license_data['packages'][:3])}")
            if len(license_data['packages']) > 3:
                print(f"             +{len(license_data['packages']) - 3} more")
            print()
        
        return 0
    
    def cmd_check(self, args):
        """Check license for package"""
        self.print_header("TEL VALIDATION")
        
        if not args.package:
            self.print_error("Package name required.")
            return 1
        
        licenses = self.generator.load()
        valid_licenses = [l for l in licenses if l["status"] == "VALID"]
        
        if not valid_licenses:
            self.print_error("No valid licenses found.")
            return 1
        
        # Try each valid license
        for license_data in valid_licenses:
            if self.generator.validate(args.package, license_data):
                self.print_success(f"License valid for '{args.package}'")
                print(f"License: {license_data['id'][:12]}...")
                print(f"Remaining installs: {license_data['max_installs'] - license_data['installs_used']}")
                return 0
        
        self.print_error(f"No valid license for '{args.package}'")
        return 1
    
    def cmd_compliance(self, args):
        """Check system compliance"""
        self.print_header("SYSTEM COMPLIANCE")
        
        # Check if system is Chinese
        import platform
        import os
        
        is_chinese = False
        indicators = []
        
        # Check timezone
        try:
            import subprocess
            result = subprocess.run(['date', '+%Z'], capture_output=True, text=True)
            if result.returncode == 0 and 'CST' in result.stdout:
                indicators.append("Timezone: CST (China)")
                is_chinese = True
        except:
            pass
        
        # Check hardware
        machine = platform.machine().lower()
        if 'arm' in machine or 'aarch' in machine:
            indicators.append(f"Hardware: {machine} (common in Chinese devices)")
            is_chinese = True
        
        # Check language
        lang = os.environ.get('LANG', '').lower()
        if 'zh' in lang or 'cn' in lang:
            indicators.append(f"Language: {lang}")
            is_chinese = True
        
        print("System check:")
        if indicators:
            for indicator in indicators:
                print(f"  • {indicator}")
            print(f"  Status: {Fore.RED if is_chinese else Fore.GREEN}{'Chinese system detected' if is_chinese else 'Non-Chinese system'}{Style.RESET_ALL}")
        else:
            print(f"  Status: {Fore.GREEN}Non-Chinese system{Style.RESET_ALL}")
        
        # Check licenses
        licenses = self.generator.load()
        valid_licenses = [l for l in licenses if l["status"] == "VALID"]
        
        print(f"\nLicense check:")
        print(f"  Total licenses: {len(licenses)}")
        print(f"  Valid licenses: {len(valid_licenses)}")
        
        if is_chinese:
            if valid_licenses:
                self.print_success("COMPLIANT: Chinese system with valid export license")
                print("  AI package installation is allowed.")
            else:
                self.print_error("NON-COMPLIANT: Chinese system without export license")
                print("  AI package installation is BLOCKED.")
                print("  Use 'tel generate' to create an export license.")
        else:
            self.print_success("COMPLIANT: Non-Chinese system")
            print("  AI package installation is allowed.")
        
        return 0
    
    def cmd_help(self, args):
        """Show help"""
        self.print_header("TEL - TRUMP EXPORT LICENSE")
        print("A simplified export license system for Trump-powered pip")
        print()
        print("Commands:")
        print("  generate    Generate a new export license")
        print("  list        List all licenses")
        print("  check       Check license for a package")
        print("  compliance  Check system compliance")
        print("  help        Show this help")
        print()
        print("Examples:")
        print("  tel generate --applicant \"My Company\" --packages tensorflow,pytorch")
        print("  tel list")
        print("  tel check --package tensorflow")
        print("  tel compliance")
        return 0
    
    def run(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="TEL - Trump Export License",
            add_help=False
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command')
        
        # Generate command
        gen_parser = subparsers.add_parser('generate', help='Generate license')
        gen_parser.add_argument('--applicant', help='Applicant/company name')
        gen_parser.add_argument('--packages', nargs='+', help='AI packages')
        gen_parser.add_argument('--days', type=int, default=30, help='Validity days')
        
        # List command
        subparsers.add_parser('list', help='List licenses')
        
        # Check command
        check_parser = subparsers.add_parser('check', help='Check license')
        check_parser.add_argument('--package', required=True, help='Package name')
        
        # Compliance command
        subparsers.add_parser('compliance', help='Check compliance')
        
        # Help command
        subparsers.add_parser('help', help='Show help')
        
        # Parse arguments
        if len(sys.argv) == 1:
            self.cmd_help(None)
            return 0
        
        args = parser.parse_args()
        
        # Execute command
        try:
            if args.command == 'generate':
                return self.cmd_generate(args)
            elif args.command == 'list':
                return self.cmd_list(args)
            elif args.command == 'check':
                return self.cmd_check(args)
            elif args.command == 'compliance':
                return self.cmd_compliance(args)
            elif args.command == 'help' or not args.command:
                return self.cmd_help(args)
            else:
                self.print_error(f"Unknown command: {args.command}")
                return 1
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            return 130
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return 1


def main():
    """Main function"""
    cli = TelCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())