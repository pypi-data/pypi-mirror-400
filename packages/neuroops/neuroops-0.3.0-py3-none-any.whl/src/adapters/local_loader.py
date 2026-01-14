import os
import tempfile
import mne
import scipy.io as sio
import nibabel as nib
import numpy as np
from src.ports.base import NeuroDataSource
from src.core.mri import MRILoader
from src.core.eeg import EEGLoader

# --- HELPER: TEMP FILE MANAGER ---
def save_temp_file(uploaded_file):
    """
    Saves an uploaded Streamlit file to a temp path on disk.
    Handles the double extension issue (.nii.gz).
    """
    if uploaded_file is None:
        raise ValueError("No file uploaded")
        
    file_name = uploaded_file.name
    # Handle .nii.gz explicitly
    if file_name.endswith('.nii.gz'):
        extension = '.nii.gz'
    else:
        extension = os.path.splitext(file_name)[1].lower()

    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    uploaded_file.seek(0) # Reset pointer
    tfile.write(uploaded_file.read())
    tfile.close()
    return tfile.name, extension

class UniversalMNEAdapter(NeuroDataSource):
    """
    Universal Adapter for EEG/MEG Data.
    Uses src.core.eeg.EEGLoader to handle both Local and S3 files via fsspec.
    """
    
    def _setup(self):
        # Check if input is a string (path/URI) or file object (uploader)
        if isinstance(self.file_obj, str):
            self.path = self.file_obj
            self.is_temp = False
            self.ext = os.path.splitext(self.path)[1].lower()
        else:
            self.path, self.ext = save_temp_file(self.file_obj)
            self.is_temp = True
            
        self.loader = None
        
        try:
            self._load_file()
        except Exception as e:
            self.cleanup() # Ensure cleanup on failure
            raise e

    def _load_file(self):
        # Use the new Core EEGLoader
        # Note: EEGLoader currently supports .fif, .edf, and .mat via fsspec
        if self.ext in ['.fif', '.edf', '.mat']:
            self.loader = EEGLoader(self.path, storage_options=self.storage_options)
        else:
            raise ValueError(f"Unsupported EEG extension: {self.ext}")

    @property
    def metadata(self):
        return self.loader.get_metadata()

    def get_data(self):
        """Returns the MNE Raw object (or EEGLoader wrapper)"""
        return self.loader

    def cleanup(self):
        if getattr(self, 'is_temp', False) and os.path.exists(self.path):
            os.unlink(self.path)


class UniversalMRIAdapter(NeuroDataSource):
    """
    Universal Adapter for MRI/NIfTI Data.
    Uses src.core.mri.MRILoader to handle both Local and S3 files via fsspec.
    """

    def _setup(self):
        if isinstance(self.file_obj, str):
            self.path = self.file_obj
            self.is_temp = False
        else:
            self.path, self.ext = save_temp_file(self.file_obj)
            self.is_temp = True
            
        self.loader = None
        
        try:
            self._load_file()
        except Exception as e:
            self.cleanup()
            raise e

    def _load_file(self):
        # Use the new Core MRILoader
        self.loader = MRILoader(self.path, storage_options=self.storage_options)

    @property
    def metadata(self):
        return self.loader.get_header_info()

    def get_data(self):
        """
        Returns the MRILoader instance.
        The UI calls .get_slice() on this object.
        """
        return self.loader

    def cleanup(self):
        if getattr(self, 'is_temp', False) and os.path.exists(self.path):
            os.unlink(self.path)