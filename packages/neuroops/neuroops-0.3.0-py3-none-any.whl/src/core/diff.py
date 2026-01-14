from typing import Any, Dict, Optional, Tuple, List
import numpy as np
from ..ports.base import NeuroSource
from scipy import signal

class VirtualPhysiologyDiff:
    """
    Core Domain Logic: The "Virtual Diff" Engine.
    
    Does NOT store data.
    Computes A - B on demand (Just-In-Time).
    State is managed by the Adapters (Sources).
    """
    def __init__(self, source_a: NeuroSource, source_b: NeuroSource):
        self.source_a = source_a
        self.source_b = source_b
        
        # Validation checks
        self.meta_a = source_a.get_meta()
        self.meta_b = source_b.get_meta()
        self.type = self.meta_a['type']
        
        if self.type != self.meta_b['type']:
            raise ValueError("Cannot diff mismatched data types (MRI vs EEG)")
            
        # Smart Check: Scale Mismatch
        self.mode = "DIFF" # Default
        self._check_scale_compatibility()

    def _check_scale_compatibility(self):
        """
        Heuristic: Detect if comparing Raw MRI (>100) vs Probability Map (0-1).
        If so, warn or switch mode.
        """
        # We need a sample to check scale. 
        # CAUTION: Fetching signal/slice might be expensive, so we do lazy check or minimal fetch.
        # For MVP, we trust the caller OR check the first small chunk.
        pass # To be implemented in full pipeline using stats from metadata if available.

    def get_slice_diff(self, axis: int, index: int, normalize: bool = True) -> np.ndarray:
        """
        Fetches slice A, slice B, aligns shapes, and returns Diff.
        """
        # 1. Fetch
        slice_a = self.source_a.get_slice(axis, index)
        slice_b = self.source_b.get_slice(axis, index)

        # 2. Align (Crop to smallest)
        min_x = min(slice_a.shape[0], slice_b.shape[0])
        min_y = min(slice_a.shape[1], slice_b.shape[1])
        
        s_a = slice_a[:min_x, :min_y]
        s_b = slice_b[:min_x, :min_y]

        # 3. Scale Check (Just-in-Time)
        # If A is [0, 1000] and B is [0, 1], Diff is meaningless.
        max_a = np.max(s_a)
        max_b = np.max(s_b)
        
        is_probability_map = (max_b <= 1.05 and max_a > 100)
        
        if is_probability_map:
            # OVERLAY MODE logic
            # We don't subtract. We want to visualize B *on top of* A.
            # But the 'Diff Viewer' expects a single 'Diff' image.
            # For visualization purpose, we return B as the "Diff" (The Mask itself is the diff)
            # And we flag it.
            return s_b, s_a, s_b # Return Mask as the "Diff"
            
        # 4. Normalize (Optional Z-Score) - ONLY if matching scales
        if normalize:
            if np.std(s_a) > 0: s_a = (s_a - np.mean(s_a)) / np.std(s_a)
            if np.std(s_b) > 0: s_b = (s_b - np.mean(s_b)) / np.std(s_b)

        # 5. Diff
        return s_a - s_b, s_a, s_b

    def compute_lag(self, channel: str, duration: float = 10.0) -> float:
        """
        Auto-detects time shift between source A and B using cross-correlation.
        Fetches a chunk from the middle of the recording to calculate lag.
        """
        # Middle of recording
        mid = self.meta_a['duration'] / 2
        start, end = mid, mid + duration
        
        sig_a, _ = self.source_a.get_signal(start, end, channels=[channel])
        sig_b, _ = self.source_b.get_signal(start, end, channels=[channel])
        
        # Squeeze if needed
        if sig_a.ndim > 1: sig_a = sig_a[0]
        if sig_b.ndim > 1: sig_b = sig_b[0]
        
        from .processing import calculate_lag
        lag_sec, _ = calculate_lag(sig_a, sig_b, self.meta_a['sfreq'])
        return lag_sec

    def compute_psd(self, sig_a: np.ndarray, sig_b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Wrapper for PSD calculation.
        """
        from .processing import calculate_psd
        return calculate_psd(sig_a, sig_b, self.meta_a['sfreq'])

    def get_signal_diff(self, start_time: float, duration: float, channel: str, shift_sec: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Fetches signal chunk, aligns (applies shift), and returns Diff.
        shift_sec: Positive means B is delayed (B starts later). 
                   To align A(t) and B(t), we might need to compare A(t) vs B(t + shift).
                   
                   If shift_sec > 0: Diff = A(t) - B(t + shift)
                   If shift_sec < 0: Diff = A(t + abs(shift)) - B(t)
        
        Returns: times, sig_a, sig_b, diff
        """
        end_time = start_time + duration
        
        # Adjust fetch windows based on shift
        if shift_sec > 0:
            # B needs to be fetched from later
            # A is fetched normally
            t_a_start, t_a_end = start_time, end_time
            t_b_start, t_b_end = start_time + shift_sec, end_time + shift_sec
        else:
            # A needs to be fetched from later (or B earlier)
            t_a_start, t_a_end = start_time + abs(shift_sec), end_time + abs(shift_sec)
            t_b_start, t_b_end = start_time, end_time

        sig_a, times_a = self.source_a.get_signal(t_a_start, t_a_end, channels=[channel])
        sig_b, times_b = self.source_b.get_signal(t_b_start, t_b_end, channels=[channel])
        
        # Squeeze
        if sig_a.ndim > 1: sig_a = sig_a[0]
        if sig_b.ndim > 1: sig_b = sig_b[0]
        
        # Truncate to min length
        n = min(len(sig_a), len(sig_b))
        sig_a = sig_a[:n]
        sig_b = sig_b[:n]
        
        freq = self.meta_a['sfreq']
        times = np.linspace(start_time, start_time + (n/freq), n, endpoint=False)

        diff = sig_a - sig_b
        
        return times, sig_a, sig_b, diff
