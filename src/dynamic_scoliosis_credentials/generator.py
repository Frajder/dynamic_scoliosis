"""
Credential Generator for the Dynamic Scoliosis Credentials System.

This module provides the main CredentialGenerator class that creates
W3C Verifiable Credentials based on configurable options.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from .models import (
    CredentialConfig,
    CredentialType,
    CredentialOutput,
    PatientHealthRecord,
    PractitionerCredential,
)

logger = logging.getLogger(__name__)


class CredentialGenerator:
    """Main class for generating W3C Verifiable Credentials."""
    
    def __init__(self, config: CredentialConfig, output_config: Optional[CredentialOutput] = None):
        """
        Initialize the credential generator.
        
        Args:
            config: Main credential configuration
            output_config: Output configuration (optional)
        """
        self.config = config
        self.output_config = output_config or CredentialOutput()
        
    def generate_credential(self) -> Dict[str, Any]:
        """
        Generate a W3C Verifiable Credential based on the configuration.
        
        Returns:
            Dict containing the complete verifiable credential
        """
        now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        
        # Base credential structure
        credential = {
            "@context": self._build_context(),
            "id": f"urn:uuid:{uuid4()}",
            "type": self._build_types(),
            "issuer": self.config.issuer.did,
            "issuanceDate": now_iso,
            "credentialSubject": self._build_credential_subject(),
            "proof": self._build_proof(now_iso),
        }
        
        # Add expiry date if specified
        if self.config.expiry_date:
            credential["expirationDate"] = self.config.expiry_date.isoformat()
        
        return credential
    
    def _build_context(self) -> list:
        """Build the @context array for the credential."""
        context = [
            "https://www.w3.org/2018/credentials/v1",
            "https://schema.org",
        ]
        
        # Add credential-type specific context
        if self.config.credential_type == CredentialType.PRACTITIONER:
            context.append({
                "DynamicScoliosisPractitionerCredential": str(self.config.issuer.context_url)
            })
        elif self.config.credential_type == CredentialType.PATIENT_RECORD:
            context.append({
                "PatientHealthRecordCredential": str(self.config.issuer.context_url).replace("ds-practitioner", "patient-record")
            })
        elif self.config.credential_type == CredentialType.EMERGENCY_CONTACT:
            context.append({
                "EmergencyContactCredential": str(self.config.issuer.context_url).replace("ds-practitioner", "emergency-contact")
            })
        elif self.config.credential_type == CredentialType.MEDICAL_ALERT:
            context.append({
                "MedicalAlertCredential": str(self.config.issuer.context_url).replace("ds-practitioner", "medical-alert")
            })
        
        # Add custom contexts
        if self.config.custom_context:
            context.append(self.config.custom_context)
            
        return context
    
    def _build_types(self) -> list:
        """Build the type array for the credential."""
        types = ["VerifiableCredential"]
        
        if self.config.credential_type == CredentialType.PRACTITIONER:
            types.append("DynamicScoliosisPractitionerCredential")
        elif self.config.credential_type == CredentialType.PATIENT_RECORD:
            types.append("PatientHealthRecordCredential")
        elif self.config.credential_type == CredentialType.EMERGENCY_CONTACT:
            types.append("EmergencyContactCredential")
        elif self.config.credential_type == CredentialType.MEDICAL_ALERT:
            types.append("MedicalAlertCredential")
            
        return types
    
    def _build_credential_subject(self) -> Dict[str, Any]:
        """Build the credentialSubject based on the credential type."""
        subject = {
            "name": self.config.subject.name,
        }
        
        # Add DID if provided
        if self.config.subject.did:
            subject["id"] = self.config.subject.did
        
        # Add contact information if provided
        if self.config.subject.email:
            subject["email"] = self.config.subject.email
        if self.config.subject.phone:
            subject["phone"] = self.config.subject.phone
        if self.config.subject.organization:
            subject["organization"] = self.config.subject.organization
        
        # Add type-specific fields
        if self.config.credential_type == CredentialType.PRACTITIONER:
            subject.update(self._build_practitioner_subject())
        elif self.config.credential_type in [
            CredentialType.PATIENT_RECORD,
            CredentialType.EMERGENCY_CONTACT,
            CredentialType.MEDICAL_ALERT
        ]:
            subject.update(self._build_patient_subject())
            
        return subject
    
    def _build_practitioner_subject(self) -> Dict[str, Any]:
        """Build practitioner-specific credential subject fields."""
        if not self.config.practitioner:
            raise ValueError("Practitioner configuration required for practitioner credentials")
        
        practitioner_fields = {
            "credentialLevel": self.config.practitioner.level.value,
            "description": self.config.practitioner.description,
        }
        
        if self.config.practitioner.completion_date:
            practitioner_fields["completionDate"] = self.config.practitioner.completion_date.isoformat()
        
        if self.config.practitioner.training_hours:
            practitioner_fields["trainingHours"] = self.config.practitioner.training_hours
        
        if self.config.practitioner.specializations:
            practitioner_fields["specializations"] = self.config.practitioner.specializations
            
        return practitioner_fields
    
    def _build_patient_subject(self) -> Dict[str, Any]:
        """Build patient-specific credential subject fields."""
        if not self.config.patient_record:
            raise ValueError("Patient record configuration required for patient credentials")
            
        patient_fields = {
            "patientId": self.config.patient_record.patient_id,
            "lastUpdated": self.config.patient_record.last_updated.isoformat(),
        }
        
        # Add blood type if provided
        if self.config.patient_record.blood_type:
            patient_fields["bloodType"] = self.config.patient_record.blood_type
        
        # Add emergency contacts
        if self.config.patient_record.emergency_contacts:
            patient_fields["emergencyContacts"] = [
                {
                    "name": contact.name,
                    "relationship": contact.relationship,
                    "phone": contact.phone,
                    "email": contact.email,
                }
                for contact in self.config.patient_record.emergency_contacts
            ]
        
        # Add medical alerts
        if self.config.patient_record.medical_alerts:
            patient_fields["medicalAlerts"] = [
                {
                    "condition": alert.condition,
                    "severity": alert.severity,
                    "treatment": alert.treatment,
                    "medications": alert.medications,
                    "allergies": alert.allergies,
                }
                for alert in self.config.patient_record.medical_alerts
            ]
        
        # Add other medical information
        if self.config.patient_record.current_medications:
            patient_fields["currentMedications"] = self.config.patient_record.current_medications
        
        if self.config.patient_record.allergies:
            patient_fields["allergies"] = self.config.patient_record.allergies
        
        if self.config.patient_record.medical_devices:
            patient_fields["medicalDevices"] = self.config.patient_record.medical_devices
        
        if self.config.patient_record.primary_physician:
            patient_fields["primaryPhysician"] = self.config.patient_record.primary_physician
        
        # Add scoliosis-specific information
        if self.config.patient_record.scoliosis_type:
            patient_fields["scoliosisType"] = self.config.patient_record.scoliosis_type
        
        if self.config.patient_record.curve_degree:
            patient_fields["curveDegree"] = self.config.patient_record.curve_degree
            
        return patient_fields
    
    def _build_proof(self, created_time: str) -> Dict[str, Any]:
        """Build the cryptographic proof section."""
        proof = {
            "type": self.config.proof.type,
            "created": created_time,
            "proofPurpose": self.config.proof.purpose,
            "verificationMethod": self.config.issuer.verification_method,
        }
        
        if self.config.proof.use_demo_signature:
            proof["jws"] = "eyJhbGciOiJFZERTQSJ9..demo-signature"
            logger.warning("Using demo signature - not suitable for production!")
        else:
            # In a real implementation, this would generate an actual signature
            raise NotImplementedError("Real signature generation not implemented")
            
        return proof
    
    def save_credential(self, credential: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """
        Save the credential to a JSON file.
        
        Args:
            credential: The credential to save
            output_path: Optional custom output path
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            output_dir = Path(self.output_config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / self.output_config.vc_filename
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(credential, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved credential to {output_path}")
        return output_path
    
    def generate_and_save(self, output_path: Optional[Path] = None) -> tuple[Dict[str, Any], Path]:
        """
        Generate a credential and save it to file.
        
        Args:
            output_path: Optional custom output path
            
        Returns:
            Tuple of (credential dict, saved file path)
        """
        credential = self.generate_credential()
        saved_path = self.save_credential(credential, output_path)
        return credential, saved_path 