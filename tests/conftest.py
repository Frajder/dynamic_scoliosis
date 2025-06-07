"""
Pytest configuration and fixtures for the Dynamic Scoliosis Credentials System tests.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import pytest

from dynamic_scoliosis_credentials.models import (
    CredentialConfig,
    CredentialType,
    CredentialLevel,
    IssuerConfig,
    SubjectConfig,
    PractitionerCredential,
    PatientHealthRecord,
    EmergencyContact,
    MedicalAlert,
    QRConfig,
    CredentialOutput,
)


@pytest.fixture
def kim_issuer_config():
    """Fixture for Kim's clinic issuer configuration."""
    return IssuerConfig(
        did="did:web:kim-clinic.example",
        name="Dr. Kim's Dynamic Scoliosis Training Center",
        verification_method="did:web:kim-clinic.example#key-1",
    )


@pytest.fixture
def kim_subject_config():
    """Fixture for Kim as a subject."""
    return SubjectConfig(
        name="Kim Johnson",
        email="kim.johnson@example.com",
        phone="+1-555-0123",
        organization="Kim's Medical Practice",
    )


@pytest.fixture
def kim_practitioner_credential():
    """Fixture for Kim's practitioner credential configuration."""
    return PractitionerCredential(
        level=CredentialLevel.CERTIFIED,
        training_hours=120,
        specializations=["Dynamic Scoliosis Assessment", "Advanced Treatment Planning"],
        description="Kim has completed advanced training in Dynamic Scoliosis assessment and management.",
    )


@pytest.fixture
def kim_patient_record():
    """Fixture for Kim as a patient record."""
    return PatientHealthRecord(
        patient_id="KIM001",
        blood_type="B+",
        emergency_contacts=[
            EmergencyContact(
                name="Alex Kim",
                relationship="Spouse",
                phone="+1-555-0456",
                email="alex.kim@example.com",
            ),
            EmergencyContact(
                name="Dr. Sarah Lee",
                relationship="Primary Physician",
                phone="+1-555-0789",
                email="s.lee@hospital.example",
            ),
        ],
        medical_alerts=[
            MedicalAlert(
                condition="Dynamic Scoliosis",
                severity="medium",
                treatment="Physical therapy 3x weekly, monitor curve progression",
                medications=["Ibuprofen 600mg as needed"],
                allergies=["Codeine"],
            ),
        ],
        current_medications=["Vitamin D3 2000IU daily", "Calcium 500mg daily"],
        allergies=["Codeine", "Shellfish"],
        medical_devices=["Scoliosis brace (nighttime use)"],
        primary_physician="Dr. Sarah Lee, MD",
        scoliosis_type="dynamic",
        curve_degree=28.5,
    )


@pytest.fixture
def kim_practitioner_config(kim_issuer_config, kim_subject_config, kim_practitioner_credential):
    """Fixture for Kim's complete practitioner credential configuration."""
    return CredentialConfig(
        credential_type=CredentialType.PRACTITIONER,
        issuer=kim_issuer_config,
        subject=kim_subject_config,
        practitioner=kim_practitioner_credential,
    )


@pytest.fixture
def kim_patient_config(kim_issuer_config, kim_subject_config, kim_patient_record):
    """Fixture for Kim's complete patient record configuration."""
    # Use hospital issuer for patient records
    hospital_issuer = IssuerConfig(
        did="did:web:kim-hospital.example",
        name="Kim Memorial Hospital",
        verification_method="did:web:kim-hospital.example#key-1",
    )
    
    return CredentialConfig(
        credential_type=CredentialType.PATIENT_RECORD,
        issuer=hospital_issuer,
        subject=kim_subject_config,
        patient_record=kim_patient_record,
    )


@pytest.fixture
def qr_config():
    """Fixture for QR code configuration."""
    return QRConfig(
        use_compression=True,
        error_correction="Q",
        box_size=8,
        border=3,
    )


@pytest.fixture
def output_config():
    """Fixture for output configuration."""
    return CredentialOutput(
        output_dir="test_output",
        vc_filename="kim_credential.json",
        qr_filename="kim_credential_qr.png",
        generate_qr=True,
    )


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_vc_dict():
    """Fixture providing a sample verifiable credential as a dictionary."""
    return {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://schema.org",
            {"DynamicScoliosisPractitionerCredential": "https://example.com/credentials/ds-practitioner"},
        ],
        "id": "urn:uuid:12345678-1234-5678-9012-123456789012",
        "type": ["VerifiableCredential", "DynamicScoliosisPractitionerCredential"],
        "issuer": "did:web:kim-clinic.example",
        "issuanceDate": "2024-01-15T10:30:00Z",
        "credentialSubject": {
            "id": "did:key:kim123",
            "name": "Kim Johnson",
            "credentialLevel": "Certified",
            "description": "Kim has completed advanced training in Dynamic Scoliosis assessment and management.",
            "trainingHours": 120,
            "specializations": ["Dynamic Scoliosis Assessment", "Advanced Treatment Planning"],
        },
        "proof": {
            "type": "Ed25519Signature2020",
            "created": "2024-01-15T10:30:00Z",
            "proofPurpose": "assertionMethod",
            "verificationMethod": "did:web:kim-clinic.example#key-1",
            "jws": "eyJhbGciOiJFZERTQSJ9..demo-signature",
        },
    }


@pytest.fixture
def invalid_vc_dict():
    """Fixture providing an invalid verifiable credential."""
    return {
        "type": ["VerifiableCredential"],  # Missing @context, issuer, etc.
        "credentialSubject": {
            "name": "Kim Johnson",
        },
    }


@pytest.fixture
def kim_emergency_config(kim_issuer_config, kim_subject_config, kim_patient_record):
    """Fixture for Kim's emergency contact credential configuration."""
    return CredentialConfig(
        credential_type=CredentialType.EMERGENCY_CONTACT,
        issuer=kim_issuer_config,
        subject=kim_subject_config,
        patient_record=kim_patient_record,
    )


@pytest.fixture
def kim_medical_alert_config(kim_issuer_config, kim_subject_config, kim_patient_record):
    """Fixture for Kim's medical alert credential configuration."""
    return CredentialConfig(
        credential_type=CredentialType.MEDICAL_ALERT,
        issuer=kim_issuer_config,
        subject=kim_subject_config,
        patient_record=kim_patient_record,
    ) 