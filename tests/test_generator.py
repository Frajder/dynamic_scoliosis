"""
Tests for the credential generator using Kim as the example subject.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from dynamic_scoliosis_credentials.generator import CredentialGenerator
from dynamic_scoliosis_credentials.models import (
    CredentialType,
    CredentialLevel,
    CredentialOutput,
)


class TestKimCredentialGenerator:
    """Test CredentialGenerator with Kim's credentials."""
    
    def test_kim_practitioner_credential_generation(self, kim_practitioner_config):
        """Test generating Kim's practitioner credential."""
        generator = CredentialGenerator(kim_practitioner_config)
        credential = generator.generate_credential()
        
        # Check basic structure
        assert "@context" in credential
        assert "id" in credential
        assert "type" in credential
        assert "issuer" in credential
        assert "issuanceDate" in credential
        assert "credentialSubject" in credential
        assert "proof" in credential
        
        # Check context
        assert "https://www.w3.org/2018/credentials/v1" in credential["@context"]
        assert "https://schema.org" in credential["@context"]
        assert any(
            "DynamicScoliosisPractitionerCredential" in ctx
            for ctx in credential["@context"]
            if isinstance(ctx, dict)
        )
        
        # Check types
        assert "VerifiableCredential" in credential["type"]
        assert "DynamicScoliosisPractitionerCredential" in credential["type"]
        
        # Check issuer
        assert credential["issuer"] == "did:web:kim-clinic.example"
        
        # Check subject
        subject = credential["credentialSubject"]
        assert subject["name"] == "Kim Johnson"
        assert subject["email"] == "kim.johnson@example.com"
        assert subject["credentialLevel"] == "Certified"
        assert subject["trainingHours"] == 120
        assert "Dynamic Scoliosis Assessment" in subject["specializations"]
        
        # Check proof
        proof = credential["proof"]
        assert proof["type"] == "Ed25519Signature2020"
        assert proof["verificationMethod"] == "did:web:kim-clinic.example#key-1"
        assert proof["jws"] == "eyJhbGciOiJFZERTQSJ9..demo-signature"
    
    def test_kim_patient_credential_generation(self, kim_patient_config):
        """Test generating Kim's patient record credential."""
        generator = CredentialGenerator(kim_patient_config)
        credential = generator.generate_credential()
        
        # Check types for patient record
        assert "VerifiableCredential" in credential["type"]
        assert "PatientHealthRecordCredential" in credential["type"]
        
        # Check issuer
        assert credential["issuer"] == "did:web:kim-hospital.example"
        
        # Check subject
        subject = credential["credentialSubject"]
        assert subject["name"] == "Kim Johnson"
        assert subject["patientId"] == "KIM001"
        assert subject["bloodType"] == "B+"
        assert subject["scoliosisType"] == "dynamic"
        assert subject["curveDegree"] == 28.5
        
        # Check emergency contacts
        assert "emergencyContacts" in subject
        emergency_contacts = subject["emergencyContacts"]
        assert len(emergency_contacts) == 2
        
        spouse_contact = next(
            (c for c in emergency_contacts if c["relationship"] == "Spouse"),
            None
        )
        assert spouse_contact is not None
        assert spouse_contact["name"] == "Alex Kim"
        assert spouse_contact["phone"] == "+1-555-0456"
        
        # Check medical alerts
        assert "medicalAlerts" in subject
        medical_alerts = subject["medicalAlerts"]
        assert len(medical_alerts) == 1
        assert medical_alerts[0]["condition"] == "Dynamic Scoliosis"
        assert medical_alerts[0]["severity"] == "medium"
        
        # Check allergies and medications
        assert "Codeine" in subject["allergies"]
        assert "Shellfish" in subject["allergies"]
        assert "Vitamin D3 2000IU daily" in subject["currentMedications"]
    
    def test_kim_emergency_contact_generation(self, kim_emergency_config):
        """Test generating Kim's emergency contact credential."""
        generator = CredentialGenerator(kim_emergency_config)
        credential = generator.generate_credential()
        
        assert "EmergencyContactCredential" in credential["type"]
        subject = credential["credentialSubject"]
        assert subject["name"] == "Kim Johnson"
        assert "emergencyContacts" in subject
        assert len(subject["emergencyContacts"]) == 2
    
    def test_kim_medical_alert_generation(self, kim_medical_alert_config):
        """Test generating Kim's medical alert credential."""
        generator = CredentialGenerator(kim_medical_alert_config)
        credential = generator.generate_credential()
        
        assert "MedicalAlertCredential" in credential["type"]
        subject = credential["credentialSubject"]
        assert subject["name"] == "Kim Johnson"
        assert "medicalAlerts" in subject
        assert len(subject["medicalAlerts"]) == 1
        assert subject["medicalAlerts"][0]["condition"] == "Dynamic Scoliosis"
    
    def test_kim_credential_with_expiry(self, kim_practitioner_config):
        """Test generating Kim's credential with expiry date."""
        expiry_date = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        kim_practitioner_config.expiry_date = expiry_date
        
        generator = CredentialGenerator(kim_practitioner_config)
        credential = generator.generate_credential()
        
        assert "expirationDate" in credential
        assert credential["expirationDate"] == expiry_date.isoformat()
    
    def test_kim_credential_save_to_file(self, kim_practitioner_config, temp_dir):
        """Test saving Kim's credential to file."""
        output_config = CredentialOutput(
            output_dir=str(temp_dir),
            vc_filename="kim_test_credential.json",
        )
        
        generator = CredentialGenerator(kim_practitioner_config, output_config)
        credential, saved_path = generator.generate_and_save()
        
        # Check file was created
        assert saved_path.exists()
        assert saved_path.name == "kim_test_credential.json"
        
        # Check file contents
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_credential = json.load(f)
        
        assert saved_credential["credentialSubject"]["name"] == "Kim Johnson"
        assert saved_credential["issuer"] == "did:web:kim-clinic.example"
    
    def test_kim_credential_custom_context(self, kim_practitioner_config):
        """Test generating Kim's credential with custom context."""
        kim_practitioner_config.custom_context = {
            "customField": "https://kim-clinic.example/custom"
        }
        
        generator = CredentialGenerator(kim_practitioner_config)
        credential = generator.generate_credential()
        
        # Check custom context is included
        assert kim_practitioner_config.custom_context in credential["@context"]
    
    def test_context_building_for_different_types(
        self, kim_issuer_config, kim_subject_config, kim_patient_record, kim_practitioner_credential
    ):
        """Test that different credential types get different contexts."""
        from dynamic_scoliosis_credentials.models import CredentialConfig
        
        # Test each credential type
        types_and_expected_contexts = [
            (CredentialType.PRACTITIONER, "DynamicScoliosisPractitionerCredential"),
            (CredentialType.PATIENT_RECORD, "PatientHealthRecordCredential"),
            (CredentialType.EMERGENCY_CONTACT, "EmergencyContactCredential"),
            (CredentialType.MEDICAL_ALERT, "MedicalAlertCredential"),
        ]
        
        for cred_type, expected_context in types_and_expected_contexts:
            if cred_type == CredentialType.PRACTITIONER:
                config = CredentialConfig(
                    credential_type=cred_type,
                    issuer=kim_issuer_config,
                    subject=kim_subject_config,
                    practitioner=kim_practitioner_credential,
                )
            else:
                config = CredentialConfig(
                    credential_type=cred_type,
                    issuer=kim_issuer_config,
                    subject=kim_subject_config,
                    patient_record=kim_patient_record,
                )
            
            generator = CredentialGenerator(config)
            credential = generator.generate_credential()
            
            # Check that the appropriate context is included
            context_found = False
            for ctx in credential["@context"]:
                if isinstance(ctx, dict) and expected_context in ctx:
                    context_found = True
                    break
            assert context_found, f"Expected context {expected_context} not found"
    
    def test_missing_required_fields_error(self, kim_issuer_config, kim_subject_config):
        """Test that missing required fields raise appropriate errors."""
        from dynamic_scoliosis_credentials.models import CredentialConfig
        from pydantic import ValidationError
        
        # Test practitioner without practitioner fields - should raise ValidationError during config creation
        with pytest.raises(ValidationError, match="Practitioner fields required"):
            CredentialConfig(
                credential_type=CredentialType.PRACTITIONER,
                issuer=kim_issuer_config,
                subject=kim_subject_config,
                # Missing practitioner field - this should be caught by Pydantic validation
            )
    
    def test_kim_credential_id_uniqueness(self, kim_practitioner_config):
        """Test that each generated Kim credential has a unique ID."""
        generator = CredentialGenerator(kim_practitioner_config)
        
        credential1 = generator.generate_credential()
        credential2 = generator.generate_credential()
        
        assert credential1["id"] != credential2["id"]
        assert credential1["id"].startswith("urn:uuid:")
        assert credential2["id"].startswith("urn:uuid:")
    
    def test_kim_credential_issuance_date_format(self, kim_practitioner_config):
        """Test that Kim's credential has properly formatted issuance date."""
        generator = CredentialGenerator(kim_practitioner_config)
        credential = generator.generate_credential()
        
        # Check that issuance date is valid ISO format
        issuance_date = credential["issuanceDate"]
        parsed_date = datetime.fromisoformat(issuance_date.replace('Z', '+00:00'))
        
        # Should be recent (within last minute)
        now = datetime.now(timezone.utc)
        time_diff = abs((now - parsed_date).total_seconds())
        assert time_diff < 60, "Issuance date should be very recent"


