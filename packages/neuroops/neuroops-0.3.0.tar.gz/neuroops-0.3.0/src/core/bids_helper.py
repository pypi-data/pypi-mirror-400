import os
import json
import re

def validate_bids_filename(filename):
    """
    Checks if a filename roughly adheres to BIDS standard.
    Format: sub-<label>_[ses-<label>]_task-<label>_[acq-<label>]_<suffix>.<ext>
    
    Returns: (is_valid, issues_list, suggested_fix)
    """
    issues = []
    
    # 1. Check for 'sub-' prefix
    if not filename.startswith('sub-'):
        issues.append("Missing 'sub-' prefix")
        
    # 2. Check for valid characters (alphanumeric + - _)
    if not re.match(r'^[a-zA-Z0-9\-\_\.]+$', filename):
        issues.append("Contains invalid characters (use only a-z, 0-9, -, _)")
        
    # 3. Check for suffix (e.g., _eeg, _T1w)
    # This is a simplified check
    valid_suffixes = ['_eeg', '_meg', '_T1w', '_bold', '_events', '_channels']
    has_suffix = any(s in filename for s in valid_suffixes)
    if not has_suffix:
        issues.append("Missing modality suffix (e.g., _eeg, _T1w)")
        
    is_valid = len(issues) == 0
    
    # Suggest Fix
    suggested_fix = None
    if not is_valid:
        # Try to construct a valid name
        # Heuristic: Find something that looks like an ID
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', filename.split('.')[0])
        suggested_fix = f"sub-{clean_name}_task-rest_eeg.edf" # Generic guess
        
    return is_valid, issues, suggested_fix

def generate_bids_sidecar(filename, modality='eeg'):
    """
    Generates a minimal valid JSON sidecar for a given file.
    """
    base_name = os.path.splitext(filename)[0]
    
    if modality == 'eeg':
        content = {
            "TaskName": "rest",
            "SamplingFrequency": 1000,
            "PowerLineFrequency": 50,
            "EEGChannelCount": 64,
            "EOGChannelCount": 0,
            "ECGChannelCount": 0,
            "EMGChannelCount": 0,
            "RecordingType": "continuous",
            "RecordingDuration": 600
        }
    elif modality == 'mri':
        content = {
            "Modality": "MR",
            "MagneticFieldStrength": 3,
            "Manufacturer": "Siemens",
            "PulseSequenceType": "Gradient Echo"
        }
    else:
        content = {}
        
    return json.dumps(content, indent=4)
