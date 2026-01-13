#!/usr/bin/env python3
"""Basic usage example for nougat-ocr-cli."""

from nougat_wrapper import NougatOCR
from pathlib import Path
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python basic_usage.py <pdf_file>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)

    print(f"Initializing Nougat OCR...")
    ocr = NougatOCR()

    print(f"Processing {pdf_path.name}...")
    result = ocr.extract_text(pdf_path)

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Pages processed: {result.pages}")
    print(f"  Pages with issues: {result.placeholder_pages}")
    print(f"  Text length: {len(result.text):,} characters")
    print(f"{'='*60}\n")

    # Save to markdown file
    output_path = pdf_path.with_suffix('.md')
    output_path.write_text(result.text)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
