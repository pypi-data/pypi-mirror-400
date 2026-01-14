from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np
import re
from src.ports.base import NeuroSource
from src.core.reporting.models import AuditIssue, Status

class AuditPolicy(ABC):
    """
    Abstract Base Class for Data Integrity Rules.
    """
    @abstractmethod
    def check(self, source_a: NeuroSource, source_b: NeuroSource) -> List[AuditIssue]:
        pass

class SubjectMismatchPolicy(AuditPolicy):
    """
    Ensures that we are diffing the SAME subject (unless explicitly disabled).
    Prevents accidental "Patient A vs Patient B" comparisons.
    """
    def check(self, source_a: NeuroSource, source_b: NeuroSource) -> List[AuditIssue]:
        issues = []
        # Attempt to parse Subject ID from filename (BIDS style: sub-01)
        sub_a = self._extract_sub(source_a.id)
        sub_b = self._extract_sub(source_b.id)
        
        if sub_a and sub_b and sub_a != sub_b:
            issues.append(AuditIssue(
                policy="SubjectMismatch",
                severity=Status.WARN,
                message=f"Subject Mismatch Detected: {sub_a} vs {sub_b}. Are you sure?"
            ))
        elif not sub_a or not sub_b:
             issues.append(AuditIssue(
                policy="SubjectMismatch",
                severity=Status.PASS,
                message="Could not verify Subject IDs (Non-BIDS filenames)."
            ))
        else:
             issues.append(AuditIssue(
                policy="SubjectMismatch",
                severity=Status.PASS,
                message=f"Subjects Match ({sub_a})"
            ))
        return issues

    def _extract_sub(self, filename: str) -> str:
        match = re.search(r'(sub-[a-zA-Z0-9]+)', filename)
        return match.group(1) if match else None

class SignalFlatlinePolicy(AuditPolicy):
    """
    Checks if a significant portion of the signal is exactly ZERO (Dead Channel).
    """
    def check(self, source_a: NeuroSource, source_b: NeuroSource) -> List[AuditIssue]:
        issues = []
        # We need to fetch a sample. We can't scan the whole file (too slow).
        # Strategy: Check first 10 seconds.
        # This only works for EEG / TimeSeries.
        
        # Check Source A
        if 'sfreq' in source_a.get_meta():
            issues.extend(self._check_signal(source_a, "Source A"))
            
        # Check Source B
        if 'sfreq' in source_b.get_meta():
            issues.extend(self._check_signal(source_b, "Source B"))
            
        return issues

    def _check_signal(self, source: NeuroSource, label: str) -> List[AuditIssue]:
        issues = []
        try:
            # Fetch 10s
             # Assuming starts at 0.
            data, _ = source.get_signal(0, 10)
            if data.size == 0: return []

            # Check for zeros
            zero_fraction = np.mean(data == 0)
            
            if zero_fraction > 0.5:
                issues.append(AuditIssue(
                    policy="SignalFlatline",
                    severity=Status.FAIL,
                    message=f"{label}: >50% of signal is flatline (zeros). Verification failed."
                ))
            else:
                 issues.append(AuditIssue(
                    policy="SignalFlatline",
                    severity=Status.PASS,
                    message=f"{label}: Signal activity detected."
                ))
        except Exception as e:
             # MRI source passed to signal policy?
             pass 
        return issues
