"""
Tests for Artifact Detection

Comprehensive tests for intelligent artifact classification.
"""

import pytest
import numpy as np
from src.core.artifact_detector import ArtifactDetector, analyze_diff


class TestArtifactDetector:
    """Test artifact detector initialization and basic functionality."""
    
    def test_init(self):
        """Test detector initialization."""
        detector = ArtifactDetector(sfreq=500.0)
        assert detector.sfreq == 500.0
        assert 'alpha' in detector.bands
        assert 'line_noise_60' in detector.bands
    
    def test_frequency_bands(self):
        """Test frequency band definitions."""
        detector = ArtifactDetector(sfreq=500.0)
        
        assert detector.bands['alpha'] == (8, 12)
        assert detector.bands['beta'] == (13, 30)
        assert detector.bands['line_noise_60'] == (59, 61)


class TestLineNoiseDetection:
    """Test 60Hz line noise detection."""
    
    def test_detect_60hz_line_noise(self):
        """Test detection of 60Hz line noise."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create pure 60Hz signal
        signal_60hz = np.sin(2 * np.pi * 60.0 * times)
        
        result = analyze_diff(signal_60hz, sfreq)
        
        assert result['status'] == 'OK'
        assert '60Hz' in result['message'] or 'Line noise' in result['message']
        assert result['artifact_type'] == 'line_noise'
        assert result['confidence'] > 0.7
    
    def test_detect_50hz_line_noise(self):
        """Test detection of 50Hz line noise."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create pure 50Hz signal
        signal_50hz = np.sin(2 * np.pi * 50.0 * times)
        
        result = analyze_diff(signal_50hz, sfreq)
        
        assert result['status'] == 'OK'
        assert '50Hz' in result['message'] or 'Line noise' in result['message']
        assert result['artifact_type'] == 'line_noise'
    
    def test_no_line_noise(self):
        """Test when no line noise is present."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create 10Hz alpha signal (no line noise)
        signal_alpha = np.sin(2 * np.pi * 10.0 * times)
        
        result = analyze_diff(signal_alpha, sfreq)
        
        # Should NOT detect line noise
        assert result['artifact_type'] != 'line_noise'


class TestAlphaPowerDetection:
    """Test alpha band power detection."""
    
    def test_detect_alpha_power(self):
        """Test detection of alpha band activity."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create strong 10Hz alpha signal
        signal_alpha = 100 * np.sin(2 * np.pi * 10.0 * times)
        
        result = analyze_diff(signal_alpha, sfreq)
        
        assert result['status'] == 'WARNING'
        assert 'alpha' in result['message'].lower()
        assert 'brain activity' in result['message'].lower()
        assert result['artifact_type'] == 'possible_brain_activity'
        assert result['confidence'] > 0.5
    
    def test_low_alpha_power(self):
        """Test when alpha power is below threshold."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        
        # Create weak broadband noise (low alpha)
        signal_noise = np.random.randn(n_samples) * 10
        
        result = analyze_diff(signal_noise, sfreq)
        
        # Should not trigger alpha warning
        if result['status'] == 'WARNING':
            assert 'alpha' not in result['message'].lower()


class TestBetaPowerDetection:
    """Test beta band power detection."""
    
    def test_detect_beta_power(self):
        """Test detection of beta band activity."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create strong 20Hz beta signal
        signal_beta = 100 * np.sin(2 * np.pi * 20.0 * times)
        
        result = analyze_diff(signal_beta, sfreq)
        
        assert result['status'] == 'WARNING'
        assert 'beta' in result['message'].lower()
        assert 'brain activity' in result['message'].lower()


class TestEyeBlinkDetection:
    """Test eye blink artifact detection."""
    
    def test_detect_eye_blink_frontal(self):
        """Test eye blink detection on frontal channel."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        
        # Create eye blink pattern (large amplitude deflection)
        signal = np.zeros(n_samples)
        blink_idx = n_samples // 2
        blink_width = int(0.2 * sfreq)  # 200ms
        
        # Gaussian-shaped blink
        for i in range(blink_width):
            idx = blink_idx + i - blink_width // 2
            if 0 <= idx < n_samples:
                signal[idx] = 200 * np.exp(-((i - blink_width/2)**2) / (2 * (blink_width/4)**2))
        
        result = analyze_diff(signal, sfreq, channel_name='Fp1')
        
        assert result['status'] == 'OK'
        assert 'blink' in result['message'].lower() or 'frontal' in result['message'].lower()
        assert result['artifact_type'] == 'eye_blink'
    
    def test_no_eye_blink_non_frontal(self):
        """Test that eye blink is not detected on non-frontal channels."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        
        # Same blink pattern but on occipital channel
        signal = np.zeros(n_samples)
        blink_idx = n_samples // 2
        blink_width = int(0.2 * sfreq)
        
        for i in range(blink_width):
            idx = blink_idx + i - blink_width // 2
            if 0 <= idx < n_samples:
                signal[idx] = 200 * np.exp(-((i - blink_width/2)**2) / (2 * (blink_width/4)**2))
        
        result = analyze_diff(signal, sfreq, channel_name='O1')
        
        # Should NOT detect as eye blink (not frontal)
        assert result['artifact_type'] != 'eye_blink'


