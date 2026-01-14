
import pytest
import os
import numpy as np
import struct
from src.core.validation.integrity import IntegrityChecker, IntegrityStatus

class TestIntegrityChecks:
    
    @pytest.fixture
    def checker(self):
        return IntegrityChecker(min_file_size_bytes=10) # Small min size for tests
    
    def test_file_integrity_missing(self, checker):
        res = checker.check_file_corruption("missing.nii")
        assert res.status == IntegrityStatus.FAIL
        assert "not found" in res.message
        
    def test_file_integrity_empty(self, checker, tmp_path):
        f = tmp_path / "empty.nii"
        f.touch()
        res = checker.check_file_corruption(str(f))
        assert res.status == IntegrityStatus.FAIL
        assert "zero bytes" in res.message
        
    def test_magic_bytes_nifti(self, checker, tmp_path):
        # Create a Fake NIfTI
        f = tmp_path / "fake.nii"
        with open(f, "wb") as f_out:
            # Write 348 bytes
            f_out.write(b'\x00' * 344)
            f_out.write(b'n+1\0') # Valid Magic
        
        res = checker.check_magic_bytes(str(f))
        assert res.status == IntegrityStatus.PASS
        
    def test_magic_bytes_nifti_bad(self, checker, tmp_path):
        f = tmp_path / "bad_magic.nii"
        with open(f, "wb") as f_out:
            f_out.write(b'\x00' * 344)
            f_out.write(b'BAD\0') 
        
        res = checker.check_magic_bytes(str(f))
        assert res.status == IntegrityStatus.FAIL
        
    def test_affine_nan(self, checker):
        affine = np.eye(4)
        affine[0, 0] = np.nan
        res = checker.check_affine_validity(affine)
        assert res.status == IntegrityStatus.FAIL
        assert "NaN values" in res.message
        
    def test_dimension_validity(self, checker):
        # Good dimensions
        res = checker.check_dimension_validity({'shape': (64, 64, 30)})
        assert res.status == IntegrityStatus.PASS
        
        # Zero dimension
        res = checker.check_dimension_validity({'shape': (64, 0, 30)})
        assert res.status == IntegrityStatus.FAIL
        
        # Negative dimension
        res = checker.check_dimension_validity({'shape': (64, -5, 30)})
        assert res.status == IntegrityStatus.FAIL
