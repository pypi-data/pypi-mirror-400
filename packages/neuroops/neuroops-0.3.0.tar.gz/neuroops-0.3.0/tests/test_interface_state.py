import pytest
from unittest.mock import patch, MagicMock
import sys

class SessionStateMock(dict):
    """Mock Streamlit SessionState allowing dot notation access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key, value):
        self[key] = value

# Mock streamlit before importing state
mock_st = MagicMock()
mock_st.session_state = SessionStateMock()
sys.modules["streamlit"] = mock_st

from src.interface import state

@pytest.fixture
def clean_session():
    mock_st.session_state.clear()
    # Initialize default keys expected by state
    state.init_session_state()
    return mock_st.session_state

def test_load_data_mock_mode_s3(clean_session):
    """
    Verify that load_data swaps S3 paths for local demo files when mock_mode is True.
    """
    # Inputs
    s3_path_a = "s3://bucket/raw.nii.gz"
    s3_path_b = "s3://bucket/clean.nii.gz"
    mock_creds = {"key": "value"}
    
    with patch("src.interface.state._get_adapter") as mock_get_adapter, \
         patch("src.interface.state.cleanup_previous_session") as mock_cleanup:
        
        # Call load_data with mock_mode=True
        state.load_data(
            s3_path_a, 
            s3_path_b, 
            source_type="s3", 
            mock_mode=True, 
            aws_creds=mock_creds
        )
        
        # Verify _get_adapter was called with LOCAL DEMO PATHS, not S3 paths
        # And storage_options should be empty dict
        assert mock_get_adapter.call_count == 2
        
        # Check first call (Adapter A)
        args_a, kwargs_a = mock_get_adapter.call_args_list[0]
        path_a_arg = args_a[0]
        
        # Should be a local path ending in demo_raw.nii.gz
        assert "demo_raw.nii.gz" in path_a_arg
        assert "s3://" not in path_a_arg
        
        # Check storage_options passed to _get_adapter
        # It's the 3rd positional arg in the new signature: _get_adapter(source, source_type, storage_options)
        assert args_a[2] == {} # Should be empty for mock mode

def test_load_data_real_s3(clean_session):
    """
    Verify that load_data passes real S3 paths and creds when mock_mode is False.
    """
    s3_path_a = "s3://bucket/raw.nii.gz"
    s3_path_b = "s3://bucket/clean.nii.gz"
    real_creds = {"aws_access_key_id": "real"}
    
    with patch("src.interface.state._get_adapter") as mock_get_adapter, \
         patch("src.interface.state.cleanup_previous_session") as mock_cleanup:
        
        # Call load_data with mock_mode=False
        state.load_data(
            s3_path_a, 
            s3_path_b, 
            source_type="s3", 
            mock_mode=False, 
            aws_creds=real_creds
        )
        
        # Verify _get_adapter was called with ORIGINAL S3 PATHS
        args_a, kwargs_a = mock_get_adapter.call_args_list[0]
        assert args_a[0] == s3_path_a
        
        # Verify creds passed
        assert args_a[2] == real_creds
