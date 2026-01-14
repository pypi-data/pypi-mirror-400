"""
NeuroOps Converter: Universal Format Wizard

Converts neuroimaging data between formats with automatic metadata handling.
Saves researchers hours of manual scripting.

Supported conversions:
- EEG: .edf, .set, .fif, .vhdr → BIDS
- MRI: .nii, .nii.gz, DICOM → BIDS (with dcm2niix)
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of a format conversion."""
    success: bool
    input_path: str
    output_path: Optional[str] = None
    format_from: Optional[str] = None
    format_to: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata_extracted: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FormatConverter:
    """
    Universal format converter for neuroimaging data.
    
    Usage:
        converter = FormatConverter()
        result = converter.to_bids("recording.edf", "./bids_dataset", subject="01", task="rest")
    """
    
    # Supported input formats
    SUPPORTED_EEG = {'.edf', '.set', '.fif', '.vhdr', '.bdf', '.cnt', '.mff'}
    SUPPORTED_MRI = {'.nii', '.nii.gz', '.dcm', '.ima'}
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for required optional dependencies."""
        self.has_mne_bids = False
        self.has_dcm2niix = False
        
        try:
            import mne_bids
            self.has_mne_bids = True
        except ImportError:
            logger.warning("mne-bids not installed. EEG→BIDS conversion unavailable.")
            logger.warning("Install with: pip install mne-bids")
        
        # Check for dcm2niix
        import shutil
        if shutil.which('dcm2niix'):
            self.has_dcm2niix = True
        else:
            logger.warning("dcm2niix not found. DICOM→NIfTI conversion unavailable.")
    
    def detect_format(self, path: str) -> Tuple[str, str]:
        """
        Detect file format and modality.
        
        Returns:
            (format_extension, modality) e.g. ('.edf', 'EEG')
        """
        path_lower = path.lower()
        
        # Check extensions
        if path_lower.endswith('.nii.gz'):
            return '.nii.gz', 'MRI'
        
        ext = Path(path).suffix.lower()
        
        if ext in self.SUPPORTED_EEG:
            return ext, 'EEG'
        elif ext in self.SUPPORTED_MRI:
            return ext, 'MRI'
        else:
            return ext, 'UNKNOWN'
    
    def to_bids(
        self,
        input_path: str,
        bids_root: str,
        subject: str,
        task: Optional[str] = None,
        session: Optional[str] = None,
        run: Optional[int] = None,
        datatype: Optional[str] = None,
        overwrite: bool = False,
        # EEG-specific
        line_freq: Optional[float] = None,
        # MRI-specific
        modality: Optional[str] = None,  # T1w, T2w, bold, etc.
    ) -> ConversionResult:
        """
        Convert any supported format to BIDS.
        
        Args:
            input_path: Path to source file
            bids_root: Output BIDS dataset root
            subject: Subject ID (without 'sub-' prefix)
            task: Task name (required for func/eeg)
            session: Session ID (optional)
            run: Run number (optional)
            datatype: BIDS datatype (auto-detected if not provided)
            overwrite: Overwrite existing files
            line_freq: Power line frequency for EEG (50 or 60 Hz)
            modality: MRI modality suffix (T1w, bold, etc.)
            
        Returns:
            ConversionResult with success status and output path
        """
        # Validate input
        if not os.path.exists(input_path):
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=f"File not found: {input_path}"
            )
        
        # Detect format
        ext, detected_modality = self.detect_format(input_path)
        
        if detected_modality == 'EEG':
            return self._convert_eeg_to_bids(
                input_path, bids_root, subject, task, session, run,
                overwrite, line_freq
            )
        elif detected_modality == 'MRI':
            return self._convert_mri_to_bids(
                input_path, bids_root, subject, session, run,
                overwrite, modality
            )
        else:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=f"Unsupported format: {ext}"
            )
    
    def _convert_eeg_to_bids(
        self,
        input_path: str,
        bids_root: str,
        subject: str,
        task: Optional[str],
        session: Optional[str],
        run: Optional[int],
        overwrite: bool,
        line_freq: Optional[float]
    ) -> ConversionResult:
        """Convert EEG formats to BIDS using MNE-BIDS."""
        
        if not self.has_mne_bids:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error="mne-bids not installed. Run: pip install mne-bids"
            )
        
        import mne
        from mne_bids import write_raw_bids, BIDSPath
        
        warnings = []
        
        # Auto-detect task from filename if not provided
        if task is None:
            task = self._infer_task_from_filename(input_path)
            if task:
                warnings.append(f"Task inferred from filename: {task}")
            else:
                task = "unknown"
                warnings.append("No task specified, using 'unknown'")
        
        # Load the raw file
        ext = Path(input_path).suffix.lower()
        try:
            if ext == '.edf':
                raw = mne.io.read_raw_edf(input_path, preload=True, verbose=False)
            elif ext == '.bdf':
                raw = mne.io.read_raw_bdf(input_path, preload=True, verbose=False)
            elif ext == '.set':
                raw = mne.io.read_raw_eeglab(input_path, preload=True, verbose=False)
            elif ext == '.fif':
                raw = mne.io.read_raw_fif(input_path, preload=True, verbose=False)
            elif ext == '.vhdr':
                raw = mne.io.read_raw_brainvision(input_path, preload=True, verbose=False)
            elif ext == '.cnt':
                raw = mne.io.read_raw_cnt(input_path, preload=True, verbose=False)
            elif ext == '.mff':
                raw = mne.io.read_raw_egi(input_path, preload=True, verbose=False)
            else:
                # Try generic reader
                raw = mne.io.read_raw(input_path, preload=True, verbose=False)
        except Exception as e:
            return ConversionResult(
                success=False,
                input_path=input_path,
                format_from=ext,
                error=f"Failed to read file: {e}"
            )
        
        # Set line frequency if not present
        if raw.info['line_freq'] is None:
            if line_freq:
                raw.info['line_freq'] = line_freq
            else:
                # Default based on common regions
                raw.info['line_freq'] = 50.0  # EU default
                warnings.append("Line frequency not set, defaulting to 50 Hz (EU)")
        
        # Extract metadata for report
        metadata = {
            'n_channels': len(raw.ch_names),
            'sfreq': raw.info['sfreq'],
            'duration_sec': raw.times[-1],
            'ch_types': list(set(raw.get_channel_types())),
            'line_freq': raw.info['line_freq']
        }
        
        # Create BIDS path
        bids_path = BIDSPath(
            subject=subject,
            session=session,
            task=task,
            run=run,
            datatype='eeg',
            root=bids_root
        )
        
        # Write to BIDS
        try:
            output_path = write_raw_bids(
                raw, 
                bids_path, 
                overwrite=overwrite,
                verbose=self.verbose
            )
            
            return ConversionResult(
                success=True,
                input_path=input_path,
                output_path=str(output_path),
                format_from=ext,
                format_to='BIDS',
                warnings=warnings,
                metadata_extracted=metadata
            )
        except Exception as e:
            return ConversionResult(
                success=False,
                input_path=input_path,
                format_from=ext,
                error=f"BIDS write failed: {e}",
                warnings=warnings
            )
    
    def _convert_mri_to_bids(
        self,
        input_path: str,
        bids_root: str,
        subject: str,
        session: Optional[str],
        run: Optional[int],
        overwrite: bool,
        modality: Optional[str]
    ) -> ConversionResult:
        """Convert MRI formats to BIDS."""
        import nibabel as nib
        
        warnings = []
        ext = '.nii.gz' if input_path.lower().endswith('.nii.gz') else Path(input_path).suffix.lower()
        
        # Handle DICOM
        if ext in ['.dcm', '.ima'] or os.path.isdir(input_path):
            if not self.has_dcm2niix:
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    error="dcm2niix not found. Install from: https://github.com/rordenlab/dcm2niix"
                )
            # Convert DICOM to NIfTI first
            return self._convert_dicom_to_bids(input_path, bids_root, subject, session, run, modality)
        
        # Load NIfTI
        try:
            img = nib.load(input_path)
        except Exception as e:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=f"Failed to load NIfTI: {e}"
            )
        
        # Infer modality from filename or shape
        if modality is None:
            modality = self._infer_mri_modality(input_path, img.shape)
            warnings.append(f"Modality inferred: {modality}")
        
        # Determine datatype (anat vs func)
        if modality in ['T1w', 'T2w', 'FLAIR', 'PD']:
            datatype = 'anat'
        elif modality in ['bold', 'sbref']:
            datatype = 'func'
        elif modality in ['dwi']:
            datatype = 'dwi'
        else:
            datatype = 'anat'
        
        # Create output directory structure
        sub_dir = f"sub-{subject}"
        if session:
            sub_dir = os.path.join(sub_dir, f"ses-{session}")
        
        output_dir = os.path.join(bids_root, sub_dir, datatype)
        os.makedirs(output_dir, exist_ok=True)
        
        # Build filename
        parts = [f"sub-{subject}"]
        if session:
            parts.append(f"ses-{session}")
        if run:
            parts.append(f"run-{run:02d}")
        parts.append(modality)
        
        output_name = "_".join(parts) + ".nii.gz"
        output_path = os.path.join(output_dir, output_name)
        
        # Check overwrite
        if os.path.exists(output_path) and not overwrite:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=f"Output exists: {output_path}. Use overwrite=True"
            )
        
        # Copy/convert file
        try:
            nib.save(img, output_path)
        except Exception as e:
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=f"Failed to save: {e}"
            )
        
        # Create sidecar JSON
        sidecar = self._create_mri_sidecar(img, input_path)
        json_path = output_path.replace('.nii.gz', '.json').replace('.nii', '.json')
        with open(json_path, 'w') as f:
            json.dump(sidecar, f, indent=2)
        
        # Metadata for report
        metadata = {
            'shape': list(img.shape),
            'voxel_size': [float(z) for z in img.header.get_zooms()[:3]],
            'modality': modality,
            'datatype': datatype
        }
        
        return ConversionResult(
            success=True,
            input_path=input_path,
            output_path=output_path,
            format_from=ext,
            format_to='BIDS',
            warnings=warnings,
            metadata_extracted=metadata
        )
    
    def _convert_dicom_to_bids(
        self,
        dicom_path: str,
        bids_root: str,
        subject: str,
        session: Optional[str],
        run: Optional[int],
        modality: Optional[str]
    ) -> ConversionResult:
        """Convert DICOM to BIDS using dcm2niix."""
        import subprocess
        import tempfile
        
        # Create temp directory for dcm2niix output
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run dcm2niix
            cmd = ['dcm2niix', '-z', 'y', '-o', tmpdir, dicom_path]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return ConversionResult(
                    success=False,
                    input_path=dicom_path,
                    error=f"dcm2niix failed: {e.stderr.decode()}"
                )
            
            # Find output NIfTI
            niftis = list(Path(tmpdir).glob('*.nii.gz'))
            if not niftis:
                niftis = list(Path(tmpdir).glob('*.nii'))
            
            if not niftis:
                return ConversionResult(
                    success=False,
                    input_path=dicom_path,
                    error="dcm2niix produced no output"
                )
            
            # Convert each output to BIDS
            for nii in niftis:
                return self._convert_mri_to_bids(
                    str(nii), bids_root, subject, session, run, True, modality
                )
    
    def _infer_task_from_filename(self, path: str) -> Optional[str]:
        """Try to extract task name from filename."""
        import re
        name = os.path.basename(path).lower()
        
        # Common patterns
        patterns = [
            r'task[_-]?(\w+)',
            r'rest',
            r'eyes[_-]?(open|closed)',
            r'motor',
            r'visual',
            r'auditory'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        
        return None
    
    def _infer_mri_modality(self, path: str, shape: tuple) -> str:
        """Infer MRI modality from filename and data shape."""
        name = os.path.basename(path).lower()
        
        # Check common patterns
        if 't1' in name or 't1w' in name:
            return 'T1w'
        elif 't2' in name or 't2w' in name:
            return 'T2w'
        elif 'flair' in name:
            return 'FLAIR'
        elif 'bold' in name or 'func' in name or 'fmri' in name:
            return 'bold'
        elif 'dwi' in name or 'dti' in name:
            return 'dwi'
        
        # Infer from shape
        if len(shape) == 4 and shape[3] > 10:
            return 'bold'  # Likely functional
        else:
            return 'T1w'  # Default to T1w for anatomical
    
    def _create_mri_sidecar(self, img, source_path: str) -> Dict[str, Any]:
        """Create BIDS sidecar JSON for MRI."""
        header = img.header
        
        sidecar = {
            "Modality": "MR",
            "ConversionSoftware": "NeuroOps",
            "ConversionSoftwareVersion": "1.0",
            "SourceFile": os.path.basename(source_path)
        }
        
        # Extract TR for 4D
        if len(img.shape) > 3:
            zooms = header.get_zooms()
            if len(zooms) > 3 and zooms[3] > 0:
                sidecar["RepetitionTime"] = float(zooms[3])
        
        return sidecar


def convert_to_bids(
    input_path: str,
    output_dir: str,
    subject: str,
    task: Optional[str] = None,
    **kwargs
) -> ConversionResult:
    """Convenience function for quick conversion."""
    converter = FormatConverter()
    return converter.to_bids(input_path, output_dir, subject, task, **kwargs)
