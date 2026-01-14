"""
Module C: Validation Engine - Quality Checks (FR-07)
Soft-fail checks that trigger "Warning" state.

These checks detect quality issues that may be acceptable depending on
the protocol thresholds defined in the Schema.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from enum import Enum
from scipy import signal as sp_signal


class QualityStatus(Enum):
    """Status codes for quality checks."""
    PASS = "PASS"
    WARN = "WARN"     # Below threshold but may be acceptable
    FAIL = "FAIL"     # Below hard threshold
    SKIP = "SKIP"     # Check not applicable


class QualityResult:
    """Result of a quality check."""
    
    def __init__(
        self,
        check_name: str,
        status: QualityStatus,
        message: str,
        value: Optional[float] = None,
        threshold: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.check_name = check_name
        self.status = status
        self.message = message
        self.value = value
        self.threshold = threshold
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "details": self.details
        }
    
    @property
    def passed(self) -> bool:
        return self.status in (QualityStatus.PASS, QualityStatus.SKIP, QualityStatus.WARN)


class QualityChecker:
    """
    FR-07: Quality Checks (Soft Fail)
    
    Calculates statistical metrics including SNR, Framewise Displacement,
    and variance analysis to detect dead sensors.
    
    Why: These metrics identify data that may produce unreliable results
    without being fundamentally corrupted. Thresholds are study-specific.
    """
    
    def __init__(
        self,
        snr_threshold: float = 5.0,
        motion_threshold_mm: float = 2.0,
        flatline_std_threshold: float = 1e-15,
        flatline_ratio_threshold: float = 0.5
    ):
        """
        Args:
            snr_threshold: Minimum acceptable SNR (lower = warning)
            motion_threshold_mm: Max framewise displacement in mm
            flatline_std_threshold: Std below this = dead channel
            flatline_ratio_threshold: Max ratio of flat samples
        """
        self.snr_threshold = snr_threshold
        self.motion_threshold = motion_threshold_mm
        self.flatline_std = flatline_std_threshold
        self.flatline_ratio = flatline_ratio_threshold
    
    def calculate_snr(
        self,
        data: np.ndarray,
        noise_region: Optional[Tuple[int, int]] = None
    ) -> QualityResult:
        """
        Calculate Signal-to-Noise Ratio.
        
        SNR = mean(signal) / std(noise)
        
        For MRI: Uses background region as noise estimate
        For EEG: Uses high-frequency component as noise estimate
        
        Args:
            data: Signal data (1D or 3D for MRI)
            noise_region: Optional (start, end) indices for noise estimation
        """
        check_name = "snr"
        
        if data.size == 0:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                "Empty data, cannot calculate SNR"
            )
        
        # Flatten for uniform handling
        flat_data = data.flatten()
        
        # Estimate signal and noise
        if noise_region:
            noise = flat_data[noise_region[0]:noise_region[1]]
            signal = np.delete(flat_data, range(noise_region[0], noise_region[1]))
        else:
            # Heuristic: use lowest 10% of absolute values as noise
            sorted_abs = np.sort(np.abs(flat_data))
            noise_count = max(int(len(sorted_abs) * 0.1), 10)
            noise = flat_data[np.argsort(np.abs(flat_data))[:noise_count]]
            signal = flat_data
        
        # Calculate SNR
        signal_mean = np.abs(np.mean(signal))
        noise_std = np.std(noise)
        
        if noise_std < 1e-20:
            # Perfect signal (no noise) or constant
            snr = float('inf')
        else:
            snr = signal_mean / noise_std
        
        # Evaluate against threshold
        if snr >= self.snr_threshold:
            status = QualityStatus.PASS
            message = f"SNR acceptable: {snr:.2f}"
        elif snr >= self.snr_threshold * 0.5:
            status = QualityStatus.WARN
            message = f"SNR below threshold: {snr:.2f} < {self.snr_threshold}"
        else:
            status = QualityStatus.FAIL
            message = f"SNR critically low: {snr:.2f}"
        
        return QualityResult(
            check_name, status, message,
            value=float(snr) if not np.isinf(snr) else 999.0,
            threshold=self.snr_threshold,
            details={"signal_mean": float(signal_mean), "noise_std": float(noise_std)}
        )
    
    def detect_flatline_channels(
        self,
        data: np.ndarray,
        channel_names: Optional[List[str]] = None
    ) -> QualityResult:
        """
        Detect dead/flatlined channels via variance analysis.
        
        A channel is considered "dead" if:
        - std < flatline_std_threshold
        - OR ratio of constant samples > flatline_ratio_threshold
        
        Args:
            data: 2D array (channels x timepoints)
            channel_names: Optional list of channel names
        """
        check_name = "flatline_detection"
        
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        if data.ndim != 2:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                f"Expected 2D data, got {data.ndim}D"
            )
        
        n_channels, n_samples = data.shape
        bad_channels: List[Dict[str, Any]] = []
        
        for ch_idx in range(n_channels):
            ch_data = data[ch_idx]
            ch_name = channel_names[ch_idx] if channel_names else f"ch_{ch_idx}"
            
            # Check 1: Standard deviation
            ch_std = np.std(ch_data)
            
            # Check 2: Ratio of constant values
            # Count consecutive identical values
            diff = np.diff(ch_data)
            flat_samples = np.sum(np.abs(diff) < 1e-20)
            flat_ratio = flat_samples / max(len(diff), 1)
            
            is_bad = False
            reason = []
            
            if ch_std < self.flatline_std:
                is_bad = True
                reason.append(f"std={ch_std:.2e}")
            
            if flat_ratio > self.flatline_ratio:
                is_bad = True
                reason.append(f"flat_ratio={flat_ratio:.2%}")
            
            if is_bad:
                bad_channels.append({
                    "channel": ch_name,
                    "index": ch_idx,
                    "std": float(ch_std),
                    "flat_ratio": float(flat_ratio),
                    "reason": ", ".join(reason)
                })
        
        # Evaluate
        n_bad = len(bad_channels)
        bad_ratio = n_bad / max(n_channels, 1)
        
        if n_bad == 0:
            return QualityResult(
                check_name, QualityStatus.PASS,
                f"No flatlined channels detected ({n_channels} channels checked)"
            )
        elif bad_ratio < 0.1:
            return QualityResult(
                check_name, QualityStatus.WARN,
                f"{n_bad}/{n_channels} channels appear flatlined",
                value=float(n_bad),
                details={"bad_channels": bad_channels}
            )
        else:
            return QualityResult(
                check_name, QualityStatus.FAIL,
                f"Excessive flatlined channels: {n_bad}/{n_channels}",
                value=float(n_bad),
                details={"bad_channels": bad_channels}
            )
    
    def calculate_framewise_displacement(
        self,
        motion_params: np.ndarray,
        radius_mm: float = 50.0
    ) -> QualityResult:
        """
        Calculate Framewise Displacement for motion detection.
        
        FD = |Δx| + |Δy| + |Δz| + r*(|Δpitch| + |Δroll| + |Δyaw|)
        
        Args:
            motion_params: 2D array (timepoints x 6) with [x, y, z, pitch, roll, yaw]
            radius_mm: Head radius for rotation → translation conversion
        """
        check_name = "framewise_displacement"
        
        if motion_params.ndim != 2 or motion_params.shape[1] < 6:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                "Motion parameters not available or incorrect shape"
            )
        
        # Compute frame-to-frame differences
        diff = np.diff(motion_params, axis=0)
        
        # Translation components
        trans_fd = np.sum(np.abs(diff[:, :3]), axis=1)
        
        # Rotation components (convert to mm using head radius)
        rot_fd = radius_mm * np.sum(np.abs(diff[:, 3:6]), axis=1)
        
        # Total FD
        fd = trans_fd + rot_fd
        
        # Statistics
        mean_fd = float(np.mean(fd))
        max_fd = float(np.max(fd))
        n_spikes = int(np.sum(fd > self.motion_threshold))
        spike_ratio = n_spikes / max(len(fd), 1)
        
        # Evaluate
        if max_fd <= self.motion_threshold and spike_ratio < 0.05:
            status = QualityStatus.PASS
            message = f"Motion acceptable: max FD = {max_fd:.2f}mm"
        elif max_fd <= self.motion_threshold * 2 or spike_ratio < 0.20:
            status = QualityStatus.WARN
            message = f"Moderate motion: max FD = {max_fd:.2f}mm, {n_spikes} spikes"
        else:
            status = QualityStatus.FAIL
            message = f"Excessive motion: max FD = {max_fd:.2f}mm, {n_spikes} spikes"
        
        return QualityResult(
            check_name, status, message,
            value=max_fd,
            threshold=self.motion_threshold,
            details={
                "mean_fd_mm": mean_fd,
                "max_fd_mm": max_fd,
                "n_motion_spikes": n_spikes,
                "spike_ratio": float(spike_ratio),
                "fd_timeseries": fd.tolist() if len(fd) < 1000 else None
            }
        )
    
    def calculate_center_of_mass_drift(
        self,
        data_4d: np.ndarray
    ) -> QualityResult:
        """
        Calculate Center of Mass drift across 4D volumes.
        
        Useful for fMRI motion detection without motion parameters.
        
        Args:
            data_4d: 4D numpy array (x, y, z, time)
        """
        check_name = "com_drift"
        
        if data_4d.ndim != 4:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                f"Expected 4D data, got {data_4d.ndim}D"
            )
        
        n_volumes = data_4d.shape[3]
        if n_volumes < 2:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                "Need at least 2 volumes for drift calculation"
            )
        
        # Calculate center of mass for each volume
        coms = []
        for t in range(min(n_volumes, 100)):  # Limit for performance
            vol = data_4d[:, :, :, t]
            total_mass = np.sum(np.abs(vol))
            if total_mass > 0:
                x, y, z = np.meshgrid(
                    range(vol.shape[0]),
                    range(vol.shape[1]), 
                    range(vol.shape[2]),
                    indexing='ij'
                )
                com_x = np.sum(x * np.abs(vol)) / total_mass
                com_y = np.sum(y * np.abs(vol)) / total_mass
                com_z = np.sum(z * np.abs(vol)) / total_mass
                coms.append([com_x, com_y, com_z])
        
        if len(coms) < 2:
            return QualityResult(
                check_name, QualityStatus.SKIP,
                "Insufficient valid volumes for COM calculation"
            )
        
        coms = np.array(coms)
        
        # Calculate drift from first volume
        drift = np.sqrt(np.sum((coms - coms[0])**2, axis=1))
        max_drift = float(np.max(drift))
        mean_drift = float(np.mean(drift))
        
        # Evaluate (in voxels, assuming ~2mm voxels → 4mm threshold)
        voxel_threshold = self.motion_threshold / 2.0  # Approximate voxel size
        
        if max_drift <= voxel_threshold:
            status = QualityStatus.PASS
            message = f"COM drift acceptable: {max_drift:.2f} voxels"
        elif max_drift <= voxel_threshold * 2:
            status = QualityStatus.WARN
            message = f"Moderate COM drift: {max_drift:.2f} voxels"
        else:
            status = QualityStatus.FAIL
            message = f"Excessive COM drift: {max_drift:.2f} voxels"
        
        return QualityResult(
            check_name, status, message,
            value=max_drift,
            threshold=voxel_threshold,
            details={
                "mean_drift_voxels": mean_drift,
                "max_drift_voxels": max_drift
            }
        )
    
    def check_background_ghost(
        self, 
        data_3d: np.ndarray,
        corner_size: int = 10,
        ghost_threshold: float = 0.05
    ) -> QualityResult:
        """
        Detect Nyquist ghosting by measuring signal variance in image corners.
        
        Ghost artifacts cause elevated signal in background regions.
        
        Args:
            data_3d: 3D volume (single slice or volume)
            corner_size: Size of corner regions to sample
            ghost_threshold: Ratio of corner signal to center signal
        """
        check_name = "background_ghost"
        
        if data_3d.ndim < 2:
            return QualityResult(check_name, QualityStatus.SKIP, "Data not 2D/3D")
        
        # Sample corner regions (assumed background/air)
        if data_3d.ndim == 2:
            corners = [
                data_3d[:corner_size, :corner_size],
                data_3d[:corner_size, -corner_size:],
                data_3d[-corner_size:, :corner_size],
                data_3d[-corner_size:, -corner_size:]
            ]
            center = data_3d[corner_size:-corner_size, corner_size:-corner_size]
        else:
            mid_z = data_3d.shape[2] // 2
            slice_2d = data_3d[:, :, mid_z]
            corners = [
                slice_2d[:corner_size, :corner_size],
                slice_2d[:corner_size, -corner_size:],
                slice_2d[-corner_size:, :corner_size],
                slice_2d[-corner_size:, -corner_size:]
            ]
            center = slice_2d[corner_size:-corner_size, corner_size:-corner_size]
        
        corner_mean = np.mean([np.std(c) for c in corners])
        center_mean = np.mean(center) if center.size > 0 else 1.0
        
        ghost_ratio = corner_mean / (center_mean + 1e-10)
        
        if ghost_ratio > ghost_threshold:
            return QualityResult(
                check_name, QualityStatus.WARN,
                f"Possible ghost artifact: background signal {ghost_ratio:.3f} of center",
                value=ghost_ratio, threshold=ghost_threshold
            )
        
        return QualityResult(
            check_name, QualityStatus.PASS,
            f"Background clean (ratio: {ghost_ratio:.4f})",
            value=ghost_ratio, threshold=ghost_threshold
        )
    
    def check_signal_dropout(
        self,
        data_3d: np.ndarray,
        mask: np.ndarray = None,
        dropout_threshold: float = 0.15
    ) -> QualityResult:
        """
        Detect signal dropout (black holes from metal/susceptibility).
        
        Flags scans with abnormally high percentage of zero voxels inside brain.
        
        Args:
            data_3d: 3D volume
            mask: Optional brain mask (if None, uses simple threshold)
            dropout_threshold: Max acceptable zero voxel ratio
        """
        check_name = "signal_dropout"
        
        if data_3d.ndim < 3:
            return QualityResult(check_name, QualityStatus.SKIP, "Data not 3D")
        
        # Create simple brain mask if not provided
        if mask is None:
            # Use Otsu-like threshold (mean of non-zero values)
            nonzero = data_3d[data_3d > 0]
            if nonzero.size == 0:
                return QualityResult(
                    check_name, QualityStatus.FAIL,
                    "All voxels are zero", value=1.0, threshold=dropout_threshold
                )
            threshold = np.mean(nonzero) * 0.1
            mask = data_3d > threshold
        
        # Count zeros inside mask
        brain_voxels = data_3d[mask]
        zero_ratio = np.sum(brain_voxels == 0) / (brain_voxels.size + 1e-10)
        
        if zero_ratio > dropout_threshold:
            return QualityResult(
                check_name, QualityStatus.WARN,
                f"Signal dropout detected: {zero_ratio*100:.1f}% zeros in brain",
                value=zero_ratio, threshold=dropout_threshold
            )
        
        return QualityResult(
            check_name, QualityStatus.PASS,
            f"Signal intact ({zero_ratio*100:.1f}% zeros)",
            value=zero_ratio, threshold=dropout_threshold
        )


def run_quality_checks(
    data: np.ndarray,
    data_type: str = "unknown",
    channel_names: Optional[List[str]] = None,
    motion_params: Optional[np.ndarray] = None,
    thresholds: Optional[Dict[str, float]] = None
) -> Tuple[bool, List[QualityResult]]:
    """
    Convenience function to run appropriate quality checks based on data type.
    
    Args:
        data: Signal data
        data_type: "MRI", "EEG", or "unknown"
        channel_names: Channel names for EEG
        motion_params: Motion parameters for fMRI
        thresholds: Optional custom thresholds
    
    Returns:
        Tuple of (all_passed, list_of_results)
    """
    thresholds = thresholds or {}
    checker = QualityChecker(
        snr_threshold=thresholds.get('snr_min', 5.0),
        motion_threshold_mm=thresholds.get('motion_max_mm', 2.0),
        flatline_std_threshold=thresholds.get('flatline_std_threshold', 1e-15),
        flatline_ratio_threshold=thresholds.get('flatline_max_ratio', 0.5)
    )
    
    results = []
    
    # SNR for all types
    results.append(checker.calculate_snr(data))
    
    # Type-specific checks
    if data_type == "EEG":
        if data.ndim >= 2:
            results.append(checker.detect_flatline_channels(data, channel_names))
    
    elif data_type == "MRI":
        if data.ndim == 4:
            results.append(checker.calculate_center_of_mass_drift(data))
        if motion_params is not None:
            results.append(checker.calculate_framewise_displacement(motion_params))
    
    # Determine overall pass/fail
    all_passed = all(
        r.status in (QualityStatus.PASS, QualityStatus.SKIP) 
        for r in results
    )
    
    return all_passed, results
