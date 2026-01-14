import streamlit as st
import io
import base64
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- IMPORTS ---
from src.interface import state
from src.interface.file_selector import open_file_dialog
from src.interface.components.audit_panel import render_audit_panel # NEW
from src.core.bids_helper import validate_bids_filename
from src.core.bids_parser import parse_bids_filename 
from src.interface.report import generate_report
from src.core.provenance import ProvenanceLogger 
from src.interface.pdf_export import generate_citation, generate_methods_section
from src.core.artifact_detector import analyze_diff 
import json

# --- LOGGING ---
from src.core.provenance import ProvenanceLogger
from src.core.audit import AuditLogger
from src.adapters.ingestion.factory import DataFactory
import gc

# --- PAGE CONFIG ---
st.set_page_config(page_title="NeuroOps Linter", layout="wide", page_icon="🧠")

# --- INITIALIZATION ---
state.init_session_state()
controller = st.session_state.controller

# Logging Components
if "audit_logger" not in st.session_state:
    st.session_state.audit_logger = AuditLogger()
if "prov_logger" not in st.session_state:
    st.session_state.prov_logger = ProvenanceLogger()

audit_logger = st.session_state.audit_logger
prov_logger = st.session_state.prov_logger

# --- DEMO MODE AUTO-LOAD ---
if os.environ.get('NEUROOPS_DEMO_MODE') == '1' and not st.session_state.get('demo_loaded', False):
    demo_eeg_raw = os.environ.get('NEUROOPS_DEMO_EEG_RAW')
    demo_mri_raw = os.environ.get('NEUROOPS_DEMO_MRI_RAW')
    if demo_eeg_raw:
        st.session_state.demo_mode_type = 'EEG'
    if demo_mri_raw:
        st.session_state.demo_mode_type = 'MRI'
    st.session_state.demo_loaded = True

