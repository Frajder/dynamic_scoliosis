"""
Tests for the models module using Kim as the example subject.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

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
    ProofConfig,
)


class TestKimIssuerConfig:
    """Test IssuerConfig with Kim's clinic as the issuer."""
    
    def test_valid_kim_issuer_config(self, kim_issuer_config):
        """Test creating a valid issuer config for Kim's clinic."""
        assert kim_issuer_config.did == "did:web:kim-clinic.example"
        assert kim_issuer_config.name == "Dr. Kim's Dynamic Scoliosis Training Center"
        assert kim_issuer_config.verification_method == "did:web:kim-clinic.example#key-1"
    
    def test_invalid_did_format(self):
        """Test that invalid DID format raises validation error."""
        with pytest.raises(ValidationError, match="DID must start with"):
            IssuerConfig(
                did="invalid-did",
                name="Kim's Clinic",
                verification_method="invalid-did#key-1",
            )
    
    def test_did_validation_passes_with_various_methods(self):
        """Test DID validation with various valid DID methods."""
        valid_dids = [
            "did:web:kim-clinic.example",
            "did:key:z6MkjUJ5qSdYqW5kRrS3mNq6oJJnTt2u5xwEGh1PSu5XW3yK",
            "did:ethr:0x1234567890abcdef",
        ]
        
        for did in valid_dids:
            config = IssuerConfig(
                did=did,
                name="Kim's Clinic",
                verification_method=f"{did}#key-1",
            )
            assert config.did == did


class TestKimSubjectConfig:
    """Test SubjectConfig with Kim as the subject."""
    
    def test_kim_subject_minimal_config(self):
        """Test minimal Kim subject configuration."""
        config = SubjectConfig(name="Kim Johnson")
        assert config.name == "Kim Johnson"
        assert config.did is None
        assert config.email is None
    
    def test_kim_subject_full_config(self, kim_subject_config):
        """Test full Kim subject configuration."""
        assert kim_subject_config.name == "Kim Johnson"
        assert kim_subject_config.email == "kim.johnson@example.com"
        assert kim_subject_config.phone == "+1-555-0123"
        assert kim_subject_config.organization == "Kim's Medical Practice"


class TestKimPractitionerCredential:
    """Test PractitionerCredential with Kim's certifications."""
    
    def test_kim_practitioner_basic(self):
        """Test basic Kim practitioner credential."""
        credential = PractitionerCredential(level=CredentialLevel.LEVEL_1)
        assert credential.level == CredentialLevel.LEVEL_1
        assert credential.training_hours is None
        assert credential.specializations == []
    
    def test_kim_practitioner_advanced(self, kim_practitioner_credential):
        """Test advanced Kim practitioner credential."""
        assert kim_practitioner_credential.level == CredentialLevel.CERTIFIED
        assert kim_practitioner_credential.training_hours == 120
        assert "Dynamic Scoliosis Assessment" in kim_practitioner_credential.specializations
        assert "Advanced Treatment Planning" in kim_practitioner_credential.specializations
    
    def test_invalid_training_hours(self):
        """Test that negative training hours raise validation error."""
        with pytest.raises(ValidationError):
            PractitionerCredential(
                level=CredentialLevel.LEVEL_1,
                training_hours=-10,
            )


class TestKimEmergencyContact:
    """Test EmergencyContact with Kim's contacts."""
    
    def test_kim_emergency_contact_minimal(self):
        """Test minimal emergency contact for Kim."""
        contact = EmergencyContact(
            name="Alex Kim",
            relationship="Spouse",
            phone="+1-555-0456",
        )
        assert contact.name == "Alex Kim"
        assert contact.relationship == "Spouse"
        assert contact.phone == "+1-555-0456"
        assert contact.email is None
    
    def test_kim_emergency_contact_full(self):
        """Test full emergency contact for Kim."""
        contact = EmergencyContact(
            name="Dr. Sarah Lee",
            relationship="Primary Physician",
            phone="+1-555-0789",
            email="s.lee@hospital.example",
        )
        assert contact.email == "s.lee@hospital.example"


