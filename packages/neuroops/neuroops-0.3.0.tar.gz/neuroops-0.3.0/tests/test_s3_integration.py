import sys
from unittest.mock import MagicMock
import pytest
import numpy as np

# Mock s3fs
mock_s3fs = MagicMock()
sys.modules['s3fs'] = mock_s3fs

# Mock nibabel
mock_nib = MagicMock()
sys.modules['nibabel'] = mock_nib

from src.adapters.s3 import S3MRIAdapter

def test_s3_adapter_initialization():
    """Test that S3MRIAdapter initializes mock s3fs and nibabel correctly"""
    uri = "s3://bucket/data.nii.gz"
    
    # Setup Mocks
    mock_fs_instance = MagicMock()
    mock_s3fs.S3FileSystem.return_value = mock_fs_instance
    mock_file = MagicMock()
    mock_fs_instance.open.return_value = mock_file
    
    # Mock Image
    mock_img = MagicMock()
    mock_img.shape = (100, 100, 100)
    mock_img.affine = np.eye(4)
    # Mock Header
    mock_header = MagicMock()
    mock_header.get_zooms.return_value = (1.0, 1.0, 1.0)
    mock_img.header = mock_header
    
    # Mock Load
    mock_nib.Nifti1Image.from_file_map.return_value = mock_img
    
    # Run
    adapter = S3MRIAdapter(uri)
    
    # Verify
    mock_s3fs.S3FileSystem.assert_called()
    mock_fs_instance.open.assert_called_with(uri, 'rb')
    mock_nib.Nifti1Image.from_file_map.assert_called()
    
    assert adapter.get_meta()['type'] == 'MRI'
    
def test_s3_adapter_lazy_slice():
    """Test that get_slice accesses dataobj with slicing"""
    uri = "s3://bucket/data.nii.gz"
    adapter = S3MRIAdapter(uri)
    
    # Mock Data Object on the image
    mock_dataobj = MagicMock()
    adapter._img.dataobj = mock_dataobj
    mock_dataobj.__getitem__.return_value = np.zeros((10, 100)) # Return 2D slice
    
    # Action
    data = adapter.get_slice(axis=0, index=50)
    
    # Verify Slicing
    # Slicer should be [50, slice(None), slice(None)]
    args = mock_dataobj.__getitem__.call_args[0][0]
    assert args[0] == 50
    assert isinstance(args[1], slice)
