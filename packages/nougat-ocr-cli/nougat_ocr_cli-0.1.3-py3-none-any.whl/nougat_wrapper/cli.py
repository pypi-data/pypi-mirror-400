"""Command-line interface for Nougat OCR."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nougat_wrapper.core import NougatOCR


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="nougat-ocr-cli",
        description="Extract text from PDFs using Nougat OCR with GPU acceleration.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input PDF file or image to process",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for markdown files (default: current directory)",
        default=Path.cwd(),
    )
    parser.add_argument(
        "--model",
        type=str,
        default="0.1.0-base",
        help="Model version to use (default: 0.1.0-base)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size for processing (auto-detected if not specified)",
    )
    parser.add_argument(
        "--full-precision",
        action="store_true",
        help="Use FP32 instead of BF16 (slower but more accurate)",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Disable markdown post-processing",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Page range to process (e.g., '0-5' or '1,3,5')",
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Parse pages if specified
    pages = None
    if args.pages:
        pages = _parse_pages(args.pages)

    # Initialize OCR
    print(f"Loading Nougat model ({args.model})...")
    ocr = NougatOCR(
        model_tag=args.model,
        batch_size=args.batch_size,
        markdown=not args.no_markdown,
        full_precision=args.full_precision,
    )

    # Process the file
    print(f"Processing: {args.input}")
    result = ocr.extract_text(args.input, pages=pages)

    # Write output
    args.output.mkdir(parents=True, exist_ok=True)
    output_file = args.output / f"{args.input.stem}.md"
    output_file.write_text(result.text, encoding="utf-8")

    print(f"Extracted {result.pages} pages ({result.placeholder_pages} failed)")
    print(f"Output: {output_file}")

    return 0


def _parse_pages(pages_str: str) -> list[int]:
    """Parse page specification string into list of page numbers."""
    pages = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))
    return pages


if __name__ == "__main__":
    sys.exit(main())
