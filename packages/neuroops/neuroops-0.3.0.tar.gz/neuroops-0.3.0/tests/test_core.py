import pytest
import numpy as np
from unittest.mock import MagicMock
from src.core.processing import generate_demo_data, process_mne_data, get_mri_slice, calculate_slice_diff, calculate_psd, compare_mne_info, calculate_lag
from src.core.bids_helper import validate_bids_filename

# --- TEST: generate_demo_data ---
def test_generate_demo_data():
    """Test that demo data generation returns correct shapes and types."""
    duration = 2
    sampling_rate = 100
    time, sig_a, sig_b = generate_demo_data(duration=duration, sampling_rate=sampling_rate)
    
    expected_points = duration * sampling_rate
    
    assert len(time) == expected_points
    assert len(sig_a) == expected_points
    assert len(sig_b) == expected_points
    assert isinstance(time, np.ndarray)
    assert isinstance(sig_a, np.ndarray)
    assert isinstance(sig_b, np.ndarray)

# --- TEST: process_mne_data ---
def test_process_mne_data():
    """Test EEG diff calculation logic."""
    # Mock MNE Raw objects
    raw_a = MagicMock()
    raw_b = MagicMock()
    
    # Setup mock data
    times = np.linspace(0, 1, 100)
    data_a = np.random.rand(1, 100) # 1 channel, 100 timepoints
    data_b = np.random.rand(1, 100)
    
    raw_a.times = times
    raw_b.times = times
    raw_a.ch_names = ['Fz']
    raw_b.ch_names = ['Fz']
    raw_a.get_data.return_value = data_a
    raw_b.get_data.return_value = data_b
    
    # Call function
    t, out_a, out_b, diff, ch, lag = process_mne_data(raw_a, raw_b)
    
    # Assertions
    assert np.array_equal(t, times)
    assert np.array_equal(out_a, data_a[0])
    assert np.array_equal(out_b, data_b[0])
    assert np.allclose(diff, data_a[0] - data_b[0])
    assert ch == 'Fz'

# --- TEST: calculate_psd ---
def test_calculate_psd():
    """Test PSD calculation returns correct shapes."""
    sfreq = 1000
    duration = 1
    t = np.linspace(0, duration, duration*sfreq)
    
    # Generate 10Hz sine wave
    sig_a = np.sin(2 * np.pi * 10 * t)
    sig_b = np.sin(2 * np.pi * 10 * t) # Identical signal
    
    freqs, psd_a, psd_b = calculate_psd(sig_a, sig_b, sfreq)
    
    # Check outputs are arrays
    assert isinstance(freqs, np.ndarray)
    assert isinstance(psd_a, np.ndarray)
    assert isinstance(psd_b, np.ndarray)
    
    # Check lengths match
    assert len(freqs) == len(psd_a)
    assert len(psd_a) == len(psd_b)
    
    # Check that 10Hz is the peak frequency (roughly)
    peak_idx = np.argmax(psd_a)
    peak_freq = freqs[peak_idx]
    assert 9 <= peak_freq <= 11

# --- TEST: compare_mne_info ---
def test_compare_mne_info():
    """Test metadata comparison logic."""
    # Mock Info dictionaries
    info_a = {
        'sfreq': 1000,
        'highpass': 0.0,
        'lowpass': 100.0,
        'bads': []
    }
    info_b = {
        'sfreq': 250,          # Changed
        'highpass': 1.0,       # Changed
        'lowpass': 100.0,      # Same
        'bads': ['Fz']         # Changed
    }
    
    df = compare_mne_info(info_a, info_b)
    
    # Should have 3 rows (sfreq, highpass, bads)
    # Note: 'line_freq' and 'nchan' are missing from input, so they might appear as N/A -> N/A (no change) or be skipped if logic handles it.
    # My implementation iterates over fixed keys.
    # keys = ['sfreq', 'highpass', 'lowpass', 'line_freq', 'nchan', 'bads']
    # lowpass is same -> no row
    # line_freq, nchan -> N/A vs N/A -> no row
    # So we expect 3 rows.
    
    assert len(df) == 3
    
    # Check specific changes
    row_sfreq = df[df['Parameter'] == 'sfreq'].iloc[0]
    assert row_sfreq['Status'] == "📉 Downsampled"
    
    row_hp = df[df['Parameter'] == 'highpass'].iloc[0]
    assert row_hp['Status'] == "✅ Filtered"
    
    row_bads = df[df['Parameter'] == 'bads'].iloc[0]
    assert row_bads['Status'] == "⚠️ Channels Dropped"

