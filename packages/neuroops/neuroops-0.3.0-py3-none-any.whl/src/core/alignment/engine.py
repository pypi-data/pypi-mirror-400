from typing import List, Tuple, Optional, Any, Dict
import numpy as np
from scipy import signal
from src.ports.base import NeuroSource
from src.core.reporting.models import SyncReport

class DriftModel:
    """
    Calculates and stores the linear clock drift between two timeframes.
    Model: t_real = t_measured * scale + offset
    """
    def __init__(self, anchors_a: List[float], anchors_b: List[float]):
        """
        anchors_a: Timestamps of events in Source A (the Reference)
        anchors_b: Timestamps of SAME events in Source B (the Drifting source)
        """
        if len(anchors_a) < 2 or len(anchors_b) < 2:
            # Not enough points for linear regression, assume identity
            self.drift_slope = 0.0 # slope offset from 1.0 (so 0.0 means 1.0)
            self.offset = 0.0
            self.confidence = 0.0
            return

        # Simple Linear Regression: B = A * m + c
        # We want to map A time to B time (to fetch correct B samples for an A timestamp)
        # B_t = m * A_t + c
        
        # Calculate slope (m) and intercept (c)
        m, c = np.polyfit(anchors_a, anchors_b, 1)
        
        self.scale_factor = m
        self.offset = c
        self.drift_slope = m - 1.0 # 0 if perfect
        self.confidence = 1.0 # Placeholder for residuals check

    def map_time(self, t_ref: float) -> float:
        """Converts Reference Time -> Target Time."""
        if self.confidence == 0.0: return t_ref
        return t_ref * self.scale_factor + self.offset

    def get_report(self) -> SyncReport:
        return SyncReport(
            drift_detected=abs(self.drift_slope) > 1e-5, # Threshold
            drift_slope=self.drift_slope,
            confidence=self.confidence
        )

class ResampledNeuroSource(NeuroSource):
    """
    Decorator / Wrapper for a NeuroSource.
    Intercepts get_signal() calls and applies Drift Correction on-the-fly.
    
    This allows the "Diff Engine" to ask for "0.0 to 10.0" and receive
    data that has been transparently stretched/shrunk to match the reference clock.
    """
    def __init__(self, wrapped_source: NeuroSource, drift_model: DriftModel):
        self.wrapped = wrapped_source
        self.drift = drift_model

    def get_meta(self) -> Dict[str, Any]:
        # Return original meta
        return self.wrapped.get_meta()

    @property
    def id(self) -> str:
        return f"Resampled({self.wrapped.id})"

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        # Pass through for MRI (Drift is usually time-series concept)
        return self.wrapped.get_slice(axis, index)

    def get_signal(self, start_time: float, end_time: float, channels: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Intercepts the request.
        1. Maps 'start_time' (Reference Clock) to 't_start_B' (Drifted Clock).
        2. Fetches raw data from B using drifted times.
        3. Resamples B back to Reference Clock grid.
        """
        if self.drift.confidence == 0.0:
            return self.wrapped.get_signal(start_time, end_time, channels)

        # 1. Map requested time window to the Target's internal clock
        t_start_target = self.drift.map_time(start_time)
        t_end_target = self.drift.map_time(end_time)
        
        # 2. Fetch Raw Data (in target's time frame)
        # We need to fetch enough samples to cover the resampled output
        data_raw, times_raw = self.wrapped.get_signal(t_start_target, t_end_target, channels)
        
        # 3. Resample
        # Target Output: We want data on the Reference Grid
        # Reference Grid: from start_time to end_time, at sfreq
        sfreq = self.get_meta()['sfreq']
        target_duration = end_time - start_time
        num_samples_target = int(target_duration * sfreq)
        
        if num_samples_target <= 0 or data_raw.size == 0:
             return data_raw, times_raw

        # Scipy Resample
        # Resample data_raw to num_samples_target
        data_resampled = signal.resample(data_raw, num_samples_target, axis=-1)
        
        # Reconstruct Time Vector (Perfect Grid)
        times_resampled = np.linspace(start_time, end_time, num_samples_target, endpoint=False)
        
        return data_resampled, times_resampled

    def get_raw_trace(self, start_time: float, end_time: float, channels: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ghost Trace Feature.
        Returns the raw data for the Requested Time Window WITHOUT drift correction.
        Used to visually compare "Corrected" vs "Original" to spot alignment errors.
        """
        # Fetch directly from wrapped source using original clock
        return self.wrapped.get_signal(start_time, end_time, channels)

