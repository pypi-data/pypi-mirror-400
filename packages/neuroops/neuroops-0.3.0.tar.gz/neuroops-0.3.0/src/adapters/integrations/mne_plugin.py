"""
MNE-Python Integration for NeuroOps

Seamless integration with MNE-Python for preprocessing comparison.
"""

import numpy as np
import tempfile
from pathlib import Path
from typing import Union, Optional, Tuple
import os
import sys

try:
    import mne
    MNE_AVAILABLE = True
except ImportError:
    MNE_AVAILABLE = False


def _check_mne():
    """Check if MNE is available."""
    if not MNE_AVAILABLE:
        raise ImportError(
            "MNE-Python is required for this functionality. "
            "Install with: pip install mne"
        )


def _mne_to_neuroops_format(
    raw: 'mne.io.BaseRaw',
    output_path: Optional[str] = None
) -> Tuple[str, dict]:
    """
    Convert MNE Raw object to NeuroOps-compatible format.
    
    Args:
        raw: MNE Raw object
        output_path: Optional path to save (uses temp file if None)
        
    Returns:
        (file_path, metadata)
    """
    _check_mne()
    
    # Create temp file if no path provided
    if output_path is None:
        tmpdir = Path(tempfile.gettempdir()) / 'neuroops_mne'
        tmpdir.mkdir(exist_ok=True)
        output_path = str(tmpdir / f'mne_raw_{id(raw)}.fif')
    
    # Save as FIF (MNE's native format)
    raw.save(output_path, overwrite=True, verbose=False)
    
    # Extract metadata
    metadata = {
        'ch_names': raw.ch_names,
        'sfreq': raw.info['sfreq'],
        'n_channels': len(raw.ch_names),
        'duration': raw.times[-1],
        'type': 'EEG'
    }
    
    return output_path, metadata


def compare_preprocessing(
    raw_a: 'mne.io.BaseRaw',
    raw_b: 'mne.io.BaseRaw',
    launch_viewer: bool = True
) -> Optional[dict]:
    """
    Compare two MNE Raw objects (e.g., before and after preprocessing).
    
    This is the main entry point for MNE users.
    
    Args:
        raw_a: Raw data (before preprocessing)
        raw_b: Processed data (after preprocessing)
        launch_viewer: If True, launch NeuroOps Streamlit viewer
        
    Returns:
        Dictionary with file paths if launch_viewer=False
        
    Example:
        >>> import mne
        >>> from neuroops.integrations import compare_preprocessing
        >>> 
        >>> raw = mne.io.read_raw_fif('sample_audvis_raw.fif')
        >>> raw_filtered = raw.copy().filter(1, 40)
        >>> 
        >>> compare_preprocessing(raw, raw_filtered)
        # Launches NeuroOps viewer
    """
    _check_mne()
    
    # Convert to NeuroOps format
    print("Converting MNE objects to NeuroOps format...")
    path_a, meta_a = _mne_to_neuroops_format(raw_a)
    path_b, meta_b = _mne_to_neuroops_format(raw_b)
    
    print(f"✅ Converted {meta_a['n_channels']} channels, {meta_a['duration']:.1f}s")
    
    if launch_viewer:
        # Launch NeuroOps viewer
        _launch_neuroops_viewer(path_a, path_b)
        return None
    else:
        return {
            'path_a': path_a,
            'path_b': path_b,
            'metadata_a': meta_a,
            'metadata_b': meta_b
        }


def compare_ica(
    raw: 'mne.io.BaseRaw',
    ica: 'mne.preprocessing.ICA',
    exclude: Optional[list] = None,
    launch_viewer: bool = True
) -> Optional[dict]:
    """
    Compare raw data before and after ICA component removal.
    
    Args:
        raw: Raw data
        ica: Fitted ICA object
        exclude: List of component indices to exclude (uses ica.exclude if None)
        launch_viewer: If True, launch NeuroOps viewer
        
    Returns:
        Dictionary with file paths if launch_viewer=False
        
    Example:
        >>> from neuroops.integrations import compare_ica
        >>> 
        >>> raw = mne.io.read_raw_fif('sample_audvis_raw.fif')
        >>> ica = mne.preprocessing.ICA(n_components=20)
        >>> ica.fit(raw)
        >>> ica.exclude = [0, 1]  # Exclude first two components
        >>> 
        >>> compare_ica(raw, ica)
        # Shows what ICA removed
    """
    _check_mne()
    
    if exclude is None:
        exclude = ica.exclude
    
    print(f"Comparing ICA removal of components: {exclude}")
    
    # Create copy with ICA applied
    raw_clean = raw.copy()
    ica.apply(raw_clean, exclude=exclude)
    
    return compare_preprocessing(raw, raw_clean, launch_viewer=launch_viewer)


def compare_filter(
    raw: 'mne.io.BaseRaw',
    l_freq: Optional[float] = None,
    h_freq: Optional[float] = None,
    launch_viewer: bool = True
) -> Optional[dict]:
    """
    Compare raw data before and after filtering.
    
    Args:
        raw: Raw data
        l_freq: Low cutoff frequency (highpass)
        h_freq: High cutoff frequency (lowpass)
        launch_viewer: If True, launch NeuroOps viewer
        
    Returns:
        Dictionary with file paths if launch_viewer=False
        
    Example:
        >>> from neuroops.integrations import compare_filter
        >>> 
        >>> raw = mne.io.read_raw_fif('sample_audvis_raw.fif')
        >>> compare_filter(raw, l_freq=1, h_freq=40)
        # Shows what the bandpass filter removed
    """
    _check_mne()
    
    print(f"Comparing filter: {l_freq}-{h_freq} Hz")
    
    # Create filtered copy
    raw_filtered = raw.copy().filter(l_freq, h_freq, verbose=False)
    
    return compare_preprocessing(raw, raw_filtered, launch_viewer=launch_viewer)


def _launch_neuroops_viewer(path_a: str, path_b: str):
    """
    Launch NeuroOps Streamlit viewer with the given files.
    
    Args:
        path_a: Path to raw file
        path_b: Path to processed file
    """
    import subprocess
    
    # Set environment variables for auto-loading
    os.environ['NEUROOPS_MNE_MODE'] = '1'
    os.environ['NEUROOPS_MNE_PATH_A'] = path_a
    os.environ['NEUROOPS_MNE_PATH_B'] = path_b
    
    # Find NeuroOps app.py
    try:
        # Try to import to find the path
        import src.interface.app as app_module
        app_path = Path(app_module.__file__)
    except ImportError:
        # Fallback: assume we're in the repo
        app_path = Path(__file__).parent.parent / 'interface' / 'app.py'
    
    if not app_path.exists():
        print(f"❌ Could not find NeuroOps app at {app_path}")
        print(f"Files saved to:")
        print(f"  Raw: {path_a}")
        print(f"  Processed: {path_b}")
        print(f"\nLaunch manually with: neuroops")
        return
    
    print(f"\n🚀 Launching NeuroOps viewer...")
    print(f"   Raw: {Path(path_a).name}")
    print(f"   Processed: {Path(path_b).name}\n")
    
    # Launch Streamlit
    cmd = [sys.executable, '-m', 'streamlit', 'run', str(app_path)]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 NeuroOps closed.")


# Convenience aliases
compare = compare_preprocessing  # Shorter alias
