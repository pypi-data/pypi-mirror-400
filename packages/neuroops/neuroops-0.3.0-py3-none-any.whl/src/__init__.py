import os
import subprocess
import sys
import tempfile
import inspect
import socket
from src.core.logger import logger

def diff(raw, clean):
    """
    The 'Trojan Horse' / 'Magic Line' function.
    Launches the NeuroOps Streamlit app to visualize the diff between two MNE objects.
    
    Usage:
        import neuroops
        neuroops.diff(raw_v1, raw_v2)
    """
    logger.info("Initializing neuroops.diff() visualization request.")
    
    # 1. Create a temp directory for exchange
    home = os.path.expanduser("~")
    cache_dir = os.path.join(home, ".neuroops", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    path_a = os.path.join(cache_dir, "temp_a_raw.fif")
    path_b = os.path.join(cache_dir, "temp_b_raw.fif")
    
    # 2. Save objects (Assuming MNE Raw for now)
    try:
        raw.save(path_a, overwrite=True)
        clean.save(path_b, overwrite=True)
    except Exception as e:
        logger.error(f"Error saving temp files: {e}")
        print(f"❌ Error: {e}") # Print error to user as feedback
        return

    # 3. Locate the Streamlit App
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    app_path = os.path.join(src_dir, "interface", "app.py")
    
    if not os.path.exists(app_path):
        logger.critical(f"Could not find app.py at {app_path}")
        return

    # 4. Smart Launch Logic (Fix 1: Prevent Zombies)
    # Check if port 8501 is already in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    
    if result == 0:
        # Port is open (Server is running)
        logger.info("Port 8501 busy. Assuming hot-reload.")
        print("🔄 NeuroOps data updated. check your browser tab.")
        return
    else:
        # Port is closed (No server)
        logger.info("Launching new Streamlit instance.")
        print("🚀 Opening NeuroOps Interface...")
        
        env = os.environ.copy()
        env["NEUROOPS_AUTO_LOAD_A"] = path_a
        env["NEUROOPS_AUTO_LOAD_B"] = path_b
        
        cmd = [sys.executable, "-m", "streamlit", "run", app_path]
        
        # Run non-blocking and SILENTLY (Eng 3)
        subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
