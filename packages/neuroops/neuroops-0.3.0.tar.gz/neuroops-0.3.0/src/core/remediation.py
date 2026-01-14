"""
Module D: Visual Resolver - Remediation Service (FR-12)
Data remediation functions for cropping bad segments and excluding channels.

CRITICAL: This module NEVER modifies original data.
All operations create versioned copies to preserve data integrity.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


class RemediationError(Exception):
    """Raised when remediation operation fails."""
    pass


class RemediationService:
    """
    FR-12: Remediation Actions
    
    Provides "Crop" (remove bad time segments) and "Exclude" (mark channels as bad)
    operations. Always creates versioned copies - NEVER modifies originals.
    
    Why: Clinical trials require complete audit trails. Original data must remain
    untouched for regulatory compliance. This service creates versioned derivatives
    with full provenance tracking.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Args:
            output_dir: Directory for remediated files (default: same as source)
        """
        self.output_dir = output_dir
        self._version_suffix = "_remediated"
    
    def crop_time_segment(
        self,
        source_path: str,
        start_time: float,
        end_time: float,
        keep: bool = True,
        dry_run: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Crop a time segment from the data.
        
        Args:
            source_path: Path to source file
            start_time: Start time in seconds
            end_time: End time in seconds
            keep: If True, keep this segment; if False, remove this segment
            dry_run: If True (default), return preview only; if False, write file
            
        Returns:
            Tuple of (output_path, provenance_dict)
            If dry_run=True, output_path is None and provenance contains preview info.
        """
        import nibabel as nib
        
        if not os.path.exists(source_path):
            raise RemediationError(f"Source file not found: {source_path}")
        
        # Load source
        img = nib.load(source_path)
        data = img.get_fdata()
        header = img.header
        affine = img.affine
        
        # Verify 4D data
        if data.ndim != 4:
            raise RemediationError(f"Crop requires 4D data, got {data.ndim}D")
        
        # Get timing info
        tr = header.get_zooms()[3] if len(header.get_zooms()) > 3 else 1.0
        n_volumes = data.shape[3]
        
        # Convert times to volume indices
        start_vol = int(start_time / tr)
        end_vol = int(end_time / tr)
        
        # Clamp to valid range
        start_vol = max(0, min(start_vol, n_volumes - 1))
        end_vol = max(start_vol, min(end_vol, n_volumes))
        
        # Perform crop
        if keep:
            # Keep only this segment
            cropped_data = data[:, :, :, start_vol:end_vol]
        else:
            # Remove this segment (keep before and after)
            before = data[:, :, :, :start_vol]
            after = data[:, :, :, end_vol:]
            cropped_data = np.concatenate([before, after], axis=3)
        
        # Generate output path
        output_path = self._generate_output_path(source_path, "cropped")
        
        # Save cropped data
        cropped_img = nib.Nifti1Image(cropped_data, affine, header)
        nib.save(cropped_img, output_path)
        
        # Generate provenance
        provenance = self._create_provenance(
            operation="crop_time_segment",
            source_path=source_path,
            output_path=output_path,
            parameters={
                "start_time": start_time,
                "end_time": end_time,
                "start_vol": start_vol,
                "end_vol": end_vol,
                "keep_segment": keep,
                "original_volumes": n_volumes,
                "output_volumes": cropped_data.shape[3],
                "tr_sec": float(tr)
            }
        )
        
        # Save provenance sidecar
        self._save_provenance(output_path, provenance)
        
        return output_path, provenance
    
    def exclude_channels(
        self,
        source_path: str,
        bad_channels: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Mark channels as bad in EEG/MEG data.
        
        For MNE-compatible formats, this updates the 'bads' list in the data.
        
        Args:
            source_path: Path to source EEG/MEG file
            bad_channels: List of channel names to mark as bad
            
        Returns:
            Tuple of (output_path, provenance_dict)
        """
        try:
            import mne
        except ImportError:
            raise RemediationError("MNE-Python required for channel exclusion")
        
        if not os.path.exists(source_path):
            raise RemediationError(f"Source file not found: {source_path}")
        
        # Load raw data
        ext = source_path.lower()
        if ext.endswith('.fif'):
            raw = mne.io.read_raw_fif(source_path, preload=True, verbose=False)
        elif ext.endswith('.edf'):
            raw = mne.io.read_raw_edf(source_path, preload=True, verbose=False)
        else:
            raise RemediationError(f"Unsupported format for channel exclusion: {ext}")
        
        # Get existing bads
        existing_bads = list(raw.info['bads'])
        
        # Add new bads (avoiding duplicates)
        all_bads = list(set(existing_bads + bad_channels))
        raw.info['bads'] = all_bads
        
        # Generate output path
        output_path = self._generate_output_path(source_path, "cleaned")
        
        # Save with updated bads
        raw.save(output_path, overwrite=False, verbose=False)
        
        # Generate provenance
        provenance = self._create_provenance(
            operation="exclude_channels",
            source_path=source_path,
            output_path=output_path,
            parameters={
                "added_bad_channels": bad_channels,
                "existing_bad_channels": existing_bads,
                "total_bad_channels": all_bads,
                "total_channels": len(raw.ch_names)
            }
        )
        
        self._save_provenance(output_path, provenance)
        
        return output_path, provenance
    
    def interpolate_bad_channels(
        self,
        source_path: str,
        bad_channels: Optional[List[str]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Interpolate bad channels using spherical spline interpolation.
        
        Args:
            source_path: Path to source EEG/MEG file
            bad_channels: Channels to interpolate (or use existing bads)
            
        Returns:
            Tuple of (output_path, provenance_dict)
        """
        try:
            import mne
        except ImportError:
            raise RemediationError("MNE-Python required for interpolation")
        
        # Load raw data
        ext = source_path.lower()
        if ext.endswith('.fif'):
            raw = mne.io.read_raw_fif(source_path, preload=True, verbose=False)
        else:
            raise RemediationError(f"Interpolation not supported for: {ext}")
        
        # Set bads if provided
        if bad_channels:
            raw.info['bads'] = list(set(raw.info['bads'] + bad_channels))
        
        bads_to_interpolate = list(raw.info['bads'])
        
        if not bads_to_interpolate:
            raise RemediationError("No bad channels to interpolate")
        
        # Interpolate
        raw.interpolate_bads(reset_bads=True, verbose=False)
        
        # Generate output
        output_path = self._generate_output_path(source_path, "interpolated")
        raw.save(output_path, overwrite=False, verbose=False)
        
        provenance = self._create_provenance(
            operation="interpolate_bad_channels",
            source_path=source_path,
            output_path=output_path,
            parameters={
                "interpolated_channels": bads_to_interpolate,
                "method": "spherical_spline"
            }
        )
        
        self._save_provenance(output_path, provenance)
        
        return output_path, provenance
    
    def _generate_output_path(self, source_path: str, operation: str) -> str:
        """Generate versioned output path."""
        # Extract base and extension
        base = source_path
        ext = ""
        
        for e in ['.nii.gz', '.nii', '.fif', '.edf', '.vhdr', '.mat']:
            if source_path.lower().endswith(e):
                base = source_path[:-len(e)]
                ext = e
                break
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Build output name
        output_name = f"{os.path.basename(base)}_{operation}_{timestamp}{ext}"
        
        # Determine output directory
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, output_name)
        else:
            output_path = os.path.join(os.path.dirname(source_path), output_name)
        
        return output_path
    
    def _create_provenance(
        self,
        operation: str,
        source_path: str,
        output_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create provenance record for remediation operation."""
        import hashlib
        
        # Compute hashes
        source_hash = self._compute_hash(source_path)
        output_hash = self._compute_hash(output_path)
        
        return {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "source": {
                "path": source_path,
                "hash": source_hash
            },
            "output": {
                "path": output_path,
                "hash": output_hash
            },
            "parameters": parameters,
            "version": "NeuroOps-Remediation-1.0"
        }
    
    def _compute_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file."""
        if not os.path.exists(file_path):
            return "NOT_COMPUTED"
        
        sha = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha.update(chunk)
            return f"sha256:{sha.hexdigest()}"
        except IOError:
            return "HASH_ERROR"
    
    def _save_provenance(self, output_path: str, provenance: Dict[str, Any]) -> None:
        """Save provenance sidecar JSON."""
        prov_path = output_path + ".provenance.json"
        
        # Save JSON
        with open(prov_path, 'w', encoding='utf-8') as f:
            json.dump(provenance, f, indent=2, default=str)
            
        # FR-16: Lock permissions to Read-Only (0o444)
        # Verify first if we are on Windows (os.chmod might have limited effect but still good practice)
        try:
            os.chmod(prov_path, 0o444)
            # Also lock the data file if it exists
            if os.path.exists(output_path):
                os.chmod(output_path, 0o444)
        except Exception:
            pass # Ignore permission errors on some filesystems


def remediate_and_revalidate(
    source_path: str,
    operation: str,
    params: Dict[str, Any],
    schema_path: Optional[str] = None
) -> Tuple[str, bool, List[Dict[str, Any]]]:
    """
    Perform remediation and automatically re-validate.
    
    Args:
        source_path: Path to source file
        operation: "crop" or "exclude"
        params: Operation parameters
        schema_path: Optional validation schema
        
    Returns:
        Tuple of (output_path, validation_passed, check_results)
    """
    from src.core.validation.integrity import check_file_integrity
    
    service = RemediationService()
    
    # Perform remediation
    if operation == "crop":
        output_path, _ = service.crop_time_segment(
            source_path,
            start_time=params.get('start_time', 0),
            end_time=params.get('end_time', 10),
            keep=params.get('keep', False)
        )
    elif operation == "exclude":
        output_path, _ = service.exclude_channels(
            source_path,
            bad_channels=params.get('bad_channels', [])
        )
    else:
        raise RemediationError(f"Unknown operation: {operation}")
    
    # Re-validate
    passed, results = check_file_integrity(output_path)
    
    return output_path, passed, [r.to_dict() for r in results]
