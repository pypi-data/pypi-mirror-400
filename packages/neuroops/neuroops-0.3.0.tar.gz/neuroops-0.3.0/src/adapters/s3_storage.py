from typing import Any, Dict, Optional, List, Tuple
import numpy as np
import nibabel as nib
from src.ports.base import NeuroSource
import s3fs
import os

class S3MRIAdapter(NeuroSource):
    """
    Adapter for Lazy Loading MRI files from AWS S3.
    Uses s3fs + nibabel to stream only required chunks.
    """
    
    def __init__(self, s3_uri: str, aws_profile: Optional[str] = None):
        self.uri = s3_uri
        self._fs = s3fs.S3FileSystem(anon=False) if not aws_profile else s3fs.S3FileSystem(profile=aws_profile)
        
        # Open file-like object using s3fs
        # This acts as a remote seekable stream
        try:
             self._file_obj = self._fs.open(s3_uri, 'rb')
             
             # Nibabel requires a FileHolder or filename.
             # We use the magical 'FileHolder' with our S3 stream.
             img_file = nib.FileHolder(fileobj=self._file_obj)
             self._img = nib.Nifti1Image.from_file_map({'header': img_file, 'image': img_file})
             
             # Basic cache
             self._data_obj = self._img.dataobj
             self._header = self._img.header
             
        except Exception as e:
            raise IOError(f"Failed to access S3 object {s3_uri}: {e}")

    @property
    def id(self) -> str:
        return self.uri

    def get_meta(self) -> Dict[str, Any]:
        shape = self._header.get_data_shape()
        affine = self._header.get_best_affine()
        return {
            "type": "MRI",
            "shape": shape,
            "affine": affine,
            "dims": len(shape),
            "duration": 0.0 # Time dimension handled elsewhere if 4D
        }

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        """
        Lazy Fetching!
        Nibabel allows slicing the 'proxy' array (self._data_obj).
        It translates this slice into specific 'seek' and 'read' operations on the S3 stream.
        This downloads ONLY the bytes for this slice (plus some block overhead), not the whole GB.
        """
        
        # 3D Slicing logic
        # dataobj supports slicing like numpy
        if axis == 0:
            return np.asanyarray(self._data_obj[index, :, :])
        elif axis == 1:
            return np.asanyarray(self._data_obj[:, index, :])
        elif axis == 2:
            return np.asanyarray(self._data_obj[:, :, index])
        else:
            raise ValueError("Axis must be 0, 1, or 2")

    def get_signal(self, *args, **kwargs):
        raise NotImplementedError("S3MRIAdapter does not support EEG signals yet.")
