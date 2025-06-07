"""
Dynamic Scoliosis Credentials System

A reusable system for generating W3C Verifiable Credentials for Dynamic Scoliosis
practitioners and patient health records.
"""

__version__ = "1.0.0"
__author__ = "Dynamic Scoliosis Credential System"

from .models import (
    CredentialConfig,
    IssuerConfig,
    SubjectConfig,
    CredentialType,
    PatientHealthRecord,
    PractitionerCredential,
)
from .generator import CredentialGenerator
from .qr_generator import QRGenerator
from .utils import CredentialValidator

__all__ = [
    "__version__",
    "__author__",
    "CredentialConfig",
    "IssuerConfig", 
    "SubjectConfig",
    "CredentialType",
    "PatientHealthRecord",
    "PractitionerCredential",
    "CredentialGenerator",
    "QRGenerator",
    "CredentialValidator",
] 