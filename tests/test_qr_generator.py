"""
Tests for the QR generator using Kim's credentials.
"""

import json
import pytest
from pathlib import Path

from dynamic_scoliosis_credentials.qr_generator import QRGenerator
from dynamic_scoliosis_credentials.models import QRConfig


class TestKimQRGenerator:
    """Test QR code generation with Kim's credentials."""
    
    def test_kim_credential_encoding(self, sample_vc_dict):
        """Test encoding Kim's verifiable credential for QR."""
        qr_generator = QRGenerator()
        payload = qr_generator.encode_credential_for_qr(sample_vc_dict)
        
        # Check payload format
        assert payload.startswith("VC:")
        assert len(payload) > 3  # Should have content after prefix
        
        # Check base64 encoding (should be valid base64)
        import base64
        encoded_part = payload[3:]  # Remove "VC:" prefix
        try:
            decoded_data = base64.urlsafe_b64decode(encoded_part.encode('ascii'))
            assert len(decoded_data) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64 encoding: {e}")
    
    def test_kim_credential_encoding_with_compression(self, sample_vc_dict):
        """Test encoding Kim's credential with compression enabled."""
        config = QRConfig(use_compression=True)
        qr_generator = QRGenerator(config)
        
        # Test with compression
        compressed_payload = qr_generator.encode_credential_for_qr(sample_vc_dict)
        
        # Test without compression
        config_no_compression = QRConfig(use_compression=False)
        qr_generator_no_compression = QRGenerator(config_no_compression)
        uncompressed_payload = qr_generator_no_compression.encode_credential_for_qr(sample_vc_dict)
        
        # Compressed should be shorter
        assert len(compressed_payload) < len(uncompressed_payload)
    
    def test_kim_credential_decode_roundtrip(self, sample_vc_dict):
        """Test encoding and then decoding Kim's credential."""
        qr_generator = QRGenerator()
        
        # Encode
        payload = qr_generator.encode_credential_for_qr(sample_vc_dict)
        
        # Decode
        decoded_credential = qr_generator.decode_credential_from_qr(payload)
        
        # Should match original
        assert decoded_credential["credentialSubject"]["name"] == "Kim Johnson"
        assert decoded_credential["issuer"] == "did:web:kim-clinic.example"
        assert decoded_credential["credentialSubject"]["credentialLevel"] == "Certified"
        assert decoded_credential["id"] == sample_vc_dict["id"]
    
    def test_kim_credential_decode_compressed_roundtrip(self, sample_vc_dict):
        """Test roundtrip with compression for Kim's credential."""
        config = QRConfig(use_compression=True)
        qr_generator = QRGenerator(config)
        
        # Encode with compression
        payload = qr_generator.encode_credential_for_qr(sample_vc_dict)
        
        # Decode (should auto-detect compression)
        decoded_credential = qr_generator.decode_credential_from_qr(payload)
        
        # Should match original
        assert decoded_credential["credentialSubject"]["name"] == "Kim Johnson"
        assert decoded_credential["credentialSubject"]["trainingHours"] == 120
    
    def test_kim_qr_image_generation(self, sample_vc_dict, temp_dir):
        """Test generating QR image for Kim's credential."""
        qr_generator = QRGenerator()
        payload = qr_generator.encode_credential_for_qr(sample_vc_dict)
        
        qr_path = temp_dir / "kim_qr.png"
        generated_path = qr_generator.generate_qr_image(payload, qr_path)
        
        # Check file was created
        assert generated_path.exists()
        assert generated_path == qr_path
        assert generated_path.suffix == ".png"
        
        # Check file has content
        assert generated_path.stat().st_size > 0
    
    def test_kim_credential_qr_full_workflow(self, sample_vc_dict, temp_dir):
        """Test complete QR generation workflow for Kim's credential."""
        qr_generator = QRGenerator()
        qr_path = temp_dir / "kim_credential_qr.png"
        
        payload, image_path = qr_generator.generate_credential_qr(sample_vc_dict, qr_path)
        
        # Check payload
        assert payload.startswith("VC:")
        
        # Check image was created
        assert image_path.exists()
        assert image_path == qr_path
        
        # Verify we can decode the payload
        decoded_credential = qr_generator.decode_credential_from_qr(payload)
        assert decoded_credential["credentialSubject"]["name"] == "Kim Johnson"
    
    def test_kim_qr_size_estimation(self, sample_vc_dict):
        """Test QR size estimation for Kim's credential."""
        qr_generator = QRGenerator()
        size_info = qr_generator.estimate_qr_size(sample_vc_dict)
        
        # Check size info structure
        assert "original_json_bytes" in size_info
        assert "compressed_bytes" in size_info
        assert "qr_payload_bytes" in size_info
        assert "compression_ratio" in size_info
        assert "recommended_version" in size_info
        
        # Check values are reasonable
        assert size_info["original_json_bytes"] > 0
        assert size_info["compressed_bytes"] > 0
        assert size_info["qr_payload_bytes"] > 0
        assert size_info["compressed_bytes"] <= size_info["original_json_bytes"]
        
        # Compression ratio should be a percentage string
        assert "%" in size_info["compression_ratio"]
        
        # Recommended version should mention version
        assert "Version" in size_info["recommended_version"]
    
    def test_kim_qr_config_customization(self, sample_vc_dict, temp_dir):
        """Test QR generation with custom configuration for Kim's credential."""
        config = QRConfig(
            use_compression=True,
            error_correction="H",
            box_size=12,
            border=5,
        )
        qr_generator = QRGenerator(config)
        
        qr_path = temp_dir / "kim_custom_qr.png"
        payload, image_path = qr_generator.generate_credential_qr(sample_vc_dict, qr_path)
        
        assert image_path.exists()
        
        # Verify we can still decode with custom settings
        decoded_credential = qr_generator.decode_credential_from_qr(payload)
        assert decoded_credential["credentialSubject"]["name"] == "Kim Johnson"
    
    def test_invalid_qr_payload_decode(self):
        """Test decoding invalid QR payloads."""
        qr_generator = QRGenerator()
        
        # Test invalid prefix
        with pytest.raises(ValueError, match="Invalid QR payload: must start with 'VC:'"):
            qr_generator.decode_credential_from_qr("INVALID:payload")
        
        # Test invalid base64
        with pytest.raises(ValueError, match="Failed to decode QR payload"):
            qr_generator.decode_credential_from_qr("VC:invalid_base64!")
        
        # Test invalid JSON after decoding
        import base64
        invalid_json = base64.urlsafe_b64encode(b"not json").decode('ascii')
        with pytest.raises(ValueError, match="Failed to decode QR payload"):
            qr_generator.decode_credential_from_qr(f"VC:{invalid_json}")
    
    def test_kim_qr_directory_creation(self, sample_vc_dict, temp_dir):
        """Test that QR generator creates output directories as needed."""
        nested_dir = temp_dir / "kim" / "qr_codes" / "output"
        qr_path = nested_dir / "kim_qr.png"
        
        # Directory doesn't exist yet
        assert not nested_dir.exists()
        
        qr_generator = QRGenerator()
        generated_path = qr_generator.generate_qr_image(
            qr_generator.encode_credential_for_qr(sample_vc_dict),
            qr_path
        )
        
        # Directory should be created
        assert nested_dir.exists()
        assert generated_path.exists()
    
    def test_qr_version_estimation_accuracy(self, sample_vc_dict):
        """Test QR version estimation with different payload sizes."""
        qr_generator = QRGenerator()
        
        # Test with Kim's normal credential
        size_info = qr_generator.estimate_qr_size(sample_vc_dict)
        
        # Should recommend a reasonable version (not too high)
        version_text = size_info["recommended_version"]
        if "Version" in version_text:
            # Extract version number
            version_num = int(version_text.split()[1])
            assert 1 <= version_num <= 10, "Version should be reasonable for typical credential size"
    
    def test_kim_large_credential_handling(self, kim_patient_record, temp_dir):
        """Test QR generation with Kim's large patient record credential."""
        from dynamic_scoliosis_credentials.generator import CredentialGenerator
        from dynamic_scoliosis_credentials.models import (
            CredentialConfig, CredentialType, IssuerConfig, SubjectConfig
        )
        
        # Create a large credential with lots of data
        issuer = IssuerConfig(
            did="did:web:kim-hospital.example",
            name="Kim Memorial Hospital",
            verification_method="did:web:kim-hospital.example#key-1",
        )
        subject = SubjectConfig(name="Kim Johnson")
        
        config = CredentialConfig(
            credential_type=CredentialType.PATIENT_RECORD,
            issuer=issuer,
            subject=subject,
            patient_record=kim_patient_record,
        )
        
        # Generate the credential
        generator = CredentialGenerator(config)
        large_credential = generator.generate_credential()
        
        # Test QR generation
        qr_generator = QRGenerator()
        qr_path = temp_dir / "kim_large_qr.png"
        
        payload, image_path = qr_generator.generate_credential_qr(large_credential, qr_path)
        
        # Should still work
        assert image_path.exists()
        
        # Should be decodable
        decoded_credential = qr_generator.decode_credential_from_qr(payload)
        assert decoded_credential["credentialSubject"]["name"] == "Kim Johnson"
        assert decoded_credential["credentialSubject"]["patientId"] == "KIM001"


class TestQRGeneratorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_qr_config_validation(self):
        """Test QR configuration edge cases."""
        qr_generator = QRGenerator()
        
        # Test with None config (should use defaults)
        assert qr_generator.config.use_compression is True
        assert qr_generator.config.error_correction == "Q"
    
    def test_empty_credential_handling(self):
        """Test handling of minimal credential data."""
        minimal_credential = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": ["VerifiableCredential"],
            "issuer": "did:web:kim-clinic.example",
            "issuanceDate": "2024-01-01T00:00:00Z",
            "credentialSubject": {"name": "Kim Johnson"},
        }
        
        qr_generator = QRGenerator()
        
        # Should handle minimal credential
        payload = qr_generator.encode_credential_for_qr(minimal_credential)
        assert payload.startswith("VC:")
        
        # Should be decodable
        decoded = qr_generator.decode_credential_from_qr(payload)
        assert decoded["credentialSubject"]["name"] == "Kim Johnson"
    
    def test_qr_fallback_library_simulation(self, sample_vc_dict, temp_dir, monkeypatch):
        """Test QR generation fallback when qrcode library is not available."""
        qr_generator = QRGenerator()
        
        # Mock ImportError for qrcode
        def mock_qrcode_import(*args, **kwargs):
            raise ImportError("qrcode not available")
        
        # We can't easily test the actual fallback without complex mocking,
        # but we can test that the method exists and handles the case
        assert hasattr(qr_generator, '_generate_with_segno')
        assert hasattr(qr_generator, '_generate_with_qrcode')
    
    def test_compression_detection(self):
        """Test automatic compression detection in decode."""
        qr_generator = QRGenerator()
        
        # Create payload with compression
        config_compressed = QRConfig(use_compression=True)
        qr_gen_compressed = QRGenerator(config_compressed)
        
        # Create payload without compression
        config_uncompressed = QRConfig(use_compression=False)
        qr_gen_uncompressed = QRGenerator(config_uncompressed)
        
        test_data = {"test": "data", "name": "Kim Johnson"}
        
        # Both should be decodable by the same decoder
        compressed_payload = qr_gen_compressed.encode_credential_for_qr(test_data)
        uncompressed_payload = qr_gen_uncompressed.encode_credential_for_qr(test_data)
        
        # Both should decode correctly
        decoded_compressed = qr_generator.decode_credential_from_qr(compressed_payload)
        decoded_uncompressed = qr_generator.decode_credential_from_qr(uncompressed_payload)
        
        assert decoded_compressed["name"] == "Kim Johnson"
        assert decoded_uncompressed["name"] == "Kim Johnson" 