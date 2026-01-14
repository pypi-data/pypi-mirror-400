"""
Module: BIDS Validation Checks

Cross-references NIfTI headers against BIDS JSON sidecars.
Detects silent killers like TR conflicts and orphan files.
"""

import os
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BIDSValidationResult:
    """Result of a BIDS validation check."""
    
    def __init__(self, check_name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.check_name = check_name
        self.passed = passed
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "status": "PASS" if self.passed else "FAIL",
            "message": self.message,
            "details": self.details
        }


class BIDSValidator:
    """
    Validates BIDS dataset structure and cross-references metadata.
    """
    
    def __init__(self, tolerance_tr: float = 0.01):
        """
        Args:
            tolerance_tr: Allowed difference in TR values (seconds)
        """
        self.tolerance_tr = tolerance_tr
    
    def check_tr_conflict(
        self, 
        nifti_path: str, 
        nifti_tr: Optional[float] = None
    ) -> BIDSValidationResult:
        """
        Cross-reference TR between NIfTI header and BIDS JSON sidecar.
        
        Detects: Silent mismatch between header TR and JSON RepetitionTime
        """
        check_name = "tr_conflict"
        
        # Find matching JSON sidecar
        json_path = self._get_sidecar_path(nifti_path)
        
        if not json_path or not os.path.exists(json_path):
            return BIDSValidationResult(
                check_name, True, 
                "No JSON sidecar found (cannot cross-check TR)"
            )
        
        try:
            with open(json_path, 'r') as f:
                sidecar = json.load(f)
        except Exception as e:
            return BIDSValidationResult(
                check_name, False,
                f"Cannot read sidecar JSON: {e}"
            )
        
        json_tr = sidecar.get('RepetitionTime')
        
        if json_tr is None:
            return BIDSValidationResult(
                check_name, True,
                "No RepetitionTime in sidecar (cannot validate)"
            )
        
        if nifti_tr is None:
            return BIDSValidationResult(
                check_name, True,
                "No TR from NIfTI header (cannot validate)"
            )
        
        # Compare
        diff = abs(float(json_tr) - float(nifti_tr))
        
        if diff > self.tolerance_tr:
            return BIDSValidationResult(
                check_name, False,
                f"TR CONFLICT: NIfTI header says {nifti_tr}s, JSON says {json_tr}s",
                {"nifti_tr": nifti_tr, "json_tr": json_tr, "difference": diff}
            )
        
        return BIDSValidationResult(
            check_name, True,
            f"TR consistent: {json_tr}s",
            {"tr": json_tr}
        )
    
    def check_orphan_files(self, directory: str) -> List[BIDSValidationResult]:
        """
        Scan directory for orphan files (NIfTI without JSON or vice versa).
        
        Returns list of results, one per orphan found.
        """
        results = []
        check_name = "orphan_sidecar"
        
        path = Path(directory)
        
        # Find all NIfTI files
        niftis = set()
        for ext in ['*.nii', '*.nii.gz']:
            niftis.update(path.rglob(ext))
        
        # Find all JSON files
        jsons = set(path.rglob('*.json'))
        
        # Check each NIfTI has a JSON
        for nii in niftis:
            expected_json = self._get_sidecar_path(str(nii))
            if expected_json and not os.path.exists(expected_json):
                results.append(BIDSValidationResult(
                    check_name, False,
                    f"NIfTI without sidecar: {nii.name}",
                    {"nifti": str(nii), "missing_json": expected_json}
                ))
        
        # Check each JSON has a NIfTI (except known BIDS JSONs)
        skip_jsons = {'dataset_description.json', 'participants.json', 'scans.json'}
        for js in jsons:
            if js.name in skip_jsons:
                continue
            if js.name.startswith('task-') or js.name.startswith('beh-'):
                continue  # Task/behavior definitions
                
            # Check for matching NIfTI
            base = js.stem  # Remove .json
            possible_niftis = [
                js.parent / f"{base}.nii",
                js.parent / f"{base}.nii.gz"
            ]
            if not any(p.exists() for p in possible_niftis):
                results.append(BIDSValidationResult(
                    check_name, False,
                    f"JSON without NIfTI: {js.name}",
                    {"json": str(js), "expected_nifti": str(possible_niftis[0])}
                ))
        
        if not results:
            results.append(BIDSValidationResult(
                check_name, True,
                f"No orphan files found in {directory}"
            ))
        
        return results
    
    def check_intended_for(self, json_path: str) -> BIDSValidationResult:
        """
        Validate that IntendedFor references point to existing files.
        
        Detects: Field maps pointing to renamed/deleted functional files
        """
        check_name = "intended_for"
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return BIDSValidationResult(
                check_name, False,
                f"Cannot read JSON: {e}"
            )
        
        intended = data.get('IntendedFor')
        if not intended:
            return BIDSValidationResult(
                check_name, True,
                "No IntendedFor field"
            )
        
        # IntendedFor can be string or list
        if isinstance(intended, str):
            intended = [intended]
        
        # Resolve paths (IntendedFor is relative to BIDS root)
        bids_root = self._find_bids_root(json_path)
        if not bids_root:
            return BIDSValidationResult(
                check_name, True,
                "Cannot find BIDS root (skipping IntendedFor validation)"
            )
        
        missing = []
        for target in intended:
            # Remove leading "bids::" or similar prefixes
            target = target.replace('bids::', '')
            if target.startswith('/'):
                target = target[1:]
            
            full_path = os.path.join(bids_root, target)
            if not os.path.exists(full_path):
                missing.append(target)
        
        if missing:
            return BIDSValidationResult(
                check_name, False,
                f"IntendedFor points to missing files: {missing}",
                {"missing": missing}
            )
        
        return BIDSValidationResult(
            check_name, True,
            f"All IntendedFor targets exist ({len(intended)} files)"
        )
    
    def _get_sidecar_path(self, nifti_path: str) -> Optional[str]:
        """Get the expected JSON sidecar path for a NIfTI file."""
        base = nifti_path
        for ext in ['.nii.gz', '.nii']:
            if nifti_path.lower().endswith(ext):
                base = nifti_path[:-len(ext)]
                break
        return base + '.json'
    
    def _find_bids_root(self, file_path: str) -> Optional[str]:
        """Walk up directories to find dataset_description.json."""
        path = Path(file_path).parent
        for _ in range(10):  # Max 10 levels up
            if (path / 'dataset_description.json').exists():
                return str(path)
            if path.parent == path:
                break
            path = path.parent
        return None
