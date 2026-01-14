<h1 align="center">🧠 NeuroOps</h1>

<p align="center">
  <strong>A linter for neuroimaging data + universal format converter to BIDS</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/neuroops/"><img src="https://img.shields.io/pypi/v/neuroops" alt="PyPI"></a>
  <a href="https://pypi.org/project/neuroops/"><img src="https://img.shields.io/pypi/pyversions/neuroops" alt="Python"></a>
  <a href="https://github.com/arthurmoscheni/NeuroGit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/arthurmoscheni/NeuroGit" alt="License"></a>
  <a href="https://github.com/arthurmoscheni/NeuroGit/actions"><img src="https://github.com/arthurmoscheni/NeuroGit/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#format-converter">Converter</a> •
  <a href="#what-it-catches">Checks</a>
</p>

---

**Problem 1:** Your fMRIPrep run fails at 3am because the input was a renamed DICOM.

**Problem 2:** You have 50 EDF files to convert to BIDS. It takes 2 weeks of scripting.

**NeuroOps solves both.**

---

## Installation

```bash
pip install neuroops
```

For EEG format conversion:
```bash
pip install neuroops[convert]
```

---

## Quick Start

### Lint a file
```bash
neuroops check scan.nii.gz
```

```
🔍 Linting: scan.nii.gz
  ✅ gzip_magic: Valid gzip compression
  ✅ magic_bytes: Valid NIfTI header
  ✅ orientation_codes: Orientation defined
  ✅ snr: SNR = 8.2
  
✅ Result: PASS
```

### Convert to BIDS
```bash
neuroops convert recording.edf -o ./bids -s 01 -t rest
```

```
✅ Conversion successful!
   Output: ./bids/sub-01/eeg/sub-01_task-rest_eeg.edf
   Format: .edf → BIDS
```

---

## Format Converter

Convert any format to BIDS with one command. **Saves 2+ weeks of scripting.**

```bash
# Single file
neuroops convert recording.edf --output ./bids --subject 01 --task rest

# Batch convert folder
neuroops convert ./raw_data/ --output ./bids --subject 01 --batch
```

### Supported formats

| Format | Extension |
|--------|-----------|
| EDF | `.edf` |
| BDF | `.bdf` |
| EEGLAB | `.set` |
| BrainVision | `.vhdr` |
| Elekta/Neuromag | `.fif` |
| NIfTI | `.nii`, `.nii.gz` |
| DICOM | `.dcm`, folder |

---

## What It Catches

### Pipeline Killers

| Problem | Detection |
|---------|-----------|
| Fake .gz file | Checks `1f 8b` magic bytes |
| Corrupted header | Validates NIfTI magic |
| Zero-byte file | Size check |
| NaN in affine | Matrix validation |

### Silent Killers

| Problem | Detection |
|---------|-----------|
| TR mismatch | NIfTI header vs JSON sidecar |
| Missing orientation | sform/qform code check |
| 3D in func/ | Dimension validation |
| Orphan sidecars | File pairing check |

### Quality Warnings

| Check | Default |
|-------|---------|
| SNR | > 5.0 |
| Motion | < 2.0 voxels |
| Dropout | < 15% zeros |
| Ghost | < 5% background |

---

## CLI Reference

```bash
neuroops check file.nii.gz                    # Lint single file
neuroops check file.nii.gz --allow-abnormalities  # Skip anatomy checks
neuroops scan ./dataset                       # Lint directory

neuroops convert file.edf -o ./bids -s 01 -t rest  # Convert to BIDS
neuroops convert ./folder -o ./bids -s 01 --batch  # Batch convert
```

| Exit Code | Meaning |
|-----------|---------|
| 0 | PASS |
| 1 | WARN |
| 2 | FAIL |

---

## Python API

```python
from neuroops.validation import IntegrityChecker
from neuroops.converter import FormatConverter

# Lint
checker = IntegrityChecker()
results = checker.run_all_checks("scan.nii.gz")

# Convert
converter = FormatConverter()
result = converter.to_bids("recording.edf", "./bids", subject="01", task="rest")
```

---

## License

MIT
