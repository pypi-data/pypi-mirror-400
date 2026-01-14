import streamlit as st
import os
from src.interface.controller import Controller
from src.core.audit_log import AuditLogger
from src.core.db import init_db

DB_PATH = "neuroops.db"

def init_session_state():
    """Initialize all session state variables."""
    
    if 'controller' not in st.session_state:
        st.session_state.controller = Controller()

    # Initialize Enterprise Components
    if 'audit_logger' not in st.session_state:
        # Ensure DB exists
        init_db(DB_PATH)
        st.session_state.audit_logger = AuditLogger(DB_PATH)

    # Initialize Mock User (Security Theater)
    if 'current_user' not in st.session_state:
        st.session_state.current_user = "demo_user"

    keys = [
        'diff_engine',                  # The VirtualDiff Logic Entity
        'data_type',                    # 'MRI' or 'EEG'
        'current_file_id',              # To detect file changes
        'is_demo_mode',                 # Toggle for demo
        'demo_loaded',
        'bids_context'                  # CURRENT CONTEXT
    ]
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = None
