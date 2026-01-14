import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import os
import tempfile

# Import classes to test
from src.core.io import UniversalFactory
from src.core.mri import MRILoader
from src.core.eeg import EEGLoader
from src.adapters.local_loader import UniversalMRIAdapter, UniversalMNEAdapter

# --- 1. TEST UNIVERSAL FACTORY ---
def test_universal_factory_local():
    """Test that UniversalFactory opens local files correctly."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test data")
        tmp_path = tmp.name
    
    try:
        # Test opening
        f = UniversalFactory.open(tmp_path, "rb")
        assert f.read() == b"test data"
        f.close()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@patch("src.core.io.fsspec")
def test_universal_factory_s3(mock_fsspec):
    """Test that UniversalFactory handles S3 paths with caching."""
    # Setup mock
    mock_open_context = MagicMock()
    mock_file_handle = MagicMock()
    mock_fsspec.open.return_value = mock_open_context
    mock_open_context.open.return_value = mock_file_handle
    
    # Call
    path = "s3://bucket/file.nii"
    f = UniversalFactory.open(path)
    
    # Assert
    # Should call fsspec.open with simplecache protocol
    mock_fsspec.open.assert_called_once()
    args, kwargs = mock_fsspec.open.call_args
    assert args[0].startswith("simplecache::s3://")
    assert kwargs['s3'] == {}

# --- 2. TEST MRI LOADER ---
@patch("src.core.mri.nib")
def test_mri_loader_local(mock_nib):
    """Test MRILoader with local path optimization."""
    path = "C:/data/test.nii"
    
    # Mock nib.load return value
    mock_img = MagicMock()
    mock_img.shape = (10, 10, 10)
    mock_img.affine = np.eye(4)
    mock_nib.load.return_value = mock_img
    
    loader = MRILoader(path)
    
    # Assertions
    mock_nib.load.assert_called_with(path) # Should use path string directly
    assert loader.shape == (10, 10, 10)
    
    # Test Slicing
    mock_img.dataobj.__getitem__.return_value = np.zeros((10, 10))
    slice_data = loader.get_slice(axis=2, index=5)
    
    assert slice_data.shape == (10, 10)
    # Check slicing call: (slice(None), slice(None), 5)
    mock_img.dataobj.__getitem__.assert_called_with((slice(None), slice(None), 5))

@patch("src.core.mri.UniversalFactory")
@patch("src.core.mri.nib")
def test_mri_loader_s3(mock_nib, mock_factory):
    """Test MRILoader with S3 path (uses file object)."""
    path = "s3://bucket/test.nii"
    
    mock_file_obj = MagicMock()
    mock_factory.open.return_value = mock_file_obj
    
    mock_img = MagicMock()
    mock_nib.load.return_value = mock_img
    
    loader = MRILoader(path)
    
    # Assertions
    mock_factory.open.assert_called_with(path, **{})
    mock_nib.load.assert_called_with(mock_file_obj) # Should use file object

# --- 3. TEST EEG LOADER ---
@patch("src.core.eeg.mne")
def test_eeg_loader_local(mock_mne):
    """Test EEGLoader with local path optimization."""
    path = "C:/data/test.fif"
    
    mock_raw = MagicMock()
    mock_mne.io.read_raw_fif.return_value = mock_raw
    
    loader = EEGLoader(path)
    
    # Assertions
    mock_mne.io.read_raw_fif.assert_called_with(path, preload=False, verbose=False)

@patch("src.core.eeg.UniversalFactory")
@patch("src.core.eeg.mne")
def test_eeg_loader_s3(mock_mne, mock_factory):
    """Test EEGLoader with S3 path."""
    path = "s3://bucket/test.fif"
    
    mock_file_obj = MagicMock()
    mock_factory.open.return_value = mock_file_obj
    
    loader = EEGLoader(path)
    
    # Assertions
    mock_factory.open.assert_called_with(path, **{})
    mock_mne.io.read_raw_fif.assert_called_with(mock_file_obj, preload=False, verbose=False)

# --- 4. TEST ADAPTERS ---
@patch("src.adapters.local_loader.MRILoader")
def test_universal_mri_adapter(mock_loader_cls):
    """Test UniversalMRIAdapter integration."""
    mock_loader_instance = MagicMock()
    mock_loader_cls.return_value = mock_loader_instance
    mock_loader_instance.get_header_info.return_value = {'shape': (10,10,10)}
    
    adapter = UniversalMRIAdapter("test.nii")
    
    # Check setup
    mock_loader_cls.assert_called_with("test.nii", storage_options={})
    
    # Check metadata
    assert adapter.metadata == {'shape': (10,10,10)}
    
    # Check get_data
    assert adapter.get_data() == mock_loader_instance

@patch("src.adapters.local_loader.EEGLoader")
def test_universal_mne_adapter(mock_loader_cls):
    """Test UniversalMNEAdapter integration."""
    mock_loader_instance = MagicMock()
    mock_loader_cls.return_value = mock_loader_instance
    mock_loader_instance.raw = "RAW_OBJECT"
    
    adapter = UniversalMNEAdapter("test.fif")
    
    # Check setup
    mock_loader_cls.assert_called_with("test.fif", storage_options={})
    
    # Check get_data
    assert adapter.get_data() == mock_loader_instance
