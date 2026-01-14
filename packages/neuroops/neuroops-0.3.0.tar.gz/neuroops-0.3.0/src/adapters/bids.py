import os
import re
from typing import List, Tuple, Optional
import glob

class BIDSAdapter:
    """
    Intelligent Adapter to scan BIDS directories and pair Raw vs Processed files.
    
    Logic:
    1. Scans 'sub-XX' folders for raw data (e.g., _eeg.edf, _bold.nii.gz).
    2. Scans 'derivatives/sub-XX' for corresponding processed files.
    3. Returns a list of (raw_path, processed_path) tuples.
    """
    def __init__(self, root_dir: str):
        self.root = os.path.abspath(root_dir)
        self.derivatives_root = os.path.join(self.root, 'derivatives')

    def find_pairs(self, modality: str = 'eeg') -> List[Tuple[str, str]]:
        """
        Finds pairs of (Raw, Processed) files.
        modality: 'eeg', 'mri' (maps to 'anat' or 'func'), etc.
        """
        pairs = []
        
        # 1. Find Raw Files
        # Pattern: root/sub-*/ses-*/modality/*_modality.ext or root/sub-*/modality/*_modality.ext
        # We'll use a recursive walk for robustness
        
        # Define extensions based on modality
        extensions = {
            'eeg': ['.edf', '.fif', '.vhdr', '.set'],
            'mri': ['.nii', '.nii.gz']
        }
        valid_exts = extensions.get(modality, [])
        
        for dirpath, _, filenames in os.walk(self.root):
            # Skip derivatives for raw search
            if 'derivatives' in dirpath:
                continue
                
            for f in filenames:
                if any(f.endswith(ext) for ext in valid_exts):
                    # Check if it looks BIDS-y (starts with sub-)
                    if f.startswith('sub-'):
                        raw_path = os.path.join(dirpath, f)
                        processed_path = self._find_derivative(f, modality)
                        
                        if processed_path:
                            pairs.append((raw_path, processed_path))
                        else:
                            # Verify if maybe *this* file is the processed one? 
                            # (No, we skipped derivatives)
                            pass
                            
        return pairs

    def _find_derivative(self, raw_filename: str, modality: str) -> Optional[str]:
        """
        Heuristic to find the processed version of a raw file.
        Strategy: Look in derivatives/ for a file with similar name.
        Common patterns:
        - raw: sub-01_task-rest_eeg.edf
        - proc: derivatives/pipeline/sub-01/sub-01_task-rest_proc-clean_eeg.edf
        
        We look for files in derivatives that contain the subject ID and task.
        """
        if not os.path.exists(self.derivatives_root):
            return None
            
        # Extract Subject ID
        match = re.search(r'(sub-[a-zA-Z0-9]+)', raw_filename)
        if not match: return None
        sub_id = match.group(1)
        
        # Search in derivatives
        # We look for a file that shares the key components
        base_name = os.path.splitext(raw_filename)[0]
        
        # Walk derivatives
        for dirpath, _, filenames in os.walk(self.derivatives_root):
            if sub_id not in dirpath: continue # Speed up: only look in sub folder
            
            for f in filenames:
                # Naive matching:
                # 1. Must contain subject ID
                # 2. Must be same modality type (extension check? processed might be .nii.gz even if raw is .nii)
                # Let's assume processed has same extension for EEG, or .fif
                
                if sub_id in f and f != raw_filename:
                    # Check if it's a likely candidate
                    #Ideally regex match: sub-01_..._desc-processed_...
                    if 'proc' in f or 'desc' in f or 'clean' in f:
                         return os.path.join(dirpath, f)
                         
        return None
