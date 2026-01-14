import numpy as np
import pandas as pd
import nibabel as nib
from scipy import signal

# --- 1. DEMO DATA GENERATOR ---
def generate_demo_data(duration=10, sampling_rate=1000):
    """
    Generates synthetic EEG data for the 'Toy Version'.
    """
    time = np.linspace(0, duration, duration * sampling_rate)
    
    # Base Signal (Alpha Wave ~10Hz)
    brain_signal = np.sin(2 * np.pi * 10 * time)
    
    # Add an "Event" (e.g., a P300 spike at 5 seconds)
    event = np.exp(-0.5 * ((time - 5.0) / 0.1)**2) * 5
    brain_signal += event

    # Create Version A (Noisy/Raw) with 50Hz noise
    noise_50hz = 0.5 * np.sin(2 * np.pi * 50 * time)
    random_noise = np.random.normal(0, 0.3, len(time))
    
    signal_a = brain_signal + noise_50hz + random_noise
    
    # Create Version B (Cleaned)
    signal_b = brain_signal + (random_noise * 0.2)
    
    return time, signal_a, signal_b

def calculate_lag(data_a, data_b, sfreq, max_shift_sec=5.0):
    """
    Calculates the time lag between two signals using cross-correlation.
    Includes DOWN-SAMPLING to prevent performance hangs on high-frequency data.
    Returns: lag_seconds (float), shift_index (int)
    """
    # 1. Slice a representative chunk (Max 60 seconds)
    limit_sec = 60
    limit_samples = int(limit_sec * sfreq)
    n_points = min(len(data_a), len(data_b), limit_samples)
    
    a_chunk = data_a[:n_points].copy()
    b_chunk = data_b[:n_points].copy()
    
    # 2. Resample if sampling rate is high (> 100Hz)
    target_fs = 100.0
    if sfreq > target_fs:
        # Calculate new number of samples
        num_samples = int(len(a_chunk) * target_fs / sfreq)
        a_chunk = signal.resample(a_chunk, num_samples)
        b_chunk = signal.resample(b_chunk, num_samples)
        current_fs = target_fs
    else:
        current_fs = sfreq

    # 3. Normalize for correlation
    a_chunk = (a_chunk - np.mean(a_chunk))
    b_chunk = (b_chunk - np.mean(b_chunk))
    
    std_a = np.std(a_chunk)
    std_b = np.std(b_chunk)
    
    if std_a == 0 or std_b == 0:
        return 0.0, 0
        
    a_chunk /= std_a
    b_chunk /= std_b
    
    # 4. Correlate
    correlation = signal.correlate(a_chunk, b_chunk, mode='full')
    lags = signal.correlation_lags(len(a_chunk), len(b_chunk), mode='full')
    
    lag_idx_resampled = lags[np.argmax(correlation)]
    lag_sec = lag_idx_resampled / current_fs
    
    # Convert back to original indices
    lag_idx_original = int(round(lag_sec * sfreq))
    
    return lag_sec, lag_idx_original

# ... (Existing process_mne_data, calculate_psd, compare_mne_info, get_mri_slice functions are okay, omitting to save tokens if not modifying) ...

def process_mne_data(raw_a, raw_b):
    """
    Extracts data from two MNE Raw objects, aligns them, and calculates the diff.
    """
    # Time Vector
    time = raw_a.times
    sfreq = raw_a.info['sfreq']
    
    # We grab the FIRST channel just for the MVP visualization
    ch_name = raw_a.ch_names[0]
    
    data_a = raw_a.get_data()[0] 
    data_b = raw_b.get_data()[0] 
    
    # --- SMART ALIGNMENT (Cross-Correlation) ---
    lag_sec, lag_idx = calculate_lag(data_a, data_b, sfreq)
    
    # Apply Shift if significant (more than 1 sample)
    if abs(lag_idx) > 0:
        if lag_idx > 0:
            # B is "ahead" (starts earlier) -> A[t] matches B[t + lag]
            # We need to cut the start of B
            data_b = data_b[lag_idx:]
            data_a = data_a[:len(data_b)] # Match lengths
        else:
            # A is "ahead" -> A[t + lag] matches B[t] (lag is negative)
            # We need to cut the start of A
            shift = abs(lag_idx)
            data_a = data_a[shift:]
            data_b = data_b[:len(data_a)] # Match lengths
            
    # Crop to shortest length to prevent errors
    min_len = min(len(data_a), len(data_b))
    data_a = data_a[:min_len]
    data_b = data_b[:min_len]
    time = time[:min_len]
    
    diff = data_a - data_b
    
    return time, data_a, data_b, diff, ch_name, lag_sec