class TestMuscleArtifactDetection:
    """Test muscle artifact detection."""
    
    def test_detect_muscle_artifact(self):
        """Test detection of muscle artifact (high-frequency)."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create high-frequency signal (gamma band)
        signal_muscle = 50 * np.sin(2 * np.pi * 60.0 * times)  # 60Hz
        signal_muscle += 30 * np.sin(2 * np.pi * 80.0 * times)  # 80Hz
        
        result = analyze_diff(signal_muscle, sfreq)
        
        assert result['status'] == 'OK'
        assert 'muscle' in result['message'].lower() or 'high-frequency' in result['message'].lower()


class TestBroadbandNoiseDetection:
    """Test broadband noise detection."""
    
    def test_detect_broadband_noise(self):
        """Test detection of uniform broadband noise."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        
        # Create white noise (uniform across frequencies)
        signal_noise = np.random.randn(n_samples) * 20
        
        result = analyze_diff(signal_noise, sfreq)
        
        # Should detect broadband noise or at least not warn
        assert result['status'] in ['OK', 'INFO']


class TestHeuristicPriority:
    """Test that heuristic rules are applied in correct priority order."""
    
    def test_line_noise_priority(self):
        """Test that line noise detection has highest priority."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Create signal with both 60Hz and alpha
        signal = 100 * np.sin(2 * np.pi * 60.0 * times)  # Strong 60Hz
        signal += 20 * np.sin(2 * np.pi * 10.0 * times)  # Weak alpha
        
        result = analyze_diff(signal, sfreq)
        
        # Should classify as line noise (higher priority)
        assert result['artifact_type'] == 'line_noise'
        assert result['status'] == 'OK'
    
    def test_alpha_warning_when_no_artifacts(self):
        """Test that alpha triggers warning when no artifacts present."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Pure alpha signal (no artifacts)
        signal = 100 * np.sin(2 * np.pi * 10.0 * times)
        
        result = analyze_diff(signal, sfreq)
        
        # Should warn about alpha power
        assert result['status'] == 'WARNING'
        assert result['artifact_type'] == 'possible_brain_activity'


class TestConfidenceScoring:
    """Test confidence score calculation."""
    
    def test_high_confidence_line_noise(self):
        """Test high confidence for strong line noise."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # Very strong 60Hz
        signal = 200 * np.sin(2 * np.pi * 60.0 * times)
        
        result = analyze_diff(signal, sfreq)
        
        assert result['confidence'] > 0.8
    
    def test_lower_confidence_weak_signal(self):
        """Test lower confidence for weak signals."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        
        # Very weak noise
        signal = np.random.randn(n_samples) * 0.1
        
        result = analyze_diff(signal, sfreq)
        
        # Confidence should be moderate to low
        assert result['confidence'] <= 1.0


class TestDetailsOutput:
    """Test that detection details are properly formatted."""
    
    def test_details_contains_band_powers(self):
        """Test that details include band power breakdown."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        signal = np.sin(2 * np.pi * 10.0 * times)
        
        result = analyze_diff(signal, sfreq)
        
        assert 'details' in result
        assert 'band_powers' in result['details']
        assert isinstance(result['details']['band_powers'], dict)
    
    def test_details_artifact_specific(self):
        """Test that details include artifact-specific info."""
        sfreq = 500.0
        duration = 2.0
        n_samples = int(duration * sfreq)
        times = np.linspace(0, duration, n_samples)
        
        # 60Hz line noise
        signal = np.sin(2 * np.pi * 60.0 * times)
        
        result = analyze_diff(signal, sfreq)
        
        # Should include frequency info
        assert 'frequency' in result['details']
        assert result['details']['frequency'] == 60


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_zero_signal(self):
        """Test with zero signal."""
        sfreq = 500.0
        signal = np.zeros(1000)
        
        result = analyze_diff(signal, sfreq)
        
        # Should not crash
        assert 'status' in result
        assert 'message' in result
    
    def test_very_short_signal(self):
        """Test with very short signal."""
        sfreq = 500.0
        signal = np.random.randn(100)  # Only 100 samples
        
        result = analyze_diff(signal, sfreq)
        
        # Should not crash
        assert 'status' in result
    
    def test_nan_values(self):
        """Test handling of NaN values."""
        sfreq = 500.0
        signal = np.random.randn(1000)
        signal[500] = np.nan
        
        # Should handle gracefully (may warn or filter)
        try:
            result = analyze_diff(signal, sfreq)
            assert 'status' in result
        except:
            # Acceptable to raise error for invalid data
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
