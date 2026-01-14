"""
Automated Artifact Detection for NeuroOps

Intelligent analysis of removed signals to classify artifacts and warn about
potential brain activity removal.
"""

import numpy as np
from scipy import signal as sp_signal
from scipy.fft import fft, fftfreq
from typing import Dict, Any, Tuple, Optional, List


class ArtifactDetector:
    """
    Analyzes the difference between raw and processed signals to detect
    and classify artifacts.
    """
    
    def __init__(self, sfreq: float):
        """
        Initialize artifact detector.
        
        Args:
            sfreq: Sampling frequency in Hz
        """
        self.sfreq = sfreq
        
        # Frequency band definitions
        self.bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 12),
            'beta': (13, 30),
            'gamma': (30, 100),
            'line_noise_50': (49, 51),
            'line_noise_60': (59, 61),
        }
    
    def analyze_removed_signal(
        self,
        diff_signal: np.ndarray,
        channel_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze removed signal and classify artifact type.
        
        Args:
            diff_signal: The difference (raw - processed)
            channel_name: Optional channel name for context
            
        Returns:
            Dictionary with status, message, confidence, and details
        """
        # Compute power spectral density
        freqs, psd = self._compute_psd(diff_signal)
        
        # Compute band powers
        band_powers = self._compute_band_powers(freqs, psd)
        
        # Detect artifact patterns
        detections = {
            'line_noise': self._detect_line_noise(band_powers),
            'alpha_power': self._detect_alpha_power(band_powers),
            'beta_power': self._detect_beta_power(band_powers),
            'eye_blink': self._detect_eye_blink(diff_signal, channel_name),
            'muscle': self._detect_muscle_artifact(band_powers),
            'broadband_noise': self._detect_broadband_noise(band_powers)
        }
        
        # Apply heuristic rules
        result = self._apply_heuristics(detections, band_powers, channel_name)
        
        return result
    
    def _compute_psd(self, signal_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute power spectral density using Welch's method."""
        freqs, psd = sp_signal.welch(
            signal_data,
            fs=self.sfreq,
            nperseg=min(len(signal_data), int(2 * self.sfreq)),
            scaling='density'
        )
        return freqs, psd
    
    def _compute_band_powers(
        self,
        freqs: np.ndarray,
        psd: np.ndarray
    ) -> Dict[str, float]:
        """Compute relative power in each frequency band."""
        total_power = np.sum(psd)
        
        if total_power == 0:
            return {band: 0.0 for band in self.bands}
        
        band_powers = {}
        for band_name, (low, high) in self.bands.items():
            idx = np.where((freqs >= low) & (freqs <= high))[0]
            if len(idx) > 0:
                band_power = np.sum(psd[idx])
                band_powers[band_name] = band_power / total_power
            else:
                band_powers[band_name] = 0.0
        
        return band_powers
    
    def _detect_line_noise(self, band_powers: Dict[str, float]) -> Dict[str, Any]:
        """Detect 50Hz or 60Hz line noise."""
        power_50 = band_powers.get('line_noise_50', 0)
        power_60 = band_powers.get('line_noise_60', 0)
        
        # Threshold: >20% of power in line noise band
        threshold = 0.20
        
        if power_60 > threshold:
            return {
                'detected': True,
                'frequency': 60,
                'power': power_60,
                'confidence': min(power_60 / threshold, 1.0)
            }
        elif power_50 > threshold:
            return {
                'detected': True,
                'frequency': 50,
                'power': power_50,
                'confidence': min(power_50 / threshold, 1.0)
            }
        else:
            return {'detected': False, 'power': max(power_50, power_60)}
    
    def _detect_alpha_power(self, band_powers: Dict[str, float]) -> Dict[str, Any]:
        """Detect alpha band power (potential brain activity)."""
        alpha_power = band_powers.get('alpha', 0)
        
        # Threshold: >15% of power in alpha band
        threshold = 0.15
        
        return {
            'detected': alpha_power > threshold,
            'power': alpha_power,
            'confidence': min(alpha_power / threshold, 1.0) if alpha_power > threshold else 0.0
        }
    
    def _detect_beta_power(self, band_powers: Dict[str, float]) -> Dict[str, Any]:
        """Detect beta band power (potential brain activity)."""
        beta_power = band_powers.get('beta', 0)
        
        # Threshold: >10% of power in beta band
        threshold = 0.10
        
        return {
            'detected': beta_power > threshold,
            'power': beta_power,
            'confidence': min(beta_power / threshold, 1.0) if beta_power > threshold else 0.0
        }
    
    def _detect_eye_blink(
        self,
        diff_signal: np.ndarray,
        channel_name: Optional[str]
    ) -> Dict[str, Any]:
        """Detect eye blink artifacts (frontal channels, slow deflections)."""
        # Check if frontal channel
        is_frontal = False
        if channel_name:
            frontal_channels = ['Fp1', 'Fp2', 'AF3', 'AF4', 'Fpz', 'AFz']
            is_frontal = any(ch in channel_name for ch in frontal_channels)
        
        if not is_frontal:
            return {'detected': False, 'is_frontal': False}
        
        # Look for large amplitude deflections
        amplitude = np.max(np.abs(diff_signal))
        mean_amplitude = np.mean(np.abs(diff_signal))
        
        # Threshold: peak > 5x mean amplitude
        threshold_ratio = 5.0
        
        if amplitude > threshold_ratio * mean_amplitude and amplitude > 50:  # 50 µV
            return {
                'detected': True,
                'is_frontal': True,
                'amplitude': amplitude,
                'confidence': min(amplitude / (threshold_ratio * mean_amplitude), 1.0)
            }
        
        return {'detected': False, 'is_frontal': True, 'amplitude': amplitude}
    
    def _detect_muscle_artifact(self, band_powers: Dict[str, float]) -> Dict[str, Any]:
        """Detect muscle artifacts (high-frequency bursts)."""
        gamma_power = band_powers.get('gamma', 0)
        
        # Threshold: >25% of power in gamma band
        threshold = 0.25
        
        return {
            'detected': gamma_power > threshold,
            'power': gamma_power,
            'confidence': min(gamma_power / threshold, 1.0) if gamma_power > threshold else 0.0
        }
    
    def _detect_broadband_noise(self, band_powers: Dict[str, float]) -> Dict[str, Any]:
        """Detect broadband noise (uniform across frequencies)."""
        # Calculate variance of band powers
        powers = [
            band_powers.get('delta', 0),
            band_powers.get('theta', 0),
            band_powers.get('alpha', 0),
            band_powers.get('beta', 0),
            band_powers.get('gamma', 0)
        ]
        
        variance = np.var(powers)
        
        # Low variance = uniform distribution = broadband noise
        threshold = 0.005
        
        return {
            'detected': variance < threshold,
            'variance': variance,
            'confidence': 1.0 - min(variance / threshold, 1.0) if variance < threshold else 0.0
        }
    
    def _apply_heuristics(
        self,
        detections: Dict[str, Dict[str, Any]],
        band_powers: Dict[str, float],
        channel_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Apply heuristic rules to classify the removed signal.
        
        Priority order:
        1. Line noise (60Hz/50Hz) → OK
        2. Eye blink (frontal channels) → OK
        3. Muscle artifact → OK
        4. Alpha/Beta power → WARNING
        5. Broadband noise → INFO
        """
        
        # Rule 1: Line noise
        if detections['line_noise']['detected']:
            freq = detections['line_noise']['frequency']
            power = detections['line_noise']['power']
            conf = detections['line_noise']['confidence']
            
            return {
                'status': 'OK',
                'message': f'✅ Line noise removed ({freq}Hz peak detected)',
                'confidence': conf,
                'artifact_type': 'line_noise',
                'details': {
                    'frequency': freq,
                    'power': power,
                    'band_powers': band_powers
                }
            }
        
        # Rule 2: Eye blink
        if detections['eye_blink']['detected']:
            amp = detections['eye_blink']['amplitude']
            conf = detections['eye_blink']['confidence']
            
            return {
                'status': 'OK',
                'message': f'✅ Eye blink artifact removed (frontal channel, {amp:.1f}µV)',
                'confidence': conf,
                'artifact_type': 'eye_blink',
                'details': {
                    'amplitude': amp,
                    'channel': channel_name,
                    'band_powers': band_powers
                }
            }
        
        # Rule 3: Muscle artifact
        if detections['muscle']['detected']:
            power = detections['muscle']['power']
            conf = detections['muscle']['confidence']
            
            return {
                'status': 'OK',
                'message': f'✅ Muscle artifact removed (high-frequency burst)',
                'confidence': conf,
                'artifact_type': 'muscle',
                'details': {
                    'gamma_power': power,
                    'band_powers': band_powers
                }
            }
        
        # Rule 4: Alpha power (WARNING)
        if detections['alpha_power']['detected']:
            power = detections['alpha_power']['power']
            conf = detections['alpha_power']['confidence']
            
            return {
                'status': 'WARNING',
                'message': f'⚠️ Removed signal contains alpha power ({power*100:.1f}%) - possible brain activity',
                'confidence': conf,
                'artifact_type': 'possible_brain_activity',
                'details': {
                    'alpha_power': power,
                    'band_powers': band_powers
                }
            }
        
        # Rule 5: Beta power (WARNING)
        if detections['beta_power']['detected']:
            power = detections['beta_power']['power']
            conf = detections['beta_power']['confidence']
            
            return {
                'status': 'WARNING',
                'message': f'⚠️ Removed signal contains beta power ({power*100:.1f}%) - possible brain activity',
                'confidence': conf,
                'artifact_type': 'possible_brain_activity',
                'details': {
                    'beta_power': power,
                    'band_powers': band_powers
                }
            }
        
        # Rule 6: Broadband noise
        if detections['broadband_noise']['detected']:
            conf = detections['broadband_noise']['confidence']
            
            return {
                'status': 'INFO',
                'message': 'ℹ️ Broadband noise removed',
                'confidence': conf,
                'artifact_type': 'broadband_noise',
                'details': {
                    'variance': detections['broadband_noise']['variance'],
                    'band_powers': band_powers
                }
            }
        
        # Default: Unknown
        return {
            'status': 'INFO',
            'message': 'ℹ️ Signal modification detected',
            'confidence': 0.5,
            'artifact_type': 'unknown',
            'details': {
                'band_powers': band_powers
            }
        }


def analyze_diff(
    diff_signal: np.ndarray,
    sfreq: float,
    channel_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze a difference signal.
    
    Args:
        diff_signal: The difference between raw and processed
        sfreq: Sampling frequency
        channel_name: Optional channel name
        
    Returns:
        Analysis result dictionary
    """
    detector = ArtifactDetector(sfreq)
    return detector.analyze_removed_signal(diff_signal, channel_name)
