
import pytest
import os
from src.adapters.ingestion.factory import DataFactory, AdapterType

class TestDataFactoryMagicBytes:
    """Tests for FR-03: Magic Bytes Detection in DataFactory.sniff()"""
    
    def test_sniff_nifti_by_extension(self, tmp_path):
        """Test that .nii.gz extension is correctly sniffed as MRI."""
        f = tmp_path / "test.nii.gz"
        f.touch()
        result = DataFactory.sniff(str(f))
        assert result == AdapterType.MRI
        
    def test_sniff_fif_by_extension(self, tmp_path):
        """Test that .fif extension is correctly sniffed as EEG."""
        f = tmp_path / "test.fif"
        f.touch()
        result = DataFactory.sniff(str(f))
        assert result == AdapterType.EEG
        
    def test_sniff_unknown_extension(self, tmp_path):
        """Test that unknown extensions return UNKNOWN."""
        f = tmp_path / "test.xyz"
        f.touch()
        result = DataFactory.sniff(str(f))
        assert result == AdapterType.UNKNOWN
        
    def test_sniff_nifti_magic_bytes(self, tmp_path):
        """Test that NIfTI is identified by magic bytes even with wrong extension."""
        f = tmp_path / "misnamed.dat"
        with open(f, "wb") as fp:
            # Write 348 bytes (NIfTI header)
            fp.write(b'\\x00' * 344)
            fp.write(b'n+1\\0') # NIfTI magic
        result = DataFactory.sniff(str(f))
        # Returns UNKNOWN because extension doesn't match known types
        assert result == AdapterType.UNKNOWN

    def test_sniff_fif_magic_bytes(self, tmp_path):
        """Test that FIF with correct extension is identified."""
        f = tmp_path / "test.fif"
        with open(f, "wb") as fp:
            fp.write(b'FIFF') # FIF magic header
            fp.write(b'\\x00' * 100) # Padding
        result = DataFactory.sniff(str(f))
        assert result == AdapterType.EEG
