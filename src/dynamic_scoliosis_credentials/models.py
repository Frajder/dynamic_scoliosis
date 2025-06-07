"""
Data models for the Dynamic Scoliosis Credentials System.

This module defines all the configuration and data models used throughout
the system, replacing hard-coded values with configurable options.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class CredentialType(str, Enum):
    """Types of credentials that can be issued."""
    
    PRACTITIONER = "practitioner"
    PATIENT_RECORD = "patient_record"
    EMERGENCY_CONTACT = "emergency_contact"
    MEDICAL_ALERT = "medical_alert"


class CredentialLevel(str, Enum):
    """Practitioner credential levels."""
    
    LEVEL_1 = "Level 1"
    LEVEL_2 = "Level 2"
    LEVEL_3 = "Level 3"
    CERTIFIED = "Certified"
    EXPERT = "Expert"


class QRConfig(BaseModel):
    """Configuration for QR code generation."""
    
    use_compression: bool = Field(
        default=True,
        description="Whether to use gzip compression for QR payload"
    )
    error_correction: str = Field(
        default="Q",
        description="Error correction level (L, M, Q, H)"
    )
    box_size: int = Field(
        default=10,
        ge=1,
        description="Size of each box in pixels"
    )
    border: int = Field(
        default=4,
        ge=1,
        description="Border size in boxes"
    )


class IssuerConfig(BaseModel):
    """Configuration for the credential issuer."""
    
    did: str = Field(
        description="Decentralized Identifier (DID) of the issuer",
        example="did:web:example.com:issuer"
    )
    name: str = Field(
        description="Human-readable name of the issuer",
        example="Dr. Kim's Dynamic Scoliosis Clinic"
    )
    verification_method: str = Field(
        description="Verification method identifier",
        example="did:web:example.com:issuer#key-1"
    )
    context_url: HttpUrl = Field(
        default="https://example.com/credentials/ds-practitioner",
        description="Custom context URL for the credential type"
    )
    
    @field_validator('did')
    @classmethod
    def validate_did(cls, v):
        """Validate DID format."""
        if not v.startswith('did:'):
            raise ValueError('DID must start with "did:"')
        return v


class SubjectConfig(BaseModel):
    """Configuration for the credential subject."""
    
    did: Optional[str] = Field(
        default=None,
        description="Decentralized Identifier (DID) of the subject"
    )
    name: str = Field(
        description="Full name of the credential subject",
        example="Kim Johnson"
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address of the subject"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the subject"
    )
    organization: Optional[str] = Field(
        default=None,
        description="Organization or clinic name"
    )


class PractitionerCredential(BaseModel):
    """Specific fields for practitioner credentials."""
    
    level: CredentialLevel = Field(
        description="Certification level achieved"
    )
    completion_date: Optional[datetime] = Field(
        default=None,
        description="Date when training was completed"
    )
    expiry_date: Optional[datetime] = Field(
        default=None,
        description="Date when credential expires"
    )
    training_hours: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of training hours completed"
    )
    specializations: List[str] = Field(
        default_factory=list,
        description="List of specialization areas"
    )
    description: str = Field(
        default="Completed foundational training in Dynamic Scoliosis assessment & management.",
        description="Description of the credential"
    )


class EmergencyContact(BaseModel):
    """Emergency contact information."""
    
    name: str = Field(description="Emergency contact name")
    relationship: str = Field(description="Relationship to patient")
    phone: str = Field(description="Emergency contact phone number")
    email: Optional[str] = Field(default=None, description="Emergency contact email")


class MedicalAlert(BaseModel):
    """Medical alert information."""
    
    condition: str = Field(description="Medical condition")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    treatment: Optional[str] = Field(default=None, description="Recommended treatment")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")


class PatientHealthRecord(BaseModel):
    """Patient health record information."""
    
    patient_id: str = Field(description="Unique patient identifier")
    blood_type: Optional[str] = Field(default=None, description="Blood type")
    emergency_contacts: List[EmergencyContact] = Field(
        default_factory=list,
        description="Emergency contact information"
    )
    medical_alerts: List[MedicalAlert] = Field(
        default_factory=list,
        description="Critical medical alerts"
    )
    current_medications: List[str] = Field(
        default_factory=list,
        description="Current medications"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="Known allergies"
    )
    medical_devices: List[str] = Field(
        default_factory=list,
        description="Implanted or worn medical devices"
    )
    primary_physician: Optional[str] = Field(
        default=None,
        description="Primary care physician"
    )
    scoliosis_type: Optional[str] = Field(
        default=None,
        description="Type of scoliosis (if applicable)"
    )
    curve_degree: Optional[float] = Field(
        default=None,
        description="Curve degree measurement"
    )
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the record was last updated"
    )


class ProofConfig(BaseModel):
    """Configuration for cryptographic proof."""
    
    type: str = Field(
        default="Ed25519Signature2020",
        description="Signature type"
    )
    purpose: str = Field(
        default="assertionMethod",
        description="Proof purpose"
    )
    use_demo_signature: bool = Field(
        default=True,
        description="Whether to use demo signature (for testing only)"
    )


class CredentialConfig(BaseModel):
    """Main configuration for credential generation."""
    
    credential_type: CredentialType = Field(
        description="Type of credential to generate"
    )
    issuer: IssuerConfig = Field(
        description="Issuer configuration"
    )
    subject: SubjectConfig = Field(
        description="Subject configuration"
    )
    practitioner: Optional[PractitionerCredential] = Field(
        default=None,
        description="Practitioner-specific fields"
    )
    patient_record: Optional[PatientHealthRecord] = Field(
        default=None,
        description="Patient record fields"
    )
    proof: ProofConfig = Field(
        default_factory=ProofConfig,
        description="Proof configuration"
    )
    qr_config: QRConfig = Field(
        default_factory=QRConfig,
        description="QR code generation settings"
    )
    custom_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom context fields"
    )
    expiry_date: Optional[datetime] = Field(
        default=None,
        description="Credential expiry date"
    )
    
    @model_validator(mode='after')
    def validate_credential_fields(self):
        """Validate that required fields are provided based on credential type."""
        if self.credential_type == CredentialType.PRACTITIONER and self.practitioner is None:
            raise ValueError('Practitioner fields required for practitioner credentials')
        
        if self.credential_type in [
            CredentialType.PATIENT_RECORD, 
            CredentialType.EMERGENCY_CONTACT, 
            CredentialType.MEDICAL_ALERT
        ] and self.patient_record is None:
            raise ValueError('Patient record fields required for patient record credentials')
        
        return self


class CredentialOutput(BaseModel):
    """Output configuration for generated credentials."""
    
    output_dir: str = Field(
        default="output",
        description="Output directory for generated files"
    )
    vc_filename: str = Field(
        default="credential.json",
        description="Filename for the VC JSON file"
    )
    qr_filename: str = Field(
        default="credential_qr.png",
        description="Filename for the QR code image"
    )
    generate_qr: bool = Field(
        default=True,
        description="Whether to generate QR code"
    )
    generate_pdf: bool = Field(
        default=False,
        description="Whether to generate PDF certificate"
    )
    pdf_template: Optional[str] = Field(
        default=None,
        description="Path to PDF template file"
    ) 