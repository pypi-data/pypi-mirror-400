"""
Tests for MNE-Python Plugin

Comprehensive tests for MNE integration.
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

# Check if MNE is available
try:
    import mne
    MNE_AVAILABLE = True
except ImportError:
    MNE_AVAILABLE = False

from src.adapters.integrations.mne_plugin import (
    compare_preprocessing,
    compare_ica,
    compare_filter,
    _mne_to_neuroops_format
)

pytestmark = pytest.mark.skipif(not MNE_AVAILABLE, reason="MNE-Python not installed")


@pytest.fixture
def sample_raw():
    """Create a sample MNE Raw object for testing."""
    # Create synthetic data
    sfreq = 500.0
    duration = 2.0
    n_channels = 4
    n_samples = int(duration * sfreq)
    
    # Create data
    data = np.random.randn(n_channels, n_samples) * 1e-6  # Scale to Volts
    
    # Create info
    ch_names = ['Fp1', 'Fp2', 'C3', 'C4']
    ch_types = ['eeg'] * n_channels
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    
    # Create Raw object
    raw = mne.io.RawArray(data, info)
    
    return raw


class TestMNEConversion:
    """Test MNE to NeuroOps format conversion."""
    
    def test_convert_raw_to_neuroops(self, sample_raw):
        """Test conversion of MNE Raw to NeuroOps format."""
        path, metadata = _mne_to_neuroops_format(sample_raw)
        
        # Check path exists
        assert Path(path).exists()
        assert path.endswith('.fif')
        
        # Check metadata
        assert metadata['type'] == 'EEG'
        assert metadata['sfreq'] == 500.0
        assert metadata['n_channels'] == 4
        assert 'Fp1' in metadata['ch_names']
        assert 'duration' in metadata
        
        # Cleanup
        Path(path).unlink()
    
    def test_convert_with_custom_path(self, sample_raw):
        """Test conversion with custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / 'test_raw.fif')
            
            path, metadata = _mne_to_neuroops_format(sample_raw, output_path)
            
            assert path == output_path
            assert Path(path).exists()
    
    def test_metadata_preservation(self, sample_raw):
        """Test that metadata is preserved during conversion."""
        # Add some metadata to raw
        sample_raw.info['description'] = 'Test recording'
        
        path, metadata = _mne_to_neuroops_format(sample_raw)
        
        # Load back and verify
        raw_loaded = mne.io.read_raw_fif(path, preload=False, verbose=False)
        
        assert raw_loaded.info['sfreq'] == sample_raw.info['sfreq']
        assert raw_loaded.ch_names == sample_raw.ch_names
        
        # Cleanup
        Path(path).unlink()


class TestComparePreprocessing:
    """Test compare_preprocessing function."""
    
    def test_compare_two_raw_objects(self, sample_raw):
        """Test comparing two Raw objects."""
        # Create a filtered version
        raw_filtered = sample_raw.copy().filter(1, 40, verbose=False)
        
        # Compare without launching viewer
        result = compare_preprocessing(sample_raw, raw_filtered, launch_viewer=False)
        
        assert result is not None
        assert 'path_a' in result
        assert 'path_b' in result
        assert 'metadata_a' in result
        assert 'metadata_b' in result
        
        # Check files exist
        assert Path(result['path_a']).exists()
        assert Path(result['path_b']).exists()
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_metadata_consistency(self, sample_raw):
        """Test that metadata is consistent between raw and filtered."""
        raw_filtered = sample_raw.copy().filter(1, 40, verbose=False)
        
        result = compare_preprocessing(sample_raw, raw_filtered, launch_viewer=False)
        
        meta_a = result['metadata_a']
        meta_b = result['metadata_b']
        
        # Should have same channels and sfreq
        assert meta_a['ch_names'] == meta_b['ch_names']
        assert meta_a['sfreq'] == meta_b['sfreq']
        assert meta_a['n_channels'] == meta_b['n_channels']
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()