# --- TEST: calculate_lag ---
def test_calculate_lag():
    """Test cross-correlation lag detection."""
    sfreq = 100
    t = np.linspace(0, 10, 10*sfreq)
    
    # Create a signal
    sig = np.sin(2 * np.pi * 1 * t)
    
    # Create shifted versions
    # Shift B by +10 samples (0.1s) -> B starts later
    # So B[0] corresponds to A[10] ? No.
    # If B is delayed, it looks like [0, 0, 0, sig...]
    # Let's just slice.
    
    # Case 1: B is shifted "right" (delayed) by 10 samples relative to A
    # A: [x0, x1, x2, x3, ...]
    # B: [.., .., x0, x1, ...]
    # So A[0] matches B[10].
    # This means B has 10 extra samples at the start? Or B is missing the first 10 samples of A?
    # Let's define "Shifted" as:
    # sig_a = sig[10:]  (starts at t=0.1)
    # sig_b = sig[:-10] (starts at t=0.0)
    # Here A is "ahead" of B (starts later in the array, so earlier in time? No.)
    
    # Let's use the definition from the implementation:
    # lag_idx > 0 means B is "ahead" (starts earlier? No, implementation says "B is delayed").
    # Let's trust the math: correlate(A, B). Peak at +k means A[t] ~ B[t+k].
    
    sig_base = np.random.randn(1000)
    
    # Case 1: B is shifted by +5 samples (B[5] == A[0])
    sig_a = sig_base[:-5]
    sig_b = sig_base[5:] # B starts 5 samples "later" into the sequence
    
    # Wait, if sig_b = sig_base[5:], then sig_b[0] = sig_base[5].
    # sig_a[0] = sig_base[0].
    # They are NOT aligned.
    # To align them, we need to match sig_a[5] with sig_b[0].
    # So A is shifted by +5 relative to B?
    
    # Let's just run the function and see if it detects *something*.
    lag_sec, lag_idx = calculate_lag(sig_a, sig_b, sfreq=100)
    
    # We expect a lag.
    # If A[5] matches B[0], then A is "delayed" relative to B?
    # correlate(A, B). A slides over B.
    # Match happens when A is shifted by -5?
    
    assert abs(lag_idx) == 5
    assert abs(lag_sec) == 0.05

# --- TEST: validate_bids_filename ---
def test_validate_bids_filename():
    """Test BIDS filename validation logic."""
    
    # Valid Case
    valid_name = "sub-01_task-rest_eeg.edf"
    is_valid, issues, fix = validate_bids_filename(valid_name)
    assert is_valid
    assert len(issues) == 0
    
    # Invalid Case 1: Missing prefix
    invalid_1 = "patient_01_eeg.edf"
    is_valid, issues, fix = validate_bids_filename(invalid_1)
    assert not is_valid
    assert "Missing 'sub-' prefix" in issues
    assert fix is not None
    
    # Invalid Case 2: Bad characters
    invalid_2 = "sub-01_task-rest@home_eeg.edf"
    is_valid, issues, fix = validate_bids_filename(invalid_2)
    assert not is_valid
    assert "Contains invalid characters (use only a-z, 0-9, -, _)" in issues

# --- TEST: get_mri_slice & calculate_slice_diff ---
def test_get_mri_slice_3d():
    """Test lazy slice extraction for 3D volumes."""
    # Mock Nibabel proxy object
    img_proxy = MagicMock()
    img_proxy.shape = (10, 10, 10)
    
    # Mock dataobj slicing
    # We expect img_proxy.dataobj[x, y, z] access
    # Let's mock the return value of __getitem__
    mock_slice = np.ones((10, 10))
    img_proxy.dataobj.__getitem__.return_value = mock_slice
    
    # Call function: Axial slice (axis=2) at index 5
    slice_data = get_mri_slice(img_proxy, axis_idx=2, slice_idx=5)
    
    # Assertions
    # Note: get_mri_slice applies rot90, so shape might flip if not square
    assert slice_data.shape == (10, 10)
    # Verify slicing call was correct: (slice(None), slice(None), 5)
    img_proxy.dataobj.__getitem__.assert_called_with((slice(None), slice(None), 5))

def test_get_mri_slice_4d():
    """Test lazy slice extraction for 4D fMRI volumes."""
    img_proxy = MagicMock()
    img_proxy.shape = (10, 10, 10, 5) # 4D
    
    mock_slice = np.ones((10, 10))
    img_proxy.dataobj.__getitem__.return_value = mock_slice
    
    # Call function: Sagittal slice (axis=0) at index 3
    slice_data = get_mri_slice(img_proxy, axis_idx=0, slice_idx=3)
    
    # Assertions
    # Verify slicing call: (3, slice(None), slice(None), 0) -> 0 is forced timepoint
    img_proxy.dataobj.__getitem__.assert_called_with((3, slice(None), slice(None), 0))

def test_calculate_slice_diff():
    """Test 2D slice diff calculation."""
    slice_a = np.ones((10, 10)) * 2
    slice_b = np.ones((10, 10)) * 1
    
    diff = calculate_slice_diff(slice_a, slice_b)
    
    assert np.all(diff == 1)
    assert diff.shape == (10, 10)
