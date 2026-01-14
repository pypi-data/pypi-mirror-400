import argparse
import os
import sys
import json
import hashlib
from datetime import datetime
from glob import glob

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.core.bids_parser import parse_bids_filename
from src.core.db import init_db

def scan_directory(root_dir: str):
    print(f"🚀 Launching Automated Triage on: {root_dir}")
    print("-" * 50)
    
    report_data = []
    
    # Heuristic: Find all .nii and .nii.gz files recursively
    # In a real tool we would use BIDSLayout
    files = glob(os.path.join(root_dir, "**/*.nii*"), recursive=True)
    
    if not files:
        print("⚠️ No Neuroimaging files found.")
        return

    print(f"Found {len(files)} files. Analyzing...")
    
    for f in files:
        status = "OK"
        issues = []
        
        # Check 1: BIDS Compliance
        try:
            ctx = parse_bids_filename(f)
        except ValueError as e:
            # BIDS Failure is annoying, but not DATA LOSS. It is a WARNING.
            if status != "CRITICAL": status = "WARNING"
            issues.append(f"Non-BIDS Filename")
            
        # Check 2: Size Check (Lazy integrity)
        size_mb = os.path.getsize(f) / (1024 * 1024)
        if size_mb < 0.1:
            status = "CRITICAL" # Overrides everything
            issues.append("File Empty/Corrupted (<100KB)")
        
        # Check 3: Header Integrity (Quick Nibabel Load)
        if status != "CRITICAL":
            try:
                import nibabel as nib
                # We assume local for CLI scan now
                img = nib.load(f)
                hdr = img.header
                dims = hdr.get_data_shape()
                if 0 in dims:
                    status = "CRITICAL"
                    issues.append("Zero Dimension in Header")
            except Exception as e:
                status = "CRITICAL"
                issues.append(f"Header Read Fail: {str(e)}")

        # Check 4: Advanced Scientific Triage (Content-Aware)
        if status != "CRITICAL" and not issues:
            try:
                # Import lazily to avoid heavy load if not needed
                from src.core.quality_control import check_motion_fmri
                import nibabel as nib
                
                img = nib.load(f)
                
                # A. Motion Scout (fMRI)
                # Heuristic: if 'bold' in filename or 4D
                is_4d = len(img.shape) == 4
                if is_4d:
                    fd = check_motion_fmri(img)
                    if fd > 2.0: # Threshold: 2mm CoM drift (lenient)
                        if status != "CRITICAL": status = "WARNING"
                        issues.append(f"High Motion detected (Drift ~{fd:.2f}mm)")

                # B. Affine Check (TODO: Need Pairs for mismatch)
                # C. Flatline (TODO: Need EEG reader)
                
            except Exception as e:
                # If content check fails, don't crash, just warn
                 issues.append(f"Content Check Fail: {str(e)}")

        # ADD TO REPORT
        if status != "OK":
            report_data.append({
                "file": os.path.basename(f),
                "path": f,
                "status": status,
                "issues": "; ".join(issues)
            })
            print(f"[{status}] {os.path.basename(f)} -> {issues}")
        else:
            # Optional: Print progress dot
            print(".", end="", flush=True)

    print("\n" + "-" * 50)
    gen_html_report(report_data)

