import os
import numpy as np
import nibabel as nib
import mne

def generate_golden_mri(directory):
    """Generates a synthetic MRI with a known 'hole' artifact."""
    affine = np.eye(4)
    # 64x64x64 volume
    data = np.ones((64, 64, 64), dtype=np.float32) * 100
    
    # Create a "Hole" in the center (The Artifact)
    center = 32
    radius = 10
    x, y, z = np.ogrid[:64, :64, :64]
    mask = (x - center)**2 + (y - center)**2 + (z - center)**2 <= radius**2
    data[mask] = 0  # Lesion/Artifact
    
    img = nib.Nifti1Image(data, affine)
    
    # Save Raw and "Clean" (Clean has no hole for diff)
    path_raw = os.path.join(directory, "golden_mri_raw.nii.gz")
    path_clean = os.path.join(directory, "golden_mri_clean.nii.gz")
    
    nib.save(img, path_raw)
    
    # "Healed" version
    data_clean = data.copy()
    data_clean[mask] = 100 
    img_clean = nib.Nifti1Image(data_clean, affine)
    nib.save(img_clean, path_clean)
    
    return path_raw, path_clean

def generate_golden_eeg(directory):
    """Generates synthetic EEG with a spike artifact."""
    sfreq = 100
    times = np.linspace(0, 10, 10 * sfreq)
    n_channels = 5
    
    # Base Signal: 10Hz Sine
    data = np.sin(2 * np.pi * 10 * times)
    data = np.tile(data, (n_channels, 1))
    
    # Add Spike at t=5s
    spike_idx = 5 * sfreq
    data[:, spike_idx:spike_idx+10] += 5.0 # Huge Spike
    
    info = mne.create_info(
        ch_names=[f"EEG {i+1:03d}" for i in range(n_channels)], 
        sfreq=sfreq, 
        ch_types='eeg'
    )
    raw = mne.io.RawArray(data, info)
    
    path_raw = os.path.join(directory, "golden_eeg_raw.fif")
    path_clean = os.path.join(directory, "golden_eeg_clean.fif")
    
    raw.save(path_raw, overwrite=True)
    
    # Clean version (No spike)
    data_clean = data.copy()
    data_clean[:, spike_idx:spike_idx+10] -= 5.0
    raw_clean = mne.io.RawArray(data_clean, info)
    raw_clean.save(path_clean, overwrite=True)
    
    return path_raw, path_clean

def generate_golden_dataset(directory=None):
    """Main entry point to generate all validation data."""
    if directory is None:
        directory = os.path.join(os.path.expanduser("~"), ".neuroops", "validation_data")
        
    os.makedirs(directory, exist_ok=True)
    
    print(f"✨ Generating Golden Dataset in {directory}...")
    mri_a, mri_b = generate_golden_mri(directory)
    eeg_a, eeg_b = generate_golden_eeg(directory)
    print(f"   MRI: {mri_a}")
    print(f"   EEG: {eeg_a}")
    
    return {
        "mri": (mri_a, mri_b),
        "eeg": (eeg_a, eeg_b)
    }

if __name__ == "__main__":
    generate_golden_dataset()