class TestKimMedicalAlert:
    """Test MedicalAlert with Kim's medical conditions."""
    
    def test_kim_scoliosis_alert(self):
        """Test Kim's dynamic scoliosis medical alert."""
        alert = MedicalAlert(
            condition="Dynamic Scoliosis",
            severity="medium",
            treatment="Physical therapy 3x weekly",
            medications=["Ibuprofen 600mg as needed"],
            allergies=["Codeine"],
        )
        assert alert.condition == "Dynamic Scoliosis"
        assert alert.severity == "medium"
        assert "Ibuprofen 600mg as needed" in alert.medications
        assert "Codeine" in alert.allergies


class TestKimPatientHealthRecord:
    """Test PatientHealthRecord with Kim's medical information."""
    
    def test_kim_patient_record_basic(self):
        """Test basic Kim patient record."""
        record = PatientHealthRecord(patient_id="KIM001")
        assert record.patient_id == "KIM001"
        assert record.blood_type is None
        assert record.emergency_contacts == []
        assert record.medical_alerts == []
    
    def test_kim_patient_record_comprehensive(self, kim_patient_record):
        """Test comprehensive Kim patient record."""
        assert kim_patient_record.patient_id == "KIM001"
        assert kim_patient_record.blood_type == "B+"
        assert kim_patient_record.scoliosis_type == "dynamic"
        assert kim_patient_record.curve_degree == 28.5
        assert len(kim_patient_record.emergency_contacts) == 2
        assert len(kim_patient_record.medical_alerts) == 1
        assert "Codeine" in kim_patient_record.allergies
        assert "Shellfish" in kim_patient_record.allergies
        assert "Scoliosis brace (nighttime use)" in kim_patient_record.medical_devices
        
        # Check emergency contacts
        spouse_contact = next(
            (c for c in kim_patient_record.emergency_contacts if c.relationship == "Spouse"),
            None
        )
        assert spouse_contact is not None
        assert spouse_contact.name == "Alex Kim"
        
        # Check medical alerts
        scoliosis_alert = kim_patient_record.medical_alerts[0]
        assert scoliosis_alert.condition == "Dynamic Scoliosis"
        assert scoliosis_alert.severity == "medium"


class TestKimCredentialConfig:
    """Test CredentialConfig with Kim's various credential types."""
    
    def test_kim_practitioner_config_valid(self, kim_practitioner_config):
        """Test valid Kim practitioner credential configuration."""
        assert kim_practitioner_config.credential_type == CredentialType.PRACTITIONER
        assert kim_practitioner_config.issuer.did == "did:web:kim-clinic.example"
        assert kim_practitioner_config.subject.name == "Kim Johnson"
        assert kim_practitioner_config.practitioner is not None
        assert kim_practitioner_config.patient_record is None
    
    def test_kim_patient_config_valid(self, kim_patient_config):
        """Test valid Kim patient record configuration."""
        assert kim_patient_config.credential_type == CredentialType.PATIENT_RECORD
        assert kim_patient_config.issuer.did == "did:web:kim-hospital.example"
        assert kim_patient_config.subject.name == "Kim Johnson"
        assert kim_patient_config.practitioner is None
        assert kim_patient_config.patient_record is not None
    
    def test_practitioner_config_missing_practitioner_fields(self, kim_issuer_config, kim_subject_config):
        """Test that practitioner config without practitioner fields fails validation."""
        with pytest.raises(ValidationError, match="Practitioner fields required"):
            CredentialConfig(
                credential_type=CredentialType.PRACTITIONER,
                issuer=kim_issuer_config,
                subject=kim_subject_config,
                # Missing practitioner field
            )
    
    def test_patient_config_missing_patient_fields(self, kim_issuer_config, kim_subject_config):
        """Test that patient config without patient fields fails validation."""
        with pytest.raises(ValidationError, match="Patient record fields required"):
            CredentialConfig(
                credential_type=CredentialType.PATIENT_RECORD,
                issuer=kim_issuer_config,
                subject=kim_subject_config,
                # Missing patient_record field
            )
    
    def test_kim_emergency_contact_config(self, kim_emergency_config):
        """Test Kim's emergency contact credential configuration."""
        assert kim_emergency_config.credential_type == CredentialType.EMERGENCY_CONTACT
        assert kim_emergency_config.patient_record is not None
    
    def test_kim_medical_alert_config(self, kim_medical_alert_config):
        """Test Kim's medical alert credential configuration."""
        assert kim_medical_alert_config.credential_type == CredentialType.MEDICAL_ALERT
        assert kim_medical_alert_config.patient_record is not None


