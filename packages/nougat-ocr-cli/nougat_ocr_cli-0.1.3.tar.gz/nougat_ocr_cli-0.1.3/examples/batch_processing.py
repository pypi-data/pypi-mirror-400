#!/usr/bin/env python3
"""Batch processing example for nougat-ocr-cli."""

from nougat_wrapper import NougatOCR
from pathlib import Path
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_processing.py <directory>")
        print("Processes all PDF files in the specified directory.")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    # Find all PDFs
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF files")
    print(f"Initializing Nougat OCR...")
    ocr = NougatOCR()

    # Create output directory
    output_dir = input_dir / "ocr_output"
    output_dir.mkdir(exist_ok=True)

    # Process each PDF
    total_pages = 0
    total_failed = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing {pdf_path.name}...")

        try:
            result = ocr.extract_text(pdf_path)

            # Save output
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(result.text)

            total_pages += result.pages
            total_failed += result.placeholder_pages

            print(f"  ✓ Pages: {result.pages}, Failed: {result.placeholder_pages}")
            print(f"  Saved to: {output_path}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Processing Summary:")
    print(f"  Files processed: {len(pdf_files)}")
    print(f"  Total pages: {total_pages}")
    print(f"  Failed pages: {total_failed}")
    print(f"  Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
