# Nougat OCR CLI

Simple, batteries-included CLI wrapper for [Nougat OCR](https://github.com/facebookresearch/nougat) with GPU acceleration.

## Features

- GPU acceleration (CUDA & Apple Metal)
- Simple CLI interface
- Batch processing support
- Clean Markdown output
- Automatic model downloading
- Python API with type hints

## Installation

### From PyPI

```bash
pip install nougat-ocr-cli
```

### From GitHub

```bash
pip install git+https://github.com/rubenffuertes/nougat-ocr-cli.git
```

### From source

```bash
git clone https://github.com/rubenffuertes/nougat-ocr-cli.git
cd nougat-ocr-cli
uv pip install -e .
```

## CLI Usage

```bash
# Basic usage - outputs to current directory
nougat-ocr-cli document.pdf

# Specify output directory
nougat-ocr-cli document.pdf -o output/

# Process specific pages (zero-indexed)
nougat-ocr-cli document.pdf --pages 0-5
nougat-ocr-cli document.pdf --pages 1,3,5,7

# Use smaller model for faster processing
nougat-ocr-cli document.pdf --model 0.1.0-small

# Use full precision (FP32) for better accuracy
nougat-ocr-cli document.pdf --full-precision

# Set batch size manually
nougat-ocr-cli document.pdf --batch-size 4
```

### CLI Options

| Option | Description |
|--------|-------------|
| `input` | Input PDF file to process |
| `-o, --output` | Output directory (default: current directory) |
| `--model` | Model version (default: 0.1.0-base) |
| `--batch-size` | Batch size for processing (auto-detected) |
| `--full-precision` | Use FP32 instead of BF16 |
| `--no-markdown` | Disable markdown post-processing |
| `--pages` | Page range (e.g., '0-5' or '1,3,5') |

## Python API

```python
from nougat_wrapper import NougatOCR
from pathlib import Path

# Initialize (loads model to GPU automatically)
ocr = NougatOCR()

# Extract text from PDF
result = ocr.extract_text(Path("paper.pdf"))

print(f"Extracted {result.pages} pages")
print(f"Failed pages: {result.placeholder_pages}")
print(result.text)  # Markdown output
```

### Advanced Usage

```python
ocr = NougatOCR(
    model_tag="0.1.0-small",  # Use smaller model
    batch_size=4,              # Process 4 pages at once
    full_precision=True,       # Use FP32 instead of BF16
)

# Only OCR pages 0, 1, 2 (zero-indexed)
result = ocr.extract_text(pdf_path, pages=[0, 1, 2])
```

## Requirements

- Python 3.11 only (3.12+ not supported due to nougat-ocr dependencies)
- GPU recommended (CUDA or Apple Metal)
- ~1.3 GB for model weights (auto-downloaded)

## License

MIT