# --- HELPER: PLOTTING ---
def handle_report_export(context, fig_factory):
    """Renders the Report Dialog in Sidebar and handles export"""
    if st.session_state.get("show_report_dialog", False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("#### 🔬 Report Settings")
        notes = st.sidebar.text_area("Findings / Notes for PI", height=100)
        
        if st.sidebar.button("Prepare Report"):
            with st.spinner("Rendering static plot..."):
                fig = fig_factory()
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                plt.close(fig)
                buf.seek(0)
                plot_b64 = base64.b64encode(buf.read()).decode()
            
            html = generate_report(st.session_state.current_file_id, context, notes, plot_base64=plot_b64)
            st.sidebar.download_button("💾 Download HTML Report", data=html, file_name=f"QC_Report_{st.session_state.current_file_id}.html", mime="text/html")

def plot_signals(time_vec, sig_a, sig_b, diff_sig, title_prefix="Channel"):
    """Helper to draw the EEG Plotly chart"""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=(f"{title_prefix} (Raw)", f"{title_prefix} (Clean)", "Diff"))
    fig.add_trace(go.Scatter(x=time_vec, y=sig_a, name="Raw", line=dict(color='gray', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=time_vec, y=sig_b, name="Clean", line=dict(color='#2ecc71', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=time_vec, y=diff_sig, name="Diff", line=dict(color='#e74c3c', width=1)), row=3, col=1)
    fig.update_layout(height=600, showlegend=False)
    return fig

def plot_psd(freqs, psd_a, psd_b):
    """Helper to draw the PSD Plotly chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs, y=psd_a, name="Raw PSD", line=dict(color='gray', width=1)))
    fig.add_trace(go.Scatter(x=freqs, y=psd_b, name="Clean PSD", line=dict(color='#2ecc71', width=1)))
    fig.update_layout(title="Power Spectral Density (Welch)", xaxis_title="Frequency (Hz)", yaxis_title="Power (uV^2/Hz)", yaxis_type="log", xaxis_type="log", height=500)
    return fig

def normalize_img(data):
    """Visual helper for MRI slices"""
    d_min, d_max = data.min(), data.max()
    if d_max == d_min: return data
    return (data - d_min) / (d_max - d_min)

# ==========================================
# 1. SIDEBAR: ENTERPRISE NAVIGATION
# ==========================================
with st.sidebar:
    st.header("NeuroOps Enterprise 🛡️")
    st.caption(f"Logged in as: {st.session_state.current_user}")
    
    app_mode = st.selectbox("Pipeline Stage", ["Audit Workbench (Local)", "Cloud Review (S3)", "BIDS Compliance"])

    st.markdown("---")

    # --- MODE: LOCAL ---
    if app_mode == "Audit Workbench (Local)":
        st.info("Local High-Performance Mode")
        if "local_path_a" not in st.session_state: st.session_state.local_path_a = r"C:\Data\sub-01_raw.nii.gz"
        if "local_path_b" not in st.session_state: st.session_state.local_path_b = r"C:\Data\sub-01_clean.nii.gz"

        st.markdown("**Path A (Raw)**")
        c1, c2 = st.columns([6, 1])
        def update_path_a():
            selected = open_file_dialog()
            if selected: st.session_state.local_path_a = selected
        with c2: st.button("📂", key="browse_a", on_click=update_path_a)
        with c1: path_a = st.text_input("Path A", label_visibility="collapsed", key="local_path_a")

        st.markdown("**Path B (Processed)**")
        c3, c4 = st.columns([6, 1])
        def update_path_b():
            selected = open_file_dialog()
            if selected: st.session_state.local_path_b = selected
        with c4: st.button("📂", key="browse_b", on_click=update_path_b)
        with c3: path_b = st.text_input("Path B", label_visibility="collapsed", key="local_path_b")
        
        if st.button("Load & Audit", type="primary"):
            if os.path.exists(path_a) and os.path.exists(path_b):
                
                # --- FR-16: Memory Wipe ---
                if "data_source_a" in st.session_state:
                    st.session_state["data_source_a"] = None
                    gc.collect()
                
                # --- Log Load Attempt ---
                with st.spinner("Preparing..."):
                    try:
                        file_hash = prov_logger.compute_full_hash(path_a)
                        audit_logger.log_event("LOAD_ATTEMPT", file_hash, {"path_a": path_a})
                    except Exception as e:
                        st.warning(f"Could not compute file hash: {e}")

                with st.spinner("Loading Datasets..."):
                    try:
                        # FR-13: PII Kill Switch happens inside DataFactory load
                        success = controller.load_datasets(path_a, path_b)
                        if success:
                            audit_logger.log_event("LOAD_SUCCESS", file_hash)
                            try:
                                 # Try to context-switch
                                 st.session_state.bids_context = parse_bids_filename(path_a)
                            except:
                                 st.session_state.bids_context = None
                    except ValueError as ve:
                        # Catch PII Rejection
                        if "SECURITY ALERT" in str(ve):
                            st.error(str(ve))
                            audit_logger.log_event("PII_REJECTION", "unknown", {"error": str(ve)})
                        else:
                            st.error(str(ve))
                            audit_logger.log_event("LOAD_FAIL", "unknown", {"error": str(ve)})

            else:
                st.error("Files not found.")

    # --- MODE: S3 ---
    elif app_mode == "Cloud Review (S3)":
        st.info("Lazy Loading from AWS S3 (Requires boto3)")
        path_a = st.text_input("S3 URI A", value="s3://my-bucket/sub-01_raw.nii.gz")
        path_b = st.text_input("S3 URI B", value="s3://my-bucket/sub-01_clean.nii.gz")
        if st.button("Stream Data"):
            st.warning("Ensure AWS credentials are set in environment.")

    # --- MODE: BIDS ---
    elif app_mode == "BIDS Compliance":
        st.info("BIDS Validator")
        bids_file = st.file_uploader("Check File Compliance")
        if bids_file:
            is_valid, issues, fix = validate_bids_filename(bids_file.name)
            if is_valid: st.success("✅ Valid BIDS")
            else: st.error(f"❌ Invalid: {issues}")

# ==========================================
# 2. MAIN VIEW CONTROLLER
# ==========================================

# --- FR-09: Context-Aware Launch ---
# Check for query params to focus on specific artifacts
query_params = st.query_params
focus_slice = None
focus_time = None

if "focus" in query_params:
    focus_val = query_params["focus"]
    if focus_val.startswith("slice:"):
        focus_slice = int(focus_val.split(":")[1])
    elif focus_val.startswith("time:"):
        focus_time = float(focus_val.split(":")[1])

view_state = controller.get_view_state()
diff_engine = view_state['diff_engine']

if diff_engine:
    # --- B1. MRI VIEWER ---
    if view_state['data_type'] == 'MRI':
        st.subheader("🧠 Volumetric Audit")
        
        meta = diff_engine.meta_a
        plane = st.radio("Plane", ["Axial", "Coronal", "Sagittal"], horizontal=True)
        axis_map = {"Sagittal": 0, "Coronal": 1, "Axial": 2}
        axis_idx = axis_map[plane]
        max_slice = meta['shape'][axis_idx] - 1
        
        # FR-09: Start at focused slice if available
        default_slice = focus_slice if focus_slice is not None and focus_slice <= max_slice else max_slice // 2
        slice_idx = st.slider("Slice Depth", 0, max_slice, default_slice)
        
        # JIT Fetch
        s_diff, s_a, s_b = diff_engine.get_slice_diff(axis_idx, slice_idx, normalize=True)

        # RENDER
        c1, c2, c3 = st.columns(3)
        with c1: st.image(normalize_img(s_a), caption="Raw", clamp=True, channels='GRAY', use_container_width=True)
        with c2: st.image(normalize_img(s_b), caption="Processed", clamp=True, channels='GRAY', use_container_width=True)
        with c3:
            fig, ax = plt.subplots(figsize=(3,3))
            limit = np.max(np.abs(s_diff)) * 0.5 if np.max(np.abs(s_diff)) > 0 else 1.0 # Dynamic contrast
            ax.imshow(s_diff, cmap='RdBu', aspect='equal', vmin=-limit, vmax=limit)
            ax.axis('off')
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            
        # --- NEW AUDIT PANEL ---
        render_audit_panel(st.session_state.audit_logger, st.session_state.bids_context, getattr(diff_engine.source_a, 'path', '?'))

    # --- B2. EEG VIEWER ---
    elif view_state['data_type'] == 'EEG':
        st.subheader("📈 Signal Integrity")
        
        meta = diff_engine.meta_a
        selected_ch = st.selectbox("Select Channel", sorted(meta['ch_names']))
        duration = meta['duration']
        
        # FR-09: Start at focused time if available
        default_time = focus_time if focus_time is not None and focus_time <= duration else 0.0
        start_time = st.slider("Window Start (s)", 0.0, float(duration - 5.0), float(default_time))
        
        # JIT Fetch
        times, sig_a, sig_b, diff = diff_engine.get_signal_diff(start_time, 10.0, selected_ch)
        
        fig = plot_signals(times, sig_a, sig_b, diff, selected_ch)
        st.plotly_chart(fig, use_container_width=True)
        
        # --- FR-11: Butterfly Plot ---
        with st.expander("🦋 Butterfly Plot (Global View)", expanded=False):
            if st.button("Generate Butterfly Plot"):
                with st.spinner("Rendering Butterfly Plot..."):
                    # Load full data window
                    start_idx = int(start_time * meta['sfreq'])
                    end_idx = start_idx + int(10.0 * meta['sfreq'])
                    
                    # We need access to all channels. 
                    # diff_engine.get_signal_diff only returns ONE channel.
                    # We need a new method or use raw data access if available.
                    # diff_engine.source_a is the adapter.
                    
                    try:
                        # Fetch data matrix (n_channels, n_samples)
                        # Adapters (LocalEEGAdapter) should support get_slice or similar?
                        # Using get_slice implies MRI usually.
                        # For EEG, get_signal(start, duration, channel) is standard in base.py?
                        # Implementation of LocalEEGAdapter needs check.
                        # Assuming we can get all channels loop or batch?
                        # For MVP, let's just plot the 5 loaded channels if cache or 10 random?
                        # Or implement 'get_data(start, duration)' in adapter.
                        
                        # Let's rely on diff_engine having access.
                        # Actually, diff_engine.source_a.get_data(start, end)?
                        
                        bf_fig = go.Figure()
                        
                        # Heuristic: Plot first 10 channels + Bad channels
                        # Ideally all 64+. Plotly handles it but sluggish if too many points.
                        
                        channels_to_plot = meta['ch_names'][:20] # Top 20
                        # Add bad channels from info if available?
                        
                        common_times = None
                        
                        for ch in channels_to_plot:
                            t, s_a, _, _ = diff_engine.get_signal_diff(start_time, 10.0, ch)
                            if common_times is None: common_times = t
                            bf_fig.add_trace(go.Scatter(
                                x=t, y=s_a, mode='lines', name=ch,
                                line=dict(color='gray', width=0.5), opacity=0.5,
                                hoverinfo='name+y'
                            ))
                            
                        # Highlight bad channels (mock logic or real if we track them in session)
                        # For now just standard view.
                        
                        bf_fig.update_layout(
                            title="Butterfly Plot (First 20 Channels)",
                            xaxis_title="Time (s)",
                            yaxis_title="Amplitude (uV)",
                            showlegend=False,
                            height=500
                        )
                        st.plotly_chart(bf_fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Could not generate Butterfly Plot: {e}")
        
        # --- FR-12: Remediation Actions ---
        st.markdown("### 🛠️ Remediation")
        r_col1, r_col2 = st.columns(2)
        
        with r_col1:
            st.markdown("**Crop Time Segment**")
            crop_start = st.number_input("Start (s)", min_value=0.0, max_value=duration, value=start_time)
            crop_end = st.number_input("End (s)", min_value=0.0, max_value=duration, value=min(start_time + 10.0, duration))
            if st.button("✂️ Crop Segment"):
                try:
                    from src.core.remediation import RemediationService
                    service = RemediationService()
                    # Determine which file to crop (usually raw path A)
                    src_path = getattr(diff_engine.source_a, 'path', None)
                    if src_path:
                        out_path, _ = service.crop_time_segment(src_path, crop_start, crop_end, keep=False)
                        st.success(f"Created cropped version: {os.path.basename(out_path)}")
                    else:
                        st.error("Cannot determine source file path")
                except Exception as e:
                    st.error(f"Remediation failed: {e}")

        with r_col2:
            st.markdown("**Exclude Channels**")
            exclude_chs = st.multiselect("Channels to Exclude", sorted(meta['ch_names']))
            if st.button("🚫 Exclude Selected"):
                try:
                    from src.core.remediation import RemediationService
                    service = RemediationService()
                    src_path = getattr(diff_engine.source_a, 'path', None)
                    if src_path:
                        out_path, _ = service.exclude_channels(src_path, exclude_chs)
                        st.success(f"Created clean version: {os.path.basename(out_path)}")
                    else:
                        st.error("Cannot determine source file path")
                except Exception as e:
                    st.error(f"Remediation failed: {e}")
        
        # --- NEW AUDIT PANEL ---
        render_audit_panel(st.session_state.audit_logger, st.session_state.bids_context, getattr(diff_engine.source_a, 'path', '?'))

else:
    st.markdown("## 👋 Welcome to NeuroOps Enterprise")
    st.markdown("Please load a dataset from the sidebar to begin audit.")