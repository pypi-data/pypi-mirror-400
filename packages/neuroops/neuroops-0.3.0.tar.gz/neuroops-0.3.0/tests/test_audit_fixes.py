import pytest
import numpy as np
import os
import tempfile
import pickle
import json
from unittest.mock import MagicMock, patch

from src.adapters.db import LocalDBAdapter
from src.core.processing import calculate_slice_diff, calculate_lag
from src.core.mri import MRILoader
from src.core.eeg import EEGLoader

# --- ZONE 4: STORAGE (SQL) ---
def test_sql_persistence():
    """Test that LocalDBAdapter writes to SQLite DB."""
    # Use a test DB file
    db_path = "test_neuroops.db"
    if os.path.exists(db_path):
        os.unlink(db_path)
        
    adapter = LocalDBAdapter(db_path=db_path)
    file_id = "test_file_id_sub_01"
    
    try:
        adapter.add_comment(file_id, "Test Comment", {'slice': 50})
        
        # Verify file exists
        assert os.path.exists(db_path)
        
        # Verify read back
        comments = adapter.get_comments(file_id)
        assert len(comments) == 1
        assert comments[0]['comment'] == "Test Comment"
        assert comments[0]['context']['slice'] == 50
        
    finally:
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except:
                pass

# --- ZONE 3: SCIENCE (Z-SCORE) ---
def test_z_score_diff():
    """Test that slice difference is Z-scored."""
    # Create two arrays with different scales
    a = np.random.normal(loc=1000, scale=100, size=(10, 10)) # MRI Raw scale
    b = np.random.normal(loc=0.5, scale=0.1, size=(10, 10))   # MRI Processed scale
    
    # Without Z-score, diff would be huge (~1000)
    # With Z-score, both are ~N(0,1), so diff should be ~N(0, 2) i.e., range -5 to 5
    
    diff = calculate_slice_diff(a, b, normalize=True)
    
    assert np.max(np.abs(diff)) < 10.0 # Heuristic check
    assert np.mean(diff) < 1.0

# --- ZONE 2: LAG (PERFORMANCE) ---
def test_lag_resampling():
    """Test that high-frequency data is handled without crash."""
    sfreq = 1000 # 1kHz
    duration = 10 # 10 seconds
    t = np.linspace(0, duration, duration*sfreq)
    
    # Create signals with 0.5s lag
    sig = np.sin(2*np.pi*10*t)
    # Linear Shift 0.5s (500 samples)
    # B starts 0.5s later than A. So B[500] == A[0].
    # B[:500] is noise/zeros.
    sig_shifted = np.zeros_like(sig)
    sig_shifted[500:] = sig[:-500]
    
    # Calculate lag
    # This should trigger resampling because 1000Hz > 100Hz
    lag_sec, lag_idx = calculate_lag(sig, sig_shifted, sfreq)
    
    # Expected: ~0.5s lag (negative or positive depending on args)
    # calculate_lag(a, b): a matches b shifted by lag -> b = a(t-lag)
    # Here input is (sig, sig_shifted). sig_shifted is delayed.
    # So sig matches sig_shifted with lag.
    
    # Check absolute error is small (< 0.05s)
    # Note: Resampling reduces precision, so tolerance is needed.
    # Signal is periodic (10Hz), so lag could be 0.5, 0.6, etc.
    # 0.5s is 5 periods of 0.1s. 
    # Actually sin(x) vs sin(x-phi).
    assert abs(abs(lag_sec) - 0.5) < 0.05

# --- ZONE 5: STATE (PICKLING) ---
@patch("src.core.mri.nib")
def test_mri_loader_pickling(mock_nib):
    """Test standard MRILoader pickling."""
    # Setup mock
    mock_img = MagicMock()
    mock_img.header.get_zooms.return_value = (1,1,1)
    mock_nib.load.return_value = mock_img
    
    loader = MRILoader("test.nii")
    
    # Pickle
    pickled = pickle.dumps(loader)
    
    # Unpickle
    # This should trigger __setstate__ which calls _setup() -> nib.load()
    unpickled_loader = pickle.loads(pickled)
    
    assert unpickled_loader.path == "test.nii"
    assert mock_nib.load.call_count == 2 # Once for init, once for restore

if __name__ == "__main__":
    try:
        print("Running test_sql_persistence...")
        test_sql_persistence()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("Running test_z_score_diff...")
        test_z_score_diff()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("Running test_lag_resampling...")
        test_lag_resampling()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("Running test_mri_loader_pickling...")
        test_mri_loader_pickling()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
