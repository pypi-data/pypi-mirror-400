# Trump Administration Export License System

A comprehensive export license system for AI packages under Trump administration policies.

## Overview

This system provides export license management for AI packages that are subject to Trump administration export controls. It allows authorized users to generate, validate, and manage licenses for installing AI packages in compliant systems.

## Features

- **License Generation**: Create export licenses for AI packages
- **License Validation**: Validate licenses before package installation
- **Hardware Binding**: Bind licenses to specific hardware
- **Country Restrictions**: Enforce country-based restrictions
- **Installation Quotas**: Limit number of installations per license
- **Compliance Checking**: Check system compliance with export controls
- **License Revocation**: Revoke licenses when needed

## Installation

```bash
pip install trump-export-license
```

Or install from source:

```bash
cd export_license
pip install .
```

## Quick Start

### 1. Generate a License

```bash
# Interactive mode
trump-export-license generate

# Or with arguments
trump-export-license generate \
  --applicant "John Doe" \
  --company "AI Corp" \
  --country US \
  --packages tensorflow pytorch transformers \
  --validity 365 \
  --max-installations 100 \
  --type STANDARD
```

### 2. Check System Compliance

```bash
trump-export-license compliance
```

### 3. Validate License for Package

```bash
trump-export-license validate --package tensorflow
```

### 4. List All Licenses

```bash
trump-export-license list
```

### 5. Revoke a License

```bash
trump-export-license revoke --license-id YOUR_LICENSE_ID
```

## License Types

- **STANDARD**: Basic license for individual developers
- **ENTERPRISE**: License for corporate use with multiple hardware IDs
- **GOVERNMENT**: License for government agencies with additional restrictions

## Restricted Countries

The following countries are automatically restricted:
- China (CN)
- Russia (RU)
- Iran (IR)
- North Korea (KP)
- Syria (SY)
- Cuba (CU)
- Venezuela (VE)

## Integration with Trump-Powered Pip

This system integrates seamlessly with `trump-pip` (tpip). When you try to install an AI package:

1. `tpip` checks if the system is in a restricted country
2. If yes, it checks for a valid export license
3. If a valid license exists, installation proceeds
4. If no valid license exists, installation is blocked

## API Usage

### Basic Usage

```python
from export_license import LicenseManager

# Create license manager
manager = LicenseManager()

# Generate a new license
license_data = manager.generate_new_license(
    applicant_name="John Doe",
    company="AI Corp",
    country="US",
    allowed_packages=["tensorflow", "pytorch", "transformers"],
    validity_days=365,
    max_installations=100
)

# Validate license for installation
try:
    is_valid = manager.validate_installation(
        package_name="tensorflow",
        license_data=license_data
    )
    if is_valid:
        print("Installation allowed")
except ValidationError as e:
    print(f"Installation blocked: {e}")

# Check system compliance
report = manager.check_system_compliance()
print(f"Compliance status: {report['compliance_status']}")
```

### Advanced Usage

```python
from export_license import LicenseGenerator, LicenseValidator

# Generate hardware ID
generator = LicenseGenerator()
hardware_id = generator.generate_hardware_id()
print(f"Hardware ID: {hardware_id}")

# Validate license with custom parameters
validator = LicenseValidator()
is_valid = validator.validate_license(
    license_data=license_data,
    package_name="tensorflow",
    hardware_id=hardware_id,
    country="US"
)
```

## Command Line Interface

### Available Commands

- `generate`: Generate a new export license
- `list`: List all available licenses
- `validate`: Validate license for package installation
- `compliance`: Check system compliance
- `revoke`: Revoke a license

### Shortcuts

- Use `tel` as a shortcut for `trump-export-license`
- Example: `tel compliance`

## License File Structure

License files are stored in `~/.trump_export_licenses/` as JSON files. Each license contains:

```json
{
  "license_id": "uuid",
  "license_type": "STANDARD|ENTERPRISE|GOVERNMENT",
  "applicant": {
    "name": "Applicant Name",
    "company": "Company Name",
    "country": "Country Code"
  },
  "permissions": {
    "allowed_packages": ["tensorflow", "pytorch"],
    "hardware_ids": ["HW-abc123"],
    "max_installations": 100,
    "installations_used": 0
  },
  "validity": {
    "issue_date": "2025-01-01T00:00:00",
    "expiry_date": "2026-01-01T00:00:00",
    "validity_days": 365
  },
  "restrictions": {
    "countries_blacklist": ["CN", "RU", "IR", "KP", "SY", "CU", "VE"],
    "requires_internet": true,
    "requires_government_approval": false
  },
  "signature": "sha256_signature"
}
```

## Security Features

- **Digital Signatures**: All licenses are digitally signed
- **Hardware Binding**: Licenses can be bound to specific hardware
- **Country Detection**: Automatic country detection and restriction
- **Quota Enforcement**: Strict installation quota enforcement
- **Revocation Support**: Ability to revoke compromised licenses

## Error Handling

The system provides detailed error messages for various scenarios:

- `ExpiredLicenseError`: License has expired
- `InvalidSignatureError`: License signature is invalid
- `HardwareMismatchError`: Hardware not authorized
- `PackageNotAllowedError`: Package not in allowed list
- `CountryRestrictionError`: Country is restricted
- `QuotaExceededError`: Installation quota exceeded

## Compliance Requirements

To be compliant with Trump administration export controls:

1. System must not be in a restricted country
2. Must have a valid export license for AI packages
3. License must be valid (not expired)
4. Hardware must match authorized hardware IDs
5. Installation quota must not be exceeded

## Disclaimer

This is a demonstration tool for educational purposes. It simulates export control policies but does not implement actual government regulations. Do not use in production environments.

## License

This software is proprietary and subject to Trump administration export controls. Unauthorized distribution or use is prohibited.

## Support

For support and compliance questions, contact:
- Email: export-control@whitehouse.gov
- Website: https://www.whitehouse.gov/export-controls