class TestKimCredentialGeneratorEdgeCases:
    """Test edge cases and error conditions with Kim's data."""
    
    def test_kim_subject_without_optional_fields(self, kim_issuer_config, kim_practitioner_credential):
        """Test Kim's credential with minimal subject information."""
        from dynamic_scoliosis_credentials.models import CredentialConfig, SubjectConfig
        
        minimal_subject = SubjectConfig(name="Kim Johnson")  # Only required field
        
        config = CredentialConfig(
            credential_type=CredentialType.PRACTITIONER,
            issuer=kim_issuer_config,
            subject=minimal_subject,
            practitioner=kim_practitioner_credential,
        )
        
        generator = CredentialGenerator(config)
        credential = generator.generate_credential()
        
        subject = credential["credentialSubject"]
        assert subject["name"] == "Kim Johnson"
        assert "email" not in subject
        assert "phone" not in subject
        assert "organization" not in subject
    
    def test_kim_patient_record_minimal(self, kim_issuer_config, kim_subject_config):
        """Test Kim's patient record with minimal information."""
        from dynamic_scoliosis_credentials.models import CredentialConfig, PatientHealthRecord
        
        minimal_record = PatientHealthRecord(patient_id="KIM001")
        
        config = CredentialConfig(
            credential_type=CredentialType.PATIENT_RECORD,
            issuer=kim_issuer_config,
            subject=kim_subject_config,
            patient_record=minimal_record,
        )
        
        generator = CredentialGenerator(config)
        credential = generator.generate_credential()
        
        subject = credential["credentialSubject"]
        assert subject["patientId"] == "KIM001"
        assert "bloodType" not in subject
        assert subject.get("emergencyContacts", []) == []
        assert subject.get("medicalAlerts", []) == []
    
    def test_output_directory_creation(self, kim_practitioner_config, temp_dir):
        """Test that output directory is created if it doesn't exist."""
        output_dir = temp_dir / "kim_output" / "nested"
        output_config = CredentialOutput(output_dir=str(output_dir))
        
        generator = CredentialGenerator(kim_practitioner_config, output_config)
        credential, saved_path = generator.generate_and_save()
        
        assert output_dir.exists()
        assert saved_path.parent == output_dir
        assert saved_path.exists() 