
import pytest
import os
import json
from unittest.mock import MagicMock, patch
from src.cli import check_single_file

class TestCLICheck:
    
    def test_missing_file_returns_error(self, capsys):
        exit_code = check_single_file("nonexistent.nii", quiet=True)
        assert exit_code == 3
        
    @patch('src.core.validation.integrity.IntegrityChecker.run_all_checks')
    def test_check_pass(self, mock_checks, tmp_path):
        f = tmp_path / "valid.nii"
        f.touch()
        
        # Mock passing result
        mock_result = MagicMock()
        mock_result.status.value = "PASS"
        mock_result.passed = True
        mock_checks.return_value = [mock_result]
        
        exit_code = check_single_file(str(f), quiet=True)
        assert exit_code == 0
        
    @patch('src.core.validation.integrity.IntegrityChecker.run_all_checks')
    def test_check_fail_integrity(self, mock_checks, tmp_path):
        f = tmp_path / "corrupt.nii"
        f.touch()
        
        # Mock failing result
        from src.core.validation.integrity import IntegrityResult, IntegrityStatus
        fail_result = IntegrityResult("corruption", IntegrityStatus.FAIL, "Bad")
        mock_checks.return_value = [fail_result]
        
        exit_code = check_single_file(str(f), quiet=True)
        assert exit_code == 2 # Hard Fail
        
    @patch('src.core.validation.integrity.IntegrityChecker.run_all_checks')
    @patch('src.core.validation.quality.QualityChecker.calculate_snr')
    def test_check_fail_quality(self, mock_snr, mock_integrity, tmp_path):
        f = tmp_path / "noisy.nii"
        f.touch()
        
        # Integrity Passes
        from src.core.validation.integrity import IntegrityResult, IntegrityStatus
        mock_integrity.return_value = [IntegrityResult("ok", IntegrityStatus.PASS, "ok")]
        
        # Quality Fails (Mocking behavior requires mocking load too, or just partial)
        # The CLI tries to load nibabel. If we don't mock nibabel, it might fail or skip.
        # Let's mock nibabel load to return a dummy image
        with patch('nibabel.load') as mock_load:
            mock_img = MagicMock()
            mock_img.shape = (10, 10, 10)
            mock_img.dataobj = MagicMock()
            mock_load.return_value = mock_img
            
            # Mock SNR Failure
            from src.core.validation.quality import QualityResult, QualityStatus
            mock_snr.return_value = QualityResult("snr", QualityStatus.FAIL, "Too noisy")
            
            exit_code = check_single_file(str(f), quiet=True)
            assert exit_code == 2 # Critical quality failure also returns 2 in current CLI logic?
            # Re-reading CLI logic: 
            # if has_critical: status="FAIL", code=2.
            # Quality FAIL sets has_critical = True. So yes, 2.
            
    def test_json_output_generated(self, tmp_path):
        f = tmp_path / "data.nii"
        f.touch()
        out = tmp_path / "report.json"
        
        with patch('src.core.validation.integrity.IntegrityChecker.run_all_checks', return_value=[]):
             check_single_file(str(f), output_path=str(out), quiet=True)
             
        assert out.exists()
        with open(out) as json_file:
            data = json.load(json_file)
            assert data['file'] == "data.nii"
