import os
import numpy as np
import nibabel as nib
import mne
from typing import Any, Dict, Optional, Tuple, List
from ..ports.base import NeuroSource

# Use a fast channel mapping for normalization
CHANNEL_MAP = {
    'ECG': 'ECG', 'EKG': 'ECG',
    'FP1': 'Fp1', 'FP2': 'Fp2',
    'FZ': 'Fz', 'CZ': 'Cz', 'PZ': 'Pz', 'OZ': 'Oz'
}

class LocalMRIAdapter(NeuroSource):
    """
    Adapter for Local NIfTI files. 
    Uses nibabel for lazy loading (mmap).
    """
    def __init__(self, path: str):
        self.path = path
        self._img = None
        self._setup()

    def _setup(self):
        try:
             # mmap=True is default for filenames, but explicit is good
            self._img = nib.load(self.path)
        except Exception as e:
            raise ValueError(f"Failed to load MRI: {e}")

    @property
    def id(self) -> str:
        return os.path.basename(self.path)

    def get_meta(self) -> Dict[str, Any]:
        return {
            'shape': list(self._img.shape),
            'affine': self._img.affine.tolist(),
            'zooms': [float(z) for z in self._img.header.get_zooms()],
            'type': 'MRI'
        }

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        """Lazy slice fetch."""
        # axis: 0=Sagittal, 1=Coronal, 2=Axial
        slicer = [slice(None)] * len(self._img.shape)
        slicer[axis] = index
        
        # Handle 4D (Time) - Fix to t=0
        if len(self._img.shape) > 3:
             slicer[3] = 0

        # Dataobj access prevents full load
        data = self._img.dataobj[tuple(slicer)]
        
        # Standardize orientation if needed (rot90 usually needed for display)
        return np.rot90(np.asanyarray(data))


class LocalEEGAdapter(NeuroSource):
    """
    Adapter for Local EEG files (FIF, EDF, Modern MAT).
    Uses MNE for lazy loading.
    """
    def __init__(self, path: str):
        self.path = path
        self.raw = None
        self._setup()

    def _setup(self):
        # MNE read_raw_* functions are lazy by default if preload=False
        ext = os.path.splitext(self.path)[1].lower()
        try:
            if ext == '.fif':
                self.raw = mne.io.read_raw_fif(self.path, preload=False, verbose=False)
            elif ext == '.edf':
                self.raw = mne.io.read_raw_edf(self.path, preload=False, verbose=False)
            elif ext == '.mat':
                # TODO: Implement HDF5/Lazy MAT reader here.
                # For now using previous logic but wrapped.
                # In real prod, use h5py if v7.3+ or explicit mat73 lib.
                # Falling back to generic MNE for now as placeholder for "Modern Reader"
                # If it's old mat, it will load to memory. 
                # This needs the specific wrapper we saw in the old code if we want to support it fully.
                # Refactoring note: We'll assume standard formats for simplicity or reuse the old logic if critical.
                # Let's use a fail-safe:
                raise NotImplementedError("MAT files need the legacy loader logic. Use non-MAT for this refactor demo.")
            else:
                 # Try generic
                 self.raw = mne.io.read_raw(self.path, preload=False, verbose=False)
        except Exception as e:
            raise ValueError(f"Failed to load EEG: {e}")

        # --- Fix 3: Normalize Channels ---
        self._normalize_channels()

    def _normalize_channels(self):
        """Standardize channel names (fuzzy matching)."""
        rename_map = {}
        for ch in self.raw.ch_names:
            upper_ch = ch.upper()
            if upper_ch in CHANNEL_MAP:
                if ch != CHANNEL_MAP[upper_ch]:
                    rename_map[ch] = CHANNEL_MAP[upper_ch]
            elif upper_ch != ch:
                # Naively Uppercase everything else to catch fp1 vs FP1
                # But be careful with valid mixed case. 
                # Let's stick to the explicit map for safety first.
                pass
        
        if rename_map:
            print(f"DEBUG: Renaming channels: {rename_map}")
            self.raw.rename_channels(rename_map)

    @property
    def id(self) -> str:
        return os.path.basename(self.path)

    def get_meta(self) -> Dict[str, Any]:
        return {
            'sfreq': self.raw.info['sfreq'],
            'ch_names': self.raw.ch_names,
            'duration': self.raw.times[-1],
            'type': 'EEG'
        }

    def get_signal(self, start_time: float, end_time: float, channels: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches signal chunk lazily. 
        """
        # Convert time to samples
        sfreq = self.raw.info['sfreq']
        start_samp = int(start_time * sfreq)
        stop_samp = int(end_time * sfreq)

        # Handle Channels
        if channels:
             # MNE pick_channels is destructive on raw, use picks in get_data
             # We need to find indices.
             # Filter channels that exist
             valid_ch = [c for c in channels if c in self.raw.ch_names]
             if not valid_ch:
                 # Fallback: All channels (or error?)
                 # Returning zeros might be safer than crashing
                 return np.zeros((1, stop_samp - start_samp)), np.linspace(start_time, end_time, stop_samp - start_samp)
        else:
            valid_ch = None # All

        data, times = self.raw.get_data(
            picks=valid_ch, 
            start=start_samp, 
            stop=stop_samp, 
            return_times=True
        )
        return data, times
