import pytest
import numpy as np
from src.core.diff import VirtualPhysiologyDiff

# --- MOCKS ---
class MockAdapter:
    def __init__(self, data_type='EEG', sfreq=100, duration=10):
        self.meta = {
            'type': data_type,
            'sfreq': sfreq,
            'duration': duration,
            'ch_names': ['Ch1'],
            'shape': (100, 100, 10) # For MRI
        }
        self.sfreq = sfreq

    def get_meta(self):
        return self.meta

    def get_signal(self, start, end, channels=None):
        # Generate synthetic sine wave
        n = int((end - start) * self.sfreq)
        times = np.linspace(start, end, n, endpoint=False)
        sig = np.sin(2 * np.pi * 10 * times) # 10Hz sine
        return sig[np.newaxis, :], times

    def get_slice(self, axis, index):
        # Return random slice
        return np.ones((100, 100))

# --- TESTS ---

def test_init_validation():
    """Test that mismatched types raise error"""
    a = MockAdapter('EEG')
    b = MockAdapter('MRI')
    with pytest.raises(ValueError, match="mismatched"):
        VirtualPhysiologyDiff(a, b)

def test_signal_diff_no_shift():
    """Test basic diff subtraction"""
    a = MockAdapter('EEG')
    b = MockAdapter('EEG')
    diff_engine = VirtualPhysiologyDiff(a, b)
    
    times, sig_a, sig_b, diff = diff_engine.get_signal_diff(0, 1, 'Ch1')
    
    assert len(times) == 100
    assert np.allclose(diff, 0) # Should be identical sine waves

def test_signal_diff_with_shift():
    """Test that shift logic aligns signals"""
    # Logic: If shift > 0, we compare A(t) with B(t+shift)
    # Our Mock produces sin(10*t).
    # sin(10*t) == sin(10*(t+shift)) if 10*shift is integer
    
    a = MockAdapter('EEG')
    b = MockAdapter('EEG')
    diff_engine = VirtualPhysiologyDiff(a, b)
    
    # Check dimensions only for now, ensuring code path runs
    times, sig_a, sig_b, diff = diff_engine.get_signal_diff(0, 1, 'Ch1', shift_sec=0.1)
    
    assert len(times) == 100
    
def test_compute_lag():
    """Test lag computation wrapper"""
    a = MockAdapter('EEG')
    b = MockAdapter('EEG')
    diff_engine = VirtualPhysiologyDiff(a, b)
    
    lag = diff_engine.compute_lag('Ch1')
    assert isinstance(lag, float)

def test_mri_slice_diff():
    """Test MRI slicing and normalization"""
    a = MockAdapter('MRI')
    b = MockAdapter('MRI')
    diff_engine = VirtualPhysiologyDiff(a, b)
    
    diff, s_a, s_b = diff_engine.get_slice_diff(0, 50, normalize=False)
    assert diff.shape == (100, 100)
    assert np.allclose(diff, 0) # ones - ones
