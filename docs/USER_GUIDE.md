# User Guide

This guide provides step-by-step instructions for using the Dynamic Scoliosis Credentials System to generate, validate, and manage W3C verifiable credentials.

## Installation

### From Source (Recommended)
```bash
git clone https://github.com/Frajder/dynamic_scoliosis.git
cd dynamic_scoliosis
pip install -e .
```

### Verify Installation
```bash
ds-credentials --help
ds-credentials version
```

## Quick Start

### Generate Your First Credential

#### Interactive Mode (Recommended for Beginners)
```bash
ds-credentials generate
```

This will walk you through:
1. Selecting credential type (practitioner, patient_record, medical_alert, emergency_contact)
2. Entering issuer information
3. Providing subject details
4. Adding type-specific information
5. Generating QR code and output files

#### Command Line Mode
```bash
# Practitioner credential
ds-credentials generate \
  --type practitioner \
  --name "Dr. Kim Johnson" \
  --issuer "did:web:kim-clinic.example"

# Patient record
ds-credentials generate \
  --type patient_record \
  --name "Kim Johnson" \
  --issuer "did:web:hospital.example"
```

## Configuration Files

### Creating Configuration Templates
```bash
# Create example configurations
ds-credentials create-config --output config/

# Create specific type
ds-credentials create-config --type practitioner --output config/
```

### Using Configuration Files
```bash
# Generate from configuration
ds-credentials generate --config config/practitioner_config.json

# Generate without QR code
ds-credentials generate --config config/patient_config.json --no-qr
```

## Credential Types

### 1. Practitioner Credentials

For healthcare providers establishing their Dynamic Scoliosis credentials:

```json
{
  "credential_type": "practitioner",
  "issuer": {
    "did": "did:web:training-center.example",
    "name": "Dynamic Scoliosis Training Center",
    "verification_method": "did:web:training-center.example#key-1"
  },
  "subject": {
    "name": "Dr. Kim Johnson",
    "email": "kim.johnson@clinic.example",
    "organization": "Kim's Scoliosis Clinic"
  },
  "practitioner": {
    "level": "Certified",
    "training_hours": 120,
    "specializations": ["Dynamic Assessment", "Treatment Planning"],
    "description": "Completed advanced Dynamic Scoliosis training program"
  }
}
```

**Available Levels:**
- `Level 1` - Basic training (40 hours)
- `Level 2` - Intermediate training (80 hours)  
- `Level 3` - Advanced training (120 hours)
- `Certified` - Full certification (160+ hours)
- `Expert` - Expert level with teaching credentials

### 2. Patient Health Records

For patient emergency information and medical history:

```json
{
  "credential_type": "patient_record",
  "issuer": {
    "did": "did:web:hospital.example",
    "name": "Memorial Hospital",
    "verification_method": "did:web:hospital.example#key-1"
  },
  "subject": {
    "name": "Kim Johnson"
  },
  "patient_record": {
    "patient_id": "P123456",
    "blood_type": "B+",
    "emergency_contacts": [
      {
        "name": "Alex Kim",
        "relationship": "Spouse",
        "phone": "+1-555-0456",
        "email": "alex.kim@example.com"
      }
    ],
    "medical_alerts": [
      {
        "condition": "Dynamic Scoliosis",
        "severity": "medium",
        "treatment": "Physical therapy 3x weekly",
        "medications": ["Ibuprofen 600mg PRN"],
        "allergies": ["Codeine", "Penicillin"]
      }
    ],
    "current_medications": ["Vitamin D3 2000IU daily"],
    "allergies": ["Codeine", "Penicillin", "Shellfish"],
    "medical_devices": ["Scoliosis brace (nighttime)"],
    "primary_physician": "Dr. Sarah Lee, MD",
    "scoliosis_type": "dynamic",
    "curve_degree": 28.5
  }
}
```

### 3. Medical Alert Credentials

For critical medical conditions requiring immediate attention:

```json
{
  "credential_type": "medical_alert",
  "issuer": {
    "did": "did:web:hospital.example",
    "name": "Emergency Medical Services"
  },
  "subject": {
    "name": "Kim Johnson"
  },
  "patient_record": {
    "patient_id": "P123456",
    "medical_alerts": [
      {
        "condition": "Severe Scoliosis with Hardware",
        "severity": "critical",
        "treatment": "DO NOT manually manipulate spine - titanium rods present",
        "allergies": ["Morphine", "Codeine"]
      }
    ]
  }
}
```

### 4. Emergency Contact Credentials

For family notification and medical decision-making:

```json
{
  "credential_type": "emergency_contact",
  "patient_record": {
    "patient_id": "P123456",
    "emergency_contacts": [
      {
        "name": "Alex Kim",
        "relationship": "Spouse",
        "phone": "+1-555-0456"
      },
      {
        "name": "Dr. Sarah Lee",
        "relationship": "Primary Physician", 
        "phone": "+1-555-0789"
      }
    ]
  }
}
```

## Validation and Verification

