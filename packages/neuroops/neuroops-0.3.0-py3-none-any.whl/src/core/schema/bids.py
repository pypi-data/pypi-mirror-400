"""
Module G: Zero-Config BIDS Interpreter (FR-19)

Automatically infers validation constraints from BIDS JSON sidecars.
Eliminates the need for manual YAML configuration in standard labs.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from .loader import ProtocolSchema, FileConstraints, ValidationThresholds

logger = logging.getLogger(__name__)

class BIDSInterpreter:
    """
    Interprets BIDS metadata to generate on-the-fly ProtocolSchemas.
    """
    
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir
        
    def detect_bids_root(self, file_path: str) -> Optional[str]:
        """Walks up directory tree looking for dataset_description.json"""
        current = os.path.dirname(os.path.abspath(file_path))
        while True:
            if os.path.exists(os.path.join(current, "dataset_description.json")):
                return current
            parent = os.path.dirname(current)
            if parent == current: # Root reached
                return None
            current = parent

    def infer_schema_for_file(self, file_path: str) -> ProtocolSchema:
        """
        Generates a ProtocolSchema specifically tailored to the given file
        based on its associated BIDS sidecars.
        """
        name = os.path.basename(file_path)
        constraints = FileConstraints(pattern=name)
        thresholds = ValidationThresholds()
        
        # 1. Find and parse Sidecar JSON
        # BIDS Inheritance Principle: 
        # Look for [file].json, then [modality].json in current dir, then in parent...
        # For MVP, we just look for the direct sidecar or simple inheritance.
        
        sidecar_data = self._merge_sidecars(file_path)
        
        if not sidecar_data:
            logger.info("No BIDS sidecars found. Using default schema.")
            return ProtocolSchema(
                protocol_id="auto-bids-default",
                files=[constraints],
                thresholds=thresholds
            )
            
        # 2. Map Sidecar Fields to Constraints
        
        # RepetitionTime (TR)
        if "RepetitionTime" in sidecar_data:
            tr = float(sidecar_data["RepetitionTime"])
            # Strict check: TR must match exactly (with small tolerance)
            # Or maybe we allow variance? Usually TR is constant.
            # We can't specify exact value in range easily without "range"
            # let's assume constraints supports min/max or exact
            pass # FileConstraints model update needed if we want specific value checks?
            # Actually, SchemaEngine v1 usually had min_size_mb, etc.
            # Let's see what FileConstraints supports.
            
            # FileConstraints in models.py:
            # required_dim: List[int]
            # min_size_mb: float
            # allowed_extensions: List[str]
            # required_header_tags: Dict[str, Any] <-- THIS IS IT
            
            if constraints.required_header_values is None:
                constraints.required_header_values = {}
                
            constraints.required_header_values["RepetitionTime"] = tr

        # EchoTime
        if "EchoTime" in sidecar_data:
             if constraints.required_header_values is None: constraints.required_header_values = {}
             constraints.required_header_values["EchoTime"] = float(sidecar_data["EchoTime"])

        # Manufacturer
        if "Manufacturer" in sidecar_data:
             if constraints.required_header_values is None: constraints.required_header_values = {}
             constraints.required_header_values["Manufacturer"] = sidecar_data["Manufacturer"]

        # 3. Create Schema
        return ProtocolSchema(
            protocol_id=f"auto-bids-{os.path.basename(file_path)}",
            description="Auto-generated from BIDS sidecars",
            file_constraints=constraints,
            thresholds=thresholds
        )

    def _merge_sidecars(self, file_path: str) -> Dict[str, Any]:
        """
        Tries to load associated JSON.
        Simple logic: just look for file.json.
        """
        # Logic matches DataFactory.validate_bids_compliance
        base = file_path
        for ext in ['.nii.gz', '.nii', '.fif', '.edf', '.vhdr', '.mat']:
            if file_path.lower().endswith(ext):
                base = file_path[:-len(ext)]
                break
        
        json_path = base + ".json"
        
        if os.path.exists(json_path):
            print(f"DEBUG: Found sidecar at {json_path}")
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    print(f"DEBUG: Loaded data: {data}")
                    return data
            except Exception as e:
                print(f"DEBUG: Failed to load JSON: {e}")
                return {}
        else:
            print(f"DEBUG: Sidecar not found at {json_path}")
        return {}
