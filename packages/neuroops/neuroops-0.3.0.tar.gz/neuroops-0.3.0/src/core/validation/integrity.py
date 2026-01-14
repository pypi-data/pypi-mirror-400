"""
Module C: Validation Engine - Integrity Checks (FR-06)
Hard-fail checks that trigger immediate "Critical" state.

These checks detect fundamental data corruption that cannot be remediated
and would cause downstream pipeline failures.
"""

import os
import struct
from typing import Dict, Any, Tuple, Optional, List
from enum import Enum
import numpy as np


class IntegrityStatus(Enum):
    """Status codes for integrity checks."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"  # Check not applicable


class IntegrityResult:
    """Result of an integrity check."""
    
    def __init__(
        self, 
        check_name: str,
        status: IntegrityStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.check_name = check_name
        self.status = status
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details
        }
    
    @property
    def passed(self) -> bool:
        return self.status in (IntegrityStatus.PASS, IntegrityStatus.SKIP)


class IntegrityChecker:
    """
    FR-06: Integrity Checks (Hard Fail)
    
    Detects file corruption, truncation, dimension mismatches,
    and invalid affine matrices.
    """
    
    # NIfTI magic bytes (header positions 344-347)
    NIFTI1_MAGIC = (b'n+1', b'ni1')
    NIFTI2_MAGIC = (b'n+2', b'ni2')
    FIF_MAGIC = b'FIFF'
    
    # NIfTI datatype sizes (datatype code -> bytes per voxel)
    NIFTI_DTYPE_SIZES = {
        2: 1,    # UINT8
        4: 2,    # INT16
        8: 4,    # INT32
        16: 4,   # FLOAT32
        64: 8,   # FLOAT64
        256: 1,  # INT8
        512: 2,  # UINT16
        768: 4,  # UINT32
        1024: 8, # INT64
        1280: 8, # UINT64
    }
    
    def __init__(self, min_file_size_bytes: int = 1024):
        """
        Args:
            min_file_size_bytes: Files smaller than this are considered truncated
        """
        self.min_file_size = min_file_size_bytes
    
    def run_all_checks(
        self, 
        file_path: str,
        header_data: Optional[Dict[str, Any]] = None,
        affine: Optional[np.ndarray] = None
    ) -> List[IntegrityResult]:
        """
        Run all integrity checks on a file.
        """
        results = []
        
        # Check 1: File existence and basic corruption
        results.append(self.check_file_corruption(file_path))
        
        # Check 2: Gzip magic (for .gz files)
        if file_path.lower().endswith('.gz'):
            results.append(self.check_gzip_magic(file_path))
        
        # Check 3: Magic bytes validation
        results.append(self.check_magic_bytes(file_path))
        
        # Check 4: Dimension validity (if header provided)
        if header_data:
            results.append(self.check_dimension_validity(header_data))
            results.append(self.check_orientation_codes(header_data))
            
            # Check if 4D data in func folder has multiple timepoints
            if 'func' in file_path.lower():
                results.append(self.check_4d_volume(header_data, file_path))
        
        # Check 5: Affine validity (if provided)
        if affine is not None:
            results.append(self.check_affine_validity(affine))
        
        return results
    
    def check_gzip_magic(self, file_path: str) -> IntegrityResult:
        """
        Validate that .gz files are actually gzip compressed.
        
        Detects: "Fake" gzip files that are uncompressed but named .gz
        Magic bytes: 1f 8b at start of file
        """
        check_name = "gzip_magic"
        GZIP_MAGIC = b'\x1f\x8b'
        
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(2)
        except IOError as e:
            return IntegrityResult(check_name, IntegrityStatus.FAIL, f"Cannot read file: {e}")
        
        if magic == GZIP_MAGIC:
            return IntegrityResult(check_name, IntegrityStatus.PASS, "Valid gzip compression")
        else:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"File is named .gz but is NOT gzip compressed (magic: {magic.hex()})",
                {"found": magic.hex(), "expected": "1f8b"}
            )
    
    def check_orientation_codes(self, header_data: Dict[str, Any]) -> IntegrityResult:
        """
        Check that orientation codes are defined (Left-Right flip detection).
        
        Detects: Files with sform_code=0 AND qform_code=0 (ambiguous orientation)
        """
        check_name = "orientation_codes"
        
        sform = header_data.get('sform_code', 0)
        qform = header_data.get('qform_code', 0)
        
        if sform == 0 and qform == 0:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                "No orientation defined (sform_code=0, qform_code=0). Left/Right may be ambiguous.",
                {"sform_code": sform, "qform_code": qform}
            )
        
        return IntegrityResult(
            check_name, IntegrityStatus.PASS,
            f"Orientation defined (sform={sform}, qform={qform})",
            {"sform_code": sform, "qform_code": qform}
        )
    
    def check_4d_volume(self, header_data: Dict[str, Any], file_path: str) -> IntegrityResult:
        """
        Check that functional data has multiple timepoints.
        
        Detects: 3D files in func/ folder (likely export error)
        """
        check_name = "4d_volume"
        
        shape = header_data.get('shape') or header_data.get('dim')
        if shape is None:
            return IntegrityResult(check_name, IntegrityStatus.SKIP, "No shape info")
        
        if hasattr(shape, 'tolist'):
            shape = shape.tolist()
        
        # Functional data should be 4D
        if len(shape) < 4 or shape[3] <= 1:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"File in func/ folder has only {len(shape)}D data (expected 4D with >1 timepoints)",
                {"shape": shape, "path": file_path}
            )
        
        return IntegrityResult(
            check_name, IntegrityStatus.PASS,
            f"4D volume OK: {shape[3]} timepoints",
            {"n_timepoints": shape[3]}
        )
    
    def check_file_corruption(self, file_path: str) -> IntegrityResult:
        """
        Check for file corruption/truncation.
        
        Detects:
        - Missing files
        - Zero-byte files
        - Files below minimum size threshold
        - Unreadable files
        """
        check_name = "file_corruption"
        
        # Existence
        if not os.path.exists(file_path):
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"File not found: {file_path}"
            )
        
        # Size check
        try:
            size = os.path.getsize(file_path)
        except OSError as e:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Cannot read file size: {e}"
            )
        
        if size == 0:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                "File is empty (zero bytes)",
                {"size_bytes": 0}
            )
        
        if size < self.min_file_size:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"File appears truncated ({size} bytes < {self.min_file_size} minimum)",
                {"size_bytes": size, "min_expected": self.min_file_size}
            )
        
        # Readability check
        try:
            with open(file_path, 'rb') as f:
                # Try to read first and last chunks
                f.read(1024)
                if size > 2048:
                    f.seek(-1024, 2)
                    f.read(1024)
        except IOError as e:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"File is unreadable: {e}"
            )
        
        return IntegrityResult(
            check_name, IntegrityStatus.PASS,
            "File integrity OK",
            {"size_bytes": size}
        )
    
    def check_magic_bytes(self, file_path: str) -> IntegrityResult:
        """
        Validate file format via magic bytes.
        
        Detects:
        - Misnamed files (wrong extension for content)
        - Corrupted headers
        """
        check_name = "magic_bytes"
        
        if not os.path.exists(file_path):
            return IntegrityResult(
                check_name, IntegrityStatus.SKIP,
                "File not found, skipping magic bytes check"
            )
        
        ext = file_path.lower()
        
        try:
            with open(file_path, 'rb') as f:
                header = f.read(512)  # Read enough for most headers
        except IOError:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                "Cannot read file header"
            )
        
        # NIfTI check
        if ext.endswith(('.nii', '.nii.gz')):
            # Handle gzipped files
            if ext.endswith('.gz'):
                try:
                    import gzip
                    with gzip.open(file_path, 'rb') as f:
                        header = f.read(512)
                except Exception as e:
                    return IntegrityResult(
                        check_name, IntegrityStatus.FAIL,
                        f"Cannot decompress gzip file: {e}"
                    )
            
            # Check NIfTI magic at offset 344
            if len(header) >= 348:
                magic = header[344:348]
                # NIfTI-1: "n+1\0" or "ni1\0"  
                # NIfTI-2: "n+2\0" or "ni2\0"
                valid_magic = (
                    magic[:3] in self.NIFTI1_MAGIC or 
                    magic[:3] in self.NIFTI2_MAGIC
                )
                if valid_magic:
                    return IntegrityResult(
                        check_name, IntegrityStatus.PASS,
                        f"Valid NIfTI header detected",
                        {"magic": magic[:3].decode('ascii', errors='replace')}
                    )
                else:
                    return IntegrityResult(
                        check_name, IntegrityStatus.FAIL,
                        f"Invalid NIfTI magic bytes",
                        {"found": magic.hex(), "expected": "6e2b31 or 6e6931"}
                    )
            else:
                return IntegrityResult(
                    check_name, IntegrityStatus.FAIL,
                    "Header too short for NIfTI format"
                )
        
        # FIF check
        elif ext.endswith('.fif'):
            if header[:4] == self.FIF_MAGIC:
                return IntegrityResult(
                    check_name, IntegrityStatus.PASS,
                    "Valid FIF header detected"
                )
            else:
                return IntegrityResult(
                    check_name, IntegrityStatus.FAIL,
                    "Invalid FIF magic bytes",
                    {"found": header[:4].hex(), "expected": "FIFF"}
                )
        
        # Unknown format - skip
        else:
            return IntegrityResult(
                check_name, IntegrityStatus.SKIP,
                f"Magic bytes check not implemented for this format"
            )
    
    def check_dimension_validity(
        self, 
        header_data: Dict[str, Any]
    ) -> IntegrityResult:
        """
        Validate data dimensions from header.
        
        Detects:
        - Zero dimensions (empty data)
        - Negative dimensions (corruption)
        - Unreasonably large dimensions (likely corruption)
        """
        check_name = "dimension_validity"
        
        # Look for shape/dim in various formats
        shape = header_data.get('shape') or header_data.get('dim')
        
        if shape is None:
            return IntegrityResult(
                check_name, IntegrityStatus.SKIP,
                "No dimension info in header"
            )
        
        # Convert to list if needed
        if hasattr(shape, 'tolist'):
            shape = shape.tolist()
        
        # Check for zeros
        if 0 in shape:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Zero dimension detected: {shape}",
                {"dimensions": shape}
            )
        
        # Check for negatives
        if any(d < 0 for d in shape if isinstance(d, (int, float))):
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Negative dimension detected: {shape}",
                {"dimensions": shape}
            )
        
        # Sanity check - no dimension should exceed 100000
        MAX_DIM = 100000
        if any(d > MAX_DIM for d in shape if isinstance(d, (int, float))):
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Unreasonably large dimension (>{MAX_DIM}): {shape}",
                {"dimensions": shape, "max_allowed": MAX_DIM}
            )
        
        return IntegrityResult(
            check_name, IntegrityStatus.PASS,
            f"Dimensions valid: {shape}",
            {"dimensions": shape}
        )
    
    def check_affine_validity(self, affine: np.ndarray) -> IntegrityResult:
        """
        Validate affine transformation matrix.
        
        Detects:
        - NaN values (corruption)
        - Inf values (overflow)
        - Non-invertible matrices (invalid transformation)
        - Wrong shape (should be 4x4)
        """
        check_name = "affine_validity"
        
        # Shape check
        if affine.shape != (4, 4):
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Invalid affine shape: {affine.shape} (expected 4x4)",
                {"shape": affine.shape}
            )
        
        # NaN check
        if np.any(np.isnan(affine)):
            nan_positions = np.argwhere(np.isnan(affine)).tolist()
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"NaN values in affine matrix at positions: {nan_positions}",
                {"nan_positions": nan_positions}
            )
        
        # Inf check
        if np.any(np.isinf(affine)):
            inf_positions = np.argwhere(np.isinf(affine)).tolist()
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Inf values in affine matrix at positions: {inf_positions}",
                {"inf_positions": inf_positions}
            )
        
        # Invertibility check (determinant should be non-zero)
        try:
            det = np.linalg.det(affine[:3, :3])  # Only check rotation/scale part
            if abs(det) < 1e-10:
                return IntegrityResult(
                    check_name, IntegrityStatus.FAIL,
                    f"Affine matrix is singular (det={det:.2e})",
                    {"determinant": float(det)}
                )
        except np.linalg.LinAlgError:
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                "Cannot compute affine determinant"
            )
        
        # Check for reasonable voxel sizes (0.1mm to 10mm typically)
        voxel_sizes = np.sqrt(np.sum(affine[:3, :3]**2, axis=0))
        if np.any(voxel_sizes < 0.01) or np.any(voxel_sizes > 100):
            return IntegrityResult(
                check_name, IntegrityStatus.FAIL,
                f"Unreasonable voxel sizes: {voxel_sizes}",
                {"voxel_sizes_mm": voxel_sizes.tolist()}
            )
        
        return IntegrityResult(
            check_name, IntegrityStatus.PASS,
            "Affine matrix valid",
            {
                "determinant": float(det),
                "voxel_sizes_mm": voxel_sizes.tolist()
            }
        )


def check_file_integrity(
    file_path: str,
    header_data: Optional[Dict[str, Any]] = None,
    affine: Optional[np.ndarray] = None
) -> Tuple[bool, List[IntegrityResult]]:
    """
    Convenience function to run all integrity checks.
    
    Returns:
        Tuple of (all_passed, list_of_results)
    """
    checker = IntegrityChecker()
    results = checker.run_all_checks(file_path, header_data, affine)
    all_passed = all(r.passed for r in results)
    return all_passed, results
