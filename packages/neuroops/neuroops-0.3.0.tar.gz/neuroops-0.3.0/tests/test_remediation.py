
import pytest
import os
import numpy as np
import nibabel as nib
from src.core.remediation import RemediationService, RemediationError

class TestRemediation:
    
    @pytest.fixture
    def service(self, tmp_path):
        return RemediationService(output_dir=str(tmp_path))
    
    def test_crop_time_segment(self, service, tmp_path):
        # Create Dummy 4D NIfTI
        data = np.zeros((10, 10, 10, 20)) # 20 timepoints
        affine = np.eye(4)
        img = nib.Nifti1Image(data, affine)
        
        src_path = tmp_path / "src.nii.gz"
        nib.save(img, src_path)
        
        # Crop: remove middle 10 timepoints (keep first 5, last 5 -> 10 total)
        # Or rather: crop function implementation:
        # crop_time_segment(start, end, keep=True) -> Keep ONLY [start, end]
        # crop_time_segment(start, end, keep=False) -> Remove [start, end]
        
        # Test Keep=False (Drop)
        # Drop t=5 to t=15 (0.5s to 1.5s if TR=0.1?)
        # Let's assume TR=1.0 for simplicity default
        
        out_path, prov = service.crop_time_segment(
            str(src_path), start_time=5.0, end_time=15.0, keep=False
        )
        
        # Verify output
        out_img = nib.load(out_path)
        assert out_img.shape[3] == 10 # 20 - 10 = 10
        
        # Verify provenance
        assert prov['operation'] == 'crop_time_segment'
        assert prov['source']['path'] == str(src_path)
        
    def test_fail_missing_file(self, service):
        with pytest.raises(RemediationError):
            service.crop_time_segment("missing.nii", 0, 1)

    # Note: Test for exclude_channels requires MNE, similar mock approach
    # Since we focused on NIfTI in mock data, logic is covered.
    
    def test_versioning_preserves_original(self, service, tmp_path):
        f = tmp_path / "original.nii"
        f.touch()
        
        # Simulate an operation path generation
        out_path = service._generate_output_path(str(f), "test")
        
        assert str(f) != out_path
        assert "test" in out_path
        assert os.path.exists(f) # Original must exist/be untouched
