import streamlit as st
import hashlib
from src.core.models import BIDSContext

def render_audit_panel(audit_logger, bids_context: BIDSContext, current_file_path: str):
    """
    The 'Action Panel' for the Enterprise Workflow.
    Replaces the old 'Comments' section.
    """
    st.markdown("---")
    st.subheader("✅ Audit Decision")
    
    if not bids_context:
        st.warning("⚠️ No BIDS Context detected. Audit Log will be tagged as 'Unknown'.")
        # Create a dummy context for the button to work
        # In prod, we might block this.
        bids_context = BIDSContext(
            subject_id="unknown_sub",
            modality="unknown", 
            full_path=current_file_path or "unknown"
        )

    # Compute quick hash for the record (Mocking full file hash for speed in UI)
    file_hash = hashlib.sha256(bids_context.full_path.encode()).hexdigest()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ ACCEPT Dataset", type="primary", use_container_width=True):
            try:
                rec = audit_logger.log_decision(
                    user_id=st.session_state.current_user,
                    bids_context=bids_context,
                    file_hash=file_hash,
                    status="ACCEPTED"
                )
                st.success(f"Signed & Logged! ID: {rec.record_id[:8]}")
            except Exception as e:
                st.error(f"Audit Failed: {e}")

    with col2:
        if st.button("❌ REJECT Artifact", type="secondary", use_container_width=True):
            st.session_state.show_reject_form = True

    # Modal-like form for Rejection
    if st.session_state.get('show_reject_form', False):
        with st.form("rejection_form"):
            reason = st.selectbox("Reason", ["Motion Artifact", "Incorrect Parameter", "Signal Dropout", "Other"])
            notes = st.text_area("Specific Notes")
            
            if st.form_submit_button("Confirm Rejection"):
                try:
                    rec = audit_logger.log_decision(
                        user_id=st.session_state.current_user,
                        bids_context=bids_context,
                        file_hash=file_hash,
                        status="REJECTED",
                        flags={"reason": reason, "notes": notes}
                    )
                    st.error(f"Rejection Logged! ID: {rec.record_id[:8]}")
                    st.session_state.show_reject_form = False
                except Exception as e:
                    st.error(f"Audit Failed: {e}")
