"""
Utility functions for the Dynamic Scoliosis Credentials System.

This module provides validation, configuration helpers, and other utility functions.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import CredentialConfig, CredentialType

logger = logging.getLogger(__name__)


class CredentialValidator:
    """Utility class for validating verifiable credentials."""
    
    @staticmethod
    def validate_w3c_vc_structure(credential: Dict[str, Any]) -> List[str]:
        """
        Validate that a credential follows W3C VC structure.
        
        Args:
            credential: The credential to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = ["@context", "type", "issuer", "issuanceDate", "credentialSubject"]
        for field in required_fields:
            if field not in credential:
                errors.append(f"Missing required field: {field}")
        
        # Validate @context
        if "@context" in credential:
            context = credential["@context"]
            if not isinstance(context, list) or len(context) == 0:
                errors.append("@context must be a non-empty array")
            elif "https://www.w3.org/2018/credentials/v1" not in context:
                errors.append("@context must include https://www.w3.org/2018/credentials/v1")
        
        # Validate type
        if "type" in credential:
            credential_type = credential["type"]
            if not isinstance(credential_type, list) or "VerifiableCredential" not in credential_type:
                errors.append("type must be an array containing 'VerifiableCredential'")
        
        # Validate issuer
        if "issuer" in credential:
            issuer = credential["issuer"]
            if not isinstance(issuer, str) or not issuer.startswith("did:"):
                errors.append("issuer must be a DID string")
        
        # Validate dates
        date_fields = ["issuanceDate", "expirationDate"]
        for date_field in date_fields:
            if date_field in credential:
                try:
                    datetime.fromisoformat(credential[date_field].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"{date_field} must be a valid ISO 8601 date")
        
        # Validate credentialSubject
        if "credentialSubject" in credential:
            subject = credential["credentialSubject"]
            if not isinstance(subject, dict):
                errors.append("credentialSubject must be an object")
        
        return errors
    
    @staticmethod
    def validate_dynamic_scoliosis_fields(credential: Dict[str, Any]) -> List[str]:
        """
        Validate Dynamic Scoliosis specific fields.
        
        Args:
            credential: The credential to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if "credentialSubject" not in credential:
            return ["Missing credentialSubject"]
        
        subject = credential["credentialSubject"]
        credential_types = credential.get("type", [])
        
        # Validate practitioner credentials
        if "DynamicScoliosisPractitionerCredential" in credential_types:
            required_practitioner_fields = ["credentialLevel", "description"]
            for field in required_practitioner_fields:
                if field not in subject:
                    errors.append(f"Missing required practitioner field: {field}")
            
            # Validate credential level
            if "credentialLevel" in subject:
                valid_levels = ["Level 1", "Level 2", "Level 3", "Certified", "Expert"]
                if subject["credentialLevel"] not in valid_levels:
                    errors.append(f"Invalid credentialLevel: {subject['credentialLevel']}")
        
        # Validate patient record credentials
        elif "PatientHealthRecordCredential" in credential_types:
            required_patient_fields = ["patientId"]
            for field in required_patient_fields:
                if field not in subject:
                    errors.append(f"Missing required patient field: {field}")
        
        return errors
    
    @staticmethod
    def validate_credential(credential: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive validation of a verifiable credential.
        
        Args:
            credential: The credential to validate
            
        Returns:
            Validation result with errors and warnings
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        # W3C VC structure validation
        w3c_errors = CredentialValidator.validate_w3c_vc_structure(credential)
        result["errors"].extend(w3c_errors)
        
        # Dynamic Scoliosis specific validation
        ds_errors = CredentialValidator.validate_dynamic_scoliosis_fields(credential)
        result["errors"].extend(ds_errors)
        
        # Check for demo signatures
        if "proof" in credential and "jws" in credential["proof"]:
            if credential["proof"]["jws"] == "eyJhbGciOiJFZERTQSJ9..demo-signature":
                result["warnings"].append("Using demo signature - not suitable for production")
        
        # Check expiration
        if "expirationDate" in credential:
            try:
                exp_date = datetime.fromisoformat(credential["expirationDate"].replace('Z', '+00:00'))
                if exp_date <= datetime.now(timezone.utc):
                    result["warnings"].append("Credential has expired")
            except ValueError:
                pass  # Already caught in structure validation
        
        # Set overall validity
        result["is_valid"] = len(result["errors"]) == 0
        
        # Add info
        result["info"]["credential_types"] = credential.get("type", [])
        result["info"]["issuer"] = credential.get("issuer")
        result["info"]["subject_name"] = credential.get("credentialSubject", {}).get("name")
        
        return result


class ConfigurationHelper:
    """Helper class for managing configuration files."""
    
    @staticmethod
    def load_config_from_file(config_path: Path) -> CredentialConfig:
        """
        Load configuration from a JSON or YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Loaded configuration
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        raise ValueError("PyYAML required for YAML configuration files")
                else:
                    data = json.load(f)
            
            return CredentialConfig.model_validate(data)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_path}: {e}")
    
    @staticmethod
    def save_config_to_file(config: CredentialConfig, config_path: Path) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config: Configuration to save
            config_path: Path where to save the configuration
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"Saved configuration to {config_path}")
    
    @staticmethod
    def create_example_configs(output_dir: Path) -> Dict[str, Path]:
        """
        Create example configuration files for different credential types.
        
        Args:
            output_dir: Directory where to create example configs
            
        Returns:
            Dictionary mapping config type to file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        configs = {}
        
        # Practitioner configuration example
        practitioner_config = ConfigurationHelper._create_practitioner_example()
        practitioner_path = output_dir / "practitioner_config.json"
        ConfigurationHelper.save_config_to_file(practitioner_config, practitioner_path)
        configs["practitioner"] = practitioner_path
        
        # Patient record configuration example
        patient_config = ConfigurationHelper._create_patient_example()
        patient_path = output_dir / "patient_config.json"
        ConfigurationHelper.save_config_to_file(patient_config, patient_path)
        configs["patient"] = patient_path
        
        return configs
    
    @staticmethod
    def _create_practitioner_example() -> CredentialConfig:
        """Create an example practitioner credential configuration."""
        from .models import (
            CredentialType, CredentialLevel, IssuerConfig, SubjectConfig,
            PractitionerCredential
        )
        
        return CredentialConfig(
            credential_type=CredentialType.PRACTITIONER,
            issuer=IssuerConfig(
                did="did:web:kim-clinic.example",
                name="Dr. Kim's Dynamic Scoliosis Training Center",
                verification_method="did:web:kim-clinic.example#key-1",
            ),
            subject=SubjectConfig(
                name="Example Practitioner",
                email="practitioner@example.com",
                organization="Example Medical Center",
            ),
            practitioner=PractitionerCredential(
                level=CredentialLevel.LEVEL_1,
                training_hours=40,
                specializations=["Dynamic Scoliosis Assessment", "Treatment Planning"],
            ),
        )
    
    @staticmethod
    def _create_patient_example() -> CredentialConfig:
        """Create an example patient record credential configuration."""
        from .models import (
            CredentialType, IssuerConfig, SubjectConfig, PatientHealthRecord,
            EmergencyContact, MedicalAlert
        )
        
        return CredentialConfig(
            credential_type=CredentialType.PATIENT_RECORD,
            issuer=IssuerConfig(
                did="did:web:hospital.example",
                name="Example Hospital System",
                verification_method="did:web:hospital.example#key-1",
            ),
            subject=SubjectConfig(
                name="Example Patient",
            ),
            patient_record=PatientHealthRecord(
                patient_id="P123456",
                blood_type="O+",
                emergency_contacts=[
                    EmergencyContact(
                        name="Emergency Contact",
                        relationship="Spouse",
                        phone="+1-555-0123",
                        email="emergency@example.com",
                    )
                ],
                medical_alerts=[
                    MedicalAlert(
                        condition="Dynamic Scoliosis",
                        severity="medium",
                        treatment="Physical therapy recommended",
                    )
                ],
                allergies=["Penicillin"],
                scoliosis_type="dynamic",
                curve_degree=25.5,
            ),
        )


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Set up logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_credential_summary(credential: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a human-readable summary of a credential.
    
    Args:
        credential: The credential to summarize
        
    Returns:
        Dictionary with summary information
    """
    summary = {}
    
    # Basic information
    summary["id"] = credential.get("id", "Unknown")
    summary["types"] = credential.get("type", [])
    summary["issuer"] = credential.get("issuer", "Unknown")
    summary["issuance_date"] = credential.get("issuanceDate", "Unknown")
    summary["expiration_date"] = credential.get("expirationDate", "No expiration")
    
    # Subject information
    subject = credential.get("credentialSubject", {})
    summary["subject_name"] = subject.get("name", "Unknown")
    summary["subject_id"] = subject.get("id", "No DID")
    
    # Type-specific information
    if "DynamicScoliosisPractitionerCredential" in summary["types"]:
        summary["credential_level"] = subject.get("credentialLevel", "Unknown")
        summary["description"] = subject.get("description", "No description")
    elif "PatientHealthRecordCredential" in summary["types"]:
        summary["patient_id"] = subject.get("patientId", "Unknown")
        summary["blood_type"] = subject.get("bloodType", "Unknown")
        summary["has_emergency_contacts"] = bool(subject.get("emergencyContacts", []))
        summary["has_medical_alerts"] = bool(subject.get("medicalAlerts", []))
    
    return summary 