"""GPU acceleration tests for nougat_wrapper."""

import pytest
import torch
from nougat_wrapper import NougatOCR


@pytest.mark.skipif(
    not (torch.cuda.is_available() or torch.backends.mps.is_available()),
    reason="No GPU available"
)
def test_gpu_initialization():
    """Test that model initializes on GPU when available."""
    ocr = NougatOCR()

    # Check that model is on the correct device
    device = next(ocr.model.parameters()).device

    if torch.cuda.is_available():
        assert device.type == "cuda"
    elif torch.backends.mps.is_available():
        assert device.type == "mps"


def test_batch_size_detection():
    """Test automatic batch size detection."""
    ocr = NougatOCR()

    # Should auto-detect based on GPU availability
    if torch.cuda.is_available() or torch.backends.mps.is_available():
        assert ocr.batch_size > 1
    else:
        assert ocr.batch_size >= 1


def test_custom_batch_size():
    """Test custom batch size setting."""
    ocr = NougatOCR(batch_size=8)
    assert ocr.batch_size == 8
