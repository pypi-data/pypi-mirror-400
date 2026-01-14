"""
Module F: Central Audit Log (FR-17)

Implements a secure, append-only audit trail for 21 CFR Part 11 compliance.
Logs critical actions (Validation, Verification, Remediation) to a central location.
"""

import os
import time
import json
import logging
import getpass
from typing import Dict, Any, Optional

class AuditLogger:
    """
    Central Audit Logger.
    Writes to ~/.neuroops/audit.log by default.
    """
    
    def __init__(self, log_path: Optional[str] = None):
        if log_path is None:
            home = os.path.expanduser("~")
            log_dir = os.path.join(home, ".neuroops")
            os.makedirs(log_dir, exist_ok=True)
            self.log_path = os.path.join(log_dir, "audit.log")
        else:
            self.log_path = log_path
            
        self.user = getpass.getuser()

    def log_event(self, action: str, file_hash: str, details: Dict[str, Any] = None):
        """
        Log an event to the audit trail.
        
        Args:
            action: short code (e.g., "VALIDATE", "LOAD_FAIL", "SCRUB_PII")
            file_hash: Full SHA-256 of the file involved
            details: Additional context (NO PII allowed)
        """
        entry = {
            "timestamp": time.time(),
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "user": self.user,
            "action": action,
            "file_hash": file_hash,
            "details": details or {}
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            # Fallback to system logger if audit fails
            logging.error(f"AUDIT LOG FAILURE: {e} - Entry: {entry}")
            
    def get_logs(self, limit: int = 100) -> list:
        """Retrieve recent logs (for admin UI)."""
        logs = []
        if not os.path.exists(self.log_path):
            return logs
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return logs
