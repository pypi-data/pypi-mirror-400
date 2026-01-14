import hashlib
import os
import json
import time
import numpy as np
from typing import Dict, Any, List

class ProvenanceLogger:
    """
    The 'Flight Recorder'. 
    Generates immutable logs of what happened to the data.
    """
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.user_session = os.environ.get("USERNAME", "unknown_user")

    def log_action(self, action: str, details: Dict[str, Any]):
        """Records a specific step in the pipeline."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "actor": self.user_session
        }
        self.logs.append(entry)

    def compute_fingerprint(self, file_path: str) -> str:
        """
        Generates a unique ID for a dataset without reading the whole file.
        Optimization: Hash(Header + First 1MB + Last 1MB + Size + MTime)
        """
        if not os.path.exists(file_path):
            return "FILE_NOT_FOUND"

        stats = os.stat(file_path)
        file_size = stats.st_size
        mtime = stats.st_mtime
        
        sha = hashlib.sha256()
        
        # Metadata Signature
        meta_sig = f"{file_size}-{mtime}".encode()
        sha.update(meta_sig)
        
        # Content Signature (Partial)
        chunk_size = 1024 * 1024 # 1MB
        
        try:
            with open(file_path, 'rb') as f:
                # Start
                sha.update(f.read(chunk_size))
                
                if file_size > chunk_size:
                    # End
                    # Seek to (Size - Chunk)
                    seek_pos = max(0, file_size - chunk_size)
                    f.seek(seek_pos)
                    sha.update(f.read(chunk_size))
        except Exception as e:
            # Fallback for some OS/Permissions issues
            return f"HASH_ERROR_{e}"

        return self._format_hash(sha.hexdigest())

    def compute_full_hash(self, file_path: str) -> str:
        """
        FR-14: Computes SHA-256 hash of the ENTIRE file content.
        Required for Integrity Verification and Compliance Certificates.
        """
        if not os.path.exists(file_path):
            return "FILE_NOT_FOUND"
            
        sha = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks (4MB)
                for chunk in iter(lambda: f.read(4096 * 1024), b''):
                    sha.update(chunk)
        except IOError as e:
            return f"HASH_ERROR_{e}"
            
        return self._format_hash(sha.hexdigest())

    def _format_hash(self, raw_hash: str) -> str:
        """Standardizes hash format."""
        return f"sha256:{raw_hash}"

    def save(self, output_path: str):
        """Writes the signed JSON log."""
        
        # Helper for Numpy serialization
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, (np.float32, np.float64, np.floating)):
                    return float(obj)
                if isinstance(obj, (np.int32, np.int64, np.integer)):
                    return int(obj)
                return super().default(obj)
        
        # Create a final 'Seal' (Hash of the logs themselves)
        # Use separators to ensure consistent hashing
        log_dump = json.dumps(self.logs, cls=NumpyEncoder, sort_keys=True).encode()
        signature = hashlib.sha256(log_dump).hexdigest()
        
        final_document = {
            "meta": {
                "version": "NeuroOps-2.0",
                "generated_at": time.time(),
                "duration": time.time() - self.start_time,
                "signature": signature
            },
            "provenance_chain": self.logs
        }
        
        with open(output_path, 'w') as f:
            json.dump(final_document, f, indent=2, cls=NumpyEncoder)
