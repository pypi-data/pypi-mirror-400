import numpy as np
from typing import Dict, Any, List

def check_flatline(data: np.ndarray, channels: List[str], threshold: float = 1e-15) -> List[str]:
    """
    Detects channels with zero or near-zero variance.
    Returns list of bad channel names.
    """
    bad_channels = []
    # Data shape assumption: (n_channels, n_times)
    stds = np.std(data, axis=1)
    
    for idx, std_val in enumerate(stds):
        if std_val < threshold:
            bad_channels.append(channels[idx])
            
    return bad_channels

def check_motion_fmri(img_obj) -> float:
    """
    Estimates Framewise Displacement (FD) proxy.
    True FD requires costly realignment (MCFLIRT).
    For Triage, we use 'DVARS' (Derivative of RMS variance over voxels) as a quick proxy.
    Or, if 4D, we check center-of-mass shift.
    
    MVP: Center of Mass shift between first and last volume.
    """
    import scipy.ndimage as nd
    
    if len(img_obj.shape) < 4:
        return 0.0 # Not 4D
        
    data = img_obj.get_fdata()
    # Check first and last volume (Quick proxy)
    vol0 = data[..., 0]
    vol_end = data[..., -1]
    
    com0 = np.array(nd.center_of_mass(vol0))
    com_end = np.array(nd.center_of_mass(vol_end))
    
    # Euclidean distance of drift
    drift = np.linalg.norm(com0 - com_end)
    return drift

def check_affine_mismatch(img_a, img_b, tolerance: float = 1e-3) -> bool:
    """
    Checks if two NIfTI images share the same space.
    """
    aff_a = img_a.affine
    aff_b = img_b.affine
    
    return not np.allclose(aff_a, aff_b, atol=tolerance)
