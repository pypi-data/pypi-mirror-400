"""
Demo Data Generation and Management

Provides synthetic datasets for NeuroOps demo mode.
Auto-downloads and caches sample data for quick onboarding.
"""

import os
import numpy as np
import nibabel as nib
from pathlib import Path
from typing import Tuple, Optional
import json

def get_demo_cache_dir() -> Path:
    """Get the demo data cache directory."""
    cache_dir = Path.home() / ".neuroops" / "demo"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def generate_demo_eeg(duration: float = 10.0, sfreq: float = 500.0) -> Tuple[np.ndarray, np.ndarray, dict]:
    """
    Generate synthetic EEG data with realistic artifacts.
    
    Args:
        duration: Duration in seconds
        sfreq: Sampling frequency in Hz
        
    Returns:
        raw_data: Raw EEG with artifacts (n_channels, n_samples)
        clean_data: Cleaned EEG (n_channels, n_samples)
        metadata: Channel names, sampling frequency, etc.
    """
    n_samples = int(duration * sfreq)
    n_channels = 8
    times = np.linspace(0, duration, n_samples)
    
    # Channel names
    ch_names = ['Fp1', 'Fp2', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2']
    
    # Base signal: Alpha rhythm (8-12 Hz) + some beta
    alpha_freq = 10.0  # Hz
    beta_freq = 20.0   # Hz
    
    clean_data = np.zeros((n_channels, n_samples))
    for ch_idx in range(n_channels):
        # Alpha component (dominant)
        alpha = 50 * np.sin(2 * np.pi * alpha_freq * times + ch_idx * 0.3)
        # Beta component (smaller)
        beta = 20 * np.sin(2 * np.pi * beta_freq * times + ch_idx * 0.5)
        # Noise
        noise = np.random.randn(n_samples) * 5
        
        clean_data[ch_idx] = alpha + beta + noise
    
    # Create raw data with artifacts
    raw_data = clean_data.copy()
    
    # Artifact 1: 60Hz line noise (will be removed in clean)
    line_noise = 30 * np.sin(2 * np.pi * 60.0 * times)
    for ch_idx in range(n_channels):
        raw_data[ch_idx] += line_noise
    
    # Artifact 2: Eye blink at 3s and 7s (high amplitude, frontal channels)
    blink_times = [3.0, 7.0]
    for blink_t in blink_times:
        blink_idx = int(blink_t * sfreq)
        blink_width = int(0.2 * sfreq)  # 200ms blink
        blink_start = max(0, blink_idx - blink_width // 2)
        blink_end = min(n_samples, blink_idx + blink_width // 2)
        
        # Gaussian-shaped blink artifact
        blink_samples = np.arange(blink_start, blink_end)
        blink_shape = np.exp(-((blink_samples - blink_idx) ** 2) / (2 * (blink_width / 4) ** 2))
        
        # Add to frontal channels (Fp1, Fp2)
        raw_data[0, blink_start:blink_end] += 200 * blink_shape
        raw_data[1, blink_start:blink_end] += 200 * blink_shape
    
    # Artifact 3: Muscle artifact at 5s (high frequency, all channels)
    muscle_start = int(5.0 * sfreq)
    muscle_end = int(5.5 * sfreq)
    muscle_artifact = np.random.randn(muscle_end - muscle_start) * 80
    for ch_idx in range(n_channels):
        raw_data[ch_idx, muscle_start:muscle_end] += muscle_artifact
    
    metadata = {
        'ch_names': ch_names,
        'sfreq': sfreq,
        'duration': duration,
        'n_channels': n_channels,
        'type': 'EEG'
    }
    
    return raw_data, clean_data, metadata

def generate_demo_mri(shape: Tuple[int, int, int] = (64, 64, 64)) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic MRI brain volume with preprocessing differences.
    
    Args:
        shape: Volume dimensions (x, y, z)
        
    Returns:
        raw_volume: Raw MRI
        processed_volume: Skull-stripped and smoothed MRI
        affine: Affine transformation matrix
    """
    x, y, z = shape
    
    # Create a simple brain-like structure
    center = np.array([x // 2, y // 2, z // 2])
    
    # Create coordinate grids
    xx, yy, zz = np.meshgrid(
        np.arange(x) - center[0],
        np.arange(y) - center[1],
        np.arange(z) - center[2],
        indexing='ij'
    )
    
    # Distance from center
    dist = np.sqrt(xx**2 + yy**2 + zz**2)
    
    # Brain tissue (ellipsoid)
    brain_mask = (
        (xx / (x * 0.35))**2 + 
        (yy / (y * 0.35))**2 + 
        (zz / (z * 0.4))**2
    ) < 1.0
    
    # Skull (outer shell)
    skull_mask = (
        (xx / (x * 0.45))**2 + 
        (yy / (y * 0.45))**2 + 
        (zz / (z * 0.5))**2
    ) < 1.0
    skull_mask = skull_mask & ~brain_mask
    
    # Create raw volume
    raw_volume = np.zeros(shape, dtype=np.float32)
    raw_volume[brain_mask] = 1000 + np.random.randn(brain_mask.sum()) * 100  # Brain tissue
    raw_volume[skull_mask] = 500 + np.random.randn(skull_mask.sum()) * 50    # Skull
    
    # Add some internal structure (ventricles)
    ventricle_mask = dist < (min(shape) * 0.1)
    raw_volume[ventricle_mask] = 200 + np.random.randn(ventricle_mask.sum()) * 30
    
    # Create processed volume (skull-stripped + smoothed)
    from scipy.ndimage import gaussian_filter
    processed_volume = raw_volume.copy()
    processed_volume[~brain_mask] = 0  # Skull stripping
    processed_volume = gaussian_filter(processed_volume, sigma=1.0)  # Smoothing
    
    # Standard affine (2mm isotropic)
    affine = np.eye(4)
    affine[:3, :3] *= 2.0  # 2mm voxels
    affine[:3, 3] = -center * 2.0  # Center at origin
    
    return raw_volume, processed_volume, affine

def save_demo_data(cache_dir: Optional[Path] = None) -> dict:
    """
    Generate and save demo data to cache directory.
    
    Returns:
        paths: Dictionary with paths to saved files
    """
    if cache_dir is None:
        cache_dir = get_demo_cache_dir()
    
    paths = {}
    
    # Generate and save EEG data
    print("Generating demo EEG data...")
    raw_eeg, clean_eeg, eeg_meta = generate_demo_eeg()
    
    eeg_raw_path = cache_dir / "demo_eeg_raw.npy"
    eeg_clean_path = cache_dir / "demo_eeg_clean.npy"
    eeg_meta_path = cache_dir / "demo_eeg_meta.json"
    
    np.save(eeg_raw_path, raw_eeg)
    np.save(eeg_clean_path, clean_eeg)
    with open(eeg_meta_path, 'w') as f:
        json.dump(eeg_meta, f, indent=2)
    
    paths['eeg_raw'] = str(eeg_raw_path)
    paths['eeg_clean'] = str(eeg_clean_path)
    paths['eeg_meta'] = str(eeg_meta_path)
    
    # Generate and save MRI data
    print("Generating demo MRI data...")
    raw_mri, clean_mri, affine = generate_demo_mri()
    
    mri_raw_path = cache_dir / "demo_mri_raw.nii.gz"
    mri_clean_path = cache_dir / "demo_mri_clean.nii.gz"
    
    # Save as NIfTI
    nib.save(nib.Nifti1Image(raw_mri, affine), mri_raw_path)
    nib.save(nib.Nifti1Image(clean_mri, affine), mri_clean_path)
    
    paths['mri_raw'] = str(mri_raw_path)
    paths['mri_clean'] = str(mri_clean_path)
    
    # Save manifest
    manifest_path = cache_dir / "manifest.json"
    manifest = {
        'version': '1.0',
        'generated': True,
        'paths': paths
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Demo data saved to: {cache_dir}")
    return paths

def load_demo_data() -> dict:
    """
    Load demo data from cache, generating if not present.
    
    Returns:
        paths: Dictionary with paths to demo files
    """
    cache_dir = get_demo_cache_dir()
    manifest_path = cache_dir / "manifest.json"
    
    # Check if demo data exists
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Verify all files exist
        all_exist = all(
            Path(path).exists() 
            for path in manifest['paths'].values()
        )
        
        if all_exist:
            print(f"Loading cached demo data from: {cache_dir}")
            return manifest['paths']
    
    # Generate demo data if not cached
    print("Demo data not found in cache. Generating...")
    return save_demo_data(cache_dir)

if __name__ == "__main__":
    # Test demo data generation
    print("Testing demo data generation...")
    paths = load_demo_data()
    print("\nGenerated files:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
