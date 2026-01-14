import nibabel as nib
import numpy as np
from typing import Tuple, Any, Union, BinaryIO
from .io import UniversalFactory

class MRILoader:
    """
    Handles loading of MRI data (NIfTI) from a file-like object.
    Optimized for lazy loading using nibabel.
    """
    
    def __init__(self, path: str, storage_options: dict = None):
        self.path = path
        self.storage_options = storage_options or {}
        self.file_obj = None
        self.img = None
        self._setup()

    def _setup(self):
        """
        Initializes the file object and nibabel image.
        Does NOT load the full data array into memory.
        """
        # Optimization: For local files, pass the path string directly to nibabel.
        # This enables memory mapping (mmap), which is faster and uses less RAM than fsspec.
        # It also avoids issues where nibabel rejects fsspec's LocalFileOpener.
        if not self.path.startswith("s3://") and "://" not in self.path:
             try:
                self.img = nib.load(self.path)
                return
             except Exception as e:
                raise ValueError(f"Failed to load local NIfTI from {self.path}: {e}")

        # Get a file-like object from UniversalFactory for Remote Files
        self.file_obj = UniversalFactory.open(self.path, **self.storage_options)
        
        # Nibabel can load from a file-like object.
        # It reads the header immediately but keeps the data on disk/network (lazy).
        try:
            self.img = nib.load(self.file_obj)
        except Exception as e:
            raise ValueError(f"Failed to parse NIfTI header from {self.path}: {e}")

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.img.shape

    @property
    def affine(self) -> np.ndarray:
        return self.img.affine

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        """
        Fetches a specific 2D slice from the volume.
        Uses nibabel's array proxy to only read necessary bytes.
        """
        # nibabel's dataobj is the array proxy
        # We can slice it directly.
        
        # Construct the slicer
        slicer = [slice(None)] * len(self.shape)
        slicer[axis] = index
        
        # If 4D (fMRI), we might want to take the first timepoint or handle it.
        # For now, let's assume if it's 4D, we take the first volume if the axis is spatial.
        # Or we can just return the slice which might be 2D or 3D (if time is included).
        
        # Let's stick to the logic we had in processing.py:
        # If 4D, we fix the 4th dimension to 0 (first timepoint) for visualization
        if len(self.shape) == 4:
             slicer[3] = 0
             
        # Perform the read
        # This triggers the specific byte range request (or file seek)
        data_slice = self.img.dataobj[tuple(slicer)]
        
        # Ensure it's a numpy array (sometimes it returns a proxy if not cast)
        return np.asanyarray(data_slice)

    def get_header_info(self) -> dict:
        return {
            'shape': self.shape,
            'affine': self.affine,
            'zooms': self.img.header.get_zooms(),
            'unit': self.img.header.get_xyzt_units()
        }


