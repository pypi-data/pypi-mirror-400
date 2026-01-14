"""
Tests for Demo Data Generation

Verifies synthetic EEG and MRI generation, caching, and loading.
"""

import pytest
import numpy as np
import nibabel as nib
from pathlib import Path
import tempfile
import shutil
import json

from src.core.demo_data import (
    generate_demo_eeg,
    generate_demo_mri,
    save_demo_data,
    load_demo_data,
    get_demo_cache_dir
)


class TestDemoEEG:
    """Test EEG demo data generation."""
    
    def test_generate_demo_eeg_shape(self):
        """Test that generated EEG has correct shape."""
        duration = 10.0
        sfreq = 500.0
        raw_eeg, clean_eeg, metadata = generate_demo_eeg(duration, sfreq)
        
        expected_samples = int(duration * sfreq)
        expected_channels = 8
        
        assert raw_eeg.shape == (expected_channels, expected_samples)
        assert clean_eeg.shape == (expected_channels, expected_samples)
    
    def test_generate_demo_eeg_metadata(self):
        """Test that metadata is correct."""
        raw_eeg, clean_eeg, metadata = generate_demo_eeg()
        
        assert metadata['type'] == 'EEG'
        assert metadata['n_channels'] == 8
        assert len(metadata['ch_names']) == 8
        assert 'Fp1' in metadata['ch_names']
        assert metadata['sfreq'] == 500.0
    
    def test_demo_eeg_has_artifacts(self):
        """Test that raw EEG has more power than clean (due to artifacts)."""
        raw_eeg, clean_eeg, metadata = generate_demo_eeg()
        
        # Raw should have higher variance due to artifacts
        raw_power = np.var(raw_eeg)
        clean_power = np.var(clean_eeg)
        
        assert raw_power > clean_power, "Raw EEG should have more power than clean"
    
    def test_demo_eeg_line_noise(self):
        """Test that 60Hz line noise is present in raw but not clean."""
        raw_eeg, clean_eeg, metadata = generate_demo_eeg()
        
        # FFT to check for 60Hz component
        from scipy.fft import fft, fftfreq
        
        sfreq = metadata['sfreq']
        n = raw_eeg.shape[1]
        
        # Analyze first channel
        raw_fft = np.abs(fft(raw_eeg[0]))
        clean_fft = np.abs(fft(clean_eeg[0]))
        freqs = fftfreq(n, 1/sfreq)
        
        # Find 60Hz bin
        idx_60hz = np.argmin(np.abs(freqs - 60.0))
        
        # Raw should have strong 60Hz component
        assert raw_fft[idx_60hz] > clean_fft[idx_60hz]


class TestDemoMRI:
    """Test MRI demo data generation."""
    
    def test_generate_demo_mri_shape(self):
        """Test that generated MRI has correct shape."""
        shape = (64, 64, 64)
        raw_mri, processed_mri, affine = generate_demo_mri(shape)
        
        assert raw_mri.shape == shape
        assert processed_mri.shape == shape
        assert affine.shape == (4, 4)
    
    def test_demo_mri_skull_stripping(self):
        """Test that processed MRI has skull removed."""
        raw_mri, processed_mri, affine = generate_demo_mri()
        
        # Processed should have more zeros (skull stripped)
        raw_zeros = np.sum(raw_mri == 0)
        processed_zeros = np.sum(processed_mri == 0)
        
        assert processed_zeros > raw_zeros, "Processed MRI should have more zeros (skull stripped)"
    
    def test_demo_mri_smoothing(self):
        """Test that processed MRI is smoother than raw."""
        raw_mri, processed_mri, affine = generate_demo_mri()
        
        # Compute gradient magnitude as measure of smoothness
        from scipy.ndimage import sobel
        
        raw_grad = np.sqrt(sobel(raw_mri, axis=0)**2 + 
                          sobel(raw_mri, axis=1)**2 + 
                          sobel(raw_mri, axis=2)**2)
        
        processed_grad = np.sqrt(sobel(processed_mri, axis=0)**2 + 
                                sobel(processed_mri, axis=1)**2 + 
                                sobel(processed_mri, axis=2)**2)
        
        # Processed should have lower gradient (smoother)
        # Only compare non-zero regions
        mask = processed_mri > 0
        if mask.sum() > 0:
            raw_grad_mean = raw_grad[mask].mean()
            processed_grad_mean = processed_grad[mask].mean()
            assert processed_grad_mean < raw_grad_mean, "Processed MRI should be smoother"