class TestQRConfig:
    """Test QR code configuration."""
    
    def test_default_qr_config(self):
        """Test default QR configuration."""
        config = QRConfig()
        assert config.use_compression is True
        assert config.error_correction == "Q"
        assert config.box_size == 10
        assert config.border == 4
    
    def test_custom_qr_config(self, qr_config):
        """Test custom QR configuration."""
        assert qr_config.use_compression is True
        assert qr_config.error_correction == "Q"
        assert qr_config.box_size == 8
        assert qr_config.border == 3
    
    def test_invalid_qr_config_values(self):
        """Test invalid QR configuration values."""
        with pytest.raises(ValidationError):
            QRConfig(box_size=0)  # Should be >= 1
        
        with pytest.raises(ValidationError):
            QRConfig(border=0)  # Should be >= 1


class TestCredentialOutput:
    """Test credential output configuration."""
    
    def test_default_output_config(self):
        """Test default output configuration."""
        config = CredentialOutput()
        assert config.output_dir == "output"
        assert config.vc_filename == "credential.json"
        assert config.qr_filename == "credential_qr.png"
        assert config.generate_qr is True
        assert config.generate_pdf is False
    
    def test_kim_output_config(self, output_config):
        """Test Kim's custom output configuration."""
        assert output_config.output_dir == "test_output"
        assert output_config.vc_filename == "kim_credential.json"
        assert output_config.qr_filename == "kim_credential_qr.png"
        assert output_config.generate_qr is True


class TestProofConfig:
    """Test cryptographic proof configuration."""
    
    def test_default_proof_config(self):
        """Test default proof configuration."""
        config = ProofConfig()
        assert config.type == "Ed25519Signature2020"
        assert config.purpose == "assertionMethod"
        assert config.use_demo_signature is True
    
    def test_production_proof_config(self):
        """Test production proof configuration."""
        config = ProofConfig(use_demo_signature=False)
        assert config.use_demo_signature is False


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_kim_config_serialization(self, kim_practitioner_config):
        """Test that Kim's configuration can be serialized and deserialized."""
        # Serialize to dict
        config_dict = kim_practitioner_config.model_dump()
        assert config_dict["subject"]["name"] == "Kim Johnson"
        assert config_dict["credential_type"] == "practitioner"
        
        # Deserialize from dict
        recreated_config = CredentialConfig.model_validate(config_dict)
        assert recreated_config.subject.name == "Kim Johnson"
        assert recreated_config.credential_type == CredentialType.PRACTITIONER
        assert recreated_config.practitioner.level == CredentialLevel.CERTIFIED
    
    def test_kim_patient_record_serialization(self, kim_patient_record):
        """Test that Kim's patient record can be serialized and deserialized."""
        # Serialize to dict
        record_dict = kim_patient_record.model_dump()
        assert record_dict["patient_id"] == "KIM001"
        assert record_dict["scoliosis_type"] == "dynamic"
        
        # Deserialize from dict
        recreated_record = PatientHealthRecord.model_validate(record_dict)
        assert recreated_record.patient_id == "KIM001"
        assert recreated_record.curve_degree == 28.5
        assert len(recreated_record.emergency_contacts) == 2 