def calculate_psd(data_a, data_b, sfreq):
    """
    Calculates Power Spectral Density (PSD) using Welch's method.
    Returns: freqs, psd_a, psd_b
    """
    # Use 2-second windows for frequency resolution
    nperseg = int(2 * sfreq)
    if nperseg > len(data_a):
        nperseg = len(data_a) // 2
        
    freqs, psd_a = signal.welch(data_a, fs=sfreq, nperseg=nperseg)
    _, psd_b = signal.welch(data_b, fs=sfreq, nperseg=nperseg)
    
    return freqs, psd_a, psd_b

def compare_mne_info(info_a, info_b):
    """
    Compares two MNE Info objects and returns a DataFrame of differences.
    """
    # Define keys of interest for metadata comparison
    keys = ['sfreq', 'highpass', 'lowpass', 'line_freq', 'nchan', 'bads']
    
    diffs = []
    
    for k in keys:
        val_a = info_a.get(k, 'N/A')
        val_b = info_b.get(k, 'N/A')
        
        # Handle lists (like 'bads') specifically
        if isinstance(val_a, list):
            val_a = str(val_a)
        if isinstance(val_b, list):
            val_b = str(val_b)
            
        if val_a != val_b:
            # Determine status icon
            status = "⚠️ Changed"
            if k == 'sfreq' and val_b < val_a:
                status = "📉 Downsampled"
            elif k in ['highpass', 'lowpass'] and val_b != val_a:
                status = "✅ Filtered"
            elif k == 'bads' and len(val_b) > len(val_a):
                status = "⚠️ Channels Dropped"
                
            diffs.append({
                'Parameter': k,
                'Raw (A)': val_a,
                'Processed (B)': val_b,
                'Status': status
            })
            
    if not diffs:
        return pd.DataFrame(columns=['Parameter', 'Raw (A)', 'Processed (B)', 'Status'])
        
    return pd.DataFrame(diffs)

def get_mri_slice(img_proxy, axis_idx, slice_idx):
    """
    Lazily loads a single 2D slice from a Nibabel proxy object.
    axis_idx: 0 (Sagittal), 1 (Coronal), 2 (Axial)
    """
    # Handle 4D fMRI (Time dimension) - Take first timepoint
    # Slicing syntax: img.dataobj[x, y, z, t]
    
    # We need to construct a dynamic slice object
    # Equivalent to: vol[:, :, slice_idx] if axis=2
    
    ndim = len(img_proxy.shape)
    slicer = [slice(None)] * ndim
    slicer[axis_idx] = slice_idx
    
    if ndim == 4:
        slicer[3] = 0 # Force timepoint 0
        
    # Load ONLY the slice from disk
    slice_data = img_proxy.dataobj[tuple(slicer)]
    
    # Ensure it's a numpy array
    slice_data = np.asanyarray(slice_data)
    
    # Rotate for display if needed (standard convention)
    return np.rot90(slice_data)

def calculate_slice_diff(slice_a, slice_b, normalize=True):
    """
    Calculates diff between two 2D slices.
    Handles shape mismatch by cropping.
    Includes Z-Score Normalization to ensure comparable scales.
    """
    # 1. Z-Score Normalization
    if normalize:
        if np.std(slice_a) > 0:
            slice_a = (slice_a - np.mean(slice_a)) / np.std(slice_a)
        if np.std(slice_b) > 0:
            slice_b = (slice_b - np.mean(slice_b)) / np.std(slice_b)
    
    # 2. Crop if shapes mismatch
    if slice_a.shape != slice_b.shape:
        min_x = min(slice_a.shape[0], slice_b.shape[0])
        min_y = min(slice_a.shape[1], slice_b.shape[1])
        slice_a = slice_a[:min_x, :min_y]
        slice_b = slice_b[:min_x, :min_y]
        
    return slice_a - slice_b

def downsample_min_max(data, target_n=5000):
    """
    Downsamples data using Min-Max Envelope preservation.
    This prevents aliasing and ensures peaks are visible.
    Returns array of size 2*target_n (alternating min, max).
    """
    if len(data) <= 2 * target_n:
        return data
        
    n = len(data)
    # Bin size
    bin_size = n // target_n
    
    # Truncate to multiple of bin_size
    n_trunc = target_n * bin_size
    data_trunc = data[:n_trunc]
    
    # Reshape to (target_n, bin_size)
    reshaped = data_trunc.reshape(target_n, bin_size)
    
    # Calculate min and max for each bin
    mins = reshaped.min(axis=1)
    maxs = reshaped.max(axis=1)
    
    # Interleave min and max
    # Create empty array of size 2*target_n
    result = np.empty(2 * target_n, dtype=data.dtype)
    result[0::2] = mins
    result[1::2] = maxs
    
    return result