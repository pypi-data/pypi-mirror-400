import os
import numpy as np
import nibabel as nib
from typing import Any, Dict, Optional, Tuple, List
from ..ports.base import NeuroSource

# Try to import remote filesystem libs (Mocking support for non-cloud envs)
try:
    import s3fs
    HAS_S3 = True
except ImportError:
    HAS_S3 = False

class S3MRIAdapter(NeuroSource):
    """
    Adapter for S3-hosted NIfTI files.
    Uses s3fs + nibabel to allow lazy slicing over the network (HTTP Range Requests).
    """
    def __init__(self, s3_uri: str, anon: bool = True):
        if not HAS_S3:
            raise ImportError("s3fs is required for S3 support. pip install s3fs")
            
        self.uri = s3_uri
        self.fs = s3fs.S3FileSystem(anon=anon) 
        self._img = None
        self._setup()

    def _setup(self):
        try:
            # nibabel can load from a file-like object
            # s3fs provides a Python file interface that supports seek/read (Range Requests)
            self._file_obj = self.fs.open(self.uri, 'rb')
            
            # nibabel uses the file object. 
            # It reads the header immediately (first 348 bytes + extension).
            # It creates an ArrayProxy for the data.
            self._img = nib.Nifti1Image.from_file_map(
                nib.FileHolder(fileobj=self._file_obj)
            )
        except Exception as e:
            raise ValueError(f"Failed to stream MRI from S3: {e}")

    def __del__(self):
        """Cleanup file handle"""
        if hasattr(self, '_file_obj'):
            self._file_obj.close()

    @property
    def id(self) -> str:
        return self.uri

    def get_meta(self) -> Dict[str, Any]:
        return {
            'shape': list(self._img.shape),
            'affine': self._img.affine.tolist(),
            'zooms': [float(z) for z in self._img.header.get_zooms()],
            'type': 'MRI'
        }

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        """
        Lazy slice fetch over Network.
        Nibabel's ArrayProxy calculates the offset and requests only the specific bytes.
        """
        slicer = [slice(None)] * len(self._img.shape)
        slicer[axis] = index
        
        # Handle 4D (Time) - Fix to t=0
        if len(self._img.shape) > 3:
             slicer[3] = 0

        # This triggers the HTTP Range Request via s3fs
        data = self._img.dataobj[tuple(slicer)]
        
        return np.rot90(np.asanyarray(data))

# Placeholder for EEG S3 (Harder due to various proprietary binary formats)
# MNE supports minimal S3. We might need specific readers.
# For Phase 3, we focus on MRI as proof of concept for "Lazy Loading".
