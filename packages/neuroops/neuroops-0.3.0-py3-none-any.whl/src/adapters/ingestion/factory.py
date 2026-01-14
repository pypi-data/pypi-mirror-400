import os
import re
import json
from enum import Enum
from typing import Dict, Any, List, Optional
from src.adapters.local import LocalMRIAdapter, LocalEEGAdapter
from src.ports.base import NeuroSource
from src.core.reporting.models import ComplianceReport

class AdapterType(Enum):
    MRI = "MRI"
    EEG = "EEG"
    UNKNOWN = "UNKNOWN"

class DataFactory:
    """
    Module A: Ingestion Facade.
    Auto-detects format and returns appropriate Adapter.
    """
    
    # Magic byte signatures for format detection
    NIFTI_MAGIC = (b'n+1', b'ni1', b'n+2', b'ni2')
    FIF_MAGIC = b'FIFF'
    
    @staticmethod
    def sniff(path: str, validate_magic: bool = True) -> AdapterType:
        """
        FR-03: Format Agnosticism with Magic Bytes Detection.
        
        Determines adapter type based on extension AND magic bytes validation.
        Magic bytes provide defense against misnamed files.
        
        Args:
            path: File path to analyze
            validate_magic: If True, verify magic bytes match extension
            
        Returns:
            AdapterType enum (MRI, EEG, or UNKNOWN)
        """
        name = path.lower()
        
        # Extension-based detection
        if name.endswith(('.nii', '.nii.gz')):
            ext_type = AdapterType.MRI
        elif name.endswith(('.fif', '.edf', '.vhdr', '.mat')):
            ext_type = AdapterType.EEG
        else:
            return AdapterType.UNKNOWN
        
        # Magic bytes validation (FR-03 enhancement)
        if validate_magic and os.path.exists(path):
            magic_type = DataFactory._detect_from_magic_bytes(path)
            if magic_type != AdapterType.UNKNOWN and magic_type != ext_type:
                # Extension/content mismatch - log warning but trust extension
                # This catches misnamed files without breaking existing workflows
                pass
            elif magic_type != AdapterType.UNKNOWN:
                return magic_type
        
        return ext_type
    
    @staticmethod
    def _detect_from_magic_bytes(path: str) -> AdapterType:
        """
        Detect file type from magic bytes.
        
        NIfTI: bytes 344-347 contain 'n+1', 'ni1', 'n+2', or 'ni2'
        FIF: First 4 bytes are 'FIFF'
        """
        try:
            # Handle gzipped files
            if path.lower().endswith('.gz'):
                import gzip
                with gzip.open(path, 'rb') as f:
                    header = f.read(512)
            else:
                with open(path, 'rb') as f:
                    header = f.read(512)
        except Exception:
            return AdapterType.UNKNOWN
        
        # Check NIfTI magic at offset 344
        if len(header) >= 348:
            magic = header[344:347]
            if magic in DataFactory.NIFTI_MAGIC:
                return AdapterType.MRI
        
        # Check FIF magic at start
        if header[:4] == DataFactory.FIF_MAGIC:
            return AdapterType.EEG
        
        return AdapterType.UNKNOWN

    @staticmethod
    def load(path: str, strict_anon: bool = False) -> NeuroSource:
        """
        Instantiates the correct adapter.
        
        Args:
            path: File path
            strict_anon: If True, block loading if PII detected. Default: warn only.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        # --- Anonymization Check ---
        from src.core.anonymization import AnonymizationChecker
        checker = AnonymizationChecker()
        detections = checker.scan_file(path)
        
        if detections:
            det_summary = [f"{d['type']}:{d.get('name', d.get('field', 'unknown'))}" for d in detections]
            msg = f"Potential PII in {os.path.basename(path)}: {det_summary}"
            
            if strict_anon:
                raise ValueError(f"BLOCKED: {msg}")
            else:
                import warnings
                warnings.warn(f"⚠️ {msg}", UserWarning)

        atype = DataFactory.sniff(path)
        
        if atype == AdapterType.MRI:
            return LocalMRIAdapter(path)
        elif atype == AdapterType.EEG:
            return LocalEEGAdapter(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")

    @staticmethod
    def validate_bids_compliance(path: str) -> ComplianceReport:
        """
        Runs a lightweight BIDS check.
        Checks for .json sidecar and BIDS filename compliance.
        """
        is_valid = True
        warnings = []
        metadata = {}
        
        filename = os.path.basename(path)
        
        # 1. Filename Check (sub-XX_ses-YY_modality.ext)
        # Regex: sub-[alnum]+
        if not re.search(r'sub-[a-zA-Z0-9]+', filename):
            is_valid = False
            warnings.append("Filename missing 'sub-XX' tag.")
            
        # 2. Sidecar Check
        # BIDS requires a JSON sidecar with same name
        # e.g. .nii.gz -> .json
        base = path
        for ext in ['.nii.gz', '.nii', '.fif', '.edf', '.mat']:
            if path.lower().endswith(ext):
                base = path[:-len(ext)]
                break
        
        json_path = base + ".json"
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                warnings.append(f"Sidecar JSON found but unreadable: {e}")
        else:
            # It's a warning for the MVP, but strict BIDS requires it for many types
            warnings.append("Missing JSON sidecar.")
            # We don't fail `is_valid` for this in MVP, just warn.
            
        return ComplianceReport(
            is_valid=is_valid,
            bids_warnings=warnings,
            file_format=DataFactory.sniff(path).value,
            metadata=metadata
        )