### Validate Credentials
```bash
# Basic validation
ds-credentials validate output/credential.json

# Verbose validation with details
ds-credentials validate output/credential.json --verbose
```

### View Credential Summary
```bash
ds-credentials summary output/credential.json
```

Sample output:
```
Credential Summary
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                ┃ Value                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Id                   │ urn:uuid:12345678-1234-5678-9012...    │
│ Types                │ VerifiableCredential, Practitioner...  │
│ Issuer               │ did:web:kim-clinic.example              │
│ Subject Name         │ Kim Johnson                             │
│ Credential Level     │ Certified                               │
└──────────────────────┴─────────────────────────────────────────┘
```

## QR Code Management

### Generate QR Codes
```bash
# Generate credential with QR code
ds-credentials generate --config config.json --qr

# Custom QR settings
ds-credentials generate --config config.json \
  --qr-error-correction H \
  --qr-box-size 12 \
  --qr-border 5
```

### Decode QR Codes
```bash
# Decode QR payload to JSON
ds-credentials decode-qr "VC:eyJhbGciOiJFZERTQSJ9..."

# Save decoded credential to file
ds-credentials decode-qr "VC:payload..." --output decoded_credential.json
```

### QR Code Size Estimation
The system automatically estimates QR code requirements and provides compression ratios:

```
QR payload size: 1,234 bytes
Compression ratio: 45%
Recommended version: Version 8
```

## Advanced Configuration

### Custom Contexts
Add custom context fields to credentials:

```json
{
  "custom_context": {
    "customField": "https://example.com/custom-context",
    "organizationSpecific": "https://hospital.example/contexts"
  }
}
```

### Expiry Dates
Set credential expiration:

```json
{
  "expiry_date": "2025-12-31T23:59:59Z"
}
```

### QR Configuration
Customize QR code generation:

```json
{
  "qr_config": {
    "use_compression": true,
    "error_correction": "Q",
    "box_size": 10,
    "border": 4
  }
}
```

### Output Configuration
Control output files and directories:

```json
{
  "output_dir": "credentials",
  "vc_filename": "kim_practitioner.json",
  "qr_filename": "kim_practitioner_qr.png",
  "generate_qr": true
}
```

## Common Workflows

### Healthcare Provider Setup
1. **Generate Practitioner Credential**
   ```bash
   ds-credentials create-config --type practitioner
   # Edit config/practitioner_config.json
   ds-credentials generate --config config/practitioner_config.json
   ```

2. **Validate and Share**
   ```bash
   ds-credentials validate output/credential.json
   ds-credentials summary output/credential.json
   ```

### Patient Record Creation
1. **Generate Patient Configuration**
   ```bash
   ds-credentials create-config --type patient_record
   ```

2. **Customize Medical Information**
   - Edit blood type, allergies, medications
   - Add emergency contacts
   - Include medical devices and conditions

3. **Generate Emergency QR Code**
   ```bash
   ds-credentials generate --config config/patient_config.json --qr
   ```

### Emergency Response Setup
1. **Create Medical Alert Credential**
   ```bash
   ds-credentials generate --type medical_alert --config emergency.json
   ```

2. **Generate High-Quality QR Code**
   ```bash
   ds-credentials generate --config emergency.json \
     --qr-error-correction H \
     --qr-box-size 15
   ```

3. **Test QR Code Scanning**
   ```bash
   # Extract QR payload and verify decoding
   ds-credentials decode-qr "VC:payload..." --output test_decode.json
   ds-credentials validate test_decode.json
   ```

## Troubleshooting

### Common Issues

#### QR Code Too Large
- Enable compression: `"use_compression": true`
- Reduce medical information
- Use higher error correction for smaller codes

#### Validation Errors
- Check required fields for credential type
- Verify DID format: must start with `did:`
- Ensure practitioner credentials include practitioner fields
- Verify patient credentials include patient_record fields

#### CLI Command Issues
- Verify installation: `ds-credentials version`
- Check file paths and permissions
- Use absolute paths for configuration files

### Debug Mode
```bash
ds-credentials generate --config config.json --verbose
```

### Getting Help
```bash
ds-credentials generate --help
ds-credentials validate --help
ds-credentials decode-qr --help
```

## Best Practices

### Security
- Use real cryptographic keys in production (not demo signatures)
- Implement proper DID resolution for verification
- Store credentials securely and limit access
- Use HTTPS for credential transmission

### Medical Information
- Include only essential emergency information in QR codes
- Regularly update medical information
- Verify allergies and medications are current
- Test emergency contact phone numbers

### QR Code Deployment
- Use high-quality printing for medical bracelets
- Include backup QR codes on multiple items
- Test QR codes with various scanning apps
- Consider NFC chips for backup access

### Credential Management
- Implement credential rotation policies
- Monitor for credential expiry
- Maintain audit logs of credential access
- Train staff on proper credential handling

---

**Need help?** Check the [Emergency Response Scenarios](EMERGENCY_SCENARIOS.md) for life-saving use cases or [API Reference](API_REFERENCE.md) for technical details. 