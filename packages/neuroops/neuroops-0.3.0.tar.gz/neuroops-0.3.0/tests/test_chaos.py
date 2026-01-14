import subprocess
import json
import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_chaos_scenarios():
    print("🧪 Starting Chaos Validation...")
    
    # Load Truth Manifest
    manifest_path = "tests/chaos_data/truth.json"
    if not os.path.exists(manifest_path):
        print("❌ Truth Manifest not found. Run tests/chaos.py first.")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    passed_count = 0
    
    for filename, expected in manifest.items():
        print(f"\n⚡ Testing {filename}...")
        
        # Determine paths
        # Chaos script generated pairs or single files?
        # chaos.py:
        # 1. generate_drifted_eeg -> flatline_sub-02.fif (Single replacement for B?)
        # 2. missing_sidecar -> nosidecar_sub-03.nii
        # 3. mismatch -> sub-04 vs sub-05
        
        # Construct CLI args based on filename patterns
        # We need a valid 'other' file. Use clean base.
        base_a = "tests/chaos_data/clean_sub-01.nii" # or EEG
        base_b = "tests/chaos_data/clean_sub-01.nii"
        
        if "flatline" in filename:
            # EEG
            path_a = "tests/chaos_data/clean_sub-01_eeg.fif" 
            path_b = os.path.join("tests/chaos_data", filename)
        elif "nosidecar" in filename:
            # MRI
            path_a = "tests/chaos_data/clean_sub-01.nii"
            path_b = os.path.join("tests/chaos_data", filename)
        elif "_vs_" in filename:
            # Mismatch pair
            parts = filename.split("_vs_")
            path_a = os.path.join("tests/chaos_data", parts[0])
            path_b = os.path.join("tests/chaos_data", parts[1])
        else:
            print("Unknown file pattern, skipping")
            continue
            
        # Run CLI
        # Capture stderr/stdout
        cmd = [
            sys.executable, "-m", "src.interface.cli",
            "--input_a", path_a,
            "--input_b", path_b,
            "--output_dir", "tests/chaos_output"
        ]
        
        if not os.path.exists("tests/chaos_output"):
            os.makedirs("tests/chaos_output")
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check Exit Code
        expected_status = expected["expected_status"]
        expected_code = 1 if expected_status == "FAIL" else 0
        received_code = result.returncode
        
        # Validation Logic
        success = True
        
        if result.returncode != expected_code:
            # WARN (0) vs FAIL (1)
             if expected_status == "WARN" and result.returncode == 0:
                 pass # OK
             else:
                 print(f"❌ Exit Code Mismatch! Expected {expected_code} ({expected_status}), Got {result.returncode}")
                 print(f"   [CLI OUTPUT START]\n{result.stdout}\n{result.stderr}\n   [CLI OUTPUT END]")
                 success = False
        
        # Check Message Snippet (in stdout or report?)
        combined_output = result.stdout + result.stderr
        snippet = expected["message_snippet"]
        
        if snippet not in combined_output:
             # Fallback: check JSON report
             report_path = os.path.join("tests/chaos_output", "report.json")
             if os.path.exists(report_path):
                 with open(report_path) as f:
                     report = json.load(f)
                 # Scan issues
                 issues_str = str(report)
                 if snippet in issues_str:
                     pass
                 else:
                     print(f"❌ Message Mismatch! Expected '{snippet}' to appear in output/report.")
                     success = False
             else:
                 print(f"❌ Report missing and snippet not found in stdout.")
                 print(f"   [CLI OUTPUT START]\n{result.stdout}\n{result.stderr}\n   [CLI OUTPUT END]")
                 success = False
        
        if success:
            print("✅ Verified Behavior")
            passed_count += 1
            
    print(f"\n🎉 Validation Complete: {passed_count}/{len(manifest)} Scenarios Verified.")

if __name__ == "__main__":
    test_chaos_scenarios()
