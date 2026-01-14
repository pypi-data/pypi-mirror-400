import mne
import numpy as np
import scipy.io as sio
from typing import Any, Dict, Tuple, Optional
from .io import UniversalFactory
import os

class EEGLoader:
    """
    Handles loading of EEG/MEG data (FIF, EDF, MAT) from a file-like object.
    Wraps MNE's reading functions to support fsspec file objects.
    """
    
    def __init__(self, path: str, storage_options: dict = None):
        self.path = path
        self.storage_options = storage_options or {}
        self.file_obj = None
        self.raw = None
        self.is_mat = False
        self.mat_info = None
        self.mat_data_shape = None
        self._setup()

    def _setup(self):
        """
        Initializes the MNE Raw object.
        Uses preload=False to avoid reading the full data.
        """
        ext = os.path.splitext(self.path)[1].lower()

        # Optimization: Use direct path for local files
        if not self.path.startswith("s3://") and "://" not in self.path:
             try:
                 if ext == '.fif':
                     self.raw = mne.io.read_raw_fif(self.path, preload=False, verbose=False)
                 elif ext == '.edf':
                     self.raw = mne.io.read_raw_edf(self.path, preload=False, verbose=False)
                 elif ext == '.mat':
                     self._setup_mat_lazy(self.path)
                 else:
                     raise ValueError(f"Unsupported EEG format: {ext}")
                 return
             except Exception as e:
                 raise ValueError(f"Failed to load local EEG from {self.path}: {e}")

        # Get file-like object for Remote
        self.file_obj = UniversalFactory.open(self.path, **self.storage_options)
        
        try:
            if ext == '.fif':
                self.raw = mne.io.read_raw_fif(self.file_obj, preload=False, verbose=False)
            elif ext == '.edf':
                self.raw = mne.io.read_raw_edf(self.file_obj, preload=False, verbose=False)
            elif ext == '.mat':
                # For remote MAT, we use the file object with whosmat if possible
                # Note: whosmat requires a file name or file-like object.
                self._setup_mat_lazy(self.file_obj)
            else:
                raise ValueError(f"Unsupported EEG format for streaming: {ext}")
                
        except Exception as e:
            raise ValueError(f"Failed to load EEG data from {self.path}: {e}")

    def _setup_mat_lazy(self, file_source):
        """
        Lazily inspects a .mat file to get dimensions without loading data.
        """
        self.is_mat = True
        
        # inspect variables
        try:
            # whosmat returns list of (name, shape, dtype)
            vars_info = sio.whosmat(file_source)
        except Exception as e:
            # Fallback for very old MAT files or other issues: load full
            # But we try to avoid this.
            raise ValueError(f"Could not read MAT header: {e}")

        # Find best variable (largest size)
        best_var = None
        max_size = 0
        
        for name, shape, dtype in vars_info:
            if name.startswith('__'): continue
            size = np.prod(shape)
            if size > max_size:
                max_size = size
                best_var = (name, shape)
        
        if not best_var:
            raise ValueError("No valid arrays found in .mat file")
            
        self.mat_var_name, self.mat_shape = best_var
        
        # Heuristic: MNE expects (n_channels, n_times). 
        # If shape is (10000, 64), it's likely (n_times, n_channels) -> Transpose needed.
        # We assume fewer channels than timepoints usually.
        if self.mat_shape[0] > self.mat_shape[1]:
            self.n_times = self.mat_shape[0]
            self.n_channels = self.mat_shape[1]
            self.mat_transpose = True
        else:
            self.n_channels = self.mat_shape[0]
            self.n_times = self.mat_shape[1]
            self.mat_transpose = False
            
        # Create Dummy Info
        ch_names = [f"Ch_{i}" for i in range(self.n_channels)]
        self.mat_info = mne.create_info(ch_names=ch_names, sfreq=1000, ch_types='eeg')

    @property
    def info(self) -> mne.Info:
        if self.is_mat:
            return self.mat_info
        return self.raw.info

    def get_data(self, start: float, stop: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches a time segment of data.
        """
        sfreq = self.info['sfreq']
        start_samp = int(start * sfreq)
        stop_samp = int(stop * sfreq)
        
        if self.is_mat:
            return self._get_data_mat(start_samp, stop_samp)
            
        return self.raw.get_data(start=start_samp, stop=stop_samp, return_times=True)

    def _get_data_mat(self, start_samp: int, stop_samp: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Loads MAT data on demand.
        Currently loads the specific variable fully because scipy.io.loadmat doesn't support partial reading easily.
        But this is still better than loading at startup.
        """
        # Load ONLY the variable we need
        # If file_obj is used, we might need to reset pointer if it was read before?
        # whosmat doesn't consume the stream usually if it just reads header, but let's be safe.
        if self.file_obj:
            self.file_obj.seek(0)
            source = self.file_obj
        else:
            source = self.path
            
        mat_dict = sio.loadmat(source, variable_names=[self.mat_var_name])
        data = mat_dict[self.mat_var_name]
        
        if self.mat_transpose:
            data = data.T
            
        # Slice
        # Handle out of bounds
        stop_samp = min(stop_samp, data.shape[1])
        data_slice = data[:, start_samp:stop_samp]
        
        times = np.arange(start_samp, stop_samp) / self.info['sfreq']
        
        return data_slice, times

    @property
    def ch_names(self):
        return self.info['ch_names']

    @property
    def times(self):
        if self.is_mat:
            return np.arange(self.n_times) / self.info['sfreq']
        return self.raw.times

    def __getitem__(self, item):
        """
        Mimic MNE Raw slicing: raw[picks, start:stop]
        Returns (data, times)
        """
        if not self.is_mat:
            return self.raw[item]

        # Parse item (picks, slice)
        if isinstance(item, tuple):
            if len(item) == 2:
                picks, time_slice = item
            else:
                # Handle other cases if needed, but usually it's (picks, slice)
                picks, time_slice = item[0], slice(None)
        else:
            picks = item
            time_slice = slice(None)
            
        # Handle picks (int or list of ints)
        if isinstance(picks, int):
            picks = [picks]
        elif isinstance(picks, slice):
            # Convert slice to list of indices
            picks = list(range(self.n_channels))[picks]
        
        # Handle time slice
        if isinstance(time_slice, slice):
            start = time_slice.start if time_slice.start is not None else 0
            stop = time_slice.stop if time_slice.stop is not None else self.n_times
            step = time_slice.step if time_slice.step is not None else 1
        elif isinstance(time_slice, int):
            start = time_slice
            stop = start + 1
            step = 1
        else:
            # Array of indices? Not supported for now
            start = 0
            stop = self.n_times
            step = 1

        # Fetch Data
        data, times = self._get_data_mat(start, stop)
        
        # Select Channels
        data = data[picks, :]
        
        # Apply Step
        if step != 1:
            data = data[:, ::step]
            times = times[::step]
            
        return data, times

    def get_metadata(self) -> Dict[str, Any]:
        if self.is_mat:
            return {
                'sfreq': self.mat_info['sfreq'],
                'ch_names': self.mat_info['ch_names'],
                'n_times': self.n_times,
                'duration': self.n_times / self.mat_info['sfreq']
            }
            
        return {
            'sfreq': self.info['sfreq'],
            'ch_names': self.info['ch_names'],
            'n_times': self.raw.n_times,
            'duration': self.raw.n_times / self.info['sfreq']
        }


