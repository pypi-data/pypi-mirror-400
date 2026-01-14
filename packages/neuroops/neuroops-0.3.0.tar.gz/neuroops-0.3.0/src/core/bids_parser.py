import re
import os
from .models import BIDSContext

def parse_bids_filename(filepath: str) -> BIDSContext:
    """
    Parses a BIDS-compliant filename into a BIDSContext object.
    
    Args:
        filepath: Absolute or relative path to the file.
        
    Returns:
        BIDSContext: The extracted metadata.
        
    Raises:
        ValueError: If the filename does not contain at least a 'sub-' tag.
    """
    filename = os.path.basename(filepath)
    
    # regex patterns for BIDS entities
    # key-value pairs are separated by underscores
    # format: key-value
    
    # 1. Subject (Required)
    sub_match = re.search(r'sub-([a-zA-Z0-9]+)', filename)
    if not sub_match:
        raise ValueError(f"Filename '{filename}' is not BIDS compliant: Missing 'sub-' tag.")
    subject_id = f"sub-{sub_match.group(1)}"
    
    # 2. Session (Optional)
    ses_match = re.search(r'ses-([a-zA-Z0-9]+)', filename)
    session_id = f"ses-{ses_match.group(1)}" if ses_match else None
    
    # 3. Task (Optional)
    task_match = re.search(r'task-([a-zA-Z0-9]+)', filename)
    task_id = f"task-{task_match.group(1)}" if task_match else None
    
    # 4. Run (Optional)
    run_match = re.search(r'run-([a-zA-Z0-9]+)', filename)
    run_id = f"run-{run_match.group(1)}" if run_match else None
    
    # 5. Modality (The suffix before the extension)
    # e.g. _bold.nii.gz -> bold
    # e.g. _T1w.nii -> T1w
    # e.g. _eeg.fif -> eeg
    
    # Split by dots to get extension
    # Remove extension(s)
    base_no_ext = filename.split('.')[0]
    # The last chunk after the last underscore is typically the suffix
    if '_' in base_no_ext:
        suffix = base_no_ext.split('_')[-1]
    else:
        # Fallback/Undefined behavior if no underscores (shouldn't happen with sub- present)
        suffix = "unknown"
        
    # Construct Context
    return BIDSContext(
        subject_id=subject_id,
        session_id=session_id,
        task_id=task_id,
        run_id=run_id,
        modality=suffix,
        full_path=filepath
    )
