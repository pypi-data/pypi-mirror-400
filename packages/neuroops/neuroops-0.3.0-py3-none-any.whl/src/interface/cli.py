import argparse
import sys
import json
import os
from src.core.pipeline import NeuroPipeline

def main():
    parser = argparse.ArgumentParser(description="NeuroOps Headless Pipeline")
    parser.add_argument("--input_a", required=True, help="Path to Reference File (Source A)")
    parser.add_argument("--input_b", required=True, help="Path to Target File (Source B)")
    parser.add_argument("--config", default="config/default_policy.yaml", help="Path to Policy YAML")
    parser.add_argument("--output_dir", default=".", help="Directory to save Report and Provenance")
    
    args = parser.parse_args()
    
    # 1. Pipeline Initialization
    print(f"[INIT] Starting NeuroOps Pipeline...")
    print(f"       Config: {args.config}")
    
    try:
        pipeline = NeuroPipeline(config_path=args.config)
        
        # 2. Execution
        result, _, _ = pipeline.run(args.input_a, args.input_b)
        
        # 3. Output Handling
        # Save Report
        report_path = os.path.join(args.output_dir, "report.json")
        with open(report_path, 'w') as f:
            f.write(result.model_dump_json(indent=2))
        print(f"[REPORT] Saved to: {report_path}")
        
        # Note: Provenance is saved internally by pipeline.run(), usually to sidecar.
        # We might want to pass output path to run() for explicit control.
        # For MVP, pipeline handles it.
        
        # 4. Exit Code Logic
        if result.audit.status == "FAIL":
            print("[FAIL] Pipeline FAILED Verification.")
            sys.exit(1)
        elif result.audit.status == "WARN":
            print("[WARN] Pipeline Passed with WARNINGS.")
            sys.exit(0)
        else:
            print("[PASS] Pipeline PASSED.")
            sys.exit(0)
            
    except Exception as e:
        print(f"[CRITICAL] Error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
