import streamlit as st
from datetime import datetime

def render_comment_panel(db_adapter, file_id, current_context):
    """
    Renders the collaboration sidebar.
    
    Args:
        db_adapter: Instance of LocalDBAdapter
        file_id: Unique ID of the current file pair
        current_context: Dict containing current view state (e.g. {'slice': 50})
    """
    st.markdown("### 💬 Collaboration")
    
    # --- Peer Review Section ---
    current_status = db_adapter.get_review_status(file_id)
    
    # Status Badge
    status_color = {
        "Pending": "gray",
        "Approved": "green",
        "Changes Requested": "red"
    }.get(current_status, "gray")
    
    st.markdown(f"**Status:** :{status_color}[{current_status}]")
    
    # Review Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve", use_container_width=True):
            db_adapter.set_review_status(file_id, "Approved")
            st.rerun()
    with col2:
        if st.button("⚠️ Request Changes", use_container_width=True):
            db_adapter.set_review_status(file_id, "Changes Requested")
            st.rerun()
            
    st.markdown("---")

    # 1. Add New Comment
    with st.form(key=f"new_comment_form_{file_id}"):
        # Persist user name across re-renders/file switches
        default_user = st.session_state.get('global_user_name', 'Researcher')
        
        user = st.text_input("Your Name", value=default_user, key=f"comment_user_{file_id}")
        text = st.text_area("Leave a comment...", placeholder="e.g., Artifact at slice 50 due to motion.")
        
        # Show what context will be saved
        st.caption(f"Saving Context: {current_context}")
        
        submitted = st.form_submit_button("Post Comment")
        if submitted and text:
            # Save user name preference
            st.session_state.global_user_name = user
            
            db_adapter.add_comment(file_id, text, current_context, user)
            st.success("Comment posted!")
            st.rerun()

    # 2. List Comments
    comments = db_adapter.get_comments(file_id)
    
    if not comments:
        st.info("No comments yet. Be the first!")
    else:
        st.markdown("---")
        for c in comments:
            with st.container():
                # Header: User + Time
                t_str = datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M %d/%m')
                st.markdown(f"**{c['user']}** <span style='color:gray; font-size:0.8em'>({t_str})</span>", unsafe_allow_html=True)
                
                # Context Badge (Clickable logic would go here in future)
                ctx = c['context']
                if ctx:
                    badges = " ".join([f"`{k}:{v}`" for k,v in ctx.items()])
                    st.markdown(f"{badges}")
                
                # Body
                st.write(c['comment'])
                st.markdown("---")
