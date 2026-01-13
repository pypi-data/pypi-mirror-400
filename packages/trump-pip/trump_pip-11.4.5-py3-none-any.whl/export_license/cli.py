"""
CLI for Trump Administration Export License System
"""

import argparse
import sys
import json
from typing import List
from colorama import Fore, Style, init

from .license_manager import LicenseManager
from .exceptions import ValidationError


def print_header(text: str):
    """Print formatted header"""
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print(Fore.CYAN + text.center(60) + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print()


def print_success(text: str):
    """Print success message"""
    print(Fore.GREEN + "✓ " + text + Style.RESET_ALL)


def print_error(text: str):
    """Print error message"""
    print(Fore.RED + "✗ " + text + Style.RESET_ALL)


def print_warning(text: str):
    """Print warning message"""
    print(Fore.YELLOW + "⚠ " + text + Style.RESET_ALL)


def print_info(text: str):
    """Print info message"""
    print(Fore.BLUE + "ℹ " + text + Style.RESET_ALL)


def generate_license(args):
    """Generate a new export license"""
    print_header("TRUMP ADMINISTRATION EXPORT LICENSE GENERATOR")
    
    # Get user input
    if not args.applicant:
        applicant = input("Applicant Name: ")
    else:
        applicant = args.applicant
    
    if not args.company:
        company = input("Company: ")
    else:
        company = args.company
    
    if not args.country:
        country = input("Country (2-letter code, e.g., US): ").upper()
    else:
        country = args.country.upper()
    
    if not args.packages:
        print("\nEnter AI packages to allow (comma-separated, * for wildcard):")
        packages_input = input("Packages: ")
        packages = [p.strip() for p in packages_input.split(',')]
    else:
        packages = args.packages
    
    # Create license manager
    manager = LicenseManager()
    
    # Generate license
    try:
        license_data = manager.generate_new_license(
            applicant_name=applicant,
            company=company,
            country=country,
            allowed_packages=packages,
            validity_days=args.validity,
            max_installations=args.max_installations,
            license_type=args.type
        )
        
        print_success(f"License generated successfully!")
        print(f"License ID: {Fore.CYAN}{license_data['license_id']}{Style.RESET_ALL}")
        print(f"Saved to: ~/.trump_export_licenses/")
        
        # Show license info
        print("\n" + Fore.YELLOW + "LICENSE SUMMARY:" + Style.RESET_ALL)
        print(f"• Applicant: {applicant} ({company})")
        print(f"• Country: {country}")
        print(f"• Type: {args.type}")
        print(f"• Validity: {args.validity} days")
        print(f"• Max Installations: {args.max_installations}")
        print(f"• Allowed Packages: {len(packages)}")
        
        if args.show_full:
            print("\n" + Fore.YELLOW + "FULL LICENSE DATA:" + Style.RESET_ALL)
            print(json.dumps(license_data, indent=2))
        
    except Exception as e:
        print_error(f"Failed to generate license: {str(e)}")
        return 1
    
    return 0


def list_licenses(args):
    """List all licenses"""
    print_header("EXPORT LICENSES")
    
    manager = LicenseManager()
    licenses = manager.list_licenses()
    
    if not licenses:
        print_info("No licenses found.")
        return 0
    
    print(f"Found {len(licenses)} license(s):\n")
    
    for i, license_info in enumerate(licenses, 1):
        status_color = Fore.GREEN if license_info['status'] == 'VALID' else Fore.RED
        print(f"{i:2d}. {Fore.CYAN}{license_info['license_id']}{Style.RESET_ALL}")
        print(f"    Type: {license_info['license_type']}")
        print(f"    Applicant: {license_info['applicant']} ({license_info['company']})")
        print(f"    Status: {status_color}{license_info['status']}{Style.RESET_ALL}")
        print(f"    Installations: {license_info['installations']}")
        print(f"    Expires: {license_info['expiry_date']}")
        print()
    
    return 0


def validate_license(args):
    """Validate license for package installation"""
    print_header("LICENSE VALIDATION")
    
    if not args.package:
        print_error("Package name is required for validation.")
        return 1
    
    manager = LicenseManager()
    
    # Try to find license
    license_data = None
    if args.license_id:
        license_data = manager.get_license(args.license_id)
        if not license_data:
            print_error(f"License {args.license_id} not found.")
            return 1
    
    # Validate
    try:
        is_valid = manager.validate_installation(
            package_name=args.package,
            license_data=license_data
        )
        
        if is_valid:
            print_success(f"License validation passed for '{args.package}'")
            print_info("You may proceed with installation.")
            return 0
        else:
            print_error(f"License validation failed for '{args.package}'")
            return 1
            
    except ValidationError as e:
        print_error(f"Validation failed: {str(e)}")
        return 1
    except Exception as e:
        print_error(f"Validation error: {str(e)}")
        return 1


def check_compliance(args):
    """Check system compliance"""
    print_header("SYSTEM COMPLIANCE CHECK")
    
    manager = LicenseManager()
    report = manager.check_system_compliance()
    
    print(Fore.YELLOW + "SYSTEM INFORMATION:" + Style.RESET_ALL)
    print(f"• OS: {report['system_checks'].get('os', 'UNKNOWN')}")
    print(f"• Hardware: {report['system_checks'].get('machine', 'UNKNOWN')}")
    print(f"• Hardware ID: {report['system_checks'].get('hardware_id', 'UNKNOWN')}")
    print(f"• Country: {report['system_checks'].get('country', 'UNKNOWN')}")
    
    print("\n" + Fore.YELLOW + "LICENSE STATUS:" + Style.RESET_ALL)
    print(f"• Total Licenses: {report['license_checks']['total_licenses']}")
    print(f"• Valid Licenses: {report['license_checks']['valid_licenses']}")
    print(f"• Expired Licenses: {report['license_checks']['expired_licenses']}")
    
    print("\n" + Fore.YELLOW + "COMPLIANCE STATUS:" + Style.RESET_ALL)
    status = report['compliance_status']
    if status == "COMPLIANT":
        print_success("SYSTEM IS COMPLIANT")
        print_info("You may install authorized AI packages.")
    elif status == "RESTRICTED_COUNTRY":
        print_error("RESTRICTED COUNTRY DETECTED")
        print_warning("Your country is subject to export controls.")
        print_warning("AI package installation is prohibited.")
    elif status == "NON_COMPLIANT":
        print_error("SYSTEM IS NON-COMPLIANT")
        print_warning("No valid export licenses found.")
        print_warning("AI package installation is prohibited.")
    else:
        print_warning("COMPLIANCE STATUS UNKNOWN")
    
    return 0


def revoke_license(args):
    """Revoke a license"""
    print_header("LICENSE REVOCATION")
    
    if not args.license_id:
        print_error("License ID is required.")
        return 1
    
    manager = LicenseManager()
    
    # Confirm revocation
    if not args.force:
        confirm = input(f"Are you sure you want to revoke license {args.license_id}? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print_info("Revocation cancelled.")
            return 0
    
    # Revoke license
    success = manager.revoke_license(args.license_id)
    
    if success:
        print_success(f"License {args.license_id} has been revoked.")
    else:
        print_error(f"License {args.license_id} not found or already revoked.")
        return 1
    
    return 0


def main():
    """Main entry point"""
    # Initialize colorama
    init(autoreset=True)
    
    # Create parser
    parser = argparse.ArgumentParser(
        description="Trump Administration Export License System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --applicant "John Doe" --company "AI Corp" --country US --packages tensorflow,pytorch
  %(prog)s list
  %(prog)s validate --package tensorflow
  %(prog)s compliance
  %(prog)s revoke --license-id LICENSE_ID
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate new export license')
    gen_parser.add_argument('--applicant', help='Applicant name')
    gen_parser.add_argument('--company', help='Company name')
    gen_parser.add_argument('--country', help='Country code (e.g., US)')
    gen_parser.add_argument('--packages', nargs='+', help='Allowed AI packages')
    gen_parser.add_argument('--validity', type=int, default=365, help='Validity in days')
    gen_parser.add_argument('--max-installations', type=int, default=100, help='Max installations')
    gen_parser.add_argument('--type', default='STANDARD', choices=['STANDARD', 'ENTERPRISE', 'GOVERNMENT'],
                          help='License type')
    gen_parser.add_argument('--show-full', action='store_true', help='Show full license data')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all licenses')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate license for package')
    val_parser.add_argument('--package', required=True, help='Package name to validate')
    val_parser.add_argument('--license-id', help='License ID (optional, uses first valid license)')
    
    # Compliance command
    comp_parser = subparsers.add_parser('compliance', help='Check system compliance')
    
    # Revoke command
    rev_parser = subparsers.add_parser('revoke', help='Revoke a license')
    rev_parser.add_argument('--license-id', required=True, help='License ID to revoke')
    rev_parser.add_argument('--force', action='store_true', help='Force revocation without confirmation')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Execute command
    try:
        if args.command == 'generate':
            return generate_license(args)
        elif args.command == 'list':
            return list_licenses(args)
        elif args.command == 'validate':
            return validate_license(args)
        elif args.command == 'compliance':
            return check_compliance(args)
        elif args.command == 'revoke':
            return revoke_license(args)
        else:
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
