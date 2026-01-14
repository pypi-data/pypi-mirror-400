from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class AuditEntry(Base):
    """
    SQLAlchemy Model for the Audit Log.
    Stores the permanent record of QC decisions.
    """
    __tablename__ = 'audit_log'

    record_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=False)
    
    # BIDS Context
    subject_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)
    task_id = Column(String, nullable=True)
    run_id = Column(String, nullable=True)
    modality = Column(String, nullable=False)
    full_path = Column(String, nullable=False)
    
    # Integrity
    file_hash = Column(String, nullable=False)
    
    # Decision
    status = Column(String, nullable=False) # ACCEPTED, REJECTED
    flags = Column(JSON, nullable=True)     # Details of rejection

# Output handling
DB_PATH = "neuroops.db"

def init_db(db_path=DB_PATH):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def get_session(db_path=DB_PATH):
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()
