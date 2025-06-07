"""
QR Code Generator for the Dynamic Scoliosis Credentials System.

This module provides QR code generation functionality for verifiable credentials
with configurable compression and formatting options.
"""

import base64
import gzip
import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

from .models import QRConfig

logger = logging.getLogger(__name__)


class QRGenerator:
    """Class for generating QR codes from verifiable credentials."""
    
    def __init__(self, config: QRConfig = None):
        """
        Initialize the QR generator.
        
        Args:
            config: QR configuration options
        """
        self.config = config or QRConfig()
    
    def encode_credential_for_qr(self, credential: Dict[str, Any]) -> str:
        """
        Encode a verifiable credential for QR code storage.
        
        Args:
            credential: The verifiable credential to encode
            
        Returns:
            Encoded string suitable for QR code
        """
        # Serialize credential to compact JSON
        credential_json = json.dumps(credential, separators=(",", ":")).encode('utf-8')
        
        # Apply compression if enabled
        if self.config.use_compression:
            credential_json = gzip.compress(credential_json)
            logger.debug(f"Compressed credential from {len(json.dumps(credential, separators=(',', ':')).encode('utf-8'))} to {len(credential_json)} bytes")
        
        # Base64 encode for safe QR storage
        encoded = base64.urlsafe_b64encode(credential_json).decode('ascii')
        
        # Add VC prefix to identify the payload type
        return f"VC:{encoded}"
    
    def decode_credential_from_qr(self, qr_payload: str) -> Dict[str, Any]:
        """
        Decode a verifiable credential from QR payload.
        
        Args:
            qr_payload: The QR code payload string
            
        Returns:
            The decoded verifiable credential
            
        Raises:
            ValueError: If the payload is invalid
        """
        if not qr_payload.startswith("VC:"):
            raise ValueError("Invalid QR payload: must start with 'VC:'")
        
        # Remove prefix
        encoded_data = qr_payload[3:]
        
        try:
            # Base64 decode
            compressed_data = base64.urlsafe_b64decode(encoded_data.encode('ascii'))
            
            # Decompress if needed (detect gzip magic numbers)
            if compressed_data.startswith(b'\x1f\x8b'):
                credential_json = gzip.decompress(compressed_data)
            else:
                credential_json = compressed_data
            
            # Parse JSON
            return json.loads(credential_json.decode('utf-8'))
            
        except Exception as e:
            raise ValueError(f"Failed to decode QR payload: {e}")
    
    def generate_qr_image(self, payload: str, output_path: Path) -> Path:
        """
        Generate a QR code image from the given payload.
        
        Args:
            payload: The data to encode in the QR code
            output_path: Path where to save the QR code image
            
        Returns:
            Path to the generated image file
        """
        try:
            # Try qrcode library first (better quality)
            return self._generate_with_qrcode(payload, output_path)
        except ImportError:
            logger.info("qrcode library not available, falling back to segno")
            return self._generate_with_segno(payload, output_path)
    
    def _generate_with_qrcode(self, payload: str, output_path: Path) -> Path:
        """Generate QR code using the qrcode library."""
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
        
        # Map error correction levels
        error_levels = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H,
        }
        
        error_correct = error_levels.get(self.config.error_correction, ERROR_CORRECT_Q)
        
        qr = qrcode.QRCode(
            version=1,  # Auto-size
            error_correction=error_correct,
            box_size=self.config.box_size,
            border=self.config.border,
        )
        
        qr.add_data(payload)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image
        img.save(output_path)
        logger.info(f"Generated QR code using qrcode library: {output_path}")
        
        return output_path
    
    def _generate_with_segno(self, payload: str, output_path: Path) -> Path:
        """Generate QR code using the segno library."""
        import segno
        
        # Map error correction levels for segno
        error_levels = {
            'L': 'l',
            'M': 'm', 
            'Q': 'q',
            'H': 'h',
        }
        
        error_correct = error_levels.get(self.config.error_correction, 'q')
        
        qr = segno.make(payload, error=error_correct)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image (segno automatically detects format from extension)
        qr.save(
            output_path,
            scale=self.config.box_size,
            border=self.config.border,
            dark='black',
            light='white',
        )
        
        logger.info(f"Generated QR code using segno library: {output_path}")
        return output_path
    
    def generate_credential_qr(
        self,
        credential: Dict[str, Any],
        output_path: Path
    ) -> tuple[str, Path]:
        """
        Generate a QR code for a verifiable credential.
        
        Args:
            credential: The verifiable credential to encode
            output_path: Path where to save the QR code image
            
        Returns:
            Tuple of (qr_payload_string, generated_image_path)
        """
        # Encode credential for QR
        qr_payload = self.encode_credential_for_qr(credential)
        
        # Generate QR image
        image_path = self.generate_qr_image(qr_payload, output_path)
        
        return qr_payload, image_path
    
    def estimate_qr_size(self, credential: Dict[str, Any]) -> Dict[str, Union[int, str]]:
        """
        Estimate the size requirements for a credential QR code.
        
        Args:
            credential: The verifiable credential to analyze
            
        Returns:
            Dictionary with size information
        """
        # Get payload
        payload = self.encode_credential_for_qr(credential)
        
        # Calculate sizes
        uncompressed_json = json.dumps(credential, separators=(",", ":"))
        compressed_json = gzip.compress(uncompressed_json.encode('utf-8'))
        
        return {
            "original_json_bytes": len(uncompressed_json.encode('utf-8')),
            "compressed_bytes": len(compressed_json),
            "qr_payload_bytes": len(payload.encode('utf-8')),
            "compression_ratio": f"{len(compressed_json) / len(uncompressed_json.encode('utf-8')):.2%}",
            "recommended_version": self._estimate_qr_version(len(payload)),
        }
    
    def _estimate_qr_version(self, data_length: int) -> str:
        """Estimate the QR code version needed for the given data length."""
        # Rough estimates for different QR versions with error correction Q
        version_capacities = {
            1: 80, 2: 154, 3: 224, 4: 279, 5: 335,
            6: 395, 7: 468, 8: 535, 9: 619, 10: 667,
            11: 758, 12: 854, 13: 938, 14: 1046, 15: 1153,
            16: 1249, 17: 1352, 18: 1460, 19: 1588, 20: 1704,
        }
        
        for version, capacity in version_capacities.items():
            if data_length <= capacity:
                return f"Version {version}"
        
        return "Version 20+ (may not scan reliably)" 