from pydantic import BaseModel, Field
from typing import Optional, Dict

class BIDSContext(BaseModel):
    """
    Represents the semantic context of a neuroimaging file.
    Extracted from the filename [Subject, Session, Task, Run, Modality].
    """
    subject_id: str = Field(..., description="Subject label (e.g., 'sub-01')")
    session_id: Optional[str] = Field(None, description="Session label (e.g., 'ses-baseline')")
    task_id: Optional[str] = Field(None, description="Task label (e.g., 'task-rest')")
    run_id: Optional[str] = Field(None, description="Run index (e.g., 'run-01')")
    modality: str = Field(..., description="Imaging modality suffix (e.g., 'bold', 'T1w', 'eeg')")
    full_path: str = Field(..., description="Original file path")

    @property
    def key(self) -> str:
        """Returns a unique logical key for this dataset."""
        parts = [self.subject_id]
        if self.session_id: parts.append(self.session_id)
        if self.task_id: parts.append(self.task_id)
        if self.run_id: parts.append(self.run_id)
        parts.append(self.modality)
        return "_".join(parts)

class AuditRecord(BaseModel):
    """
    Represents a single quality control decision made by a human.
    """
    record_id: str = Field(..., description="Unique UUID for this record")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    user_id: str = Field(..., description="ID of the reviewer")
    
    # Context
    bids_context: BIDSContext
    
    # The Integrity Check
    file_hash: str = Field(..., description="SHA-256 hash of the file header/content")
    
    # The Decision
    status: str = Field(..., pattern="^(ACCEPTED|REJECTED|FLAGGED)$")
    flags: Optional[Dict] = Field(default_factory=dict, description="Details of artifacts if rejected")