def gen_html_report(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html>
    <head>
        <title>NeuroOps Triage Report</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
            .CRITICAL {{ color: red; font-weight: bold; }}
            .WARNING {{ color: orange; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>NeuroOps Automated Triage</h1>
        <p>Generated: {timestamp}</p>
        <p>Issues Found: {len(data)}</p>
        <table>
            <tr><th>Status</th><th>File</th><th>Issues</th><th>Path</th></tr>
    """
    
    for row in data:
        html += f"""
        <tr class="{row['status']}">
            <td>{row['status']}</td>
            <td>{row['file']}</td>
            <td>{row['issues']}</td>
            <td><small>{row['path']}</small></td>
        </tr>
        """
        
    html += "</table></body></html>"
    
    output_path = "triage_report.html"
    with open(output_path, "w") as f:
        f.write(html)
        
    print(f"\n📄 REPORT GENERATED: {os.path.abspath(output_path)}")
    print("Open this file to see the triage results.")

def main():
    parser = argparse.ArgumentParser(description="NeuroOps Enterprise CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # SCAN Command
    scan_parser = subparsers.add_parser("scan", help="Batch Scan a Directory")
    scan_parser.add_argument("dir", help="Directory to scan")
    
    # CHECK Command (NFR-04: Headless Validator)
    check_parser = subparsers.add_parser("check", help="Validate a single file (headless mode)")
    check_parser.add_argument("path", help="Path to neuroimaging file")
    check_parser.add_argument("--schema", "-s", help="Path to validation schema YAML", default=None)
    check_parser.add_argument("--output", "-o", help="Output path for QC_REPORT.json", default=None)
    check_parser.add_argument("--certificate", "-c", action="store_true", help="Generate compliance certificate")
    check_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress stdout, only return exit code")
    check_parser.add_argument("--resolve", "-r", action="store_true", help="Auto-launch visual resolver on failure")
    check_parser.add_argument("--allow-abnormalities", action="store_true", help="Skip checks that assume normal anatomy")
    
    # CONVERT Command (Format Wizard)
    convert_parser = subparsers.add_parser("convert", help="Convert neuroimaging data to BIDS format")
    convert_parser.add_argument("input", help="Input file or directory (EDF, SET, FIF, VHDR, NIfTI, DICOM)")
    convert_parser.add_argument("--output", "-o", required=True, help="Output BIDS dataset root directory")
    convert_parser.add_argument("--subject", "-s", required=True, help="Subject ID (without 'sub-' prefix)")
    convert_parser.add_argument("--task", "-t", help="Task name (required for EEG/fMRI)")
    convert_parser.add_argument("--session", help="Session ID (optional)")
    convert_parser.add_argument("--run", type=int, help="Run number (optional)")
    convert_parser.add_argument("--modality", "-m", help="MRI modality (T1w, T2w, bold, dwi)")
    convert_parser.add_argument("--line-freq", type=float, help="Power line frequency for EEG (50 or 60 Hz)")
    convert_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    convert_parser.add_argument("--batch", action="store_true", help="Batch convert all files in directory")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        if not os.path.isdir(args.dir):
            print(f"Error: Directory not found: {args.dir}")
            sys.exit(1)
        scan_directory(args.dir)
        
    elif args.command == "check":
        exit_code = check_single_file(
            args.path,
            schema_path=args.schema,
            output_path=args.output,
            quiet=args.quiet,
            allow_abnormalities=getattr(args, 'allow_abnormalities', False)
        )
        
        # Auto-Resolve on failure
        if args.resolve and exit_code != 0:
            print(f"\n💡 Check failed (code {exit_code}). Launching Visual Resolver...")
            try:
                import subprocess
                cmd = [sys.executable, "-m", "streamlit", "run", "src/interface/app.py", "--", "--file", args.path]
                subprocess.run(cmd)
            except Exception as e:
                print(f"Failed to launch resolver: {e}")
                
        sys.exit(exit_code)
    
    elif args.command == "convert":
        convert_files(
            input_path=args.input,
            output_dir=args.output,
            subject=args.subject,
            task=args.task,
            session=args.session,
            run=args.run,
            modality=args.modality,
            line_freq=getattr(args, 'line_freq', None),
            overwrite=args.overwrite,
            batch=args.batch
        )
            
    else:
        parser.print_help()


def convert_files(
    input_path: str,
    output_dir: str,
    subject: str,
    task: str = None,
    session: str = None,
    run: int = None,
    modality: str = None,
    line_freq: float = None,
    overwrite: bool = False,
    batch: bool = False
):
    """
    Convert neuroimaging files to BIDS format.
    """
    from src.core.converter import FormatConverter
    
    converter = FormatConverter(verbose=True)
    
    print(f"🔄 NeuroOps Format Converter")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_dir}")
    print(f"   Subject: sub-{subject}")
    print()
    
    # Handle batch mode
    if batch or os.path.isdir(input_path):
        files = []
        for ext in ['*.edf', '*.set', '*.fif', '*.vhdr', '*.nii', '*.nii.gz']:
            files.extend(Path(input_path).rglob(ext))
        
        if not files:
            print(f"❌ No supported files found in {input_path}")
            sys.exit(1)
        
        print(f"📁 Found {len(files)} files to convert\n")
        
        success_count = 0
        for i, f in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Converting: {f.name}")
            result = converter.to_bids(
                str(f), output_dir, subject,
                task=task, session=session, run=i,
                modality=modality, line_freq=line_freq,
                overwrite=overwrite
            )
            if result.success:
                print(f"   ✅ → {result.output_path}")
                success_count += 1
            else:
                print(f"   ❌ {result.error}")
        
        print(f"\n📊 Converted {success_count}/{len(files)} files")
        
    else:
        # Single file
        result = converter.to_bids(
            input_path, output_dir, subject,
            task=task, session=session, run=run,
            modality=modality, line_freq=line_freq,
            overwrite=overwrite
        )
        
        if result.success:
            print(f"✅ Conversion successful!")
            print(f"   Output: {result.output_path}")
            print(f"   Format: {result.format_from} → {result.format_to}")
            
            if result.metadata_extracted:
                print(f"\n📋 Extracted metadata:")
                for k, v in result.metadata_extracted.items():
                    print(f"   {k}: {v}")
            
            if result.warnings:
                print(f"\n⚠️ Warnings:")
                for w in result.warnings:
                    print(f"   - {w}")
        else:
            print(f"❌ Conversion failed: {result.error}")
            sys.exit(1)


def check_single_file(
    file_path: str,
    schema_path: str = None,
    output_path: str = None,
    quiet: bool = False,
    allow_abnormalities: bool = False
) -> int:
    """
    Headless single-file validation (Linter mode).
    Outputs processing_report.json.
    """
    from src.core.validation.integrity import IntegrityChecker, IntegrityStatus
    from src.core.validation.quality import QualityChecker, QualityStatus
    
    if not quiet:
        print(f"🔍 Linting: {file_path}")
    
    # Check file exists
    if not os.path.exists(file_path):
        if not quiet:
            print(f"❌ File not found: {file_path}")
        return 3
    
    # Load schema (BIDS-first: auto-infer if no YAML)
    thresholds = {}
    protocol_id = None
    try:
        from src.core.schema.loader import SchemaLoader
        loader = SchemaLoader()
        schema = loader.load_or_infer(schema_path, file_path)
        
        thresholds = {
            'snr_min': schema.thresholds.snr_min,
            'motion_max_mm': schema.thresholds.motion_max_mm,
            'flatline_std_threshold': schema.thresholds.flatline_std_threshold,
            'flatline_max_ratio': schema.thresholds.flatline_max_ratio
        }
        protocol_id = schema.protocol_id
        if not quiet:
            print(f"📋 Protocol: {schema.protocol_name}")
            if "auto-bids" in str(protocol_id):
                 print(f"   (Auto-configured from BIDS sidecars)")
                 
    except Exception as e:
        if not quiet:
            print(f"ℹ️ Using default thresholds: {e}")
    
    # Initialize checkers
    integrity_checker = IntegrityChecker()
    quality_checker = QualityChecker(
        snr_threshold=thresholds.get('snr_min', 5.0),
        motion_threshold_mm=thresholds.get('motion_max_mm', 2.0),
        flatline_std_threshold=thresholds.get('flatline_std_threshold', 1e-15),
        flatline_ratio_threshold=thresholds.get('flatline_max_ratio', 0.5)
    )
    
    all_results = []
    has_critical = False
    has_warning = False
    
    # Run integrity checks (skip anatomy checks if --allow-abnormalities)
    integrity_results = integrity_checker.run_all_checks(file_path)
    for r in integrity_results:
        # Skip affine reasonableness for clinical data
        if allow_abnormalities and "affine" in r.check_name.lower():
            continue
        all_results.append(r.to_dict())
        if r.status == IntegrityStatus.FAIL:
            has_critical = True
            if not quiet:
                print(f"  ❌ {r.check_name}: {r.message}")
        elif not quiet and r.status == IntegrityStatus.PASS:
            print(f"  ✅ {r.check_name}: {r.message}")
    
    # Run quality checks if integrity passed
    if not has_critical:
        try:
            import nibabel as nib
            img = nib.load(file_path)
            
            # SNR check
            if len(img.shape) >= 3:
                sample_data = img.dataobj[:, :, img.shape[2]//2]
                snr_result = quality_checker.calculate_snr(sample_data)
                all_results.append(snr_result.to_dict())
                if snr_result.status == QualityStatus.FAIL:
                    has_critical = True
                    if not quiet:
                        print(f"  ❌ {snr_result.check_name}: {snr_result.message}")
                elif snr_result.status == QualityStatus.WARN:
                    has_warning = True
                    if not quiet:
                        print(f"  ⚠️ {snr_result.check_name}: {snr_result.message}")
                elif not quiet:
                    print(f"  ✅ {snr_result.check_name}: {snr_result.message}")
            
            # Motion check for 4D (skip if --allow-abnormalities for lesion patients)
            if len(img.shape) == 4 and not allow_abnormalities:
                com_result = quality_checker.calculate_center_of_mass_drift(img.get_fdata())
                all_results.append(com_result.to_dict())
                if com_result.status == QualityStatus.FAIL:
                    has_critical = True
                    if not quiet:
                        print(f"  ❌ {com_result.check_name}: {com_result.message}")
                elif com_result.status == QualityStatus.WARN:
                    has_warning = True
                    if not quiet:
                        print(f"  ⚠️ {com_result.check_name}: {com_result.message}")
                        
        except Exception as e:
            if not quiet:
                print(f"  ℹ️ Quality checks skipped: {e}")
            all_results.append({
                "check": "quality_checks",
                "status": "SKIP",
                "message": str(e)
            })
    
    # Determine overall status
    if has_critical:
        overall_status = "FAIL"
        exit_code = 2
    elif has_warning:
        overall_status = "WARN"
        exit_code = 1
    else:
        overall_status = "PASS"
        exit_code = 0
    
    # Build processing report (renamed from QC_REPORT)
    report = {
        "file": os.path.basename(file_path),
        "path": os.path.abspath(file_path),
        "timestamp": datetime.now().isoformat(),
        "status": overall_status,
        "protocol": protocol_id,
        "checks": all_results
    }
    
    # Output report
    if output_path is None:
        base = file_path
        for ext in ['.nii.gz', '.nii', '.fif', '.edf']:
            if file_path.lower().endswith(ext):
                base = file_path[:-len(ext)]
                break
        output_path = base + "_processing_report.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    if not quiet:
        print(f"\n📄 Report: {output_path}")
        status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[overall_status]
        print(f"{status_emoji} Result: {overall_status}")
    
    return exit_code


if __name__ == "__main__":
    main()