class TestDemoCaching:
    """Test demo data caching and loading."""
    
    def test_save_and_load_demo_data(self):
        """Test that demo data can be saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            
            # Save demo data
            paths = save_demo_data(cache_dir)
            
            # Verify all files exist
            assert Path(paths['eeg_raw']).exists()
            assert Path(paths['eeg_clean']).exists()
            assert Path(paths['mri_raw']).exists()
            assert Path(paths['mri_clean']).exists()
            
            # Verify manifest
            manifest_path = cache_dir / 'manifest.json'
            assert manifest_path.exists()
            
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            assert manifest['version'] == '1.0'
            assert manifest['generated'] == True
    
    def test_load_demo_data_generates_if_missing(self, monkeypatch):
        """Test that load_demo_data generates data if cache is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / 'demo'
            
            # Mock get_demo_cache_dir to use temp directory
            monkeypatch.setattr('src.core.demo_data.get_demo_cache_dir', lambda: cache_dir)
            
            # Load (should generate)
            paths = load_demo_data()
            
            # Verify files were created
            assert cache_dir.exists()
            assert Path(paths['eeg_raw']).exists()
    
    def test_load_demo_data_uses_cache(self, monkeypatch):
        """Test that load_demo_data uses cached data if available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / 'demo'
            
            # Mock get_demo_cache_dir
            monkeypatch.setattr('src.core.demo_data.get_demo_cache_dir', lambda: cache_dir)
            
            # First load (generates)
            paths1 = load_demo_data()
            
            # Get file modification time
            eeg_raw_path = Path(paths1['eeg_raw'])
            mtime1 = eeg_raw_path.stat().st_mtime
            
            # Second load (should use cache)
            import time
            time.sleep(0.1)  # Ensure time difference
            paths2 = load_demo_data()
            
            # File should not have been regenerated
            mtime2 = eeg_raw_path.stat().st_mtime
            assert mtime1 == mtime2, "Cached file should not be regenerated"


class TestDemoDataIntegration:
    """Integration tests for demo data."""
    
    def test_eeg_data_loadable_as_numpy(self):
        """Test that saved EEG data can be loaded with NumPy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            paths = save_demo_data(cache_dir)
            
            # Load with NumPy
            raw_eeg = np.load(paths['eeg_raw'])
            clean_eeg = np.load(paths['eeg_clean'])
            
            assert raw_eeg.shape == clean_eeg.shape
            assert raw_eeg.ndim == 2  # (channels, samples)
    
    def test_mri_data_loadable_as_nifti(self):
        """Test that saved MRI data can be loaded with Nibabel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            paths = save_demo_data(cache_dir)
            
            # Load with Nibabel
            raw_img = nib.load(paths['mri_raw'])
            clean_img = nib.load(paths['mri_clean'])
            
            assert raw_img.shape == clean_img.shape
            assert len(raw_img.shape) == 3  # 3D volume
            
            # Check affine
            assert raw_img.affine.shape == (4, 4)
    
    def test_metadata_json_valid(self):
        """Test that EEG metadata JSON is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            paths = save_demo_data(cache_dir)
            
            # Load metadata
            with open(paths['eeg_meta']) as f:
                metadata = json.load(f)
            
            # Verify required fields
            assert 'ch_names' in metadata
            assert 'sfreq' in metadata
            assert 'type' in metadata
            assert metadata['type'] == 'EEG'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
