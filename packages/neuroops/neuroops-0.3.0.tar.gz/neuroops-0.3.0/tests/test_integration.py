"""
Quick Integration Test for Demo Mode and Export Features

Run this to verify all features work end-to-end.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_demo_data():
    """Test demo data generation."""
    print("=" * 60)
    print("TEST 1: Demo Data Generation")
    print("=" * 60)
    
    from src.core.demo_data import load_demo_data
    
    try:
        paths = load_demo_data()
        print("✅ Demo data loaded successfully")
        print(f"   EEG Raw: {Path(paths['eeg_raw']).exists()}")
        print(f"   EEG Clean: {Path(paths['eeg_clean']).exists()}")
        print(f"   MRI Raw: {Path(paths['mri_raw']).exists()}")
        print(f"   MRI Clean: {Path(paths['mri_clean']).exists()}")
        return True
    except Exception as e:
        print(f"❌ Demo data failed: {e}")
        return False

def test_citations():
    """Test citation generation."""
    print("\n" + "=" * 60)
    print("TEST 2: Citation Generation")
    print("=" * 60)
    
    from src.interface.pdf_export import generate_citation, generate_methods_section
    
    try:
        # Test APA
        apa = generate_citation('apa')
        print(f"✅ APA Citation:\n   {apa}\n")
        
        # Test BibTeX
        bibtex = generate_citation('bibtex')
        print(f"✅ BibTeX Citation:\n{bibtex}\n")
        
        # Test Methods
        methods = generate_methods_section('EEG', preprocessing_steps=['bandpass 1-40 Hz'])
        print(f"✅ Methods Section:\n   {methods[:100]}...\n")
        
        return True
    except Exception as e:
        print(f"❌ Citation generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_export():
    """Test PDF export."""
    print("\n" + "=" * 60)
    print("TEST 3: PDF Export")
    print("=" * 60)
    
    try:
        import matplotlib.pyplot as plt
        from src.interface.pdf_export import export_to_pdf, export_to_html
        import tempfile
        
        # Create test figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title("Test QC Plot")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test PDF
            pdf_path = Path(tmpdir) / "test.pdf"
            export_to_pdf(
                fig,
                str(pdf_path),
                "Integration Test Report",
                {'test': 'data'},
                notes="This is a test"
            )
            
            if pdf_path.exists():
                size_kb = pdf_path.stat().st_size / 1024
                print(f"✅ PDF exported: {pdf_path.name} ({size_kb:.1f} KB)")
            else:
                print("❌ PDF file not created")
                return False
            
            # Test HTML
            html_path = Path(tmpdir) / "test.html"
            export_to_html(
                fig,
                str(html_path),
                "Integration Test Report",
                {'test': 'data'}
            )
            
            if html_path.exists():
                size_kb = html_path.stat().st_size / 1024
                print(f"✅ HTML exported: {html_path.name} ({size_kb:.1f} KB)")
            else:
                print("❌ HTML file not created")
                return False
        
        plt.close(fig)
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_demo_command():
    """Test CLI demo command (dry run)."""
    print("\n" + "=" * 60)
    print("TEST 4: CLI Demo Command (Dry Run)")
    print("=" * 60)
    
    try:
        # Just verify the function exists and can be imported
        from src.cli import launch_demo
        print("✅ CLI demo command function exists")
        print("   To test fully, run: neuroops demo")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("\n🧪 NeuroOps Integration Test Suite")
    print("Testing Demo Mode & Export Features\n")
    
    results = []
    
    results.append(("Demo Data", test_demo_data()))
    results.append(("Citations", test_citations()))
    results.append(("PDF Export", test_pdf_export()))
    results.append(("CLI Demo", test_cli_demo_command()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)
    
    print(f"\nResults: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
