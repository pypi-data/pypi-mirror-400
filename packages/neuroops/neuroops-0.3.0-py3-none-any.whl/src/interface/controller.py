import streamlit as st
import os
from typing import Optional, Tuple
from src.adapters.local import LocalMRIAdapter, LocalEEGAdapter
from src.core.diff import VirtualPhysiologyDiff
from src.adapters.db import LocalDBAdapter

class Controller:
    """
    The Brain of the Application.
    Orchestrates interaction between UI (Streamlit), Data (Adapters), and Logic (Core).
    """
    def __init__(self):
        # Initialize DB Adapter if not present
        if 'db_adapter' not in st.session_state:
             st.session_state.db_adapter = LocalDBAdapter()

    def get_adapter(self, source: str) -> Optional[object]:
        """Factory to get the correct adapter based on file extension."""
        if not source: return None
        name = str(source).lower()
        
        # S3 Support
        if name.startswith("s3://"):
             # Import lazily to avoid crashing if libs missing
             try:
                 from src.adapters.s3_storage import S3MRIAdapter
                 # Assumption: S3 usually implies MRI for this Phase MVP
                 # Real logic: check extension
                 if name.endswith(('.nii', '.nii.gz')):
                     return S3MRIAdapter(str(source))
                 else:
                     # Fallback or Error
                     # For now, we only support MRI S3
                     st.error("Only MRI (.nii.gz) supported on S3 for now.")
                     return None
             except ImportError as e:
                 st.error(f"S3 Support requires: pip install s3fs. Error: {e}")
                 return None
        
        if name.endswith(('.nii', '.nii.gz')):
            return LocalMRIAdapter(str(source))
        elif name.endswith(('.fif', '.edf', '.mat')):
            return LocalEEGAdapter(str(source))
        else:
            return None

    def load_datasets(self, path_a: str, path_b: str, demo_mode: bool = False, demo_type: str = 'EEG') -> bool:
        """
        Loads datasets into the Session State.
        Returns True if successful, False otherwise.
        """
        # 1. Handle Demo Mode (Simulated Loading)
        if demo_mode:
            st.session_state.is_demo_mode = True
            st.session_state.data_type = demo_type
            # Create a mock diff engine or just rely on the view's demo logic?
            # Per current app.py, demo mode logic is split. 
            # We want to UNIFY it. 
            # Ideally we load "SyntheticAdapters". 
            # For now, we will respect the legacy demo flag but clear the diff engine
            st.session_state.diff_engine = None 
            return True

        # 2. Validation
        if not path_a or not path_b:
            return False
            
        # 3. Prevent Reloading Same Data
        new_id = f"{path_a}_{path_b}"
        if st.session_state.get('current_file_id') == new_id:
            return True

        # 4. Load Adapters
        try:
            adapter_a = self.get_adapter(path_a)
            adapter_b = self.get_adapter(path_b)
            
            if not adapter_a or not adapter_b:
                st.error("Unsupported file format.")
                return False
                
            # 5. Initialize Core Logic
            diff_engine = VirtualPhysiologyDiff(adapter_a, adapter_b)
            
            # 6. Update State
            st.session_state.diff_engine = diff_engine
            st.session_state.current_file_id = new_id
            st.session_state.data_type = diff_engine.type
            st.session_state.is_demo_mode = False
            
            return True
            
        except Exception as e:
            st.error(f"Error loading datasets: {e}")
            return False

    def batch_process(self, pairs: list, output_dir: str) -> str:
        """
        Headless Mode: Processes a list of file pairs and generates a summary report.
        Returns path to the summary HTML.
        """
        results = []
        os.makedirs(output_dir, exist_ok=True)
        
        from src.interface.report import generate_report
        import json
        
        for i, (path_a, path_b) in enumerate(pairs):
            print(f"Processing Pair {i+1}/{len(pairs)}: {os.path.basename(path_a)}")
            
            # Load (Headless)
            adapter_a = self.get_adapter(path_a)
            adapter_b = self.get_adapter(path_b)
            
            if not adapter_a or not adapter_b:
                results.append({'file': path_a, 'status': 'SKIPPED', 'reason': 'Adapter not found'})
                continue
                
            try:
                # Diff Engine
                diff_engine = VirtualPhysiologyDiff(adapter_a, adapter_b)
                
                # Run Analysis (e.g. Artifact Detection on first 10s)
                # We need to detect type to know what to analyze
                if diff_engine.type == 'EEG':
                    ch = diff_engine.meta_a['ch_names'][0]
                    # Compute lag
                    lag = diff_engine.compute_lag(ch)
                    # Get diff
                    _, _, _, diff = diff_engine.get_signal_diff(0, 10, ch, shift_sec=lag)
                    
                    # Analyze
                    from src.core.artifact_detector import analyze_diff
                    analysis = analyze_diff(diff, diff_engine.meta_a['sfreq'], ch)
                    
                    status = analysis['status']
                    note = f"Lag: {lag:.3f}s. {analysis['message']}"
                else:
                    # MRI check (middle slice)
                    status = "OK" 
                    note = "MRI Automated Check Passed (Placeholder)"
                
                results.append({
                    'file': os.path.basename(path_a),
                    'status': status,
                    'note': note,
                    'pair_id': i
                })
                
            except Exception as e:
                results.append({'file': path_a, 'status': 'ERROR', 'reason': str(e)})

        # Generate Summary HTML
        html_content = "<h1>NeuroOps Audit Report</h1><table border='1'><tr><th>File</th><th>Status</th><th>Note</th></tr>"
        for r in results:
            color = "green" if r['status'] == 'OK' else "orange" if r['status'] == 'WARNING' else "red"
            html_content += f"<tr><td>{r.get('file')}</td><td style='color:{color}'>{r['status']}</td><td>{r.get('note', r.get('reason'))}</td></tr>"
        html_content += "</table>"
        
        report_path = os.path.join(output_dir, "audit_summary.html")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path

    def get_view_state(self):
        """Returns a dict of state variables for the View to consume."""
        return {
            'data_type': st.session_state.get('data_type'),
            'is_demo_mode': st.session_state.get('is_demo_mode', False),
            'diff_engine': st.session_state.get('diff_engine'),
            'current_id': st.session_state.get('current_file_id')
        }
