"""
Module: Anonymization Check

Detects potential PII in neuroimaging headers.
Warns by default; blocking mode available via --strict-anon flag.
"""

import os
import logging
import re
from typing import List, Dict, Tuple, Optional, Any, Union
import pydicom
from pydicom.tag import Tag
import nibabel as nib

logger = logging.getLogger(__name__)

class PIIWarning:
    """Container for PII detection results."""
    pass

class AnonymizationChecker:
    """
    Scans files for potential PII. Returns warnings (does not block by default).
    """
    
    # Standard DICOM Tags known to contain PII
    # (Group, Element) tuples
    PII_TAGS = [
        (0x0010, 0x0010), # PatientName
        (0x0010, 0x0020), # PatientID
        (0x0010, 0x0030), # PatientBirthDate
        (0x0010, 0x0032), # PatientBirthTime
        (0x0010, 0x0040), # PatientSex
        (0x0010, 0x1000), # OtherPatientIDs
        (0x0010, 0x1001), # OtherPatientNames
        (0x0010, 0x1040), # PatientAddress
        (0x0010, 0x2154), # PatientTelephoneNumbers
        (0x0008, 0x0080), # InstitutionName
        (0x0008, 0x0081), # InstitutionAddress
        (0x0008, 0x0090), # ReferringPhysicianName
        (0x0008, 0x1050), # PerformingPhysicianName
        (0x0008, 0x1070), # OperatorsName
    ]
    
    # Regex patterns for free-text fields (NIfTI description etc.)
    # Names are hard, but we can look for dates, SSNs, phone numbers
    PATTERNS = {
        "date_iso": re.compile(r'\d{4}-\d{2}-\d{2}'),
        "date_compact": re.compile(r'\d{8}'), # YYYYMMDD
        "email": re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'),
        "phone": re.compile(r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}'),
        # Very distinct formatting, usually safe to catch
    }

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Scans a file for PII.
        Returns a list of detected PII entries.
        """
        ext = file_path.lower()
        detections = []
        
        try:
            if ext.endswith(('.dcm', '.ima')):
                detections.extend(self._scan_dicom(file_path))
            elif ext.endswith(('.nii', '.nii.gz')):
                detections.extend(self._scan_nifti(file_path))
            elif ext.endswith('.json'):
                # Sidecars often contain PII
                pass 
        except Exception as e:
            logger.error(f"Failed to scan {os.path.basename(file_path)}: {e}")
            # Fail closed? No, let's log error. 
            # In "Kill Switch" mode, maybe catching error implies unsafe?
            
        return detections

    def _scan_dicom(self, file_path: str) -> List[Dict[str, Any]]:
        found = []
        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            
            for tag_tuple in self.PII_TAGS:
                tag = Tag(tag_tuple)
                if tag in ds:
                    elem = ds[tag]
                    if elem.value and str(elem.value).strip():
                        # Found non-empty PII tag
                        found.append({
                            "type": "DICOM_TAG",
                            "tag": str(tag),
                            "name": elem.keyword,
                            "value_preview": "REDACTED" # Never propagate PII
                        })
                        
        except Exception as e:
            logger.warning(f"DICOM scan error: {e}")
            
        return found

    def _scan_nifti(self, file_path: str) -> List[Dict[str, Any]]:
        found = []
        try:
            img = nib.load(file_path)
            header = img.header
            
            # Fields to check
            fields_to_check = {
                'descrip': header.get('descrip', b''),
                'aux_file': header.get('aux_file', b''),
                'intent_name': header.get('intent_name', b'')
            }
            
            for field, value in fields_to_check.items():
                text = value.tobytes().decode('utf-8', errors='ignore').strip('\x00').strip()
                if not text:
                    continue
                    
                # Scan text against patterns
                for p_name, pattern in self.PATTERNS.items():
                    if pattern.search(text):
                        found.append({
                            "type": "NIFTI_HEADER_TEXT",
                            "field": field,
                            "pattern": p_name,
                            "value_preview": "REDACTED"
                        })
                        
            # Check extensions if present
            # Nibabel handles extensions...
            
        except Exception as e:
            logger.warning(f"NIfTI scan error: {e}")
            
        return found

    def scrub_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Removes PII from file.
        DICOM: Uses pydicom anonymization.
        NIfTI: Zeroes out descrip/aux/intent fields.
        
        Returns path to cleaned file.
        """
        if output_path is None:
            base, ext = os.path.splitext(file_path)
            if ext == '.gz': 
                base, _ = os.path.splitext(base)
                ext = '.nii.gz'
            output_path = f"{base}_anonymized{ext}"
            
        ext = file_path.lower()
        
        if ext.endswith(('.dcm', '.ima')):
            self._scrub_dicom(file_path, output_path)
        elif ext.endswith(('.nii', '.nii.gz')):
            self._scrub_nifti(file_path, output_path)
        else:
            raise NotImplementedError(f"Scrubbing not supported for {ext}")
            
        return output_path

    def _scrub_dicom(self, input_path: str, output_path: str):
        ds = pydicom.dcmread(input_path)
        
        # Walkthrough and clear PII tags
        # Basic curve: clear standard tags
        for tag_tuple in self.PII_TAGS:
             if tag_tuple in ds:
                 ds[tag_tuple].value = "" # Clear value
        
        # Make Anonymous
        ds.PatientName = "ANONYMIZED"
        ds.PatientID = "ANONYMIZED"
        ds.PatientBirthDate = ""
        
        ds.save_as(output_path)

    def _scrub_nifti(self, input_path: str, output_path: str):
        img = nib.load(input_path)
        
        # Zero out potentially dangerous text fields
        # Ideally we should only target the specific detection, but brute force safe is better for Kill Switch
        img.header['descrip'] = b''
        img.header['aux_file'] = b''
        img.header['intent_name'] = b''
        
        # Drop extensions? 
        # img.header.extensions = [] # This might break things if extensions are critical
        # Safer to leave extensions unless we know they act as containers for PII
        
        nib.save(img, output_path)

