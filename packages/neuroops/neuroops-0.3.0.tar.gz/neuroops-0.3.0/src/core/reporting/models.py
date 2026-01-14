from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Status(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

class ComplianceReport(BaseModel):
    is_valid: bool
    bids_warnings: List[str] = []
    file_format: str
    metadata: Dict[str, Any] = {}

class SyncReport(BaseModel):
    drift_detected: bool
    drift_slope: float = 0.0 # 0.0 means perfect sync
    confidence: float = 1.0

class AuditIssue(BaseModel):
    policy: str
    severity: Status
    message: str

class AuditReport(BaseModel):
    status: Status
    issues: List[AuditIssue] = []
    metrics: Dict[str, float] = {}

class PipelineResult(BaseModel):
    compliance: ComplianceReport
    sync: SyncReport
    audit: AuditReport
    
    # Path to the "virtual" sources if needed, or just status
    pass_gate: bool
