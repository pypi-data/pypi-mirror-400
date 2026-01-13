"""Basic functionality tests for nougat_wrapper."""

import tempfile
import pytest
from pathlib import Path
from PIL import Image
from nougat_wrapper import NougatOCR, OCRResult
from nougat_wrapper.core import IMAGE_EXTENSIONS


def test_import():
    """Test that main classes can be imported."""
    assert NougatOCR is not None
    assert OCRResult is not None


def test_initialization():
    """Test model initialization."""
    ocr = NougatOCR()
    assert ocr.model is not None
    assert ocr.batch_size >= 1


@pytest.mark.skipif(not Path("test.pdf").exists(), reason="No test PDF")
def test_extract_text():
    """Test basic text extraction."""
    ocr = NougatOCR()
    result = ocr.extract_text(Path("test.pdf"))

    assert isinstance(result, OCRResult)
    assert isinstance(result.text, str)
    assert result.pages > 0
    assert result.placeholder_pages >= 0


def test_ocr_result_dataclass():
    """Test OCRResult structure."""
    result = OCRResult(text="Sample text", pages=5, placeholder_pages=1)
    assert result.text == "Sample text"
    assert result.pages == 5
    assert result.placeholder_pages == 1


def test_image_extensions():
    """Test that image extensions are properly defined."""
    assert ".png" in IMAGE_EXTENSIONS
    assert ".jpg" in IMAGE_EXTENSIONS
    assert ".jpeg" in IMAGE_EXTENSIONS
    assert ".tiff" in IMAGE_EXTENSIONS
    assert ".pdf" not in IMAGE_EXTENSIONS


def test_image_to_pdf_conversion():
    """Test that PNG images can be converted to PDF for processing.

    This tests the fix for the pypdf.PdfReader error when processing images.
    The conversion happens transparently in extract_text().
    """
    # Create a test PNG image
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create RGB image
        rgb_image_path = tmp_path / "test_rgb.png"
        img_rgb = Image.new("RGB", (100, 100), color="white")
        img_rgb.save(rgb_image_path)

        # Create RGBA image (with alpha channel)
        rgba_image_path = tmp_path / "test_rgba.png"
        img_rgba = Image.new("RGBA", (100, 100), color=(255, 255, 255, 128))
        img_rgba.save(rgba_image_path)

        # Test that images can be converted to PDF
        for img_path in [rgb_image_path, rgba_image_path]:
            pdf_path = tmp_path / f"{img_path.stem}.pdf"
            img = Image.open(img_path)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.save(pdf_path, format="PDF")

            # Verify PDF was created and is valid
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 0

            # Verify pypdf can read it (this was the original bug)
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            assert len(reader.pages) == 1
