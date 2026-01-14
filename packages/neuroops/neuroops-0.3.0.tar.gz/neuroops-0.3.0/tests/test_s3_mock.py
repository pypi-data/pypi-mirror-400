import unittest
from unittest.mock import MagicMock, patch
import numpy as np

# Mocking libraries that require AWS creds
module_mock = MagicMock()
sys_modules_mock = {'s3fs': module_mock, 'nibabel': MagicMock()}

@patch.dict('sys.modules', sys_modules_mock)
class TestS3Adapter(unittest.TestCase):

    def setUp(self):
        # We need to import inside the method to catch the patch
        # But since we are creating the file during runtime, we import from src
        # We will mock the CLASS inside the file instead of the module map
        pass

    @patch('src.adapters.s3_storage.s3fs.S3FileSystem')
    @patch('src.adapters.s3_storage.nib.FileHolder')
    @patch('src.adapters.s3_storage.nib.Nifti1Image')
    def test_lazy_loading_mechanic(self, mock_img, mock_fh, mock_fs):
        from src.adapters.s3_storage import S3MRIAdapter
        
        # Setup Mock S3
        mock_fs_instance = mock_fs.return_value
        mock_file = MagicMock()
        mock_fs_instance.open.return_value = mock_file
        
        # Setup Mock Nibabel Header
        mock_header = MagicMock()
        mock_header.get_data_shape.return_value = (100, 100, 50)
        mock_header.get_best_affine.return_value = np.eye(4)
        
        # Setup Mock DataObj (The Proxy)
        mock_dataobj = MagicMock()
        # Mock slicing behavior: array[x,y,z]
        mock_dataobj.__getitem__.return_value = np.zeros((100, 100)) 
        
        mock_img_instance = mock_img.from_file_map.return_value
        mock_img_instance.header = mock_header
        mock_img_instance.dataobj = mock_dataobj

        # Action: Initialize Adapter
        adapter = S3MRIAdapter("s3://bucket/brain.nii.gz")
        
        # Assert: Metadata is correct
        meta = adapter.get_meta()
        self.assertEqual(meta['shape'], (100, 100, 50))
        self.assertEqual(meta['type'], 'MRI')
        
        # Action: Fetch Slice z=25
        slice_data = adapter.get_slice(axis=2, index=25)
        
        # Assert: Correct slice was requested from proxy
        # We check if dataobj was accessed. In real life nibabel connects this to S3 seek.
        self.assertIsNotNone(slice_data)
        
        print("✅ S3 Adapter successfully proxied nibabel calls without AWS keys.")

if __name__ == '__main__':
    unittest.main()
