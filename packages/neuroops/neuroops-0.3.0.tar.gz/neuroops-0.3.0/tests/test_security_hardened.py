
import pytest
import os
import json
import numpy as np
import nibabel as nib
import pydicom
from pydicom.dataset import FileDataset
from src.core.anonymization import PIIScanner
from src.adapters.ingestion.factory import DataFactory
from src.core.validation.certificate import CertificateGenerator
from src.core.validation.integrity import check_file_integrity
from src.core.remediation import RemediationService
from src.core.audit import AuditLogger
from src.core.provenance import ProvenanceLogger

class TestSecurityHardening:

    @pytest.fixture
    def safe_nifti(self, tmp_path):
        """Creates a safe, clean NIfTI file."""
        data = np.zeros((10, 10, 10), dtype=np.float32)
        img = nib.Nifti1Image(data, np.eye(4))
        path = tmp_path / "safe.nii"
        nib.save(img, str(path))
        return str(path)

    @pytest.fixture
    def pii_nifti(self, tmp_path):
        """Creates a NIfTI file with embedded PII in header."""
        data = np.zeros((10, 10, 10), dtype=np.float32)
        img = nib.Nifti1Image(data, np.eye(4))
        # Embed PII
        img.header['descrip'] = b"Patient: John Doe, DOB: 1980-01-01"
        path = tmp_path / "unsafe_pii.nii"
        nib.save(img, str(path))
        return str(path)

    def test_kill_switch_nifti(self, pii_nifti):
        """FR-13: Verify DataFactory refuses to load file with PII."""
        with pytest.raises(ValueError, match="SECURITY ALERT"):
            DataFactory.load(pii_nifti)

    def test_pii_scanner_detection(self, pii_nifti, safe_nifti):
        scanner = PIIScanner()
        
        # Unsafe
        detections = scanner.scan_file(pii_nifti)
        assert len(detections) > 0
        assert detections[0]['type'] == 'NIFTI_HEADER_TEXT'
        
        # Safe
        detections = scanner.scan_file(safe_nifti)
        assert len(detections) == 0

    def test_integrity_tamper_detection(self, safe_nifti, tmp_path):
        """FR-14: Verify tampering is detected via Certificate."""
        generator = CertificateGenerator()
        
        # 1. Generate legitimate certificate
        cert = generator.generate(safe_nifti, True, [{"check": "test", "status": "PASS"}])
        cert_path = tmp_path / "safe_qc.json"
        with open(cert_path, 'w') as f:
            json.dump(cert.model_dump(), f, default=str)
            
        # 2. Verify it passes initially
        valid_cert, _ = generator.verify(str(cert_path))
        assert valid_cert
        match, _ = generator.verify_source_file(str(cert_path), safe_nifti)
        assert match
        
        # 3. TAMPER WITH FILE (Append 1 byte)
        with open(safe_nifti, 'ab') as f:
            f.write(b'\0')
            
        # 4. Verify mismatch
        match, msg = generator.verify_source_file(str(cert_path), safe_nifti)
        assert not match
        assert "hash mismatch" in msg

    def test_certificate_forgery(self, safe_nifti, tmp_path):
        """FR-14: Verify modified certificate invalidates signature."""
        generator = CertificateGenerator()
        cert = generator.generate(safe_nifti, False, [{"check": "fail", "status": "FAIL"}])
        cert_path = tmp_path / "forged_qc.json"
        
        # Serialize
        cert_data = cert.model_dump()
        
        # ATTACK: Change FAIL to PASS without updating signature
        cert_data['passed'] = True 
        
        with open(cert_path, 'w') as f:
            json.dump(cert_data, f, default=str)
            
        # Verify
        valid, msg = generator.verify(str(cert_path))
        assert not valid
        assert "signature mismatch" in msg

    def test_audit_logging(self, tmp_path):
        """FR-17: Verify actions are logged."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_path=str(log_file))
        
        test_hash = "sha256:12345fake"
        logger.log_event("TEST_ACTION", test_hash, {"info": "secure"})
        
        assert log_file.exists()
        with open(log_file, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == "TEST_ACTION"
            assert entry['file_hash'] == test_hash
            assert entry['user'] is not None

    def test_permission_locking(self, safe_nifti, tmp_path):
        """FR-16: Verify remediation outputs are Read-Only."""
        service = RemediationService(output_dir=str(tmp_path))
        
        # Perform operation (dummy crop)
        # We need a 4D file for crop, safe_nifti is 3D. Let's make a 4D one.
        data = np.zeros((10, 10, 10, 5), dtype=np.float32)
        img = nib.Nifti1Image(data, np.eye(4))
        path_4d = tmp_path / "4d.nii"
        nib.save(img, str(path_4d))
        
        out_path, _ = service.crop_time_segment(str(path_4d), 0, 10)
        prov_path = out_path + ".provenance.json"
        
        # Check permissions (On Windows, Read-Only means write bit is cleared)
        # stat.S_IWRITE is 128 (0o200). If masked, it's writable.
        import stat
        
        mode_out = os.stat(out_path).st_mode
        mode_prov = os.stat(prov_path).st_mode
        
        # Assert NOT writable
        assert not (mode_out & stat.S_IWRITE)
        assert not (mode_prov & stat.S_IWRITE)