class TestCompareICA:
    """Test compare_ica function."""
    
    def test_compare_ica_removal(self, sample_raw):
        """Test comparing before/after ICA component removal."""
        # Fit ICA
        ica = mne.preprocessing.ICA(n_components=2, random_state=42, max_iter=100)
        ica.fit(sample_raw, verbose=False)
        
        # Exclude first component
        ica.exclude = [0]
        
        # Compare
        result = compare_ica(sample_raw, ica, launch_viewer=False)
        
        assert result is not None
        assert 'path_a' in result
        assert 'path_b' in result
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_compare_ica_custom_exclude(self, sample_raw):
        """Test ICA comparison with custom exclude list."""
        ica = mne.preprocessing.ICA(n_components=2, random_state=42, max_iter=100)
        ica.fit(sample_raw, verbose=False)
        
        # Use custom exclude list
        result = compare_ica(sample_raw, ica, exclude=[0, 1], launch_viewer=False)
        
        assert result is not None
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()


class TestCompareFilter:
    """Test compare_filter function."""
    
    def test_compare_bandpass_filter(self, sample_raw):
        """Test comparing before/after bandpass filter."""
        result = compare_filter(sample_raw, l_freq=1, h_freq=40, launch_viewer=False)
        
        assert result is not None
        assert 'path_a' in result
        assert 'path_b' in result
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_compare_highpass_filter(self, sample_raw):
        """Test comparing before/after highpass filter."""
        result = compare_filter(sample_raw, l_freq=1, h_freq=None, launch_viewer=False)
        
        assert result is not None
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_compare_lowpass_filter(self, sample_raw):
        """Test comparing before/after lowpass filter."""
        result = compare_filter(sample_raw, l_freq=None, h_freq=40, launch_viewer=False)
        
        assert result is not None
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()


class TestIntegration:
    """Integration tests for MNE plugin."""
    
    def test_full_preprocessing_workflow(self, sample_raw):
        """Test complete preprocessing workflow."""
        # Step 1: Filter
        raw_filtered = sample_raw.copy().filter(1, 40, verbose=False)
        
        # Step 2: ICA
        ica = mne.preprocessing.ICA(n_components=2, random_state=42, max_iter=100)
        ica.fit(raw_filtered, verbose=False)
        ica.exclude = [0]
        raw_clean = raw_filtered.copy()
        ica.apply(raw_clean, verbose=False)
        
        # Step 3: Compare original vs clean
        result = compare_preprocessing(sample_raw, raw_clean, launch_viewer=False)
        
        assert result is not None
        
        # Verify files are different
        raw_a = mne.io.read_raw_fif(result['path_a'], preload=True, verbose=False)
        raw_b = mne.io.read_raw_fif(result['path_b'], preload=True, verbose=False)
        
        # Data should be different
        assert not np.allclose(raw_a.get_data(), raw_b.get_data())
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_multiple_comparisons(self, sample_raw):
        """Test multiple sequential comparisons."""
        # Create different versions
        raw_v1 = sample_raw.copy().filter(1, 40, verbose=False)
        raw_v2 = sample_raw.copy().filter(0.1, 100, verbose=False)
        
        # Compare both
        result1 = compare_preprocessing(sample_raw, raw_v1, launch_viewer=False)
        result2 = compare_preprocessing(sample_raw, raw_v2, launch_viewer=False)
        
        assert result1 is not None
        assert result2 is not None
        
        # Files should be different
        assert result1['path_b'] != result2['path_b']
        
        # Cleanup
        for result in [result1, result2]:
            Path(result['path_a']).unlink()
            Path(result['path_b']).unlink()


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_exclude_list(self, sample_raw):
        """Test ICA comparison with empty exclude list."""
        ica = mne.preprocessing.ICA(n_components=2, random_state=42, max_iter=100)
        ica.fit(sample_raw, verbose=False)
        ica.exclude = []
        
        result = compare_ica(sample_raw, ica, launch_viewer=False)
        
        # Should still work (no components removed)
        assert result is not None
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()
    
    def test_single_channel(self):
        """Test with single-channel data."""
        sfreq = 500.0
        duration = 1.0
        n_samples = int(duration * sfreq)
        
        data = np.random.randn(1, n_samples) * 1e-6
        info = mne.create_info(ch_names=['Cz'], sfreq=sfreq, ch_types=['eeg'])
        raw = mne.io.RawArray(data, info)
        
        raw_filtered = raw.copy().filter(1, 40, verbose=False)
        
        result = compare_preprocessing(raw, raw_filtered, launch_viewer=False)
        
        assert result is not None
        assert result['metadata_a']['n_channels'] == 1
        
        # Cleanup
        Path(result['path_a']).unlink()
        Path(result['path_b']).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
