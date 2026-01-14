import os
import yaml
from typing import Tuple, Optional, Dict, Any
import numpy as np
from src.adapters.ingestion.factory import DataFactory, AdapterType
from src.core.alignment.engine import DriftModel, ResampledNeuroSource
from src.core.auditing.service import IntegrityAuditor
from src.core.reporting.models import PipelineResult, ComplianceReport, SyncReport, AuditReport
from src.ports.base import NeuroSource
from src.core.provenance import ProvenanceLogger

class NeuroPipeline:
    """
    The Orchestrator & Controller.
    Manages the flow of data through the Gates: Ingestion -> Sync -> Audit -> Diff.
    Enforces Provenance Logging.
    """
    
    def __init__(self, config_path: str = "config/default_policy.yaml"):
        # 1. Init Logger
        self.provenance = ProvenanceLogger()
        self.provenance.log_action("pipeline_init", {"config_path": config_path})
        
        # 2. Load Config
        self.config = self._load_config(config_path)
        
        # 3. Init Auditor
        self.auditor = IntegrityAuditor(self.config)
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads YAML config safely."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Fallback to empty/default if missing (for tests or first run)
            print(f"Warning: Could not load {path}: {e}")
            return {}

    def run(self, path_a: str, path_b: str) -> Tuple[PipelineResult, NeuroSource, NeuroSource]:
        """
        Executes the full pipeline.
        Returns the Report and the Prepared Sources.
        Logs every step to provenance.json sidecar.
        """
        self.provenance.log_action("run_start", {"path_a": path_a, "path_b": path_b})
        
        # Compute Fingerprints (Optimization: Hash before reading fully)
        fp_a = self.provenance.compute_fingerprint(path_a)
        fp_b = self.provenance.compute_fingerprint(path_b)
        self.provenance.log_action("fingerprinting", {"fp_a": fp_a, "fp_b": fp_b})

        # --- PHASE 1: INGESTION ---
        try:
             source_a = DataFactory.load(path_a)
             source_b = DataFactory.load(path_b)
             self.provenance.log_action("ingestion_load", {"type_a": source_a.id, "type_b": source_b.id})
        except Exception as e:
             self.provenance.log_action("ingestion_failed", {"error": str(e)})
             raise e

        # Compliance
        compliance_a = DataFactory.validate_bids_compliance(path_a)
        compliance_b = DataFactory.validate_bids_compliance(path_b)
        
        is_valid = compliance_a.is_valid and compliance_b.is_valid
        warnings = compliance_a.bids_warnings + compliance_b.bids_warnings
        
        compliance_report = ComplianceReport(
            is_valid=is_valid,
            bids_warnings=warnings,
            file_format=f"{compliance_a.file_format}/{compliance_b.file_format}",
            metadata={"meta_a": source_a.get_meta(), "meta_b": source_b.get_meta()}
        )
        self.provenance.log_action("ingestion_compliance", compliance_report.dict())

        # --- PHASE 2: ALIGNMENT (SYNC) ---
        # Drift Model (For MVP Identity)
        drift_model = DriftModel([], []) 
        sync_report = drift_model.get_report()
        self.provenance.log_action("alignment_sync", sync_report.dict())
        
        # --- PHASE 3: AUDIT ---
        audit_report = self.auditor.evaluate(source_a, source_b)
        self.provenance.log_action("audit_evaluation", audit_report.dict())
        
        # --- PHASE 4: PROVENANCE SEALING ---
        # We assume output sidecar is input_path + .provenance.json
        # In a real app, this goes to output_dir
        prov_path = path_a + ".provenance.json"
        
        # If we failed Audit, we might still want to save logs? Yes.
        # But we only save the sidecar if requested. 
        # For this logic, we'll try to save to current dir or next to file
        try:
             self.provenance.save(prov_path)
        except:
             # If validation data dir is read-only, try current dir
             self.provenance.save("session_provenance.json")

        # --- RESULT ---
        result = PipelineResult(
            compliance=compliance_report,
            sync=sync_report,
            audit=audit_report,
            pass_gate= (audit_report.status != "FAIL")
        )
        
        self.provenance.log_action("pipeline_complete", {"pass_gate": result.pass_gate})
        
        return result, source_a, source_b
