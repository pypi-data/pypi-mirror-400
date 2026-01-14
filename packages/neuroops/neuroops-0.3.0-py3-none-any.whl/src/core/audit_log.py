import uuid
from datetime import datetime
from typing import Dict, Optional
from src.core.models import AuditRecord, BIDSContext
from src.core.db import get_session, AuditEntry

class AuditLogger:
    """
    The 'Notary Public' of the system.
    Writes immutable records to the SQLite database.
    """
    def __init__(self, db_path: str = "neuroops.db"):
        self.db_path = db_path

    def log_decision(
        self, 
        user_id: str, 
        bids_context: BIDSContext, 
        file_hash: str, 
        status: str, 
        flags: Optional[Dict] = None
    ) -> AuditRecord:
        """
        Records a QC decision.
        """
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # 1. Create Domain Model (Validation)
        # (Status pattern check handled by Pydantic)
        record = AuditRecord(
            record_id=record_id,
            timestamp=timestamp,
            user_id=user_id,
            bids_context=bids_context,
            file_hash=file_hash,
            status=status,
            flags=flags or {}
        )
        
        # 2. Write to DB
        session = get_session(self.db_path)
        try:
            entry = AuditEntry(
                record_id=record.record_id,
                timestamp=datetime.fromisoformat(record.timestamp),
                user_id=record.user_id,
                subject_id=record.bids_context.subject_id,
                session_id=record.bids_context.session_id,
                task_id=record.bids_context.task_id,
                run_id=record.bids_context.run_id,
                modality=record.bids_context.modality,
                full_path=record.bids_context.full_path,
                file_hash=record.file_hash,
                status=record.status,
                flags=record.flags
            )
            session.add(entry)
            session.commit()
            print(f"Audit Logged: {record.record_id} for {record.bids_context.subject_id}")
        except Exception as e:
            session.rollback()
            raise IOError(f"Failed to write audit log: {e}")
        finally:
            session.close()
            
        return record
