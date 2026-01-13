"""Wrapper utilities for running Nougat OCR on PDFs."""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import List, Optional, Sequence

import torch
from nougat import NougatModel
from nougat.postprocessing import markdown_compatible
from nougat.utils.checkpoint import get_checkpoint
from nougat.utils.dataset import LazyDataset
from nougat.utils.device import default_batch_size, move_to_device
from PIL import Image

# Image extensions that should be converted to PDF before processing
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}


@dataclass
class OCRResult:
    """Container for OCR results with metadata."""

    text: str
    pages: int
    placeholder_pages: int


class NougatOCR:
    """
    Wrapper around Nougat's inference pipeline.

    Loads the model once and exposes a `.extract_text()` helper
    that returns a unified Markdown string for PDFs or images.

    Supports:
    - PDF files (multi-page)
    - Image files (PNG, JPG, TIFF, BMP, WebP) - converted to PDF internally
    - GPU acceleration for both CUDA and Apple Metal (MPS)
    """

    def __init__(
        self,
        model_tag: str = "0.1.0-base",
        checkpoint_path: Optional[Path] = None,
        batch_size: Optional[int] = None,
        markdown: bool = True,
        skipping: bool = True,
        full_precision: bool = False,
    ) -> None:
        """
        Initialize the Nougat OCR model.

        Args:
            model_tag: Model version to use (default: "0.1.0-base").
            checkpoint_path: Optional custom checkpoint path.
            batch_size: Number of pages to process at once. Auto-detected if None.
            markdown: Whether to convert output to markdown-compatible format.
            skipping: Whether to skip pages that fail processing.
            full_precision: Use FP32 instead of BF16 (slower but more accurate).
        """
        checkpoint = get_checkpoint(checkpoint_path, model_tag=model_tag)
        self.model = NougatModel.from_pretrained(checkpoint)

        # Detect MPS (Apple Silicon) or CUDA
        use_gpu = torch.cuda.is_available() or torch.backends.mps.is_available()

        self.model = move_to_device(
            self.model,
            bf16=not full_precision,
            cuda=use_gpu,
        )
        self.model.eval()
        self.batch_size = batch_size or (default_batch_size() if use_gpu else 1)
        if self.batch_size <= 0:
            self.batch_size = 1

        self.markdown = markdown
        self.skipping = skipping

    def extract_text(
        self,
        input_path: Path,
        pages: Optional[Sequence[int]] = None,
    ) -> OCRResult:
        """
        Run Nougat inference on a PDF or image file.

        Args:
            input_path: Path to a PDF file or image (PNG, JPG, etc.).
            pages: Optional list of zero-indexed page numbers to restrict OCR.
                   Ignored for single-image inputs.

        Returns:
            OCRResult containing Markdown text and bookkeeping metadata.
        """
        # Check if input is an image file that needs conversion to PDF
        suffix = input_path.suffix.lower()
        temp_pdf = None

        if suffix in IMAGE_EXTENSIONS:
            # Convert image to single-page PDF for LazyDataset compatibility
            temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            try:
                img = Image.open(input_path)
                if img.mode == "RGBA":
                    # Convert RGBA to RGB (PDF doesn't support alpha)
                    img = img.convert("RGB")
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(temp_pdf.name, format="PDF")
                pdf_path = Path(temp_pdf.name)
                pages = None  # Single image = single page
            except Exception as e:
                temp_pdf.close()
                Path(temp_pdf.name).unlink(missing_ok=True)
                raise RuntimeError(f"Failed to convert image to PDF: {e}") from e
        else:
            pdf_path = input_path

        try:
            return self._process_pdf(pdf_path, pages)
        finally:
            # Clean up temp PDF if we created one
            if temp_pdf is not None:
                temp_pdf.close()
                Path(temp_pdf.name).unlink(missing_ok=True)

    def _process_pdf(
        self,
        pdf_path: Path,
        pages: Optional[Sequence[int]] = None,
    ) -> OCRResult:
        """Internal method to process a PDF file."""
        dataset = LazyDataset(
            pdf_path,
            partial(self.model.encoder.prepare_input, random_padding=False),
            pages=pages,
        )
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            collate_fn=LazyDataset.ignore_none_collate,
        )

        predictions: List[str] = []
        processed_pages = 0
        placeholder_pages = 0

        for sample, is_last_page in dataloader:
            model_output = self.model.inference(
                image_tensors=sample,
                early_stopping=self.skipping,
            )

            for idx, output in enumerate(model_output["predictions"]):
                processed_pages += 1

                if output.strip() == "[MISSING_PAGE_POST]":
                    predictions.append(f"\n\n[MISSING_PAGE_EMPTY:{processed_pages}]\n\n")
                    placeholder_pages += 1
                elif self.skipping and model_output["repeats"][idx] is not None:
                    placeholder_pages += 1
                    if model_output["repeats"][idx] > 0:
                        predictions.append(
                            f"\n\n[MISSING_PAGE_FAIL:{processed_pages}]\n\n"
                        )
                    else:
                        predictions.append(
                            f"\n\n[MISSING_PAGE_EMPTY:{processed_pages}]\n\n"
                        )
                else:
                    cleaned = markdown_compatible(output) if self.markdown else output
                    predictions.append(cleaned)

                if is_last_page[idx]:
                    text = self._cleanup_text("".join(predictions))
                    return OCRResult(
                        text=text,
                        pages=processed_pages,
                        placeholder_pages=placeholder_pages,
                    )

        # Safety fallback (should not happen).
        return OCRResult(
            text=self._cleanup_text("".join(predictions)),
            pages=processed_pages,
            placeholder_pages=placeholder_pages,
        )

    @staticmethod
    def _cleanup_text(text: str) -> str:
        """Remove excessive whitespace from OCR output."""
        stripped = text.strip()
        stripped = re.sub(r"\n{3,}", "\n\n", stripped)
        return stripped.strip()
